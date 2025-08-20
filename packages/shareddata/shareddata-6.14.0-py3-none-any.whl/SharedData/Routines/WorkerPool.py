import sys
import lz4.frame
import pandas as pd
import os
import threading
import json
import requests
import lz4
import bson
import hashlib
import pymongo
import time
from pymongo import ASCENDING, DESCENDING

from SharedData.IO.MongoDBClient import MongoDBClient
from SharedData.IO.AWSKinesis import KinesisStreamProducer
from SharedData.Logger import Logger
from SharedData.IO.ClientAPI import ClientAPI
from SharedData.CollectionMongoDB import CollectionMongoDB



class WorkerPool:

    """    
    Manages a pool of worker jobs, supporting job creation, consumption, and status updates.
    
    This class facilitates job distribution and coordination either via a Kinesis stream or a REST API backed by shareddata endpoints. It handles job queuing, sending, receiving, and status management with thread-safe operations.
    
    Attributes:
        kinesis (bool): Flag to determine if Kinesis stream is used.
        jobs (dict): Dictionary storing jobs keyed by target worker names.
        lock (threading.Lock): Lock to ensure thread-safe access to shared resources.
        stream_buffer (list): Buffer to hold streamed jobs.        
    
    Methods:        
        produce(record, partitionkey=None): Send a job record to the worker pool endpoint or Kinesis stream.        
        consume(fetch_jobs=0): Fetch jobs from the shared endpoint and buffer them locally.
        get_jobs(workername): Retrieve and clean up jobs assigned to a specific worker.
        update_jobs_status(): Periodically update job statuses from NEW/WAITING to PENDING if due and dependencies are met.
    """
    def __init__(self, kinesis=False):
        """
        Initializes the object with optional Kinesis streaming support.
        
        Parameters:
            kinesis (bool): If True, initializes a KinesisStreamProducer using the
                            'WORKERPOOL_STREAM' environment variable. If False, checks
                            for 'SHAREDDATA_ENDPOINT' and 'SHAREDDATA_TOKEN' in the
                            environment variables.
        
        Attributes initialized:
            kinesis (bool): Flag indicating whether Kinesis streaming is enabled.
            jobs (dict): Dictionary to store job information.
            lock (threading.Lock): A lock to synchronize access to shared resources.            
        
        Raises:
            Exception: If kinesis is False and required environment variables are missing.
        """        
        self.jobs = {}

    @staticmethod
    def create_indexes():
        mongodb= MongoDBClient(user='master')
        coll_commands = mongodb['Text/RT/WORKERPOOL/collection/COMMANDS']
        # COMMANDS collection index
        MongoDBClient.ensure_index(coll_commands, [
            ('date', ASCENDING),
            ('status', ASCENDING),
            ('target', ASCENDING)
        ])
        # JOBS collection indexes
        coll_jobs = mongodb['Text/RT/WORKERPOOL/collection/JOBS']
        MongoDBClient.ensure_index(coll_jobs, [
            ('status', ASCENDING),
            ('user', ASCENDING),
            ('computer', ASCENDING),
            ('date', DESCENDING)
        ])
        MongoDBClient.ensure_index(coll_jobs, [('hash', ASCENDING)])
        MongoDBClient.ensure_index(coll_jobs, [
            ('status', ASCENDING),
            ('date', ASCENDING)
        ])
          
    @staticmethod
    def get_jobs(workername):
        """
        Atomically fetch and reserve pending jobs for *workername*.

        The method examines commands not older than 60 s:
        • Direct jobs (`status="NEW", target=<worker>`) are flagged **SENT**.  
        • Broadcast jobs (`status="BROADCAST", target="ALL"`) add the worker
        to *fetched* to prevent re-delivery.

        Parameters
        ----------
        workername : str
            Case-insensitive identifier of the requesting worker.

        Returns
        -------
        list[dict]
            Job documents now reserved for the worker.
        """
        
        workername = workername.upper()
        mongodb= MongoDBClient(user='master')
        coll = mongodb['Text/RT/WORKERPOOL/collection/COMMANDS']
        tnow = pd.Timestamp.utcnow().tz_localize(None)

        jobs = []

        # get direct commands
        filter_query = {
            'date': {'$gte': tnow - pd.Timedelta(seconds=60)},
            'status' : 'NEW',
            'target' : workername
        }
        update_query = {
            '$set': {
                'status': 'SENT',
                'mtime': tnow
            }
        }
        while True:
            job = coll.find_one_and_update(
                filter=filter_query,
                update=update_query,
                sort=[('date', pymongo.ASCENDING)],
                return_document=pymongo.ReturnDocument.AFTER
            )
            if job:
                jobs.append(job)
            else:
                break

        # broadcast commands
        filter_query = {
            'date':   {'$gte': tnow - pd.Timedelta(seconds=60)},
            'status': 'BROADCAST',
            'target': 'ALL',
            # Either no “fetched” field yet, or it does not contain *this* worker
            '$or': [
                {'fetched': {'$exists': False}},
                {'fetched': {'$nin': [workername]}}
            ]
        }

        update_query = {
            '$set':     {'mtime': tnow},          # keep the document fresh
            '$addToSet':{'fetched': workername}   # append once, duplicates prevented
        }

        while True:
            job = coll.find_one_and_update(
                filter          = filter_query,
                update          = update_query,
                sort            = [('date', pymongo.ASCENDING)],
                return_document = pymongo.ReturnDocument.AFTER
            )
            if job:
                jobs.append(job)
            else:
                break

        return jobs
           
    @staticmethod
    def fetch_batch_job(workername, njobs=1):
        """
        Fetches and atomically reserves a specified number of pending jobs from a MongoDB collection for a given worker.
        
        Parameters:
            workername (str): The worker identifier in the format 'user@computer'.
            njobs (int, optional): The number of jobs to fetch. Defaults to 1.
        
        Returns:
            list: A list of job documents that have been fetched and marked as 'FETCHED' for the specified worker.
        
        The method filters jobs by matching the user and computer fields (or 'ANY'), and only considers jobs with status 'PENDING'.
        Each fetched job's status is updated to 'FETCHED', the target is set to the worker, and the modification time is updated to the current UTC timestamp.
        Jobs are fetched in descending order by their 'date' field.
        """
        user = workername.split('@')[0]
        computer = workername.split('@')[1]
        mongodb= MongoDBClient(user='master')
        coll = mongodb['Text/RT/WORKERPOOL/collection/JOBS']

        filter_query = {
            'user': {'$in': [user, 'ANY']},
            'computer': {'$in': [computer, 'ANY']},
            'status': 'PENDING',  # Only fetch jobs that are in 'PENDING' status
        }

        # Define the update operation to set status to 'FETCHED'
        update_query = {
            '$set': {
                'status': 'FETCHED',
                'target': user+'@'+computer,
                'mtime': pd.Timestamp('now', tz='UTC')
            }
        }

        sort_order = [('date', pymongo.DESCENDING)]

        fetched_jobs = []
        for _ in range(njobs):
            # Atomically find and update a single job
            job = coll.find_one_and_update(
                filter=filter_query,
                update=update_query,
                sort=sort_order,
                return_document=pymongo.ReturnDocument.AFTER
            )

            if job:
                fetched_jobs.append(job)
            else:
                # No more jobs available
                break
        
        return fetched_jobs

    @staticmethod
    def update_jobs_status() -> None:
        """
        Periodically updates job statuses in the MongoDB collection from 'NEW' or 'WAITING' to 'PENDING' if the job's due date has passed and all its dependencies have been completed.
        
        This method runs indefinitely, performing the update every 5 seconds. If an error occurs during the update process, it logs the error and waits 60 seconds before retrying.
        
        The update is performed using a MongoDB aggregation pipeline that:
        - Filters jobs with status 'NEW' or 'WAITING' and a due date earlier than the current time.
        - Looks up the job dependencies and checks if all dependencies have status 'COMPLETED'.
        - Updates the status of eligible jobs to 'PENDING' and sets the modification time to the current timestamp.
        """
        while True:
            try:
                now = pd.Timestamp('now', tz='UTC')
                pipeline = [
                    {
                        '$match': {
                            'status': {'$in': ['NEW', 'WAITING']},
                            'date': {'$lt': now}
                        }
                    },
                    {
                        '$lookup': {
                            'from': 'Text/RT/WORKERPOOL/collection/JOBS',
                            'localField': 'dependencies',
                            'foreignField': 'hash',
                            'as': 'deps'
                        }
                    },
                    {
                        '$addFields': {
                            'all_deps_completed': {
                                '$cond': [
                                    {'$gt': [{'$size': {'$ifNull': ['$dependencies', []]}}, 0]},
                                    {
                                        '$allElementsTrue': {
                                            '$map': {
                                                'input': "$deps",
                                                'as': "d",
                                                'in': {'$eq': ["$$d.status", "COMPLETED"]}
                                            }
                                        }
                                    },
                                    True
                                ]
                            }
                        }
                    },
                    {
                        '$match': {'all_deps_completed': True}
                    },
                    {
                        "$project": {"date": 1, "hash": 1}
                    }
                ]
                pipeline.append({
                    "$merge": {
                        "into": "Text/RT/WORKERPOOL/collection/JOBS",
                        "whenMatched": [
                            {"$set": {"status": "PENDING", "mtime": now}}
                        ],
                        "whenNotMatched": "discard"
                    }
                })

                mongodb = MongoDBClient(user='master')
                coll = mongodb['Text/RT/WORKERPOOL/collection/JOBS']
                coll.aggregate(pipeline)

                time.sleep(5)
            except Exception as e:
                Logger.log.error(f"Error in update_jobs_status: {e}")
                time.sleep(60)  # Wait before retrying in case of error
 
    @staticmethod    
    def get_cpu_model() -> str:
        """Try to get a readable CPU model string cross-platform."""
        try:
            if sys.platform == "linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            return line.strip().split(":", 1)[1].strip()
            elif sys.platform == "darwin":  # macOS
                import subprocess
                model = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"])
                return model.decode().strip()
            else:  # Windows or fallback
                return platform.processor() or platform.uname().processor
        except Exception:
            return "UnknownCPU"