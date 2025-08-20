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
import traceback
import asyncio
import importlib

from SharedData.Logger import Logger
from SharedData.IO.AWSS3 import S3Upload, S3Download, S3ListFolder, S3GetMtime, S3DeleteFile
from SharedData.TableIndex import TableIndex
from SharedData.SharedNumpy import SharedNumpy
from SharedData.IO.ClientSocket import ClientSocket
from SharedData.IO.ClientWebSocket import ClientWebSocket
from SharedData.IO.ClientAPI import ClientAPI
from SharedData.Database import STRING_FIELDS

class Table:

    # TODO: create partitioning option yearly, monthly, daily
    """
    '''
    Represents a data table with support for disk or memory storage, partitioning, indexing, and remote synchronization.
    
    This class manages table metadata, schema initialization, record storage, and concurrency control. It supports creating, loading, and updating tables with optional partitioning by year, month, or day. The table data can be synchronized with remote storage (e.g., S3) including downloading and uploading compressed headers and tails.
    
    Key features include:
    - Initialization with schema and shared data management.
    - Support for different storage types (disk or memory).
    - Automatic handling of table partitioning and date ranges.
    - Creation and maintenance of table headers and indexes.
    - Efficient reading and writing of table data with concurrency locks.
    - Conversion between pandas DataFrames and internal record arrays.
    - Subscription and publishing capabilities over socket, websocket, or API methods.
    - Threaded upload and download operations with progress reporting.
    
    Parameters:
        shareddata: SharedData
            Shared data manager providing schema, mutex, and disk folder information.
        database: str
            Name of the database the table belongs to.
        period: str
            Data period identifier (e.g., 'M15', 'M1').
        source: str
            Data source identifier.
        tablename: str
            Name of
    """
    def __init__(self, shareddata, database, period, source, tablename,
                 records=None, names=None, formats=None, size=None, hasindex=True,
                 overwrite=False, user='master', tabletype=1, partitioning=None):
        # tabletype 1: DISK, 2: MEMORY
        """
        '''
        Initialize a table object with specified parameters, setting up schema, records, indexing, and partitioning.
        
        Parameters:
            shareddata: Shared data resource used by the table.
            database (str): Name of the database.
            period (str): Time period identifier (e.g., 'M15', 'M1').
            source (str): Data source identifier.
            tablename (str): Name of the table, possibly including partition info.
            records (optional): Initial records to populate the table.
            names (list, optional): List of field names for the table schema.
            formats (list, optional): List of data formats corresponding to field names.
            size (int, optional): Size of the table; if zero, disables indexing.
            hasindex (bool, optional): Whether the table has an index (default True).
            overwrite (bool, optional): Whether to overwrite existing table data (default False).
            user (str, optional): User identifier for table ownership (default 'master').
            tabletype (int, optional): Table storage type; 1 for DISK, 2 for MEMORY (default 1).
            partitioning (str, optional): Partitioning scheme ('yearly', 'monthly', 'daily').
        
        Raises:
        """
        self.type = tabletype

        self.shareddata = shareddata
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.subscription_thread = None
        self.publish_thread = None

        self.names = names
        self.formats = formats
        self.size = size
        if not size is None:
            if size == 0:
                self.hasindex = False
        self.hasindex = hasindex
        self.overwrite = overwrite
        self.partitioning = partitioning
        self.mindate = np.datetime64('1970-01-01', 'ns')
        self.maxdate = np.datetime64('2100-01-01', 'ns')
        if self.partitioning is not None:
            if self.partitioning == 'yearly':
                self.mindate = np.datetime64(pd.to_datetime(self.tablename.split('/')[1],format='%Y'), 'ns')
                self.maxdate = np.datetime64(self.mindate + pd.DateOffset(years=1), 'ns')
            elif self.partitioning == 'monthly':
                self.mindate = np.datetime64(pd.to_datetime(self.tablename.split('/')[1],format='%Y%m'), 'ns')
                self.maxdate = np.datetime64(self.mindate + pd.DateOffset(months=1), 'ns')
            elif self.partitioning == 'daily':
                self.mindate = np.datetime64(pd.to_datetime(self.tablename.split('/')[1],format='%Y%m%d'), 'ns')
                self.maxdate = np.datetime64(self.mindate + pd.DateOffset(days=1), 'ns')
        
        self.periodns = np.int64(24*60*60*1000*1000*1000)
        if self.period == 'M15': 
            self.periodns = np.int64(15*60*1000*1000*1000)
        elif self.period == 'M1':
            self.periodns = np.int64(1*60*1000*1000*1000)
        elif self.period == 'RT':
            self.periodns = np.int64(1*1000*1000*1000)
            self.hasindex = False

        # header
        self.hdr = None
        # creation time
        self.ctime = None
        # records
        self.recnames = []
        self.recformats = []
        self.recdtype = None
        self.records = np.ndarray([])        
        # index
        self.index = TableIndex(self)
        
        errmsg = ''
        try:            
            
            self.init_schema()

            if not records is None:
                records = self.parse_records(records)

            if (not self.exists) | (self.overwrite):

                self.create_table(records)

            elif self.exists:

                self.load_table(records)

            # set the modify time of the file
            self.hdr['isloaded'] = 1
            self.mutex['isloaded'] = 1
            mtime = max(self.hdr['mtime'],self.hdr['mtimehead'], self.hdr['mtimetail'])
            self.hdr['mtime'] = mtime
            os.utime(self.filepath, (mtime, mtime))
            
        except Exception as e:
            tb = traceback.format_exc()
            errmsg = '%s error initializing\n %s\n%s!' % (
                self.relpath, str(tb), str(e))
            # errmsg = '%s error initalizing \n%s!' % (self.relpath,str(e))
            Logger.log.error(errmsg)
        finally:
            self.release()
            if errmsg != '':
                self.free()
                raise Exception(errmsg)
    
    def init_schema(self):
        """
        Initialize the schema and related attributes for the table instance.
        
        This method sets up header and tail header formats and names, initializes mutexes for shared memory access,
        determines the storage path based on user, database, period, source, and tablename, and manages schema information
        from shared data. It handles synchronization and consistency checks for the table's loading type, updates or inserts
        the table schema if necessary, and selects an appropriate database folder based on availability and usage.
        
        It also ensures the necessary directories exist, sets file paths for data, header, and tail files, and checks for
        the existence of the table data locally or remotely.
        
        Raises:
            Exception: If there are inconsistencies in the mutex type or errors in updating or retrieving the schema or database folder.
        """
        self.header_changed = False
        # head header
        self._hdrnames = ['headersize', 'headerdescr', 'version', 'md5hashhead', 'md5hashtail',
                          'ctime', 'mtime', 'mtimehead', 'mtimetail',
                          'itemsize', 'recordssize', 'count',
                          'headsize', 'tailsize', 'minchgid',
                          'hastail', 'isloaded', 'hasindex', 'isidxcreated', 'isidxsorted',
                          'descr']
        self._hdrformats = ['<i8', '|S320', '|S8', '|S16', '|S16',
                            '<f8', '<f8', '<f8', '<f8',
                            '<i8', '<i8', '<i8',
                            '<i8', '<i8', '<i8',
                            '<u1', '<u1', '<u1', '<u1', '<u1',
                            '|SXXX']
        # tail header
        self._tailhdrnames = ['headersize', 'headerdescr',
                              'md5hash', 'mtime', 'tailsize']
        self._tailhdrformats = ['<i8', '|S80', '|S16', '<f8', '<i8']
    
        self.exists_remote = False
        self.exists_local = False
        
        # path        
        self.shm_name = f'{self.user}/{self.database}/{self.period}/{self.source}/table/{self.tablename}'
        self.relpath = str(self.shm_name)
        if os.name == 'posix':
            self.shm_name = self.shm_name.replace('/', '\\')

        # mutex
        self.pid = os.getpid()
        [self.shm_mutex, self.mutex, self.ismalloc] = \
            self.shareddata.mutex(self.shm_name, self.pid)
        if (self.mutex['type']==0): # type not initialized
            self.mutex['type'] = self.type

        elif self.mutex['type'] != self.type:
            if self.mutex['type'] == 1:
                errmsg = f'Table {self.relpath} is loaded as DISK!'
                Logger.log.error(errmsg)
                raise Exception(errmsg)
            elif self.mutex['type'] == 2:
                errmsg = f'Tabel {self.relpath} is loaded as MEMORY!'
                Logger.log.error(errmsg)
                raise Exception(errmsg)
            else:
                errmsg = f'Table {self.relpath} is loaded with unknown type!'
                Logger.log.error(errmsg)
                raise Exception(errmsg)        

        # schema
        self.database_folder = self.shareddata.dbfolders[0]
        self.schema = None
        
        if not self.shareddata.schema is None:
            errmsg=''
            try:            
                self.shareddata.schema.table.acquire()
                buff = np.full((1,),np.nan,dtype=self.shareddata.schema.dtype)
                buff['symbol'] = self.shm_name.replace('\\', '/')
                loc = self.shareddata.schema.get_loc(buff,acquire=False)
                if loc[0] != -1: # table exists
                    self.schema = self.shareddata.schema[loc[0]]
                    folder_local = self.schema['folder_local']
                    self.database_folder = folder_local.decode('utf-8')
                else: # table does not exist
                    self.shareddata.schema.upsert(buff,acquire=False)
                    loc = self.shareddata.schema.get_loc(buff,acquire=False)
                    if loc[0] == -1: # check if table was added
                        errmsg = '%s error updating schema' % self.relpath
                        Logger.log.error(errmsg)
                        raise Exception(errmsg)
                    
                    self.schema = self.shareddata.schema[loc[0]]
                    self.database_folder = ''
                
                if (self.database_folder == '') | (self.database_folder == 'nan'):
                    # select the first disk with less percent_used
                    if len(self.shareddata.dbfolders) > 1:
                        # scan folders to check if table is already initialized
                        for f in self.shareddata.dbfolders:
                            tmppath = Path(f) / self.shm_name
                            tmppath = Path(str(tmppath).replace('\\', '/'))
                            tmppath = tmppath / 'data.bin'
                            if tmppath.is_file():
                                self.database_folder = f
                                break
                        
                        # if table not initialized get the disk with less percent_used
                        if (self.database_folder == '') | (self.database_folder == 'nan'):
                            dfdisks = self.shareddata.list_disks()
                            self.database_folder = dfdisks.index[0]
                    else:                    
                        self.database_folder = self.shareddata.dbfolders[0]

                if (self.database_folder == '') | (self.database_folder == 'nan'):
                    errmsg = '%s error getting database folder' % self.relpath
                    raise Exception(errmsg)
                else:
                    self.schema['folder_local'] = self.database_folder.encode('utf-8')
                    
            except Exception as e:
                errmsg = '%s error getting database folder\n%s!' % (self.relpath,str(e))
                Logger.log.error(errmsg)
            finally:
                self.shareddata.schema.table.release()
                if errmsg != '':
                    raise Exception(errmsg)
                            
        self.path = Path(self.database_folder)
        self.path = self.path / self.shm_name
        self.path = Path(str(self.path).replace('\\', '/'))
        os.makedirs(self.path, exist_ok=True)
        self.filepath = self.path / 'data.bin'
        self.headpath = self.path / 'head.bin'
        self.tailpath = self.path / 'tail.bin'

        self.exists_local = self.filepath.is_file()
        if self.exists_local:            
            self.exists = True
        else:                                
            self.exists = self.get_exists_remote()
                
    def get_exists_remote(self):
        """
        Checks if a remote shared memory resource exists at a specified search path.
        
        The method constructs a search path by normalizing the shared memory name and removing the user component.
        It then queries the remote shared data for any tables at that path associated with the user.
        Returns True if any remote tables are found, otherwise False.
        
        Returns:
            bool: True if remote shared memory data exists at the search path, False otherwise.
        """
        searchpath = self.shm_name.replace('\\', '/').replace(self.user,'').lstrip('/')
        dftables = self.shareddata.list_remote(searchpath, user=self.user)
        if not dftables.empty:
            # TODO: fill schema
            pass 
        return not dftables.empty    

    def parse_records(self, records):
        """
        Parses the input records and extracts metadata such as field names and formats.
        
        If the input `records` is a pandas DataFrame, it is first converted to a structured array using the `df2records` method. The method then retrieves the data type descriptor (`descr`) from the array interface of the records, extracting the field names and formats into `self.names` and `self.formats` respectively. If `self.size` is not already set, it is initialized to the total number of records.
        
        Parameters:
            records (pandas.DataFrame or numpy.ndarray): The input data to parse.
        
        Returns:
            numpy.ndarray or structured array: The processed records, potentially converted from a DataFrame.
        """
        if (not records is None):                
            if isinstance(records, pd.DataFrame):
                records = self.df2records(records)
            descr = records.__array_interface__['descr']
            self.names = [item[0] for item in descr]
            self.formats = [item[1] for item in descr]
            if self.size is None:
                self.size = int(records.size)
        
        return records

    ############### CREATE ###############    
    def create_table(self, records):
        # create new table or overwrite existing table
        """
        Create a new table or overwrite an existing one with the provided records.
        
        This method performs the following steps:
        - If the table schema attributes (`names`, `formats`, and `size`) are defined, it creates the table header, file, and allocates memory.
        - If the table does not exist or overwrite is requested but schema attributes are missing, it raises an exception.
        - Inserts the given records into the table if any are provided.
        - If the table has an index, it initializes the index and verifies its coherence. If the index is not coherent, it attempts to reinitialize it and raises an exception if coherence cannot be established.
        
        Parameters:
            records (optional): The records to insert into the table after creation.
        
        Raises:
            Exception: If the table does not exist and cannot be created, or if the index cannot be properly created.
        """
        if (not self.names is None) \
            & (not self.formats is None)\
                & (not self.size is None):
            self.create_header()
            self.create_file()
            self.malloc()

        elif (not self.exists) | (self.overwrite):
            raise Exception('%s not found create first!' % (self.relpath))

        if not records is None:
            self.records.insert(records, acquire=False)

        if self.hasindex:
            self.index.initialize()
            if self.records.count>0:
                # check if index is coherent
                loc = self.records.get_loc(self.records[0:1], acquire=False)
                if loc[0]!=0: 
                    # index is not coherent
                    self.hdr['isidxcreated']=0
                    self.index.initialize()
                    loc = self.records.get_loc(self.records[0:1], acquire=False)
                    if loc[0]!=0:
                        raise Exception('Cannot create index!')

    def create_header(self):

        """
        Create and validate the header and record array dtype for the dataset.
        
        This method performs the following steps:
        - Validates that the initial columns in `self.names` match the primary key columns defined in `self.index.pkeycolumns`.
        - Ensures that the 'date' field, if present, has the correct dtype '<M8[ns]'.
        - Checks that string fields defined in `STRING_FIELDS` have string dtype '|S' if `self.hasindex` is True.
        - Inserts a 'mtime' field with dtype '<M8[ns]' if not present, or validates its dtype if present.
        - Confirms that `self.names` and `self.formats` have the same length.
        - Constructs the numpy dtype for the record array (`self.recdtype`) based on `self.names` and `self.formats`.
        - Builds the header dtype (`self.hdrdtype`) and initializes a header record array (`self.hdr`) with metadata including version, timestamps, sizes, and flags.
        - Sets flags related to indexing and loading status.
        
        Raises:
            Exception: If primary key columns do not match, or if any dtype validations fail, or if `names` and `formats` lengths differ.
        """
        check_pkey = True
        npkeys = len(self.index.pkeycolumns)
        if len(self.names) >= npkeys:
            for k in range(npkeys):
                check_pkey = (check_pkey) & (
                    self.names[k] == self.index.pkeycolumns[k])
        else:
            check_pkey = False
        if not check_pkey:
            raise Exception('First columns must be %s!' %
                            (self.index.pkeycolumns))
        else:
            if 'date' in self.names:
                if self.formats[self.names.index('date')] != '<M8[ns]':
                    raise Exception('date must be <M8[ns]!')
            
            if self.hasindex:
                for field in STRING_FIELDS:
                    if field in self.names:
                        fielddtype = self.formats[self.names.index(field)]
                        if not '|S' in fielddtype:
                            raise Exception('symbol must be a string |S!')

            if not 'mtime' in self.names:
                self.names.insert(npkeys, 'mtime')
                self.formats.insert(npkeys, '<M8[ns]')
            elif self.formats[self.names.index('mtime')] != '<M8[ns]':
                raise Exception('mtime must be <M8[ns]!')
            
            if len(self.names) != len(self.formats):
                raise Exception('names and formats must have same length!')
            
            # malloc recarray
            self.recnames = self.names
            self.rectypes = self.formats
            self.recdtype = np.dtype(
                {'names': self.recnames, 'formats': self.rectypes})
            descr_str = ','.join(self.recnames)+';'+','.join(self.rectypes)
            descr_str_b = str.encode(
                descr_str, encoding='UTF-8', errors='ignore')
            len_descr = len(descr_str_b)

            # build header
            self.hdrnames = self._hdrnames
            hdrformats = self._hdrformats.copy()
            hdrformats[-1] = hdrformats[-1].replace('XXX', str(len_descr))
            self.hdrformats = hdrformats
            hdrnames = ','.join(self.hdrnames)
            hdrdtypes = ','.join(self.hdrformats)
            hdrdescr_str = hdrnames+';'+hdrdtypes
            hdrdescr_str_b = str.encode(
                hdrdescr_str, encoding='UTF-8', errors='ignore')

            self.hdrdtype = np.dtype(
                {'names': self.hdrnames, 'formats': self.hdrformats})
            self.hdr = np.recarray(shape=(1,), dtype=self.hdrdtype)[0]
            self.hdr['headersize'] = 320
            self.hdr['headerdescr'] = b'\x00' * len(self.hdr['headerdescr'])
            self.hdr['headerdescr'] = hdrdescr_str_b
            self.hdr['version'] = importlib.metadata.version("shareddata")
            self.hdr['ctime'] = datetime.now().timestamp()
            self.ctime = self.hdr['ctime']
            self.hdr['mtime'] = datetime.now().timestamp()
            self.hdr['mtimehead'] = self.hdr['mtime']
            self.hdr['mtimetail'] = self.hdr['mtime']
            self.hdr['count'] = 0
            self.hdr['minchgid'] = self.hdr['count']
            self.hdr['itemsize'] = int(self.recdtype.itemsize)
            self.hdr['recordssize'] = int(self.size)
            self.hdr['headsize'] = 0
            self.hdr['descr'] = descr_str_b
            self.hdr['isloaded'] = 0
            if self.hasindex:
                self.hdr['hasindex'] = 1
            else:
                self.hdr['hasindex'] = 0
            self.hdr['isloaded'] = 0
            self.hdr['isidxcreated'] = 0
            self.hdr['isidxsorted'] = 1
            
    def create_file(self):
        """
        Create or extend a file at the specified filepath to a predetermined size.
        
        The target file size is calculated based on the sum of the header dtype item size and the product of the record dtype item size and the number of records (self.size). If the file does not exist, it creates the necessary directories, creates the file, and preallocates space by seeking to the last byte and writing a null byte. On POSIX systems, it uses os.posix_fallocate for efficient disk space allocation. If the file exists but is smaller than the target size, it extends the file similarly. Windows preallocation is not yet implemented.
        """
        totalbytes = int(self.hdrdtype.itemsize
                         + self.recdtype.itemsize*self.size)
        if not Path(self.filepath).is_file():
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'wb') as f:
                # Seek to the end of the file
                f.seek(totalbytes-1)
                # Write a single null byte to the end of the file
                f.write(b'\x00')
                if os.name == 'posix':
                    os.posix_fallocate(f.fileno(), 0, totalbytes)
                elif os.name == 'nt':
                    pass  # TODO: implement preallocation for windows in pyd
        elif (Path(self.filepath).stat().st_size < totalbytes):
            with open(self.filepath, 'ab') as f:
                # Seek to the end of the file
                f.seek(totalbytes-1)
                # Write a single null byte to the end of the file
                f.write(b'\x00')
                if os.name == 'posix':
                    os.posix_fallocate(f.fileno(), 0, totalbytes)
                elif os.name == 'nt':
                    pass  # TODO: implement preallocation for windows in pyd

    def copy_file(self):
        """
        Copies the original file to a temporary file while writing a new header and preserving the data.
        If the new file size is larger than the original, the file is extended with null bytes.
        After copying and extending, the original file is deleted and the temporary file is renamed to the original file path.
        Displays a progress bar during the copying process.
        """
        if self.size is None:
            self.size = self.hdr['recordssize']
        totalbytes = int(self.hdrdtype.itemsize
                         + self.recdtype.itemsize*self.size)

        orig_size = int(self.orig_hdr.dtype.itemsize
                        + self.orig_hdr['recordssize']*self.orig_hdr['itemsize'])

        self.filepathtmp = str(self.filepath)+'.tmp'
        with open(self.filepath, 'rb') as f:
            with open(self.filepathtmp, 'wb') as ftmp:
                # write new header
                ftmp.seek(0)
                ftmp.write(self.hdr.tobytes())
                # copy data
                f.seek(self.orig_hdr.dtype.itemsize)
                bwritten = self.orig_hdr.dtype.itemsize
                message = 'Copying file :%iMB %s' % (
                    orig_size / (1024*1024), self.relpath)
                buffersize = int(1024**2*250)
                with tqdm(total=orig_size, unit='B', unit_scale=True, desc=message) as pbar:
                    while bwritten < orig_size:
                        nwrite = int(min(buffersize, orig_size-bwritten))
                        ftmp.write(f.read(nwrite))
                        pbar.update(nwrite)
                        bwritten += nwrite
                    # extend file if needed
                    if totalbytes > orig_size:
                        ftmp.write(b'\x00'*(totalbytes-orig_size))
                    ftmp.flush()

        # rename file        
        os.remove(self.filepath)        
        os.rename(self.filepathtmp, self.filepath)

    ############### DOWNLOAD ###############
    def download(self):
        """
        Download and update the object's data from remote gzip-compressed files stored in S3.
        
        This method performs the following steps:
        1. Downloads the 'head' part of the data from a remote S3 path with a '.gzip' extension.
        2. If the remote 'head' file is newer than the local copy, it decompresses and reads the header,
           updating the local modification time and forcing a tail download.
        3. If the header indicates the presence of a 'tail' part, it downloads, decompresses, and reads it,
           updating the tail modification time.
        4. Creates or updates the local file representation.
        5. Reads the decompressed 'head' and 'tail' data into the object, resetting load and index flags.
        
        Dependencies:
        - S3Download: function to download files from S3, returning file-like objects and modification times.
        - gzip: used to decompress the downloaded gzip files.
        - Logger: used for debug logging of download performance.
        
        Updates internal state variables such as self.hdr with modification times and load status.
        """
        head_io = None
        tail_io = None
        mtimetail = None

        tini = time.time()
        remote_path = str(self.headpath)+'.gzip'
        if not self.hdr is None:
            mtimetail = self.hdr['mtimetail']
            [head_io_gzip, head_local_mtime, head_remote_mtime] = \
                S3Download(remote_path, local_mtime=self.hdr['mtimehead']
                        ,database_folder=self.database_folder)            
        else:
            [head_io_gzip, head_local_mtime, head_remote_mtime] = \
                S3Download(remote_path,database_folder=self.database_folder)

        if not head_io_gzip is None:
            # remote file is newer than local
            # unzip head and read
            te = time.time()-tini+0.000001
            datasize = head_io_gzip.getbuffer().nbytes/1000000
            Logger.log.debug('download head %s %.2fMB in %.2fs %.2fMBps ' %
                             (self.relpath, datasize, te, datasize/te))
            head_io_gzip.seek(0)
            head_io = gzip.GzipFile(fileobj=head_io_gzip, mode='rb')
            self.read_header(head_io)
            self.hdr['mtimehead'] = head_remote_mtime # update the head mtime            
            mtimetail = self.hdr['mtimetail'] - 1  # force tail download

        if not self.hdr is None:
            # read tail if needed
            if self.hdr['hastail'] == 1:
                remote_path = str(self.tailpath)+'.gzip'
                [tail_io_gzip, tail_local_mtime, tail_remote_mtime] = \
                    S3Download(remote_path, local_mtime=mtimetail,
                            database_folder=self.database_folder)
                if not tail_io_gzip is None:
                    tail_io_gzip.seek(0)
                    tail_io = gzip.GzipFile(fileobj=tail_io_gzip, mode='rb')
                    self.read_tailheader(tail_io)
                    self.hdr['mtimetail'] = tail_remote_mtime # update the tail mtime

        self.create_file()

        if not head_io is None:
            self.read_head(head_io)
            self.hdr['isloaded'] = 0
            self.hdr['isidxcreated'] = 0

        if not tail_io is None:
            self.read_tail(tail_io)
            self.hdr['isloaded'] = 0
            self.hdr['isidxcreated'] = 0

    ############### READ ###############
    def load_table(self, records):
        # open existing table
        """
        Load data into the table, ensuring the local file is available and up to date.
        
        If a local table file exists, it reads the header from the file. If the table is not loaded or the local file does not exist, it downloads the table data. Memory allocation for the table is then performed.
        
        If the table has an index, it initializes the index and verifies its coherence by checking the location of the first record. If the index is not coherent, it resets and reinitializes the index. If the index still cannot be created correctly, an exception is raised.
        
        Finally, if new records are provided, they are upserted into the table's records.
        """
        if self.exists_local:
            with open(self.filepath, 'rb') as io_obj:
                self.read_header(io_obj)

        if ((self.mutex['isloaded']==0) | (not self.exists_local)):
            self.download()

        self.malloc()

        if self.hasindex:
            self.index.initialize()
            if self.records.count>0:
                # check if index is coherent
                loc = self.records.get_loc(self.records[0:1], acquire=False)
                if loc[0]!=0: 
                    # index is not coherent
                    self.hdr['isidxcreated']=0
                    self.index.initialize()
                    loc = self.records.get_loc(self.records[0:1], acquire=False)
                    if loc[0]!=0:
                        raise Exception('Cannot create index!')
                    
        if not records is None:
            self.records.upsert(records, acquire=False)

    def read_header(self, io_obj):
        """
        '''
        Reads and processes the header from a binary I/O object, initializing the header and record data types and attributes.
        
        Parameters:
            io_obj (io.BufferedIOBase): A binary I/O object positioned at the start of the file.
        
        Behavior:
        - Seeks to the beginning of the I/O object.
        - Reads the size of the header description and raises an exception if empty.
        - Decodes and parses the header description to extract header field names and formats.
        - Constructs a NumPy dtype for the header and reads the header data into a structured array.
        - Decodes the record description from the header and constructs the record dtype.
        - Validates string fields if an index is present and logs warnings if mismatches occur.
        - Adjusts internal size attributes based on header values.
        - Checks if the header matches expected names; if not, converts and updates the header accordingly.
        - Sets various header flags and timestamps.
        - If a local copy exists and the I/O object is a buffered reader, closes it and copies the file locally.
        
        Raises:
            Exception: If the header description size is zero.
        
        Notes:
        - Relies on external variables and methods such as STRING_FIELDS, Logger, self.relpath, self._hdrnames, self._hdrformats, self.hasindex, self.exists
        """
        io_obj.seek(0)
        # load header dtype
        nbhdrdescr = int.from_bytes(io_obj.read(8), byteorder='little')
        if nbhdrdescr == 0:
            raise Exception('Empty header description!')
        hdrdescr_b = io_obj.read(nbhdrdescr)
        hdrdescr = hdrdescr_b.decode(encoding='UTF-8', errors='ignore')
        hdrdescr = hdrdescr.split('\x00', 1)[0]        
        self.hdrnames = hdrdescr.split(';')[0].split(',')
        self.hdrformats = hdrdescr.split(';')[1].split(',')
        self.hdrdtype = np.dtype(
            {'names': self.hdrnames, 'formats': self.hdrformats})
        # read header
        io_obj.seek(0)
        self.hdr = np.ndarray((1,), dtype=self.hdrdtype,
                              buffer=io_obj.read(self.hdrdtype.itemsize))[0]
        self.hdr = self.hdr.copy()
        # load data dtype
        try:
            descr = self.hdr['descr'].decode(encoding='UTF-8')
            self.recnames = descr.split(';')[0].split(',')
            self.recformats = descr.split(';')[1].split(',')
        except Exception as e:
            errmsg = f'Table header is corrupted!:{self.relpath}\n{str(e)}'
            Logger.log.critical(errmsg)
            if not self.names is None:
                Logger.log.warning(f'Trying to recover:{self.relpath}')
                self.recnames = self.names
                self.recformats = self.formats
                descr_str = ','.join(self.recnames)+';'+','.join(self.recformats)
                descr_str_b = str.encode(
                    descr_str, encoding='UTF-8', errors='ignore')
                len_descr = len(descr_str_b)
                if len_descr == len(self.hdr['descr']):
                    self.hdr['descr'] = descr_str_b
                    with open(self.filepath, 'r+b') as f:
                        f.seek(0)  # Move to start of file
                        f.write(self.hdr.tobytes())  # Write header bytes
                        f.flush()  # Ensure write is committed
                        os.fsync(f.fileno())  # Force disk write
                else:
                    errmsg = f'Cannot recover header!:{self.relpath}\n{str(e)}'
                    raise Exception(errmsg)                
            else:
                raise Exception(errmsg)
            
        if 'hasindex' in self.hdrnames:
            if self.hdr['hasindex']==1:
                for field in STRING_FIELDS:
                    if field in self.recnames:
                        fielddtype = self.recformats[self.recnames.index(field)]
                        # check if field is a string
                        if not (('S' in fielddtype) or ('|S' in fielddtype)):
                            warnmsg = f'{field} is not a string in {self.relpath}!'
                            Logger.log.warning(warnmsg)
                            self.hdr['hasindex']=0

        self.recdtype = np.dtype(
            {'names': self.recnames, 'formats': self.recformats})

        if self.hdr['count'] > self.hdr['recordssize']:
            self.hdr['recordssize'] = self.hdr['count']

        if self.size is None:
            self.size = self.hdr['recordssize']
        elif self.size < self.hdr['recordssize']:
            self.size = self.hdr['recordssize']                

        if self.hdrnames == self._hdrnames:            
            self.hasindex = self.hdr['hasindex']==1
            self.orig_hdr = self.hdr
        else:
            # convert header
            self.header_changed = True
            self.orig_hdr = self.hdr.copy()

            self.hdrnames = self._hdrnames
            len_descr = len(self.hdr['descr'])
            hdrformats = self._hdrformats.copy()
            hdrformats[-1] = hdrformats[-1].replace('XXX', str(len_descr))
            self.hdrformats = hdrformats
            hdrnames = ','.join(self.hdrnames)
            hdrdtypes = ','.join(self.hdrformats)
            hdrdescr_str = hdrnames+';'+hdrdtypes
            hdrdescr_str_b = str.encode(
                hdrdescr_str, encoding='UTF-8', errors='ignore')
            self.hdrdtype = np.dtype(
                {'names': self.hdrnames, 'formats': self.hdrformats})
            self.hdr = np.ndarray((1,), dtype=self.hdrdtype)[0]
            for name in self.orig_hdr.dtype.names:
                if name in self.hdr.dtype.names:
                    self.hdr[name] = self.orig_hdr[name]
            self.hdr['headerdescr'] = b'\x00' * len(self.hdr['headerdescr'])
            self.hdr['headerdescr'] = hdrdescr_str_b            
            if not 'mtimehead' in self.orig_hdr.dtype.names:
                self.hdr['mtimehead'] = self.hdr['mtime']
            if not 'mtimetail' in self.orig_hdr.dtype.names:
                self.hdr['mtimetail'] = self.hdr['mtime']            
            
            if 'hasindex' in self.orig_hdr.dtype.names:
                self.hasindex = self.orig_hdr['hasindex']==1
                self.hdr['hasindex'] = self.orig_hdr['hasindex']
            else:                
                if self.hasindex:
                    self.hdr['hasindex'] = 1
                else:
                    self.hdr['hasindex'] = 0

            self.hdr['isloaded'] = 0
            self.hdr['isidxcreated'] = 0
            self.hdr['headersize'] = 320
            self.hdr['isidxsorted'] = 0
            self.hdr['ctime'] = datetime.now().timestamp()
            self.ctime = self.hdr['ctime']
            self.hdr['version'] = importlib.metadata.version("shareddata")

            if self.exists_local:
                if isinstance(io_obj, io.BufferedReader):                    
                    io_obj.close()
                self.copy_file()

    def read_tailheader(self, tail_io):
        """
        Reads and parses the tail header from a binary stream.
        
        This method reads the tail header size and description from the provided binary IO object `tail_io`, decodes the header names and formats, constructs a NumPy dtype for the tail header, and reads the tail header data into a structured NumPy array. It then updates the instance's `tailhdrnames`, `tailhdrformats`, `tailhdrdtype`, and `tailhdr` attributes accordingly. Finally, it updates the main header dictionary `self.hdr` with metadata extracted from the tail header, including the MD5 hash, modification time, tail size, and total count.
        
        Parameters:
            tail_io (io.BytesIO or similar): A binary stream positioned at the start of the tail header data.
        
        Side Effects:
            - Sets `self.tailhdrnames`, `self.tailhdrformats`, `self.tailhdrdtype`, and `self.tailhdr`.
            - Updates `self.hdr` dictionary with keys 'md5hashtail', 'mtimetail', 'tailsize', and 'count'.
        """
        tail_io.seek(0)
        tailnbhdrdescr = int.from_bytes(tail_io.read(8), byteorder='little')
        tailhdrdescr_b = tail_io.read(tailnbhdrdescr)
        tailhdrdescr = tailhdrdescr_b.decode(encoding='UTF-8', errors='ignore')
        tailhdrdescr = tailhdrdescr.replace('\x00', '')
        self.tailhdrnames = tailhdrdescr.split(';')[0].split(',')
        self.tailhdrformats = tailhdrdescr.split(';')[1].split(',')
        self.tailhdrdtype = np.dtype(
            {'names': self.tailhdrnames, 'formats': self.tailhdrformats})

        nbtailhdr = self.tailhdrdtype.itemsize
        tail_io.seek(0)
        tailheader_buf = tail_io.read(nbtailhdr)
        self.tailhdr = np.ndarray((1,),
                                  dtype=self.tailhdrdtype, buffer=tailheader_buf)[0]
        self.tailhdr = self.tailhdr.copy()
        self.tailhdr['headersize'] = tailnbhdrdescr
        # update header
        self.hdr['md5hashtail'] = self.tailhdr['md5hash']
        self.hdr['mtimetail'] = self.tailhdr['mtime']
        self.hdr['tailsize'] = self.tailhdr['tailsize']
        self.hdr['count'] = self.hdr['headsize']+self.tailhdr['tailsize']

    def read_head(self, head_io):
        """
        Reads header data from a given IO stream and writes it to the file specified by self.filepath.
        
        The method performs the following steps:
        1. Seeks to the beginning of the input head_io stream.
        2. Opens the target file in read-write binary mode.
        3. Writes the header bytes stored in self.hdr to the beginning of the file.
        4. Seeks past the original header size in head_io.
        5. Reads the head data in chunks (up to 250 MB at a time) from head_io and writes it to the file.
        6. Displays a progress bar indicating the amount of data being unzipped and written.
        
        Parameters:
        head_io (io.IOBase): A file-like object opened in binary mode containing the header and head data to be read.
        
        Raises:
        Any exceptions related to file I/O operations may be propagated.
        """
        buffer_size = 250 * 1024 * 1024  # 250 MB buffer size
        head_io.seek(0)
        with open(self.filepath, 'rb+') as f:
            # write header
            f.seek(0)
            f.write(self.hdr.tobytes())
            # seek start of head data
            head_io.seek(self.orig_hdr.dtype.itemsize)
            # read head data
            nb_head = (self.hdr['headsize']*self.hdr['itemsize'])
            message = 'Unzipping:%iMB %s' % (
                nb_head / (1024*1024), self.relpath)
            with tqdm(total=nb_head, unit='B', unit_scale=True, desc=message) as pbar:
                while True:
                    buffer = head_io.read(buffer_size)
                    if not buffer:
                        break
                    f.write(buffer)
                    pbar.update(len(buffer))
            f.flush()

    def read_tail(self, tail_io):
        """
        Writes data from the given tail_io buffer to a specific position in the file associated with this object.
        
        The method performs the following steps:
        1. Resets the tail_io buffer's position to the beginning.
        2. Calculates the offset in the file by summing the header size (nbhdr) and the head data size (nbhead).
        3. Opens the file in read-write binary mode.
        4. Seeks to the calculated offset in the file.
        5. Advances the tail_io buffer position by the size of the tail header.
        6. Writes the remaining data from tail_io into the file at the current position.
        7. Flushes the file buffer to ensure data is written to disk.
        
        Parameters:
        tail_io (io.BytesIO or similar): A file-like object containing the tail data to be written.
        
        Raises:
        Any exceptions related to file I/O operations may be propagated.
        """
        tail_io.seek(0)
        nbhdr = self.hdr.dtype.itemsize
        nbhead = self.hdr['headsize']*self.hdr['itemsize']
        with open(self.filepath, 'rb+') as f:
            f.seek(nbhdr+nbhead)
            tail_io.seek(self.tailhdr.dtype.itemsize)
            f.write(tail_io.read())
            f.flush()

    def compare_hash(self, h1, h2):
        """
        Compare two hash strings up to the length of the shorter one.
        
        Parameters:
            h1 (str): The first hash string.
            h2 (str): The second hash string.
        
        Returns:
            bool: True if the prefixes of both hashes up to the length of the shorter hash are equal, False otherwise.
        """
        l1 = len(h1)
        l2 = len(h2)
        l = min(l1, l2)
        return h1[:l] == h2[:l]

    ############### WRITE ###############
    def write(self, force_write=False):
        """
        Writes data to a file and uploads it concurrently using separate threads.
        
        This method performs the following steps:
        1. Acquires a lock to ensure thread safety.
        2. Creates or updates the file header if necessary.
        3. Starts two threads:
           - One to upload the data (possibly to S3) with header information.
           - Another to flush/write the file data locally.
        4. Waits for both threads to complete.
        5. Logs the write operation details including file path, data size, elapsed time, and throughput.
        6. Handles exceptions by logging an error message and re-raising the exception.
        7. Releases the lock regardless of success or failure.
        
        Parameters:
            force_write (bool): If True, forces the header to be written even if not modified.
        
        Raises:
            Exception: If the write or upload operation fails.
        """
        errmsg = ''
        try:
            self.acquire()

            tini = time.time()
            # create header
            mtime = self.hdr['mtime']
            write_head = False            
            write_head = self.fill_header(force_write)                

            thread_s3 = threading.Thread(
                target=self.upload, args=(write_head, mtime, force_write))
            thread_s3.start()

            thread_flush = threading.Thread(target=self.write_file)
            thread_flush.start()

            # join threads
            thread_s3.join()
            thread_flush.join()

            te = time.time() - tini
            datasize = self.hdr['count'] * self.hdr['itemsize'] / 1000000
            Logger.log.debug('write %s %.2fMB in %.2fs %.2fMBps ' %
                             (self.relpath, datasize, te, datasize / te))
        except Exception as e:
            errmsg = 'Could not write %s\n%s!' % (self.relpath, e)
            Logger.log.error(errmsg)
        finally:
            self.release()
            if errmsg != '':
                raise Exception(errmsg)

    def partition_head_tail(self):
        
        """
        Partition the records into head and tail segments based on the presence and value of a 'date' field.
        
        If the 'date' field is not present in the records, the entire dataset is considered as the head with no tail.
        If the 'date' field exists, the records are partitioned by the start of the current year:
        - Records before the current year form the head.
        - Records from the current year onward form the tail.
        
        Updates the header dictionary (`self.hdr`) with:
        - 'headsize': number of records in the head segment.
        - 'tailsize': number of records in the tail segment.
        - 'hastail': flag indicating if a tail segment exists (1 if yes, 0 if no).
        - 'minchgid': reset to one more than the total count.
        - 'mtimehead' and 'mtimetail': modification times for head and tail segments.
        
        Returns:
            write_head (bool): Indicates whether the head segment needs to be written/updated.
            headsize (int): Number of records in the head segment.
            tailsize (int): Number of records in the tail segment.
        """
        if not 'date' in self.records.dtype.names:
            tailsize = 0
            headsize = self.hdr['count']
            self.hdr['hastail'] = 0
        else:
            # partition data by current year
            partdate = pd.Timestamp(datetime(datetime.now().year, 1, 1))      
            if self.hdr['count']>0:  
                idx = self.records['date'] >= partdate
                if np.any(idx):  # there is data for the current year
                    if np.all(idx):  # all data for the current year
                        headsize = self.hdr['count']
                        tailsize = 0
                        self.hdr['hastail'] = 0
                    else:  # some data for the current year
                        partid = np.where(idx)[0][0]
                        headsize = partid
                        tailsize = self.hdr['count'] - partid
                        self.hdr['hastail'] = 1
                else:  # there is not data for the current year
                    tailsize = 0
                    headsize = self.hdr['count']
                    self.hdr['hastail'] = 0
            else:  # there is not data for the current year
                tailsize = 0
                headsize = self.hdr['count']
                self.hdr['hastail'] = 0

        headsize_chg = (headsize != self.hdr['headsize'])
        self.hdr['headsize'] = headsize        
        self.hdr['tailsize'] = tailsize

        head_modified = (self.hdr['minchgid'] <= self.hdr['headsize'])
        self.hdr['minchgid'] = self.hdr['count']+1 # reset the minchgid
        
        write_head = (head_modified) | (headsize_chg) 
        
        self.hdr['mtimetail'] = self.hdr['mtime']
        if write_head:
            self.hdr['mtimehead'] = self.hdr['mtime']

        return write_head, headsize, tailsize

    def fill_header(self, force_write=False):

        """
        Fill and update the header and tail header information, including computing MD5 hashes for data integrity.
        
        This method partitions the data into head and tail sections, initializes the tail header record array,
        and calculates MD5 hashes for the head and tail data sections. It supports incremental hashing with a
        progress bar for large data blocks to avoid memory overload.
        
        Parameters:
            force_write (bool): If True, forces the header to be written and the MD5 hash to be recalculated,
                                regardless of the current state.
        
        Returns:
            bool: A flag indicating whether the head section should be written.
        
        Side Effects:
            - Updates self.tailhdr with tail header metadata including header size, description, modification time,
              tail size, and MD5 hash.
            - Updates self.hdr with MD5 hashes for head and tail sections.
        """
        write_head, headsize, tailsize = self.partition_head_tail()

        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_tail = int(tailsize*self.hdr['itemsize'])

        self.tailhdrdtype = np.dtype(
            {'names': self._tailhdrnames, 'formats': self._tailhdrformats})
        self.tailhdr = np.recarray(shape=(1,), dtype=self.tailhdrdtype)[0]
        self.tailhdr['headersize'] = 80
        _headerdescr = ','.join(self._tailhdrnames) + \
            ';'+','.join(self._tailhdrformats)
        _headerdescr_b = str.encode(
            _headerdescr, encoding='UTF-8', errors='ignore')
        self.tailhdr['headerdescr'] = _headerdescr_b
        self.tailhdr['mtime'] = self.hdr['mtime']
        self.tailhdr['tailsize'] = tailsize

        if (write_head) | (force_write):
            self.hdr['md5hashhead'] = 0  # reset the hash value
            nb_records_mb = (nb_header+nb_head)/(1024*1024)
            if nb_records_mb <= 100:
                m = hashlib.md5(self.records[0:self.hdr['headsize']].tobytes())
            else:
                message = 'Creating md5 hash:%iMB %s' % (
                    nb_records_mb, self.relpath)
                block_size = 100 * 1024 * 1024  # or any other block size that you prefer
                chunklines = int(block_size/self.hdr['itemsize'])
                total_lines = self.hdr['headsize']
                read_lines = 0
                nb_total = self.hdr['headsize']*self.hdr['itemsize']
                m = hashlib.md5()
                # Use a with block to manage the progress bar
                with tqdm(total=nb_total, unit='B', unit_scale=True, desc=message) as pbar:
                    # Loop until we have read all the data
                    while read_lines < total_lines:
                        # Read a block of data
                        chunk_size = min(chunklines, total_lines-read_lines)
                        # Update the shared memory buffer with the newly read data
                        m.update(
                            self.records[read_lines:read_lines+chunk_size].tobytes())
                        read_lines += chunk_size  # update the total number of bytes read so far
                        # Update the progress bar
                        pbar.update(chunk_size*self.hdr['itemsize'])
            self.hdr['md5hashhead'] = m.digest()

        if self.hdr['hastail'] == 1:
            self.tailhdr['md5hash'] = 0  # reset the hash value
            self.hdr['md5hashtail'] = 0  # reset the hash value
            nb_records_mb = (nb_tail)/(1024*1024)
            startbyte = nb_header+nb_head
            if nb_records_mb <= 100:
                m = hashlib.md5(
                    self.records[self.hdr['headsize']:self.hdr['count']].tobytes())
            else:
                message = 'Creating md5 hash:%iMB %s' % (
                    nb_records_mb, self.relpath)
                block_size = 100 * 1024 * 1024  # or any other block size that you prefer
                chunklines = int(block_size/self.hdr['itemsize'])
                total_lines = self.tailhdr['tailsize']
                read_lines = 0
                tailstart = self.hdr['headsize']
                nb_total = self.tailhdr['tailsize']*self.hdr['itemsize']
                m = hashlib.md5()
                # Use a with block to manage the progress bar
                with tqdm(total=nb_total, unit='B', unit_scale=True, desc=message) as pbar:
                    # Loop until we have read all the data
                    while read_lines < total_lines:
                        # Read a block of data
                        chunk_size = min(chunklines, total_lines-read_lines)
                        # Update the shared memory buffer with the newly read data
                        m.update(
                            self.records[tailstart+read_lines:tailstart+read_lines+chunk_size].tobytes())
                        read_lines += chunk_size  # update the total number of bytes read so far
                        # Update the progress bar
                        pbar.update(chunk_size*self.hdr['itemsize'])

            self.tailhdr['md5hash'] = m.digest()
            self.hdr['md5hashtail'] = self.tailhdr['md5hash']

        return write_head

    ############### UPLOAD ###############
    def upload(self, write_head, mtime, force_write=False):        
        """
        Uploads the head and tail files to a remote storage if certain conditions are met.
        
        Checks the modification time of the remote head and tail files (with '.gzip' extension) and compares them to the local metadata.
        - Uploads the head file if `write_head` is True, the remote head is outdated, or `force_write` is True.
        - If the header indicates a tail exists (`hastail == 1`), uploads the tail file if the remote tail is outdated.
        
        Parameters:
            write_head (bool): Flag indicating whether to force writing the head file.
            mtime (float): The modification time to use for the upload.
            force_write (bool, optional): If True, forces the head file to be uploaded regardless of remote state. Defaults to False.
        """
        remote_head_mtime = S3GetMtime(str(self.headpath)+'.gzip', self.database_folder)
        remote_head_is_updated = False
        if not remote_head_mtime is None:
            remote_head_is_updated = remote_head_mtime >= self.hdr['mtimehead']

        if (write_head) | (not remote_head_is_updated) | (force_write):
            self.upload_head(mtime)

        if self.hdr['hastail'] == 1:
            remote_tail_mtime = S3GetMtime(str(self.tailpath)+'.gzip', self.database_folder)
            remote_tail_is_updated = False
            if not remote_tail_mtime is None:
                remote_tail_is_updated = remote_tail_mtime >= self.hdr['mtimetail']
            if not remote_tail_is_updated:
                self.upload_tail(mtime)
        else:
            self.delete_tail()

    def upload_head(self, mtime):
        # zip head        
        """
        Compresses the header data in chunks using gzip and uploads the compressed file to S3.
        
        Parameters:
            mtime (float): The modification time to associate with the uploaded file.
        
        The method performs the following steps:
        - Creates an in-memory bytes buffer.
        - Compresses the header data (`self.hdr` and `self.records`) in chunks of up to 100 MB using gzip with compression level 1.
        - Displays a progress bar indicating the compression progress.
        - Uploads the resulting gzip file to an S3 bucket using the `S3Upload` function, storing it at `self.headpath` with a '.gzip' extension and associating it with the given modification time.
        """
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            gz.write(self.hdr.tobytes())
            headsize_mb = (self.hdr['headsize'] *
                           self.hdr['itemsize']) / (1024*1024)
            blocksize = 1024*1024*100
            chunklines = int(blocksize/self.hdr['itemsize'])
            descr = 'Zipping:%iMB %s' % (headsize_mb, self.relpath)
            with tqdm(total=headsize_mb, unit='B', unit_scale=True, desc=descr) as pbar:
                written = 0
                while written < self.hdr['headsize']:
                    # write in chunks of max 100 MB size
                    chunk_size = min(chunklines, self.hdr['headsize']-written)
                    gz.write(
                        self.records[written:written+chunk_size].tobytes())
                    written += chunk_size
                    pbar.update(chunk_size*self.hdr['itemsize'])
        S3Upload(gzip_io, str(self.headpath)+'.gzip', mtime,
                 database_folder=self.database_folder)

    def upload_tail(self, mtime):
        """
        Compresses the tail header and a subset of records using gzip and uploads the compressed data to S3.
        
        Parameters:
            mtime (int or float): The modification time to associate with the uploaded file.
        
        The method creates an in-memory gzip archive containing the tail header and records from the current object's data,
        then uploads this archive to an S3 bucket using the S3Upload function. The upload path is derived from the object's
        tailpath attribute with a '.gzip' extension, and the upload is stored within the specified database folder.
        """
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            gz.write(self.tailhdr.tobytes())
            gz.write(self.records[self.hdr['headsize']
                     :self.hdr['count']].tobytes())
        S3Upload(gzip_io, str(self.tailpath)+'.gzip', mtime,
                 database_folder=self.database_folder)
    
    def delete_tail(self):
        """
        Compresses the tail header and a subset of records using gzip and uploads the compressed data to S3.
        
        Parameters:
            mtime (int or float): The modification time to associate with the uploaded file.
        
        The method creates an in-memory gzip archive containing the tail header and records from the current object's data,
        then uploads this archive to an S3 bucket using the S3Upload function. The upload path is derived from the object's
        tailpath attribute with a '.gzip' extension, and the upload is stored within the specified database folder.
        """        
        # delete tail if it exists
        path = str(self.tailpath)+'.gzip'
        if self.database_folder:
            remotefilepath = str(path).replace(
                self.database_folder.rstrip('/'), '')
        else:
            remotefilepath = str(path).replace(
                os.environ['DATABASE_FOLDER'], '')
        remotefilepath = remotefilepath.replace('\\', '/')        
        S3DeleteFile(remotefilepath)        

    ############### CONVERT ###############
    def records2df(self, records):
        """
        Convert a list of records into a pandas DataFrame, decode byte-string columns to UTF-8 strings, and set the DataFrame index.
        
        Parameters:
            records (list or iterable): A collection of records (e.g., list of dictionaries) to be converted into a DataFrame.
        
        Returns:
            pandas.DataFrame: DataFrame constructed from the input records with byte-string columns decoded to UTF-8 strings and indexed by the primary key columns specified in self.index.pkeycolumns.
        """
        df = pd.DataFrame(records, copy=False)
        dtypes = df.dtypes.reset_index()
        dtypes.columns = ['tag', 'dtype']
        # convert object to string
        string_idx = pd.Index(['|S' in str(dt) for dt in dtypes['dtype']])
        string_idx = (string_idx) | pd.Index(dtypes['dtype'] == 'object')
        tags_obj = dtypes['tag'][string_idx].values
        for tag in tags_obj:
            try:
                df[tag] = df[tag].str.decode(encoding='utf-8', errors='ignore')
            except:
                pass
        df = df.set_index(self.index.pkeycolumns)
        return df

    def df2records(self, df):
        """
        Convert a pandas DataFrame into a NumPy structured array (records) with validation and type handling.
        
        This method checks if the DataFrame's index matches the expected primary key columns. If not, it raises an exception.
        It then converts the DataFrame into a NumPy structured array, handling datetime columns with timezones by converting them to UTC naive datetimes.
        If `self.recdtype` is None, it attempts to convert object columns to UTF-8 encoded byte strings and ensures no object dtype remains in the resulting array.
        If `self.recdtype` is provided, it uses this dtype to create the structured array, filling missing integer values with zero and converting columns accordingly.
        Logs errors encountered during type conversions but continues processing other columns.
        
        Parameters:
            df (pandas.DataFrame): The DataFrame to convert. Must have an index matching `self.index.pkeycolumns`.
        
        Returns:
            numpy.ndarray: A structured array representing the DataFrame records, suitable for binary operations or storage.
        
        Raises:
            Exception: If the DataFrame index does not match the expected primary key columns or if conversion to binary fails.
        """
        check_pkey = True
        if len(self.index.pkeycolumns) == len(df.index.names):
            for k in range(len(self.index.pkeycolumns)):
                check_pkey = (check_pkey) & (
                    df.index.names[k] == self.index.pkeycolumns[k])
        else:
            check_pkey = False
        if not check_pkey:
            raise Exception('First columns must be %s!' %
                            (self.index.pkeycolumns))
        else:
            if self.recdtype is None:
                df = df.reset_index()
                dtypes = df.dtypes.reset_index()
                dtypes.columns = ['tag', 'dtype']
            
                # Convert datetime columns with timezone to UTC naive datetime
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        if df[col].dt.tz is not None:
                            df[col] = df[col].dt.tz_convert('UTC').dt.tz_localize(None)
                
                # convert object to string
                tags_obj = dtypes['tag'][dtypes['dtype'] == 'object'].values
                for tag in tags_obj:
                    try:
                        df[tag] = df[tag].astype(str)
                        df[tag] = df[tag].str.encode(encoding='utf-8', errors='ignore')
                    except Exception as e:
                        Logger.log.error(f'Table.df2records(): Could not convert {self.relpath} {tag} : {str(e)}!')
                    df[tag] = df[tag].astype('|S')
                    
                rec = np.ascontiguousarray(df.to_records(index=False))
                type_descriptors = [field[1] for field in rec]
                if '|O' in type_descriptors:
                    errmsg = f'Table.df2records(): Could not convert {self.relpath} |0 type to binary'
                    Logger.log.error(errmsg)
                    raise Exception(errmsg)
                        
                return rec
            else:
                df = df.reset_index()
                # Convert datetime columns with timezone to UTC naive datetime
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        if df[col].dt.tz is not None:
                            df[col] = df[col].dt.tz_convert('UTC').dt.tz_localize(None)
                
                dtypes = self.recdtype
                
                rec = np.full((df.shape[0],), fill_value=np.nan, dtype=dtypes)
                for col in dtypes.names:
                    try:
                        if col in df.columns:
                            if pd.api.types.is_integer_dtype(dtypes[col])\
                                or pd.api.types.is_unsigned_integer_dtype(dtypes[col]):
                                df[col] = df[col].fillna(0)
                                
                            rec[col] = df[col].astype(dtypes[col])
                            
                    except Exception as e:
                        Logger.log.error(f'Table.df2records(): Could not convert {self.relpath} {col} : {str(e)}!')

                return rec

    ############### LOCK ###############
    def acquire(self):
        """
        Acquire a lock on the shared data resource using the specified mutex, process ID, and relative path.
        
        This method delegates the locking mechanism to the `acquire` method of the `shareddata` object,
        passing along the mutex, process identifier, and relative path to ensure synchronized access.
        """
        self.shareddata.acquire(self.mutex, self.pid, self.relpath)

    def release(self):
        """
        Releases the lock or resource associated with the current process and path.
        
        This method calls the `release` function of the `shareddata` object, passing
        the current mutex, process ID (`pid`), and relative path (`relpath`) to
        properly release the held resource.
        
        No return value.
        """
        self.shareddata.release(self.mutex, self.pid, self.relpath)

    ############### SUBSCRIBE ###############

    def subscribe(self, host, port, lookbacklines=1000, 
                  lookbackdate=None, method='websocket', snapshot=False, bandwidth=1e6, protocol='http'):
        """
        Starts a subscription thread to receive data from a specified host and port using the given method.
        
        Parameters:
            host (str): The hostname or IP address to connect to.
            port (int): The port number to connect to.
            lookbacklines (int, optional): Number of lines to look back on subscription start. Default is 1000.
            lookbackdate (datetime or None, optional): Specific date to look back to on subscription start. Default is None.
            method (str, optional): Connection method to use; one of 'socket', 'websocket', or 'api'. Default is 'websocket'.
            snapshot (bool, optional): Whether to take a snapshot of the data on subscription start. Default is False.
            bandwidth (float, optional): Bandwidth limit for the subscription in bytes per second. Default is 1e6.
            protocol (str, optional): Protocol to use when method is 'api'. Default is 'http'.
        
        Behavior:
            - If no subscription thread is currently running, starts a new thread based on the specified method.
            - Logs the start of the subscription or any errors encountered.
            - If a subscription is already running, logs an error and does not start a new one.
        """
        if self.subscription_thread is None:
            if method == 'socket':
                self.subscription_thread = threading.Thread(
                    target=ClientSocket.subscribe_table_thread,
                    args=(self, host, port, lookbacklines, lookbackdate, snapshot, bandwidth),
                )
                self.subscription_thread.start()
                Logger.log.info('Socket to %s:%s -> %s started...' % (host,str(port),self.relpath))
            elif method == 'websocket':
                def websocket_thread():
                    asyncio.run(ClientWebSocket.subscribe_table_thread(
                        self, host, port, lookbacklines, lookbackdate, snapshot, bandwidth,  protocol))
                
                self.subscription_thread = threading.Thread(
                    target=websocket_thread,                    
                )
                self.subscription_thread.start()                    
                Logger.log.info('Websocket to %s:%s -> %s started...' % (host,str(port),self.relpath))
            elif method == 'api':
                self.subscription_thread = threading.Thread(
                    target=ClientAPI.subscribe_table_thread,
                    args=(self, host, port, lookbacklines, lookbackdate, snapshot, bandwidth, protocol),
                )
                self.subscription_thread.start()
                Logger.log.info('API to %s:%s -> %s started...' % (host,str(port),self.relpath))
            else:
                Logger.log.error('Invalid method %s to %s:%s -> %s !!!' % (method,host,str(port),self.relpath))
        else:
            Logger.log.error('Subscription to %s:%s -> %s already running!' % (host,str(port),self.relpath))

    def publish(self, host, port=None, lookbacklines=1000, 
                  lookbackdate=None, method='websocket', snapshot=False, 
                  bandwidth=1e6, protocol='http',max_requests_per_minute=100):
        """
        '''
        Starts a publishing thread to send data to a specified host and port using the chosen method.
        
        Parameters:
            host (str): The target host address to publish data to.
            port (int, optional): The target port number. Defaults to None.
            lookbacklines (int, optional): Number of lines to look back and publish initially. Defaults to 1000.
            lookbackdate (datetime or None, optional): Specific date/time to look back from. Defaults to None.
            method (str, optional): The publishing method to use. One of 'socket', 'websocket', or 'api'. Defaults to 'websocket'.
            snapshot (bool, optional): Whether to send a snapshot of the data initially. Defaults to False.
            bandwidth (float, optional): Bandwidth limit in bits per second. Defaults to 1e6.
            protocol (str, optional): Protocol to use when method is 'api'. Defaults to 'http'.
            max_requests_per_minute (int, optional): Maximum API requests allowed per minute when method is 'api'. Defaults to 100.
        
        Behavior:
            - If no publishing thread is currently running, starts a new thread based on the specified method.
            - Logs the start of the publishing thread or errors
        """
        if self.publish_thread is None:
            if method == 'socket':
                self.publish_thread = threading.Thread(
                    target=ClientSocket.publish_table_thread,
                    args=(self, host, port, lookbacklines, lookbackdate, snapshot,bandwidth),
                )
                self.publish_thread.start()
                Logger.log.info('Socket to %s:%s -> %s started...' % (host,str(port),self.relpath))

            elif method == 'websocket':
                def websocket_thread():
                    asyncio.run(ClientWebSocket.publish_table_thread(
                        self, host, port, lookbacklines, lookbackdate, snapshot, bandwidth, protocol))
                self.publish_thread = threading.Thread(
                    target=websocket_thread,                    
                )
                self.publish_thread.start()                    
                Logger.log.info('Websocket to %s:%s -> %s started...' % (host,str(port),self.relpath))

            elif method == 'api':
                self.publish_thread = threading.Thread(
                    target=ClientAPI.publish_table_thread,
                    args=(self, host, port, lookbacklines, lookbackdate, snapshot,bandwidth, protocol, max_requests_per_minute),
                )
                self.publish_thread.start()
                Logger.log.info('API to %s:%s -> %s started...' % (host,str(port),self.relpath))
                
            else:
                Logger.log.error('Invalid method %s to %s:%s -> %s !!!' % (method,host,str(port),self.relpath))
        else:
            Logger.log.error('Subscription to %s:%s -> %s already running!' % (host,str(port),self.relpath))
