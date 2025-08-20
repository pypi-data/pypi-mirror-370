
import asyncio
import time
import math
import bson
import lz4.frame
import sys
from aiohttp import web
import os
import json
import traceback
from gunicorn.app.base import BaseApplication


from SharedData.SharedData import SharedData
shdata = SharedData('SharedData.IO.ServerWebSocket',user='master')
from SharedData.Logger import Logger
from SharedData.IO.SyncTable import SyncTable

MAX_PAYLOAD_SIZE = 64 * 1024         # 64 KB per message to client (stream subscribe)
MAX_INPUT_MSG_SIZE = 512 * 1024      # 512 KB max input for publish

class ServerWebSocket:
    """
    Websocket/stream handler. Per-worker user cache only.
    """
    BUFF_SIZE = int(128 * 1024)
    def __init__(self, app, shdata):
        # Store per-process cache for users (no global)
        self._users_lock = asyncio.Lock()
        self._users = {}
        # Known clients (per worker)
        self.clients = {}
        self.clients_lock = asyncio.Lock()
        self.shdata = shdata
        self.app = app

    async def fetch_users(self):
        """
        Query fresh users from DB.
        """
        async with self._users_lock:
            user_collection = self.shdata.collection('Symbols', 'D1', 'AUTH', 'USERS', user='SharedData')
            _users = list(user_collection.find({}))
            self._users = {user['token'] : user for user in _users}
            # Logger.log.info(f"[USERS] Refreshed to {len(self._users)} users.")

    async def refresh_users_periodically(self):
        """
        Run a user refresh every 60 seconds.
        """
        while True:
            try:
                await self.fetch_users()
            except Exception as e:
                Logger.log.warning(f"User refresh failed: {e}")
            await asyncio.sleep(60)

    def check_permissions(self, reqpath, permissions, method):
        """
        Iteratively check if given path/method are permitted.
        """
        node = permissions
        for segment in reqpath:
            if segment in node:
                node = node[segment]
            elif '*' in node:
                node = node['*']
            else:
                return False
            if not isinstance(node, dict):
                if '*' in node:
                    return True
                if isinstance(node, list) and method in node:
                    return True
                return False
        if '*' in node:
            return True
        if method in node:
            return True
        return False

    async def handle_client_thread(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        addr = request.remote

        # Add to clients map
        async with self.clients_lock:
            self.clients[ws] = {
                'watchdog': time.time_ns(),
                'transfer_rate': 0.0,
            }
        client = self.clients[ws]
        client['conn'] = ws
        client['addr'] = addr
        try:
            await self.handle_client_websocket(client)
        except Exception as e:
            # Use exception to log full trace and error message
            Logger.log.error(f"Client {addr} exception:\n{''.join(traceback.format_exception(type(e), e, e.__traceback__))}")
        finally:
            if 'stream' in client:
                try:
                    await client['stream'].async_close()
                except Exception:
                    pass
            async with self.clients_lock:
                self.clients.pop(ws, None)
            Logger.log.info(f"Client {addr} disconnected.")
            await ws.close()
        return ws

    async def handle_client_websocket(self, client):
        ws = client['conn']
        client['authenticated'] = False

        # --- LOGIN & AUTH ---
        try:
            login_msg = await ws.receive_json()
        except Exception as e:
            raise Exception("Invalid JSON at login") from e

        required_fields = ['token', 'user', 'database', 'period', 'source', 'container', 'tablename', 'action']
        if not all(field in login_msg for field in required_fields):
            raise ValueError("Missing required fields in login message")
        client['watchdog'] = time.time_ns()

        token = login_msg['token']
        async with self._users_lock:
            user_obj = self._users.get(token)
        if user_obj is None:
            await asyncio.sleep(3)  # Slow down brute force
            errmsg = f'Unknown token {token} authentication failed!'
            Logger.log.error(f"{errmsg} from {client['addr']}")
            await ws.send_json({'message': errmsg})
            raise Exception(errmsg)

        client.update(login_msg)
        client['userdata'] = user_obj

        reqpath = f"{login_msg['user']}/{login_msg['database']}/{login_msg['period']}/{client['source']}/{client['container']}/{login_msg['tablename']}"
        reqpath = reqpath.split('/')
        method = 'POST' if client['action'] == 'publish' else ('GET' if client['action'] == 'subscribe' else '')
        if not method:
            msg = 'Unknown action: %s' % client['action']
            raise Exception(msg)
        if not self.check_permissions(reqpath, user_obj['permissions'], method):
            await asyncio.sleep(3)
            errmsg = f"Client {client['addr']} permission denied!"
            Logger.log.error(errmsg)
            await ws.send_json({'message': errmsg})
            await asyncio.sleep(0)
            raise Exception(errmsg)

        await ws.send_json({'message': 'login success!'})
        Logger.log.info(f"New client connected: {client['userdata'].get('symbol','?')} {client['addr']} {'/'.join(reqpath)}")

        # --- Subscription/Publishing ---
        if client['action'] == 'subscribe':
            if client['container'] == 'table':
                client = SyncTable.init_client(client)
                await SyncTable.websocket_publish_loop(client)
            elif client['container'] == 'stream':
                await self.stream_subscribe_loop(client)
        elif client['action'] == 'publish':
            if client['container'] == 'table':
                client = SyncTable.init_client(client)
                responsemsg = {
                    'mtime': float(client['records'].mtime),
                    'count': int(client['records'].count)
                }
                await ws.send_json(responsemsg)
                await SyncTable.websocket_subscription_loop(client)
            elif client['container'] == 'stream':
                await self.stream_publish_loop(client)

    async def stream_subscribe_loop(self, client):
        """
        Subscribe the given client's connection to a data stream.
        Batches messages for throughput; tracks per-client upload/download.
        Expected client fields: conn (websocket-like), database, period, source, tablename.
        """
        conn = client['conn']
        addr = client['addr']
        client['upload'] = 0
        client['download'] = 0
        groupid = client.get('groupid', f"ws-{addr}")
        offset = client.get('offset', 'latest')
        shdata = self.shdata
        stream = None

        try:
            stream = shdata.stream(
                client['database'], client['period'], client['source'], client['tablename'],
                user=client.get('user', 'master'), use_aiokafka=True, create_if_not_exists=False
            )
            client['stream'] = stream
            await stream.async_subscribe(groupid=groupid, offset=offset)

            while True:
                try:
                    # Timeout pulls after 1s; don't compress
                    msgs = await stream.async_poll(groupid, timeout=1000, max_records=500, decompress=False)
                    if msgs:
                        payload = lz4.frame.compress(bson.BSON.encode({'data': msgs}))
                        client['upload'] += len(payload)
                        await conn.send_bytes(payload)
                    else:
                        # Prevent busy-spin if stream idle
                        payload = lz4.frame.compress(bson.BSON.encode({'ping': time.time_ns()}))
                        client['upload'] += len(payload)
                        await conn.send_bytes(payload)
                        
                except asyncio.CancelledError:
                    Logger.log.info(f"stream_subscribe_loop():{addr} cancelled.")
                    raise
                except Exception as loop_err:
                    Logger.log.warning(f"stream_subscribe_loop():{addr} inner error: {loop_err}")
                    break
        except Exception as e:
            Logger.log.error(f"stream_subscribe_loop():{addr}\n{traceback.format_exc()}")
        finally:     
            if stream:
                close_func = getattr(stream, "close", None)
                if callable(close_func):
                    try:
                        await close_func()
                    except Exception:
                        pass
            try:
                await conn.close()
            except Exception:
                pass

    async def stream_publish_loop(self, client):
        """
        Receive lz4-compressed BSON messages from websocket, validate size, publish to stream.
        """
        conn = client['conn']
        addr = client['addr']
        client['upload'] = 0
        client['download'] = 0
        shdata = self.shdata
        try:
            stream = shdata.stream(
                client['database'], client['period'], client['source'], client['tablename'],
                user=client.get('user', 'master'), use_aiokafka=True
            )
            client['stream'] = stream
            while True:
                msg_bytes = await conn.receive_bytes()
                if (not msg_bytes) or (len(msg_bytes) > MAX_INPUT_MSG_SIZE):
                    Logger.log.warning(f"Client {addr} sent too large or empty message, closing.")
                    break
                try:
                    msg = bson.BSON.decode(lz4.frame.decompress(msg_bytes))
                except Exception:
                    Logger.log.warning(f"BSON/LZ4 decode error from {addr}, closing connection.")
                    break
                client['download'] += len(msg_bytes)
                await stream.async_extend(msg['data'])
        except Exception as e:
            Logger.log.error(f"stream_publish_loop():{addr} \n{traceback.format_exc()}")
        finally:
            try:
                await conn.close()
            except Exception:
                pass

    async def send_heartbeat(self, host, port):
        """
        Emit periodic stats for this worker only.
        """
        last_total_upload = 0
        last_total_download = 0
        lasttime = time.time()
        while True:
            async with self.clients_lock:
                clients_snapshot = list(self.clients.items())
            nclients = len(clients_snapshot)
            total_upload = sum(c.get('upload', 0) for _, c in clients_snapshot)
            total_download = sum(c.get('download', 0) for _, c in clients_snapshot)
            te = time.time() - lasttime
            lasttime = time.time()
            upload = max(0, (total_upload - last_total_upload) / te)
            download = max(0, (total_download - last_total_download) / te)
            last_total_download = total_download
            last_total_upload = total_upload
            Logger.log.debug('#heartbeat#host:%s,port:%i,clients:%i,download:%.3fMB/s,upload:%.3fMB/s' %
                            (host, port, nclients, download/1024/1024, upload/1024/1024))
            await asyncio.sleep(15)

# ---- Gunicorn Embedding ----

class GunicornAioHttpApp(BaseApplication):
    """
    Embedded Gunicorn using aiohttp application.
    """
    def __init__(self, aiohttp_app, options: dict):
        self._aiohttp_app = aiohttp_app
        self._options = options
        super().__init__()

    def load_config(self):
        for key, value in self._options.items():
            if value is not None:
                self.cfg.set(key, value)

    def load(self):
        return self._aiohttp_app

# ====== MAIN APP SETUP ======
def create_app(args):
    app = web.Application()
    shdata = SharedData('SharedData.IO.ServerWebSocket', user='master')
    SyncTable.shdata = shdata

    # Prepare one handler per worker for safety
    handler = ServerWebSocket(app, shdata)

    # Attach as 'handler' for router
    app['handler'] = handler

    async def websocket_entry(request):
        return await handler.handle_client_thread(request)

    app.router.add_get('/', websocket_entry)

    async def on_startup(app):
        # Initial cache (non-blocking!)
        await handler.fetch_users()
        # Periodic user refresh task per worker
        app['user_refresh_task'] = asyncio.create_task(handler.refresh_users_periodically())
        # Per-worker stats heartbeat
        app['heartbeat'] = asyncio.create_task(handler.send_heartbeat(args.host, args.port))

    async def on_cleanup(app):
        tasks = []
        if 'user_refresh_task' in app:
            app['user_refresh_task'].cancel()
            tasks.append(app['user_refresh_task'])
        if 'heartbeat' in app:
            app['heartbeat'].cancel()
            tasks.append(app['heartbeat'])
        await asyncio.gather(*tasks, return_exceptions=True)

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

# ========== entrypoint ==========
if __name__ == '__main__':
    import argparse
    Logger.log.info('ROUTINE STARTED!')
    parser = argparse.ArgumentParser(description="Run SharedData WebSocket via Gunicorn")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--nproc", type=int, default=4, help="Number of Gunicorn worker processes")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()

    # Single aiohttp app instance (each worker gets a copy)
    app = create_app(args)

    gunicorn_opts = {
        "bind": f"{args.host}:{args.port}",
        "workers": args.nproc,
        "worker_class": "aiohttp.worker.GunicornWebWorker",
        "timeout": args.timeout,
        "loglevel": args.log_level,
    }
    # All handling is in GunicornAioHttpApp:
    GunicornAioHttpApp(app, gunicorn_opts).run()
