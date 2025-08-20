import os
import sys
import logging
import subprocess
import boto3
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import time
import pytz
import io
from tqdm import tqdm

from SharedData.Logger import Logger
from SharedData.MultiProc import io_bound_process

def S3GetSession(isupload=False):

    """
    Create and return a boto3 S3 session and bucket resource based on environment variables.
    
    This function attempts to establish a boto3 session for accessing Amazon S3 using credentials and configuration
    provided via environment variables. It supports multiple authentication methods and custom endpoint URLs.
    
    Environment variables used:
    - S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY: Access keys for S3 authentication.
    - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: Alternative access keys for AWS authentication.
    - AWS_PROFILE or S3_AWS_PROFILE: AWS CLI profile name for session creation.
    - S3_DEFAULT_REGION or AWS_DEFAULT_REGION: AWS region for the session (defaults to 'us-east-1' if not set).
    - S3_ENDPOINT_URL: Custom S3 endpoint URL (optional).
    - S3_BUCKET: Name of the S3 bucket to access (required).
    
    Parameters:
    - isupload (bool): Currently unused parameter, reserved for future use.
    
    Returns:
    - tuple: A tuple containing the boto3 S3 resource and the S3 Bucket resource.
    
    Raises:
    - Exception: If required environment variables for authentication are not set.
    """
    if 'S3_ACCESS_KEY_ID' in os.environ and 'S3_SECRET_ACCESS_KEY' in os.environ:
        if 'AWS_PROFILE' in os.environ:
            del os.environ['AWS_PROFILE']
        _session = boto3.Session(
            aws_access_key_id=os.environ['S3_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['S3_SECRET_ACCESS_KEY'],
            region_name=os.environ.get('S3_DEFAULT_REGION','us-east-1'),
        )        
    elif 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
        if 'AWS_PROFILE' in os.environ:
            del os.environ['AWS_PROFILE']
        _session = boto3.Session(
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name=os.environ.get('AWS_DEFAULT_REGION','us-east-1'),
        )
    elif 'S3_AWS_PROFILE' in os.environ:
        _session = boto3.Session(profile_name=os.environ['S3_AWS_PROFILE'])
    else:
        raise Exception('S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY or AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or S3_AWS_PROFILE must be set in environment variables')

    if 'S3_ENDPOINT_URL' in os.environ:
        _s3 = _session.resource(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])
    else:
        _s3 = _session.resource('s3')
    _bucket = _s3.Bucket(os.environ['S3_BUCKET'].replace('s3://', ''))
    return _s3, _bucket

def S3ListFolder(prefix):
    """
    Retrieve a list of S3 object keys from a specified folder prefix.
    
    Connects to an S3 bucket using an existing session, filters objects by the given prefix,
    and returns their keys as a NumPy array.
    
    Parameters:
        prefix (str): The prefix (folder path) to filter S3 objects.
    
    Returns:
        numpy.ndarray: An array of object keys (strings) matching the prefix.
    """
    s3, bucket = S3GetSession()
    keys = np.array(
        [obj_s.key for obj_s in bucket.objects.filter(Prefix=prefix)])
    return keys

def S3GetPath(remote_path, database_folder=None):
    if database_folder:        
        s3_path = str(remote_path)
        s3_path = s3_path.replace(database_folder, '')
        s3_path = s3_path.replace('\\', '/')
    else:
        s3_path = str(remote_path).replace(
            os.environ['DATABASE_FOLDER'], '').replace('\\', '/')
    s3_path = s3_path.lstrip('/').rstrip('/')
    return  s3_path

