import argparse
import asyncio
import pandas as pd
import time
import multiprocessing
from SharedData.SharedData import SharedData
from SharedData.Logger import Logger

def cache_stream_process(streams):
    """
    Each process will run this worker, launching an event loop for asynchronous work.
    """    
    shdata = SharedData(__file__, quiet=True)
    async def cache_stream_task():
        tasks = []
        for stream_descr in streams:
            user, database, period, source, container, tablename = stream_descr.split('/')
            stream = shdata.stream(database, period, source, tablename, user=user, use_aiokafka=True)
            cache = shdata.cache(database, period, source, tablename, user=user)
            tasks.append(asyncio.create_task(stream.async_cache_stream_task(cache)))
        # Run the asyncio tasks concurrently
        await asyncio.gather(*tasks)

    # Run the asyncio event loop
    asyncio.run(cache_stream_task())

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for process count and stream paths.
    """
    parser = argparse.ArgumentParser(description="Stream cache worker launcher")
    parser.add_argument(
        "--num-process", type=int, default=4,
        help="Number of worker processes to spawn."
    )
    parser.add_argument(
        "--stream-paths", type=str, nargs='+', required=True,
        help="List of stream paths in USER/DB/PERIOD/SRC/CONTAINER/TABLE format."
    )
    return parser.parse_args()

def main():
    args = parse_args()
    shdata = SharedData("SharedData.IO.StreamsCache", user='master')
    Logger.log.info('Starting stream cache and persis processes...')    
    
    num_process = args.num_process
    stream_paths = args.stream_paths    
    
    process_streams = {i: [] for i in range(num_process)}
    for s in range(len(stream_paths)):
        stream_descr = stream_paths[s]
        user, database, period, source, container, tablename = stream_descr.split('/')
        stream = shdata.stream(database,period,source,tablename,user=user,use_aiokafka=True)
        for p in range(stream.num_partitions):
            curproc = (s+p) % num_process
            process_streams[curproc].append(stream_descr)
    
    processes = []
    for p in process_streams:
        proc = (multiprocessing.Process(target=cache_stream_process, args=(process_streams[p],)))
        processes.append(proc)
        proc.start()        
        
    Logger.log.info('Processes started!')

     # Initialize cache objects and per-stream stats
    stream_caches = {}
    last_counters = {}
    for stream_descr in stream_paths:
        user, database, period, source, container, tablename = stream_descr.split('/')
        cache = shdata.cache(database, period, source, tablename, user=user)
        stream_caches[stream_descr] = cache
        last_counters[stream_descr] = {
            "cache": int(cache.header.get('cache->counter', 0)),
            "stream_cache": int(cache.header.get('stream->cache-group->cache_counter', 0)),            
        }
    try:
        lasttime = time.time()
        time.sleep(1)
        while True:
            tnow = time.time()
            telapsed = tnow - lasttime
            log_lines = []
            for stream_descr, cache in stream_caches.items():
                prev = last_counters[stream_descr]
                cache_counter = int(cache.header.get('cache->counter', 0))
                stream_cache_counter = int(cache.header.get('stream->cache-group->cache_counter', 0))                

                log_lines.append(
                    f"{stream_descr}: "
                    f"{(cache_counter - prev['cache'])/telapsed:.0f} cache/sec, "
                    f"{(stream_cache_counter - prev['stream_cache'])/telapsed:.0f} stream/sec, "
                    f"{stream_cache_counter} cached msgs"
                )

                # Update previous values:
                last_counters[stream_descr] = {
                    "cache": cache_counter,
                    "stream_cache": stream_cache_counter,
                }
            lasttime = tnow
            Logger.log.debug("#heartbeat# " + " | ".join(log_lines))
            time.sleep(15)
    except KeyboardInterrupt:
        print("Terminating processes...")
        for p in processes:
            p.terminate()
            p.join()

if __name__ == "__main__":
    main()