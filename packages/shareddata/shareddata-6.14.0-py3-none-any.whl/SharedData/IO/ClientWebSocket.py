import os
import ssl
import time
import bson
import numpy as np
import pandas as pd
import lz4.frame as lz4f
import asyncio
import struct
import json
import aiohttp
from aiohttp import ClientSession, ClientWebSocketResponse
import asyncio
from typing import Optional, Tuple, AsyncGenerator



from SharedData.Logger import Logger
from SharedData.IO.SyncTable import SyncTable


class ClientWebSocket():

    """
    ClientWebSocket provides asynchronous static methods to manage WebSocket connections for subscribing to and publishing data tables.
    
    Methods:
        subscribe_table_thread(table, host, port, lookbacklines=1000, lookbackdate=None, snapshot=False, bandwidth=1e6):
            Continuously attempts to connect to a WebSocket server at the specified host and port to subscribe to updates for a given data table.
            Sends a subscription message and maintains the subscription loop, handling reconnection on errors with a delay.
    
        publish_table_thread(table, host, port, lookbacklines=1000, lookbackdate=None, snapshot=False, bandwidth=1e6):
            Continuously attempts to connect to a WebSocket server at the specified host and port to publish data for a given table.
            Sends a publish message, processes the initial response, and maintains the publishing loop, handling reconnection on errors with a delay.
    
    Parameters for both methods:
        table: The data table object to subscribe or publish.
        host (str): The WebSocket server hostname or IP address.
        port (int): The WebSocket server port number.
        lookbacklines (int, optional): Number of historical lines to request on subscription/publish. Default is 1000.
        lookback
    """

    @staticmethod
    async def get_websocket(endpoint: str) -> tuple[aiohttp.ClientSession, ClientWebSocketResponse]:
        """
        Establish an aiohttp ClientSession and WebSocket connection using environment
        proxy and SSL settings. The caller is responsible for closing both.

        Args:
            endpoint (str): The websocket URI to connect to.

        Returns:
            tuple: (aiohttp.ClientSession, aiohttp.ClientWebSocketResponse)
        """
        ws_kwargs = {}
        cafile = os.getenv('SHAREDDATA_CAFILE')
        if cafile:
            ws_kwargs['ssl'] = ssl.create_default_context(cafile=cafile)
        proxy_endpoint = os.getenv('PROXY_ENDPOINT')
        proxy_user = os.getenv('PROXY_USER')
        proxy_pwd = os.getenv('PROXY_PWD')
        if proxy_user and proxy_pwd and proxy_endpoint:
            proxy_method, proxy_host = proxy_endpoint.split('://')[0], proxy_endpoint.split('://')[1]
            ws_kwargs['proxy'] = f"{proxy_method}://{proxy_user}:{proxy_pwd}@{proxy_host}"
        elif proxy_endpoint:
            ws_kwargs['proxy'] = proxy_endpoint

        session = aiohttp.ClientSession()
        websocket = await session.ws_connect(endpoint, **ws_kwargs)
        return session, websocket

    @staticmethod
    async def subscribe_table_thread(table, host, port=None,
            lookbacklines=1000, lookbackdate=None, snapshot=False, 
            bandwidth=1e6, protocol='ws'):
        """
        Asynchronously subscribes to a specified data table via an aiohttp WebSocket connection,
        handling reconnections and data streaming.

        Parameters are the same as before.
        """
        if port is None:
            websocket_url = f"{protocol}://{host}"
        else:
            websocket_url = f"{protocol}://{host}:{port}"

        while True:
            try:
                session, websocket = await ClientWebSocket.get_websocket(websocket_url)                
                # Send the subscription message as text
                
                msg = SyncTable.subscribe_table_message(
                    table, lookbacklines, lookbackdate, snapshot, bandwidth)
                await websocket.send_str(msg)  # or send_bytes if needed

                # Initialize client for the subscription loop
                client = json.loads(msg)
                client['conn'] = websocket
                client['addr'] = (host, port)
                client = SyncTable.init_client(client, table)

                await SyncTable.websocket_subscription_loop(client)
                # Sleep after normal termination (very rare)
                await asyncio.sleep(15)

            except Exception as e:
                msg = 'Retrying subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                    table.source, table.tablename, str(e))
                Logger.log.warning(msg)
            finally:
                if websocket is not None:
                    await websocket.close()
                if session is not None:
                    await session.close()
                Logger.log.info('Websocket closed')
                await asyncio.sleep(15)
    
    @staticmethod
    async def publish_table_thread(table, host, port=None,
            lookbacklines=1000, lookbackdate=None, snapshot=False,
            bandwidth=1e6, protocol='ws'):

        """
        '''
        Asynchronously maintains a persistent WebSocket connection to publish updates from a specified table.
        
        This coroutine continuously attempts to connect to a WebSocket server at the given host and port,
        subscribes to updates for the specified table with optional parameters such as lookback lines,
        lookback date, snapshot mode, and bandwidth limit. Upon successful subscription, it listens for
        incoming messages and processes them in a publish loop. If the connection is lost or an error
        occurs, it logs the issue and retries the subscription after a delay.
        
        Parameters:
            table (Table): The table object containing database, period, source, and tablename attributes.
            host (str): The hostname or IP address of the WebSocket server.
            port (int): The port number of the WebSocket server.
            lookbacklines (int, optional): Number of historical lines to retrieve on subscription. Default is 1000.
            lookbackdate (str or None, optional): Date string to specify the starting point for historical data. Default is None.
            snapshot (bool, optional): Whether to request a snapshot of the current table state. Default is False.
            bandwidth (float, optional): Bandwidth limit for the subscription in bits per second. Default is 1e6.
        
        Raises
        """
        while True:
            try:                
                
                if port is None:
                    websocket_url = f"{protocol}://{host}"
                else:
                    websocket_url = f"{protocol}://{host}:{port}"
                
                session, websocket = await ClientWebSocket.get_websocket(websocket_url)
                # Send the subscription message
                msg = SyncTable.publish_table_message(
                    table, lookbacklines, lookbackdate, snapshot, bandwidth)                
                await websocket.send_str(msg)
                response = await websocket.receive_json()
                
                # Subscription loop
                client = json.loads(msg)
                client['conn'] = websocket
                client['table'] = table
                client['addr'] = (host, port)
                client.update(response)
                client = SyncTable.init_client(client,table)
                
                await SyncTable.websocket_publish_loop(client)
                await asyncio.sleep(15)

            except Exception as e:
                msg = 'Retrying subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.warning(msg)
            finally:
                if websocket is not None:
                    await websocket.close()
                if session is not None:
                    await session.close()
                Logger.log.info('Websocket closed')
                await asyncio.sleep(15)
        
    @staticmethod
    async def subscribe_stream(
        database: str,
        period: str,
        source: str,
        tablename: str,
        user: str = 'master',
        endpoint: Optional[str] = None,
        token: Optional[str] = None,
        groupid: Optional[str] = None,
        offset: str = 'latest'
    ) -> AsyncGenerator[dict, None]:
        session = None
        websocket = None

        while True:
            try:
                endpoint_val = endpoint or os.environ['SHAREDDATA_WS_ENDPOINT']
                session, websocket = await ClientWebSocket.get_websocket(endpoint_val)
                login_msg = {
                    'action' : 'subscribe',
                    'container' : 'stream',
                    'database' : database,
                    'period' : period,
                    'source' : source,
                    'tablename' : tablename,
                    'user' : user,
                    'token' : token or os.environ['SHAREDDATA_TOKEN'],
                    'offset' : offset,
                }
                if groupid is not None:
                    login_msg['groupid'] = groupid
                await websocket.send_str(json.dumps(login_msg))

                login_response = await websocket.receive_json()
                if login_response.get('message') != 'login success!':
                    Logger.log.error(f'Failed to subscribe: {login_response}')
                    return

                Logger.log.info(f'Subscribed to stream {database}/{period}/{source}/{tablename}')
                while True:
                    msg = await websocket.receive_bytes()
                    msgdict = bson.BSON.decode(lz4f.decompress(msg))
                    for _msg in msgdict.get('data', []):
                        yield bson.BSON.decode(lz4f.decompress(_msg))

            except Exception as e:
                Logger.log.error(f'subscribe_stream() error: {e}')
                await asyncio.sleep(5)
            finally:
                if websocket:
                    try:
                        await websocket.close()
                    except Exception as e:
                        Logger.log.error(f'Error closing websocket: {e}')
                    finally:
                        websocket = None
                if session:
                    try:
                        await session.close()
                    except Exception as e:
                        Logger.log.error(f'Error closing session: {e}')
                    finally:
                        session = None
                Logger.log.info('Websocket closed')
        
    @staticmethod
    async def publish_stream(
        database: str,
        period: str,
        source: str,
        tablename: str,
        user: str = 'master',
        endpoint: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Tuple[asyncio.Queue, asyncio.Task]:
        """
        Publishes dictionaries from a queue to a websocket stream.
        Returns the queue and a background publishing task.
        """
        
        BATCH_SIZE = 10000
        BATCH_TIMEOUT = 0.02  # seconds
        queue: asyncio.Queue = asyncio.Queue(maxsize=50000)

        async def _worker():
            while True:
                session = websocket = None
                try:
                    session, websocket = await ClientWebSocket.get_websocket(
                        endpoint or os.environ['SHAREDDATA_WS_ENDPOINT']
                    )
                    login_msg = {
                        'action': 'publish',
                        'container': 'stream',
                        'database': database,
                        'period': period,
                        'source': source,
                        'tablename': tablename,
                        'user': user,
                        'token': token or os.environ['SHAREDDATA_TOKEN'],
                    }
                    await websocket.send_str(json.dumps(login_msg))
                    login_response = await websocket.receive_json()
                    if login_response.get('message') != 'login success!':
                        Logger.log.error(f'Failed to login: {login_response}')
                        return
                    Logger.log.info(f'Publishing to stream {database}/{period}/{source}/{tablename}')
                    while True:
                        batch = []
                        msgdict = await queue.get()
                        batch.append(msgdict)
                        for _ in range(BATCH_SIZE - 1):
                            try:
                                msgdict = await asyncio.wait_for(queue.get(), timeout=BATCH_TIMEOUT)
                                batch.append(msgdict)
                            except asyncio.TimeoutError:
                                break
                        try:
                            msg_bytes = bson.BSON.encode({'data': batch})
                            compressed_msg = lz4f.compress(msg_bytes)
                            await websocket.send_bytes(compressed_msg)
                        except Exception as e:
                            Logger.log.error(f'Error sending message batch: {e}')
                            break
                except asyncio.CancelledError:
                    # Allow cancellation to propagate
                    raise
                except Exception as e:
                    Logger.log.error(f'Error in websocket publishing worker: {e}')
                finally:
                    if websocket is not None:
                        await websocket.close()
                    if session is not None:
                        await session.close()
                    Logger.log.info('Websocket closed')
                await asyncio.sleep(15)
        task = asyncio.create_task(_worker())
        return queue, task

if __name__ == '__main__':
    import sys
    import time
    import argparse
    from SharedData.Logger import Logger
    from SharedData.SharedData import SharedData

    parser = argparse.ArgumentParser(
        description="ClientWebSocket command-line utility"
    )
    parser.add_argument("host", help="Host IP to bind")
    parser.add_argument("port", type=int, help="Port to bind")
    parser.add_argument("database", help="Database name")
    parser.add_argument("period", help="Period")
    parser.add_argument("source", help="Source")
    parser.add_argument("tablename", help="Table name")
    parser.add_argument(
        "pubsub", choices=["publish", "subscribe"], 
        help="Choose publish or subscribe"
    )

    args = parser.parse_args()

    shdata = SharedData('SharedData.IO.ClientWebSocket', user='master')
    table = shdata.table(args.database, args.period, args.source, args.tablename)
    if args.pubsub == 'publish':
        table.publish(args.host, args.port)
    elif args.pubsub == 'subscribe':
        table.subscribe(args.host, args.port)

    while True:
        time.sleep(1)