def S3Download(remote_path, local_path=None, \
        force_download=False, local_mtime=None,database_folder=None):
    """
    '''
    Download a file from an S3 bucket to memory, optionally comparing modification times to avoid unnecessary downloads.
    
    Parameters:
        remote_path (str): The S3 path of the remote file to download.
        local_path (str, optional): The local file path to compare modification time against. Defaults to None.
        force_download (bool, optional): If True, forces the download regardless of modification times. Defaults to False.
        local_mtime (float, optional): The modification time of the local file as a timestamp. Used if local_path is None. Defaults to None.
        database_folder (str, optional): A folder path to adjust the S3 key extraction from the remote_path. Defaults to None.
    
    Returns:
        list: A list containing:
            - io.BytesIO or None: The in-memory file object if downloaded, otherwise None.
            - float or None: The local modification time timestamp.
            - float or None: The remote modification time timestamp.
    
    Raises:
        Exception: If there is an error during the download process.
    
    Notes:
        - The function uses environment variables 'S3_BUCKET' and 'DATABASE_FOLDER' to determine bucket and path information.
        - Downloads the file only if it does not exist locally, or if the remote file is newer
    """
    bucket_name = os.environ['S3_BUCKET'].replace('s3://', '')
    s3_path = S3GetPath(remote_path, database_folder=database_folder)
    s3, bucket = S3GetSession()
    # load obj
    obj = s3.Object(bucket_name, s3_path)
    remote_mtime = None
    try:
        # remote mtime
        remote_mtime = obj.last_modified.timestamp()
        if 'mtime' in obj.metadata:
            remote_mtime = float(obj.metadata['mtime'])
        remote_exists = True
    except:
        # remote file dont exist
        remote_exists = False

    local_exists = False
    if not local_path is None:
        remote_isnewer = False
        local_exists = os.path.isfile(str(local_path))
        local_mtime = None
        if local_exists:
            # local mtime
            local_mtime = datetime.fromtimestamp(os.path.getmtime(local_path)).timestamp()            
    elif not local_mtime is None:        
        local_exists = True

    remote_isnewer = False
    if (local_exists) & (remote_exists):
        # compare
        remote_isnewer = remote_mtime > local_mtime

    if remote_exists:
        if (not local_exists) | (remote_isnewer) | (force_download):
            # get object size for progress bar
            obj_size = obj.content_length / (1024*1024)  # in MB
            description = 'Downloading:%iMB, %s' % (obj_size, s3_path)
            io_obj = io.BytesIO()
            try:
                if obj_size > 50:
                    with tqdm(total=obj_size, unit='MB', unit_scale=True,\
                               desc=description) as pbar:
                        obj.download_fileobj(io_obj,
                            Callback=lambda bytes_transferred: \
                                pbar.update(bytes_transferred/(1024*1024)))
                else:
                    obj.download_fileobj(io_obj)
                return [io_obj, local_mtime, remote_mtime]
            except Exception as e:
                raise Exception('downloading %s,%s ERROR!\n%s' %
                                (Logger.user, remote_path, str(e)))

    return [None, local_mtime, remote_mtime]

def UpdateModTime(local_path, remote_mtime):
    # update modification time to remote mtime 
    """
    Update the modification and access times of a local file to match a given remote modification time.
    
    Parameters:
    local_path (str): The file path of the local file to update.
    remote_mtime (float): The remote modification time as a POSIX timestamp (seconds since epoch, UTC).
    
    This function converts the remote modification time to a timezone-aware timestamp and sets both the access and modification times of the specified local file to this value.
    """
    remote_mtime_local_tz_ts = datetime.fromtimestamp(remote_mtime, timezone.utc).timestamp()
    os.utime(local_path, (remote_mtime_local_tz_ts, remote_mtime_local_tz_ts))

def S3SaveLocal(local_path, io_obj, remote_mtime):
    """
    Save the contents of a binary IO object to a local file and update its modification time.
    
    This function writes the data from a given binary IO object to a specified local file path.
    If the parent directories of the file path do not exist, they will be created.
    After writing the data, the file's modification and access times are updated to match the provided remote modification time.
    
    Parameters:
        local_path (str or Path): The local file path where the data should be saved.
        io_obj (io.BytesIO or similar): A binary IO object containing the data to write.
        remote_mtime (float): The remote modification time as a POSIX timestamp (seconds since epoch, UTC).
    
    Returns:
        None
    """
    path = Path(local_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_path, 'wb') as f:
        f.write(io_obj.getbuffer())
        f.flush()
    # update modification time
    remote_mtime_local_tz_ts = datetime.fromtimestamp(remote_mtime, timezone.utc).timestamp()
    os.utime(local_path, (remote_mtime_local_tz_ts, remote_mtime_local_tz_ts))

