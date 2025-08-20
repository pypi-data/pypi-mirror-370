import os
import threading
import time
import pandas as pd
import numpy as np
from pathlib import Path
from multiprocessing import shared_memory
import gzip
import io
import hashlib
from datetime import datetime
from tqdm import tqdm
import threading
import psutil


from SharedData.SharedNumpy import SharedNumpy
from SharedData.Table import Table

from SharedData.Utils import cpp


class TableMemory(Table):
    # TODO: create partitioning option yearly, monthly, daily

    """
    ```python
    '''
    A subclass of Table that manages in-memory table data using shared memory.
    
    This class provides functionality to allocate and free shared memory for table data,
    as well as to write the table's header and tail sections to disk efficiently with progress tracking.
    
    Attributes:
        type (int): Identifier for the table type, set to 2.
        shf_hdr (np.ndarray): Numpy array for shared header data.
        shf_data (np.ndarray): Numpy array for shared table data.
    
    Methods:
        __init__(shareddata, database, period, source, tablename, records=None, names=None,
                 formats=None, size=None, overwrite=False, user='master', partitioning=None):
            Initializes the TableMemory instance and its shared memory setup.
    
        malloc():
            Allocates shared memory for the table header and records based on the header metadata.
    
        free():
            Frees all shared memory segments associated with this table, including mutex and indexes.
    
        write_head(mtime):
            Writes the table header data from shared memory to the file system with a progress bar,
            and updates the file modification time.
    
        write_tail(mtime):
            Writes the table tail data from shared memory to the file system with a progress bar,
            and updates the file
    """
    def __init__(self, shareddata, database, period, source, tablename,
                records=None, names=None, formats=None, size=None,\
                overwrite=False, user='master',partitioning=None):
        """
        ```python
        '''
        Initializes an instance with specified parameters and sets up internal data structures.
        
        Parameters:
            shareddata: Shared data resource or context used by the instance.
            database: Database connection or identifier.
            period: Time period or range relevant to the data.
            source: Data source identifier.
            tablename: Name of the database table to interact with.
            records (optional): Data records to initialize with.
            names (optional): Names of the fields or columns.
            formats (optional): Data formats corresponding to the fields.
            size (optional): Size specification for the data structure.
            overwrite (bool, optional): Whether to overwrite existing data. Defaults to False.
            user (str, optional): User identifier for database operations. Defaults to 'master'.
            partitioning (optional): Partitioning scheme or configuration.
        
        Sets:
            self.type: An integer type identifier set to 2.
            self.shf_hdr: An empty NumPy array for header data.
            self.shf_data: An empty NumPy array for data.
        
        Calls the superclass initializer with the provided parameters and additional type information.
        '''
        ```
        """
        self.type = 2
        self.shf_hdr = np.array([])
        self.shf_data = np.array([])
        super().__init__(shareddata, database, period, source, tablename,
                         records=records, names=names, formats=formats, size=size,
                         overwrite=overwrite, user=user, tabletype=self.type, partitioning=partitioning)
       
    ############### MALLOC ###############
    def malloc(self):
        """
        ```python
        '''
        Allocate shared memory for the header and record data.
        
        This method calculates the total size needed for the shared memory segment based on the header and record sizes,
        then attempts to allocate the shared memory. If allocation fails, it raises an exception. Upon successful allocation,
        it initializes the header in the shared memory buffer and creates a SharedNumpy array for the record data.
        
        Attributes updated:
        - self.size: Set to header's 'recordssize' if not already set.
        - self.shm: The allocated shared memory object.
        - self.hdr: The header numpy structured array mapped to the shared memory buffer.
        - self.records: A SharedNumpy instance representing the record data in shared memory.
        
        Raises:
            Exception: If shared memory allocation fails.
        '''
        ```
        """
        if self.size is None:
            self.size = self.hdr['recordssize']
        nb_hdr = self.hdrdtype.itemsize  # number of header bytes
        # number of data bytes
        nb_records = int(self.hdr['recordssize']*self.hdr['itemsize'])
        total_size = int(nb_hdr+nb_records)

        [self.shm, ismalloc] = \
            self.shareddata.malloc(self.shm_name, create=True, size=total_size)
        if not ismalloc:
            raise Exception('Could not allocate shared memory!')

        # allocate header
        self.shm.buf[0:nb_hdr] = self.hdr.tobytes()
        self.hdr = np.ndarray((1,), dtype=self.hdrdtype,
                              buffer=self.shm.buf)[0]
        # allocate table data
        self.records = SharedNumpy('MEMORY',shape=(self.hdr['recordssize'],),
                                   dtype=self.recdtype, buffer=self.shm.buf, offset=nb_hdr)
        self.records.table = self
        self.records.preallocate()

    ############### FREE ###############
    def free(self):
        """
        Releases all shared memory segments and associated resources tied to this instance.
        
        This method acquires a lock to ensure thread safety while freeing multiple shared memory blocks identified by the base shared memory name and its related keys. After releasing these resources, it deletes the corresponding entry from the shared data dictionary.
        
        Steps performed:
        - Acquire the instance lock.
        - Free the main shared memory segment and its associated index segments.
        - Release the instance lock.
        - Free the mutex shared memory segment.
        - Remove the shared data entry corresponding to this instance's relative path.
        """
        self.acquire()
        self.shareddata.free(self.shm_name)
        self.shareddata.free(self.shm_name+'#pkey')
        self.shareddata.free(self.shm_name+'#dateidx')
        self.shareddata.free(self.shm_name+'#symbolidx')
        self.shareddata.free(self.shm_name+'#portidx')
        self.shareddata.free(self.shm_name+'#dtportidx')
        self.release()
        self.shareddata.free(self.shm_name+'#mutex')  # release
        del self.shareddata.data[self.relpath]
   
    ############### WRITE ###############
    def write_head(self, mtime):
        """
        ```python
        '''
        Writes the header and associated data from shared memory to a file in chunks,
        displaying a progress bar, and sets the file's modification time.
        
        Parameters:
            mtime (float): The modification time to set for the written file (as a Unix timestamp).
        
        Behavior:
        - Writes the header portion of the data (size determined by hdrdtype.itemsize) to the file.
        - Writes the main header data in chunks of up to 100 MB, updating a tqdm progress bar.
        - Flushes the file buffer to ensure all data is written.
        - Updates the file's access and modification times to the specified mtime.
        
        Assumes:
        - self.filepath is the path to the output file.
        - self.hdrdtype and self.hdr provide dtype and size information for the header.
        - self.shm.buf is a buffer containing the data to write.
        - self.relpath is used for progress bar description.
        '''
        ```
        """
        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        with open(self.filepath, 'wb') as f:
            f.write(self.shm.buf[0:nb_header])
            headsize_mb = nb_head / (1000000)
            blocksize = 1024*1024*100
            descr = 'Writing head:%iMB %s' % (headsize_mb, self.relpath)
            with tqdm(total=nb_head, unit='B', unit_scale=True, desc=descr) as pbar:
                written = 0
                while written < nb_head:
                    # write in chunks of max 100 MB size
                    chunk_size = min(blocksize, nb_head-written)
                    ib = nb_header+written
                    eb = nb_header+written+chunk_size
                    f.write(self.shm.buf[ib:eb])
                    written += chunk_size
                    pbar.update(chunk_size)
            f.flush()
        os.utime(self.filepath, (mtime, mtime))

    def write_tail(self, mtime):
        """
        ```python
        '''
        Writes the tail section of a shared memory buffer to a file with progress tracking.
        
        This method writes the tail data from a shared memory buffer to a specified file path
        in chunks of up to 100 MB, displaying a progress bar during the write operation.
        After writing, it updates the file's modification time to the given timestamp.
        
        Parameters:
            mtime (float): The modification time to set for the output file, expressed as a Unix timestamp.
        
        Behavior:
        - Calculates the sizes of the header, head, and tail sections based on metadata.
        - Opens the target file in binary write mode.
        - Writes the tail header followed by the tail data in chunks.
        - Uses tqdm to display a progress bar indicating the write progress.
        - Flushes the file buffer and sets the file's modification and access times.
        
        Assumptions:
        - `self.hdrdtype`, `self.hdr`, `self.tailhdr`, `self.tailpath`, `self.relpath`, and `self.shm.buf`
          are pre-defined attributes of the class instance.
        - `tqdm` and `os` modules are imported and available.
        '''
        ```
        """
        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_tail = int(self.tailhdr['tailsize']*self.hdr['itemsize'])

        with open(self.tailpath, 'wb') as f:
            f.write(self.tailhdr)
            tailsize_mb = nb_tail / (1000000)
            blocksize = 1024*1024*100  # 100 MB
            descr = 'Writing tail:%iMB %s' % (tailsize_mb, self.relpath)

            # Setup progress bar for tail
            with tqdm(total=nb_tail, unit='B', unit_scale=True, desc=descr) as pbar:
                written = 0
                while written < nb_tail:
                    # write in chunks of max 100 MB size
                    chunk_size = min(blocksize, nb_tail-written)
                    ib = nb_header+nb_head+written
                    eb = ib+chunk_size
                    f.write(self.shm.buf[ib:eb])
                    written += chunk_size
                    pbar.update(chunk_size)
            f.flush()
        os.utime(self.tailpath, (mtime, mtime))

