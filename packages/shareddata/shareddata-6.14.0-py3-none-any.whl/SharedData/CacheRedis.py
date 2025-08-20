from fnmatch import fnmatch
import pandas as pd
import numpy as np
import time
import os
import queue
from redis import Redis
from redis.cluster import RedisCluster, ClusterNode
from redis.asyncio import Redis as RedisAsync
from redis.asyncio.cluster import RedisCluster as RedisClusterAsync
from redis.asyncio.cluster import ClusterNode as ClusterNodeAsync
from redis.exceptions import WatchError    
from typing import Set, Dict
import bson
import asyncio

from datetime import datetime, timezone

from SharedData.Logger import Logger
from SharedData.Database import DATABASE_PKEYS

class CacheRedis:
    def __init__(self, database, period, source, tablename, user='master'):
        """Initialize RedisCluster connection."""
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.user = user

        self.path = f'{user}/{database}/{period}/{source}/cache/{tablename}'
        self.data = {}                
        self.queue = asyncio.Queue()
        self._flush_task = None
        self._flush_lock = asyncio.Lock()        
        self.pkeycolumns = DATABASE_PKEYS[database]
        self.mtime = datetime(1970,1,1, tzinfo=timezone.utc)

        if not 'REDIS_CLUSTER_NODES' in os.environ:
            raise Exception('REDIS_CLUSTER_NODES not defined')
        startup_nodes = []
        for node in os.environ['REDIS_CLUSTER_NODES'].split(','):
            startup_nodes.append( (node.split(':')[0], int(node.split(':')[1])) )
        if len(startup_nodes)>1:
            startup_nodes = [ClusterNode(node[0], int(node[1])) 
                             for node in startup_nodes]
            self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=False)            
            self.redis_async = RedisClusterAsync(startup_nodes=startup_nodes, decode_responses=False)
        else:
            node = startup_nodes[0]
            host, port = node[0], int(node[1])
            self.redis = Redis(host=host, port=port, decode_responses=False)
            self.redis_async = RedisAsync(host=host, port=port, decode_responses=False)

        self.header = CacheHeader(self)

        if not self.header['cache->counter']:
            self.header['cache->counter'] = 0

        self.set_pkeys = f"{{{self.path}}}#pkeys"
                
    def __getitem__(self, pkey):
        if not isinstance(pkey, str):
            raise Exception('pkey must be a string')
        if '#' in pkey:
            raise Exception('pkey cannot contain #')
        _bson = self.redis.get(self.get_hash(pkey))
        if _bson is None:
            return {}
        value = bson.BSON.decode(_bson)        
        self.data[pkey] = value
        return value
    
    def get(self, pkey):        
        return self.__getitem__(pkey)
    
    def mget(self, pkeys: list[str]) -> list[dict]:
        """
        Retrieve multiple entries from Redis in a single call.

        :param pkeys: List of primary keys (as strings)
        :return: List of decoded dicts (empty dict if missing)
        """
        if len(pkeys) == 0:
            return []
        if not isinstance(pkeys, list):
            raise Exception('pkeys must be a list of strings')
        if any('#' in pkey for pkey in pkeys):
            raise Exception('pkeys cannot contain #')        
        redis_keys = [self.get_hash(pkey) for pkey in pkeys]
        vals = self.redis.mget(redis_keys)
        result = []
        for pkey, _bson in zip(pkeys, vals):
            if _bson is None:
                result.append({})
            else:
                value = bson.BSON.decode(_bson)
                self.data[pkey] = value
                result.append(value)
        return result

    def load(self) -> dict:
        """Load all data from Redis into the cache dictionary using mget for efficiency."""        
        pkeys = self.list_keys('*')
        self.mget(pkeys)
        return self.data

    def get_pkey(self, value):
        key_parts = [
            str(value[col])
            for col in self.pkeycolumns
            if col in ['symbol','portfolio','tag']
        ]        
        return ','.join(key_parts)

    def get_hash(self, pkey: str) -> str:
        """
        Return the full Redis key for a given pkey, using a hash tag for cluster slot affinity.
        All keys with the same path will map to the same slot.
        """
        return f"{{{self.path}}}:{pkey}"
     
    def update_keys(self, keyword='*', count=None):
        """
        Scan all keys matching {self.path}:<pkey> and update the set of pkeys for consistency.

        Args:
            keyword: pattern for key matching in pkey part (supports wildcards, defaults to *)
            count: scan batch size (None means default)
            clear_first: whether to clear the set of pkeys before updating
        Returns:
            List of pkeys added to the set.
        """        

        pattern = f"{{{self.path}}}:{keyword}"
        result = []
        
        # Gather the pkeys to add
        scan_iter_kwargs = {'match': pattern}
        if count is not None:
            scan_iter_kwargs['count'] = count

        for key in self.redis.scan_iter(**scan_iter_kwargs):
            # key may be bytes
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            parts = key.split(':', 1)
            if len(parts) > 1:
                pkey = parts[1]
                result.append(pkey)

        # Add all the pkeys to the set in one command for efficiency
        self.redis.delete(self.set_pkeys)
        if result:
            self.redis.sadd(self.set_pkeys, *result)

        return result
    
    def list_keys(self, keyword='*', count=None):
        """
        Returns list of pkeys from the set, filtered by optional keyword (supports * wildcards).
        """
        # Get all pkeys (members of the set)
        keys = self.redis.smembers(self.set_pkeys)
        # smembers returns bytes, so decode
        decoded_keys = [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
        
        # Replace '*' with real wildcard filter
        if keyword == '*' or not keyword:
            filtered_keys = decoded_keys
        else:
            filtered_keys = [k for k in decoded_keys if fnmatch(k, keyword)]

        # Respect the count argument if present
        if count is not None:
            filtered_keys = filtered_keys[:count]

        return filtered_keys

    # def __setitem__(self, pkey, new_value):
    #     if ':' in pkey:
    #         raise Exception('pkey cannot contain :')
    #     if pkey in self.data:
    #         self.data[pkey] = self.recursive_update(self.data[pkey],new_value)
    #     else:
    #         self.data[pkey] = new_value
    #     _bson = bson.BSON.encode(self.data[pkey])
    #     self.redis.set(self.get_hash(pkey), _bson)
    #     self.redis.sadd(self.set_pkeys, pkey)

    
    def __setitem__(self, pkey, new_value):
        if not isinstance(pkey, str):
            raise Exception('pkey must be a string')
        if ':' in pkey or '#' in pkey:
            raise Exception('pkey cannot contain : or #')

        rhash = self.get_hash(pkey)

        # Retry on concurrent writers
        for _ in range(16):
            # Use transactional pipeline so WATCH is supported in RedisCluster
            pipe = self.redis.pipeline(transaction=True)
            try:
                pipe.watch(rhash)
                prev = pipe.get(rhash)
                current = bson.BSON.decode(prev) if prev else {}

                # Merge with the latest value from Redis (not only local cache)
                merged = (self.recursive_update(current, new_value)
                          if current else dict(new_value))

                _bson = bson.BSON.encode(merged)

                pipe.multi()
                pipe.set(rhash, _bson)
                pipe.sadd(self.set_pkeys, pkey)  # same hash tag => same slot
                pipe.execute()

                # Commit to local cache after successful write
                self.data[pkey] = merged
                return
            except WatchError:
                # Key changed; retry
                try:
                    pipe.reset()
                except Exception:
                    pass
                continue
            finally:
                try:
                    pipe.reset()
                except Exception:
                    pass

        raise Exception('Concurrent update conflict: failed to set value after retries')
    
    def recursive_update(self, original, updates):
        """
        Recursively update the original dictionary with updates from the new dictionary,
        preserving unmentioned fields at each level of depth.
        """
        for key, value in updates.items():
            if isinstance(value, dict):
                # Get existing nested dictionary or use an empty dict if not present
                original_value = original.get(key, {})
                if isinstance(original_value, dict):
                    # Merge recursively
                    original[key] = self.recursive_update(original_value, value)
                else:
                    # Directly assign if original is not a dict
                    original[key] = value
            else:
                # Non-dict values are directly overwritten
                original[key] = value
        return original

    def set(self, new_value, pkey=None):
        if pkey is None:
            pkey = self.get_pkey(new_value)
        self.__setitem__(pkey, new_value)

    async def async_set(self, new_value):
        """
        Asynchronously set a message in the cache and signal the queue.

        Raises:
            Exception: 
        """        
        async with self._flush_lock:
            if self._flush_task is None or self._flush_task.done():
                self._flush_task = asyncio.create_task(self.async_flush_loop())
        
        if isinstance(new_value, list):
            for item in new_value:
                await self.queue.put(item)
        else:
            await self.queue.put(new_value)
        
    # async def async_flush_loop(self, conflate_ms = 50) -> None:
    #     """Flush the queue to Redis asynchronously."""        
    #     try:
    #         while True:            
    #             flush_pkeys = set()
                
    #             new_value = await self.queue.get()

    #             tini = time.time_ns()

    #             pkey = self.get_pkey(new_value)
    #             flush_pkeys.add(pkey)
    #             if pkey in self.data:
    #                 self.data[pkey] = self.recursive_update(self.data[pkey], new_value)
    #             else:
    #                 self.data[pkey] = new_value
                                
    #             # Keep draining the queue until empty
    #             while not self.queue.empty() and (time.time_ns() - tini) < conflate_ms * 1_000_000:
    #                 new_value = await self.queue.get()
    #                 pkey = self.get_pkey(new_value)
    #                 flush_pkeys.add(pkey)
    #                 if pkey in self.data:
    #                     self.data[pkey] = self.recursive_update(self.data[pkey], new_value)
    #                 else:
    #                     self.data[pkey] = new_value
                                                    
    #             pipe = self.redis_async.pipeline()
    #             try:
    #                 for pkey in flush_pkeys:
    #                     rhash = self.get_hash(pkey)
    #                     _bson = bson.BSON.encode(self.data[pkey])
    #                     pipe.set(rhash, _bson)  
    #                 pipe.sadd(self.set_pkeys, *flush_pkeys)
    #                 await pipe.execute()                    
    #             except Exception as e:
    #                 Logger.log.error(f"Redis pipeline error: {e}")
    #             finally:
    #                 await pipe.reset()
    #             await self.header.async_incrby("cache->counter", len(flush_pkeys))
    #     except Exception as e:
    #         Logger.log.error(f"Error in async_flush_loop: {e}")

    async def async_flush_loop(self, conflate_ms = 50) -> None:
        """Flush the queue to Redis asynchronously."""        
        try:
            while True:            
                flush_pkeys = set()
                get_pkeys = set()
                
                new_value = await self.queue.get()

                tini = time.time_ns()

                pkey = self.get_pkey(new_value)
                flush_pkeys.add(pkey)
                get_pkeys.add(pkey)
                self.__getitem__(pkey)  # Ensure the key is loaded into local cache
                if pkey in self.data:
                    self.data[pkey] = self.recursive_update(self.data[pkey], new_value)
                else:
                    self.data[pkey] = new_value
                                
                # Keep draining the queue until empty
                while not self.queue.empty() and (time.time_ns() - tini) < conflate_ms * 1_000_000:                    
                    new_value = await self.queue.get()
                    pkey = self.get_pkey(new_value)
                    flush_pkeys.add(pkey)
                    if not pkey in get_pkeys:
                        get_pkeys.add(pkey)
                        self.__getitem__(pkey)
                    if pkey in self.data:
                        self.data[pkey] = self.recursive_update(self.data[pkey], new_value)
                    else:
                        self.data[pkey] = new_value
                                                    
                pipe = self.redis_async.pipeline()
                try:
                    for pkey in flush_pkeys:
                        rhash = self.get_hash(pkey)
                        _bson = bson.BSON.encode(self.data[pkey])
                        pipe.set(rhash, _bson)  
                    pipe.sadd(self.set_pkeys, *flush_pkeys)
                    await pipe.execute()                    
                except Exception as e:
                    Logger.log.error(f"Redis pipeline error: {e}")
                finally:
                    await pipe.reset()
                await self.header.async_incrby("cache->counter", len(flush_pkeys))
        except Exception as e:
            Logger.log.error(f"Error in async_flush_loop: {e}")

    def __delitem__(self, pkey: str):
        self.redis.delete(self.get_hash(pkey))
        self.redis.srem(self.set_pkeys, pkey)

    def clear(self):
        """Clear the cache."""
        # Get all pkeys
        pkeys = self.list_keys('*')
        # Delete all redis hash keys
        if pkeys:
            redis_keys = [self.get_hash(pkey) for pkey in pkeys]
            for i in range(0, len(redis_keys), 1000):
                self.redis.delete(*redis_keys[i:i+1000])
        # Delete the set of pkeys itself
        self.redis.delete(self.set_pkeys)
        # Clear local cache
        self.data = {}
        header_keys = list(self.header)
        if header_keys:
            redis_header_keys = [self.header.get_hash(k) for k in header_keys]
            self.redis.delete(*redis_header_keys)
    
    def __iter__(self):
        for key in self.list_keys():
            yield key
       
class CacheHeader():    
    """
    A dict-like interface for cached headers stored in Redis.
    Supports basic mapping operations: get, set, delete, iterate.
    """
    def __init__(self, cache):
        self.cache = cache

    def get_hash(self, pkey: str) -> str:
        return f"{{{self.cache.path}}}#{pkey}"

    def __getitem__(self, pkey: str):
        """Retrieve a header value by key."""
        val = self.cache.redis.get(self.get_hash(pkey))
        return val
    
    def get(self, pkey: str, default=None):
        """Get a header value by key, returning default if not found."""
        val = self.__getitem__(pkey)
        return val if val is not None else default

    def __setitem__(self, pkey: str, value):
        """Set a header value by key."""
        self.cache.redis.set(self.get_hash(pkey), value)

    def set(self, pkey, value):
        """Set a header value by key."""
        self.cache.redis.set(self.get_hash(pkey), value)

    def __delitem__(self, pkey: str):
        """Delete a header key."""
        self.cache.redis.delete(self.get_hash(pkey))

    def __iter__(self):
        """Iterate over header keys."""
        pattern = f"{{{self.cache.path}}}#*"
        for key in self.cache.redis.scan_iter(match=pattern):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            _, header_key = key_str.split('#', 1)
            yield header_key
    
    def incrby(self, field, value):
        _pkey = self.get_hash(field)
        self.cache.redis.incrby(_pkey,value)
    
    async def async_incrby(self, field, value):
        _pkey = self.get_hash(field)
        await self.cache.redis_async.incrby(_pkey,value)
    
    def list_keys(self, keyword = '*', count=None):
        # keys look like {self.path}:pkey
        pattern = f"{{{self.cache.path}}}#{keyword}"
        result = []
        if count is None:
            for key in self.cache.redis.scan_iter(match=pattern):
                # Extract pkey part after colon
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                # {user/db/period/source/cache/table}:pkey            
                parts = key.split('#', 1)
                if len(parts) > 1:
                    result.append(parts[1])
        else:
            for key in self.cache.redis.scan_iter(match=pattern,count=count):
                # Extract pkey part after colon
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                # {user/db/period/source/cache/table}:pkey            
                parts = key.split('#', 1)
                if len(parts) > 1:
                    result.append(parts[1])

        return result
