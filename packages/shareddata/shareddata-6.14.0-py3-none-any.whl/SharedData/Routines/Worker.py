# SharedData/Routines/Worker.py

# implements a decentralized routines worker
# connects to worker pool
# broadcast heartbeat
# listen to commands
# environment variables:
# SOURCE_FOLDER
# WORKERPOOL_STREAM
# GIT_SERVER
# GIT_USER
# GIT_ACRONYM
# GIT_TOKEN

import os
import time
import sys
import numpy as np
import importlib.metadata
import argparse
import psutil


from SharedData.Routines.WorkerLib import *
from SharedData.IO.AWSKinesis import *
from SharedData.SharedData import SharedData
shdata = SharedData('SharedData.Routines.Worker')
from SharedData.Logger import Logger
from SharedData.Routines.WorkerPool import WorkerPool

parser = argparse.ArgumentParser(description="Worker configuration")
parser.add_argument('--schedules', default='', help='Schedules to start')
parser.add_argument('--server', type=bool, default=False, help='Server port number')
parser.add_argument('--port', type=int, default=8002, help='Server port number')
parser.add_argument('--nproc', type=int, default=4, help='Number of server processes')
parser.add_argument('--nthreads', type=int, default=8, help='Number of server threads')
parser.add_argument('--batchjobs', type=int, default=0, help='Max number of jobs to fetch')
parser.add_argument('--sleep', type=int, default=5, help='Sleep time between fetches')
args = parser.parse_args()

if args.server:
    coll = shdata.collection('Text','RT','WORKERPOOL','COMMANDS')
    coll = shdata.collection('Text','RT','WORKERPOOL','JOBS')    
    WorkerPool.create_indexes()
    start_server(args.port, args.nproc,args.nthreads)    
    start_logger()
    update_jobs_status_thread = threading.Thread(target=WorkerPool.update_jobs_status, daemon=True)
    update_jobs_status_thread.start()
    
SCHEDULE_NAMES = args.schedules
if SCHEDULE_NAMES != '':
    Logger.log.info('SharedData Worker schedules:%s STARTED!' % (SCHEDULE_NAMES))
    start_schedules(SCHEDULE_NAMES)    


lastheartbeat = time.time()

SLEEP_TIME = int(args.sleep)
SHAREDDATA_VERSION = ''
try:
    SHAREDDATA_VERSION = importlib.metadata.version("shareddata")    
except:
    pass    

cpu_model = WorkerPool.get_cpu_model()
mem = psutil.virtual_memory()
mem_total_gb = mem.total / (1024 ** 3)     
Logger.log.info(
    "ROUTINE STARTED!"
    f"{cpu_model} {mem_total_gb:.1f} RAM"
)

batch_jobs = []
MAX_BATCH_JOBS = int(args.batchjobs)
completed_batch_jobs = 0
error_batch_jobs = 0
         

routines = []
while True:    
    fetch_jobs = 0
    running_batch_jobs = len(batch_jobs)
    if running_batch_jobs < MAX_BATCH_JOBS:
        fetch_jobs = MAX_BATCH_JOBS - running_batch_jobs

    jobs = []
    try:
        jobs = ClientAPI.get_workerpool(fetch_jobs=fetch_jobs)
    except Exception as e:
        Logger.log.error(f'Error fetching jobs: {e}')
        time.sleep(15)
    
    update_routines(routines)
    for command in jobs:           
        if ('job' in command) & ('target' in command):
            if ((command['target'].upper() == os.environ['USER_COMPUTER'].upper())
                    | (command['target'] == 'ALL')):                
                update_routines(routines)
                command = validate_command(command)
                process_command(command,routines,batch_jobs)
                routines = remove_finished_routines(routines)

    routines = remove_finished_routines(routines)
    batch_jobs, nfinished, nerror = remove_finished_batch_jobs(batch_jobs)
    completed_batch_jobs += nfinished
    error_batch_jobs += nerror    

    if (time.time()-lastheartbeat > 15):
        lastheartbeat = time.time()
        nroutines = len(routines)
        # Fetch CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        mem_percent = mem.percent

        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        mem_total_gb = mem.total / (1024 ** 3)        

        Logger.log.debug(
            f"#heartbeat# {SHAREDDATA_VERSION},"
            f"{nroutines}routines,"
            f"{running_batch_jobs}/{MAX_BATCH_JOBS}jobs,"
            f"{completed_batch_jobs}completed,"
            f"{error_batch_jobs}errors,"
            f"cpu={cpu_percent:.1f}%,"
            f"mem={mem_percent:.1f}%"            
        )
        # Logger.log.debug(f'#heartbeat# {nroutines}routines,{running_batch_jobs}/{MAX_BATCH_JOBS}jobs,{completed_batch_jobs}completed,{error_batch_jobs}errors,{SHAREDDATA_VERSION}')
    
    time.sleep(SLEEP_TIME * np.random.rand())