def S3Upload(file_io, path, mtime, database_folder=None):
    """
    '''
    Uploads a file-like object to an S3 bucket with retry logic and progress display.
    
    Parameters:
        file_io (io.IOBase): A file-like object opened in binary mode to upload.
        path (str): The local file path used to determine the remote S3 file path.
        mtime (float): The modification time of the file (timestamp) to be stored as metadata.
        database_folder (str, optional): The base folder path in the local database to replace with the S3 bucket name in the remote path. Defaults to None.
    
    Behavior:
        - Constructs the remote S3 file path by replacing the local database folder path with the S3 bucket name.
        - Converts Windows-style backslashes in paths to forward slashes.
        - Calculates the file size in megabytes.
        - Attempts to upload the file up to 3 times on failure.
        - For files larger than 50 MB, displays a progress bar during upload.
        - Sets the file's modification time as metadata in the S3 object.
        - Prevents the file-like object from being closed by boto3 during upload.
        - Logs warnings on upload failures and raises an exception if all retries fail.
    
    Raises:
        Exception: If the upload fails after 3 retry attempts
    """
    s3_path = S3GetPath(path, database_folder=database_folder)    

    # Check the file size
    file_size = file_io.seek(0, os.SEEK_END) / (1024*1024)  # in MB    
    description = 'Uploading:%iMB, %s' % (file_size, s3_path)

    trials = 3
    success = False
    file_io.close = lambda: None  # prevents boto3 from closing io
    while trials > 0:
        try:
            s3, bucket = S3GetSession(isupload=True)
            mtime_utc = datetime.fromtimestamp(mtime, timezone.utc).timestamp()
            mtime_str = str(mtime_utc)

            file_io.seek(0)
            if file_size > 50:
                with tqdm(total=file_size, unit='MB', unit_scale=True, desc=description) as pbar:
                    bucket.upload_fileobj(file_io, s3_path,
                                          ExtraArgs={'Metadata': {
                                              'mtime': mtime_str}},
                                          Callback=lambda bytes_transferred: pbar.update(bytes_transferred/(1024*1024)))
            else:
                bucket.upload_fileobj(file_io, s3_path, ExtraArgs={
                                      'Metadata': {'mtime': mtime_str}})
            success = True
            break
        except Exception as e:
            Logger.log.warning(Logger.user+' Uploading to S3 '+path +
                               ' FAILED! retrying(%i,3)...\n%s ' % (trials, str(e)))
            trials = trials - 1

    if not success:
        Logger.log.error(Logger.user+' Uploading to S3 '+path+' ERROR!')
        raise Exception(Logger.user+' Uploading to S3 '+path+' ERROR!')

def S3DeleteTable(remote_path):
    """
    Deletes specific files ('head.bin.gzip' and 'tail.bin.gzip') from an S3 bucket under the given remote path.
    
    Parameters:
        remote_path (str): The S3 prefix path where the target files are located.
    
    Raises:
        Exception: If any error occurs during the deletion process, the exception is logged and re-raised.
    """
    try:    
        s3, bucket = S3GetSession()
        objects_to_delete = bucket.objects.filter(Prefix=remote_path)
        delete_us = []
        for obj in objects_to_delete:
            if (remote_path+'/head.bin.gzip' == obj.key)\
                or (remote_path+'/tail.bin.gzip' == obj.key):
                delete_us.append({'Key': obj.key})
        # Batch deletes to avoid errors caused by long delete lists
        batch_size = 1000  # Adjust if necessary
        for i in range(0, len(delete_us), batch_size):
            batch = delete_us[i:i+batch_size]
            bucket.delete_objects(Delete={'Objects': batch})
    except Exception as e:
        Logger.log.error(f"S3Delete {remote_path} ERROR!\n{str(e)}")
        raise Exception(f"S3Delete {remote_path} ERROR!\n{str(e)}")
    
