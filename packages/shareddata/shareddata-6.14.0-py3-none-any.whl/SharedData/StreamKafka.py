import numpy as np
import pandas as pd
import os
import time
import uuid
import threading
import bson
import lz4.frame
import asyncio
import queue
import multiprocessing

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, KafkaError        
from confluent_kafka import Producer

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from SharedData.Database import DATABASE_PKEYS
from SharedData.Logger import Logger

class StreamKafka:

    def __init__(
        self, shdata,
        database, period, source, tablename,
        user='master',
        bootstrap_servers=None,
        replication=None,
        partitions=None,
        retention_ms=None, 
        use_aiokafka=False,        
        create_if_not_exists=True,        
    ):
        self.shdata = shdata
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.use_aiokafka = use_aiokafka
        self.topic = f'{user}/{database}/{period}/{source}/stream/{tablename}'.replace('/','-')


        if bootstrap_servers is None:
            bootstrap_servers = os.environ['KAFKA_BOOTSTRAP_SERVERS']
        self.bootstrap_servers = bootstrap_servers
        
        self.exists = False
        admin = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        # create topic if not exists
        if self.topic in admin.list_topics().topics:
            self.exists = True
        
        if not create_if_not_exists and not self.exists:
            raise FileNotFoundError(f'Topic {self.topic} does not exist')
                        
        if replication is None:
            self.replication = int(os.environ['KAFKA_REPLICATION'])
        else:
            self.replication = replication
        
        if partitions is None:
            self.partitions = int(os.environ['KAFKA_PARTITIONS'])
        else:
            self.partitions = partitions

        if retention_ms is None:
            self.retention_ms = int(os.environ['KAFKA_RETENTION'])
        else:
            self.retention_ms = retention_ms

        self.lock = threading.Lock()
        self.pkeys = DATABASE_PKEYS[database]

        self._producer = None                
        self.consumers = {}
        
        # create topic if not exists
        if not self.exists:
            new_topic = NewTopic(
                self.topic, 
                num_partitions=self.partitions, 
                replication_factor=self.replication,
                config={"retention.ms": str(self.retention_ms)} 
            )
            fs = admin.create_topics([new_topic])
            for topic, f in fs.items():
                try:
                    f.result()
                    time.sleep(2)
                    Logger.log.info(f"Topic {topic} created.")
                except Exception as e:
                    if not 'already exists' in str(e):
                        raise e
        
        #get number of partitions
        self.num_partitions = len(admin.list_topics(topic=self.topic).topics[self.topic].partitions)        

    #
    # Producer sync (confluent) and async (aiokafka)
    #
    @property
    def producer(self):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await get_async_producer()' in aiokafka mode.")
        with self.lock:
            if self._producer is None:                
                self._producer = Producer({'bootstrap.servers': self.bootstrap_servers})
            return self._producer

    async def get_async_producer(self):
        if not self.use_aiokafka:
            raise RuntimeError("This method is only available in aiokafka mode.")
        if self._producer is None:            
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,                
            )            
            await self._producer.start()
        return self._producer

    #
    # Extend (produce) sync/async
    #
    def extend(self, data):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await async_extend(...)' in aiokafka mode.")
        
        if isinstance(data, list):
            for msg in data:
                for pkey in self.pkeys:
                    if not pkey in msg:
                        raise Exception(f'extend(): Missing pkey {pkey} in {msg}')                
                message = lz4.frame.compress(bson.BSON.encode(msg))                
                self.producer.produce(self.topic, value=message)
        elif isinstance(data, dict):
            for pkey in self.pkeys:
                if not pkey in data:
                    raise Exception(f'extend(): Missing pkey {pkey} in {data}')
            message = lz4.frame.compress(bson.BSON.encode(data))
            self.producer.produce(self.topic, value=message)
        else:
            raise Exception('extend(): Invalid data type')                
      
        # Wait up to 5 seconds
        result = self.producer.flush(timeout=5.0)
        if result > 0:
            raise Exception(f"Failed to flush {result} messages")
                
    async def async_extend(self, data):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'extend()' in confluent_kafka mode.")
        
        producer = await self.get_async_producer()                            
        if isinstance(data, list):
            for msg in data:

                for pkey in self.pkeys:
                    if not pkey in msg:
                        raise Exception(f'extend(): Missing pkey {pkey} in {msg}')
                                    
                message = lz4.frame.compress(bson.BSON.encode(msg))                
                await producer.send(self.topic, value=message)            

        elif isinstance(data, dict):

            for pkey in self.pkeys:
                if not pkey in data:
                    raise Exception(f'extend(): Missing pkey {pkey} in {data}')
                            
            message = lz4.frame.compress(bson.BSON.encode(data))
            await producer.send(self.topic, value=message)

        else:
            raise Exception('extend(): Invalid data type')
                    
    #
    # Flush/close producer
    #
    def flush(self, timeout=5.0):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await async_flush()' in aiokafka mode.")
        if self._producer is not None:
            result = self._producer.flush(timeout=timeout)
            if result > 0:
                raise Exception(f"Failed to flush {result} messages")
    
    async def async_flush(self):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'flush()' in non-aiokafka mode.")
        if self._producer is not None:
            await self._producer.flush()            

    #
    # Consumer sync/async
    #
    def subscribe(self, groupid=None, offset = 'latest', autocommit=True, timeout=None):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await async_subscribe()' in aiokafka mode.")
        
        if groupid is None:
            groupid = str(uuid.uuid4())

        if groupid not in self.consumers:
            self.consumers[groupid] = []            
            consumer = Consumer({
                    'bootstrap.servers': self.bootstrap_servers,
                    'group.id': groupid,
                    'auto.offset.reset': offset,
                    'enable.auto.commit': autocommit
                })                            
            consumer.subscribe([self.topic])
            # Wait for partition assignment
            if timeout is not None:
                start = time.time()
                while not consumer.assignment():
                    if time.time() - start > timeout:
                        raise TimeoutError("Timed out waiting for partition assignment.")
                    consumer.poll(0.1)
                    time.sleep(0.1)
            self.consumers[groupid] = consumer

    async def async_subscribe(self, groupid=None, offset='latest', autocommit=True):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'subscribe()' in confluent_kafka mode.")
        
        if groupid is None:
            groupid = str(uuid.uuid4())
        
        if groupid not in self.consumers:            
            consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=groupid,
                auto_offset_reset=offset,
                enable_auto_commit=autocommit
            )            
            await consumer.start()
            self.consumers[groupid] = consumer
                            
    #
    # Poll (consume one message) sync/async
    #
    def poll(self, groupid = None, timeout=None):
        if self.use_aiokafka:
            raise RuntimeError("Use 'async_poll()' in aiokafka mode.")
        
        if groupid is None:
            if len(self.consumers) == 0:
                raise RuntimeError("You must call 'await async_subscribe()' first.")
            groupid = list(self.consumers.keys())[0] # use first consumer        

        if self.consumers[groupid] is None:
            raise RuntimeError("You must call 'await async_subscribe()' first.")
        
        consumer = self.consumers[groupid]

        if timeout is None:
            msg = consumer.poll()
        else:
            msg = consumer.poll(timeout)
            
        if msg is None:
            return None
        
        if msg.error():            
            if msg.error().code() != KafkaError._PARTITION_EOF:
                raise Exception(f"Error: {msg.error()}")
            
        msgdict = bson.BSON.decode(lz4.frame.decompress(msg.value()))        
        return msgdict
    
    async def async_poll(
        self,
        groupid: str = None,
        timeout: int = 0,
        max_records: int = None,
        decompress: bool = True
    ):
        """
        Polls all consumers for the specified groupid in parallel (asyncio), and returns a combined list of messages.

        Returns:
            list: All messages received from all consumers.
        """
        if not self.use_aiokafka:
            raise RuntimeError("Use 'poll()' in confluent_kafka mode.")

        if groupid is None:
            if len(self.consumers) == 0:
                raise RuntimeError("You must call 'await async_subscribe()' first.")
            groupid = list(self.consumers.keys())[0]  # use first consumer group

        if self.consumers[groupid] is None:
            raise RuntimeError("You must call 'await async_subscribe()' first.")
        
        msgs = []
        consumer = self.consumers[groupid]
        partitions = await consumer.getmany(timeout_ms=timeout, max_records=max_records)
        for partition, messages in partitions.items():
            for msg in messages:
                if msg.value is not None:
                    if decompress:
                        msgdict = bson.BSON.decode(lz4.frame.decompress(msg.value))
                    else:
                        msgdict = msg.value                     
                    msgs.append(msgdict)        
        return msgs
    
    async def async_commit(self, groupid: str) -> None:
        """
        Asynchronously commit the consumer offsets to Kafka for the current group.
        """
        try:
            await self.consumers[groupid].commit()
        except Exception as e:
            Logger.log.error(f"Failed to commit offsets for group {groupid}: {e}")
            raise
    #
    # Retention update (sync mode only)
    #
    def set_retention(self, retention_ms):
        if self.use_aiokafka:
            raise RuntimeError("Set retention_ms only supported in sync mode (confluent_kafka).")
        from confluent_kafka.admin import AdminClient, ConfigResource
        admin = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        config_resource = ConfigResource('topic', self.topic)
        new_config = {'retention.ms': str(retention_ms)}
        fs = admin.alter_configs([config_resource], new_configs=new_config)
        for resource, f in fs.items():
            try:
                f.result()
                Logger.log.debug(f"Retention period for topic {resource.name()} updated to {retention_ms} ms.")
                return True
            except Exception as e:
                Logger.log.error(f"Failed to update retention_ms period: {e}")
                return False

    #
    # Sync/async close for consumer (optional)
    #
    def close(self):
        for consumer in self.consumers.values():            
            consumer.stop()

    async def async_close(self):
        """
        Closes all async consumers for all groupids.
        """
        for consumer in self.consumers.values():            
            await consumer.stop()
        
        self.consumers.clear()

    def delete(self) -> bool:
        """
        Deletes the specified Kafka topic.
        Returns True if deleted, False if topic did not exist or an error occurred.
        """
        
        admin = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        if self.topic not in admin.list_topics(timeout=10).topics:
            Logger.log.warning(f"Topic {self.topic} does not exist.")
            return False
        fs = admin.delete_topics([self.topic])
        for topic, f in fs.items():
            try:
                f.result()  # Wait for operation to finish
                Logger.log.debug(f"Topic {topic} deleted.")
                return True
            except Exception as e:
                Logger.log.error(f"Failed to delete topic {topic}: {e}")
                return False
        return False
            
    async def async_cache_stream_task(self, cache, groupid = 'cache-group', offset = 'earliest'):
        try:
            await self.async_subscribe(groupid=groupid,offset=offset, autocommit=False)
        except Exception as e:
            errmsg = f"Failed to start async_cache_stream_task: {e}"
            Logger.log.error(errmsg)
            raise Exception(errmsg)
        
        while True:
            try:
                msgs = await self.async_poll(timeout=1.0, groupid=groupid, max_records=50000)
                if not msgs:
                    continue                
                await cache.async_set(msgs)
                await self.async_commit(groupid=groupid)
                await cache.header.async_incrby(f'stream->{groupid}->cache_counter', len(msgs))                                
            except Exception as e:
                errmsg = f"Failed to cache stream: {e}"
                Logger.log.error(errmsg)
                raise Exception(errmsg)

    async def async_persist_stream_task(self, cache, partitioning='daily'):
        try:
            groupid = 'persist-group'
            offset = 'earliest'
            await self.async_subscribe(offset=offset, groupid=groupid, autocommit=False)
        except Exception as e:
            errmsg = f"Failed to start async_persist_stream_task: {e}"
            Logger.log.error(errmsg)
            raise Exception(errmsg)
        
        while True:
            try:
                data = await self.async_poll(timeout=1.0, groupid=groupid, max_records=50000)
                if not data:
                    continue
                if len(data) == 0:
                    continue
                
                if 'date' in data[0]:
                    dateidx = data[0]['date']
                elif 'mtime' in data[0]:
                    dateidx = data[0]['mtime']
                    if isinstance(dateidx, (int, np.integer)):
                        dateidx = pd.to_datetime(dateidx, unit='ns')

                tablename = self.tablename                
                if not partitioning is None:
                    if partitioning=='daily':
                        tablename = f"{self.tablename}/{dateidx.strftime('%Y%m%d')}"
                    elif partitioning=='monthly':
                        tablename = f"{self.tablename}/{dateidx.strftime('%Y%m')}"
                    elif partitioning=='yearly':
                        tablename = f"{self.tablename}/{dateidx.strftime('%Y')}"

                collection = self.shdata.collection(self.database, self.period, self.source, tablename, user=self.user, hasindex=False)
                collection.extend(data)
                await self.async_commit(groupid=groupid)
                await cache.header.async_incrby(f'stream->{groupid}->persist_counter', len(data))                
            except Exception as e:
                errmsg = f"Failed to persist data: {e}"
                Logger.log.error(errmsg)
                raise Exception(errmsg)

    
# ========== USAGE PATTERNS ==========

# --- Synchronous / confluent_kafka ---
"""
stream = StreamKafka(
    database="mydb", period="1m", source="agg", tablename="prices",
    self.bootstrap_servers="localhost:9092",
    KAFKA_PARTITIONS=1,
    use_aiokafka=False
)
stream.extend({'price': 100, 'ts': time.time()})
stream.subscribe()
msg = stream.poll(timeout=1.0)
print(msg)
stream.close()
"""

# --- Asynchronous / aiokafka ---
"""
import asyncio

async def main():
    stream = StreamKafka(
        database="mydb", period="1m", source="agg", tablename="prices",
        self.bootstrap_servers="localhost:9092",
        KAFKA_PARTITIONS=1,
        use_aiokafka=True
    )
    await stream.async_extend({'price': 200, 'ts': time.time()})
    await stream.async_subscribe()
    async for msg in stream.async_poll():
        print(msg)
        break
    await stream.async_flush()
    await stream.async_close()

asyncio.run(main())
"""