def S3DeleteTimeseries(remote_path):
    """
    Deletes specific timeseries files ('timeseries_head.bin.gzip' and 'timeseries_tail.bin.gzip') from an S3 bucket under the given remote path.
    
    Parameters:
        remote_path (str): The S3 prefix path where the timeseries files are located.
    
    Raises:
        Exception: If any error occurs during the deletion process, the exception is logged and re-raised.
    """
    try:    
        s3, bucket = S3GetSession()
        objects_to_delete = bucket.objects.filter(Prefix=remote_path)
        delete_us = []
        for obj in objects_to_delete:
            if (remote_path+'/timeseries_head.bin.gzip' == obj.key)\
                or (remote_path+'/timeseries_tail.bin.gzip' == obj.key):
                delete_us.append({'Key': obj.key})
        # Batch deletes to avoid errors caused by long delete lists
        batch_size = 1000  # Adjust if necessary
        for i in range(0, len(delete_us), batch_size):
            batch = delete_us[i:i+batch_size]
            bucket.delete_objects(Delete={'Objects': batch})
    except Exception as e:
        Logger.log.error(f"S3Delete {remote_path} ERROR!\n{str(e)}")
        raise Exception(f"S3Delete {remote_path} ERROR!\n{str(e)}")
    
def S3DeleteFolder(remote_path):    
    """
    Deletes all objects within a specified folder (prefix) in an S3 bucket.
    
    Parameters:
        remote_path (str): The S3 prefix (folder path) to delete objects from.
    
    Raises:
        Exception: If there is an error during the deletion process, an exception is raised with the error details.
    
    Notes:
        - Uses batch deletion with a batch size of 1000 objects to avoid errors caused by large delete requests.
        - Relies on S3GetSession() to obtain the S3 session and bucket.
        - Logs errors using Logger.log.error before raising exceptions.
    """
    try:    
        s3, bucket = S3GetSession()
        objects_to_delete = bucket.objects.filter(Prefix=remote_path)
        delete_us = []
        for obj in objects_to_delete:
            delete_us.append({'Key': obj.key})
        # Batch deletes to avoid errors caused by long delete lists
        batch_size = 1000  # Adjust if necessary
        for i in range(0, len(delete_us), batch_size):
            batch = delete_us[i:i+batch_size]
            bucket.delete_objects(Delete={'Objects': batch})
    except Exception as e:
        Logger.log.error(f"S3Delete {remote_path} ERROR!\n{str(e)}")
        raise Exception(f"S3Delete {remote_path} ERROR!\n{str(e)}")
    
def S3DeleteFile(remote_path: str) -> None:
    """
    Delete a single file in the S3 bucket at the specified remote path.

    Parameters:
        remote_path (str): The S3 object key to delete.

    Raises:
        Exception: If there is an error during deletion.
    """
    try:        
        s3, bucket = S3GetSession()
        response = bucket.delete_objects(Delete={'Objects': [{'Key': remote_path}]})
    except Exception as e:
        Logger.log.error(f"S3DeleteFile {remote_path} ERROR!\n{str(e)}")
        raise Exception(f"S3DeleteFile {remote_path} ERROR!\n{str(e)}")    

def S3GetMtime(remote_path, database_folder=None):
    """
    Retrieve the modification time of a file stored in an S3 bucket.
    
    This function extracts the bucket name and S3 object path from environment variables and the given remote path,
    then attempts to fetch the last modified timestamp of the corresponding S3 object. If the object's metadata
    contains a custom 'mtime' field, that value is used instead.
    
    Parameters:
        remote_path (str): The full remote file path including the database folder prefix.
    
    Returns:
        float or None: The modification time as a Unix timestamp if the object exists, otherwise None.
    """
    bucket_name = os.environ['S3_BUCKET'].replace('s3://', '')
    s3_path = S3GetPath(remote_path, database_folder=database_folder)
    s3, bucket = S3GetSession()
    # load obj
    obj = s3.Object(bucket_name, s3_path)
    remote_mtime = None
    try:
        # remote mtime
        remote_mtime = obj.last_modified.timestamp()
        if 'mtime' in obj.metadata:
            remote_mtime = float(obj.metadata['mtime'])
    except Exception as e:
        # print(e)
        # remote file dont exist
        pass
    return remote_mtime

