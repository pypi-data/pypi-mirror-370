import os
import io
import hashlib
import gzip
import shutil
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from pandas.tseries.offsets import BDay
from threading import Thread
from tqdm import tqdm

from SharedData.Logger import Logger
from SharedData.TimeSeriesDisk import TimeSeriesDisk
from SharedData.TimeSeriesMemory import TimeSeriesMemory
from SharedData.IO.AWSS3 import S3Upload, S3Download, UpdateModTime


class TimeseriesContainer:

    """
    '''
    Container class for managing time series data from various sources and periods, supporting both disk and shared memory storage types.
    
    Attributes:
        shareddata: Shared data manager instance.
        user (str): Username or namespace, default is 'master'.
        database (str): Database name.
        period (str): Time period granularity ('W1', 'D1', 'M15', 'M1').
        source (str): Data source identifier.
        type (str): Storage type, either 'DISK' or 'MEMORY'.
        startDate (pd.Timestamp): Start date for the time index.
        tags (dict): Dictionary mapping tag names to their time series data handlers.
        timeidx (dict): Dictionary of time indices keyed by startDate.
        ctimeidx (dict): Dictionary of continuous time indices keyed by startDate.
        periodseconds (int): Number of seconds in the specified period.
        default_startDate (pd.Timestamp): Default start date based on period.
        loaded (bool): Flag indicating if data has been loaded.
    
    Methods:
        getTimeIndex(startDate): Returns a pandas Index of business time points starting from startDate for the specified period.
        getContinousTimeIndex(startDate): Returns a continuous numeric index aligned with the time
    """
    def __init__(self, shareddata, database, period, source,
                 user='master',type='DISK', startDate=None):

        """
        '''
        Initialize the data handler with specified parameters and set up time indexing.
        
        Parameters:
            shareddata: Shared data resource or object used across instances.
            database (str): Name or identifier of the database to connect to.
            period (str): Time period for data aggregation ('W1', 'D1', 'M15', 'M1').
            source (str): Data source identifier.
            user (str, optional): Username for database access. Defaults to 'master'.
            type (str, optional): Type of data storage or retrieval method. Defaults to 'DISK'.
            startDate (str or pd.Timestamp, optional): Starting date for data indexing. Defaults to None.
        
        Attributes set:
            tags (dict): Dictionary to store data tags.
            timeidx (dict): Dictionary for time indexing.
            ctimeidx (dict): Dictionary for continuous time indexing.
            periodseconds (int): Number of seconds in the specified period.
            default_startDate (pd.Timestamp): Default start date based on period.
            startDate (pd.Timestamp): Actual start date used for indexing.
            loaded (bool): Flag indicating if data has been loaded.
        
        Calls:
            getTimeIndex(startDate): Initializes the time index starting from startDate.
            getContinousTimeIndex
        """
        self.shareddata = shareddata
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.type = type

        # DATA DICTIONARY
        # tags[tag]
        self.tags = {}

        # TIME INDEX
        self.timeidx = {}
        self.ctimeidx = {}
        if self.period == 'W1':
            self.periodseconds = 7*60*60*24
            self.default_startDate = pd.Timestamp('1995-01-01')
        elif self.period == 'D1':
            self.periodseconds = 60*60*24
            self.default_startDate = pd.Timestamp('1995-01-01')
        elif self.period == 'M15':
            self.periodseconds = 60*15
            self.default_startDate = pd.Timestamp('2010-01-01')
        elif self.period == 'M1':
            self.periodseconds = 60
            self.default_startDate = pd.Timestamp('2010-01-01')

        if startDate is None:
            self.startDate = self.default_startDate
        else:
            self.startDate = pd.Timestamp(startDate)            
        self.getTimeIndex(self.startDate)
        self.getContinousTimeIndex(self.startDate)
        self.loaded = False        

    def getTimeIndex(self, startDate):
        """
        Generate and cache a pandas Index of business time periods starting from a given date.
        
        If the time index for the specified startDate does not exist in the cache (self.timeidx),
        this method creates it based on the object's period attribute, which can be 'D1' (daily),
        'M15' (15-minute intervals), or 'M1' (1-minute intervals). The index covers business days
        from startDate up to January 1st of the next year.
        
        For 'M15' and 'M1' periods, the index is filtered to include only times between 7 AM and 10 PM
        on weekdays (Monday to Friday). The method also sets self.periodseconds to the number of seconds
        in each period (86400 for daily, 900 for 15 minutes, and 60 for 1 minute).
        
        Parameters:
            startDate (str or datetime-like): The start date from which to generate the time index.
        
        Returns:
            pd.Index: A pandas Index object containing the time periods starting from startDate.
        """
        if not startDate in self.timeidx.keys():
            lastdate = pd.Timestamp(datetime.now().year+1, 1, 1)

            if self.period == 'D1':
                self.timeidx[startDate] = pd.Index(
                    pd.bdate_range(start=startDate,
                                   end=np.datetime64(lastdate)))
                self.periodseconds = 60*60*24

            elif self.period == 'M15':
                self.timeidx[startDate] = pd.Index(
                    pd.bdate_range(start=startDate,
                                   end=np.datetime64(lastdate), freq='15min'))
                idx = (self.timeidx[startDate].hour > 6)
                idx = (idx) & (self.timeidx[startDate].hour < 22)
                idx = (idx) & (self.timeidx[startDate].day_of_week < 5)
                self.timeidx[startDate] = self.timeidx[startDate][idx]
                self.periodseconds = 60*15

            elif self.period == 'M1':
                self.timeidx[startDate] = pd.Index(
                    pd.bdate_range(start=startDate,
                                   end=np.datetime64(lastdate), freq='1min'))
                idx = (self.timeidx[startDate].hour > 6)
                idx = (idx) & (self.timeidx[startDate].hour < 22)
                idx = (idx) & (self.timeidx[startDate].day_of_week < 5)
                self.timeidx[startDate] = self.timeidx[startDate][idx]
                self.periodseconds = 60

        return self.timeidx[startDate]

    def getContinousTimeIndex(self, startDate):
        """
        Generate and cache a continuous time index array starting from the given startDate.
        
        If the continuous time index for the specified startDate does not exist in the cache (self.ctimeidx),
        this method computes it by:
        - Obtaining the original time index corresponding to startDate.
        - Calculating the number of periods elapsed since startDate based on the time difference and the defined period length (self.periodseconds).
        - Creating a NumPy array initialized with NaNs, sized to cover all periods.
        - Filling the array at calculated period positions with sequential indices.
        
        Parameters:
            startDate (Timestamp or compatible datetime-like): The starting date/time from which to generate the continuous time index.
        
        Returns:
            numpy.ndarray: An array representing the continuous time index for the given startDate, with NaNs for missing periods.
        """
        if not startDate in self.ctimeidx.keys():
            _timeidx = self.getTimeIndex(startDate)
            nsec = (_timeidx - startDate).astype(np.int64)
            periods = (nsec/(10**9)/self.periodseconds).astype(np.int64)
            self.ctimeidx[startDate] = np.empty(max(periods)+1)
            self.ctimeidx[startDate][:] = np.nan
            self.ctimeidx[startDate][periods.values] = np.arange(len(periods))
        return self.ctimeidx[startDate]

    def get_path(self):
        """
        Constructs and returns the filesystem path and shared memory name for the timeseries data based on the object's attributes.
        
        The method builds a path using the environment variable 'DATABASE_FOLDER' combined with the user, database, period, source, and 'timeseries' subdirectories. It also creates a shared memory name string by joining these attributes with slashes. On POSIX systems, the shared memory name's slashes are replaced with backslashes.
        
        If the object's type attribute is 'DISK', it ensures that the parent directory of the constructed path exists by creating it if necessary.
        
        Returns:
            tuple: A tuple containing:
                - path (Path): The constructed Path object pointing to the timeseries directory.
                - shm_name (str): The shared memory name string with platform-specific separators.
        """
        shm_name = self.user + '/' + self.database + '/' \
            + self.period + '/' + self.source + '/timeseries'
        if os.name == 'posix':
            shm_name = shm_name.replace('/', '\\')

        path = Path(os.environ['DATABASE_FOLDER'])
        path = path / self.user
        path = path / self.database
        path = path / self.period
        path = path / self.source
        path = path / 'timeseries'
        path = Path(str(path).replace('\\', '/'))
        if (self.type == 'DISK'):
            os.makedirs(path.parent, exist_ok=True)
            
        return path, shm_name

    # READ
    def load(self):
        # read if not loaded
        """
        Load data into the object. If the data source type is 'DISK', it reads the data from disk and initializes TimeSeriesDisk objects for each binary file found in the specified path, storing them in the tags dictionary. If the data source type is not 'DISK', it checks for shared memory data; if not present, it reads the data, otherwise it maps the shared memory data for use.
        """
        if self.type == 'DISK':
            self.read()
            
            path, shm_name = self.get_path()
            tagslist = path.rglob('*.bin')
            for tag in tagslist:
                if tag.is_file():
                    tagname = str(tag).replace(str(path),'').replace('.bin','').replace('\\','/')
                    if (tagname[0] == '/') | (tagname[0] == '\\'):
                        tagname = tagname[1:]
                    if not tagname in self.tags.keys():
                        self.tags[tagname] = TimeSeriesDisk(self.shareddata, self, self.database,
                                                    self.period, self.source, tag=tagname, user=self.user)
        else:
            shdatalist = self.shareddata.list_memory()
            path, shm_name = self.get_path()
            idx = [shm_name in str(s) for s in shdatalist.index]
            if not np.any(idx):
                self.read()
            else:
                # map
                self.map(shm_name, shdatalist.index[idx])

    def map(self, shm_name, shm_name_list):
        """
        Maps shared memory names to TimeSeriesMemory objects by extracting tags from each name in shm_name_list.
        
        Parameters:
            shm_name (str): The base shared memory name to be replaced.
            shm_name_list (list of str): A list of shared memory names to process.
        
        For each shared memory name in shm_name_list, the method removes the base shm_name,
        adjusts the resulting string by removing the first character and replacing backslashes with forward slashes,
        then creates a TimeSeriesMemory object with the derived tag and stores it in the self.tags dictionary.
        """
        for shm in shm_name_list:
            tag = shm.replace(shm_name, '')[1:].replace('\\', '/')
            self.tags[tag] = TimeSeriesMemory(self.shareddata, self, self.database,
                                        self.period, self.source, tag=tag)

    def read(self):
        """
        Reads and processes time series data from S3 or local storage, handling both 'head' and 'tail' data segments.
        
        The method attempts to download gzipped 'head' and 'tail' binary files from S3, decompresses them with progress feedback,
        and writes them to either memory or disk based on the instance's type attribute. If downloading is not required or fails,
        it falls back to reading the files locally. After reading, it processes the data via the `read_io` method and cleans up
        files if necessary. The method logs the total data read and the throughput.
        
        Behavior varies depending on whether the instance type is 'MEMORY' or 'DISK':
        - For 'MEMORY', data is written to shared memory containers.
        - For 'DISK', placeholder files are created and managed.
        
        Returns:
            None
        """
        tini = time.time()
        datasize = 1
        path, shm_name = self.get_path()
        headpath = Path(str(path)+'_head.bin')
        tailpath = Path(str(path)+'_tail.bin')
        head_io = None
        tail_io = None
    
        force_download = (self.type == 'MEMORY')

        [head_io_gzip, head_local_mtime, head_remote_mtime] = \
            S3Download(str(headpath)+'.gzip', str(headpath), force_download)
        if not head_io_gzip is None:
            head_io = io.BytesIO()

            total_size = head_io_gzip.seek(0, 2)
            head_io_gzip.seek(0)
            with gzip.GzipFile(fileobj=head_io_gzip, mode='rb') as gz:
                with tqdm(total=total_size, unit='B', unit_scale=True,
                            desc='Unzipping %s' % (shm_name), dynamic_ncols=True) as pbar:
                    chunk_size = int(1024*1024)
                    while True:
                        chunk = gz.read(chunk_size)
                        if not chunk:
                            break
                        head_io.write(chunk)
                        pbar.update(len(chunk))
            
            if self.type == 'MEMORY':
                TimeseriesContainer.write_file(
                    head_io, headpath, mtime=head_remote_mtime, shm_name=shm_name)
            elif self.type == 'DISK':
                with open(headpath, 'wb') as f:
                    f.write(b'\x00')
            UpdateModTime(headpath, head_remote_mtime)

        [tail_io_gzip, tail_local_mtime, tail_remote_mtime] = \
            S3Download(str(tailpath)+'.gzip', str(tailpath), force_download)
        if not tail_io_gzip is None:
            tail_io = io.BytesIO()
            tail_io_gzip.seek(0)
            with gzip.GzipFile(fileobj=tail_io_gzip, mode='rb') as gz:
                shutil.copyfileobj(gz, tail_io)
            
            if self.type == 'MEMORY':                        
                TimeseriesContainer.write_file(
                    tail_io, tailpath, mtime=tail_remote_mtime, shm_name=shm_name)
            elif self.type == 'DISK':
                with open(tailpath, 'wb') as f:                            
                    f.write(b'\x00')
            UpdateModTime(tailpath, tail_remote_mtime)

        
        if (head_io is None):
            # read local
            if os.path.isfile(str(headpath)):
                if (headpath.stat().st_size > 1) & (self.type == 'DISK'):
                    head_io = open(str(headpath), 'rb')
                elif self.type == 'MEMORY':
                    head_io = open(str(headpath), 'rb')

        if (tail_io is None):
            if os.path.isfile(str(tailpath)):
                if (tailpath.stat().st_size > 1) & (self.type == 'DISK'):
                    tail_io = open(str(tailpath), 'rb')
                elif self.type == 'MEMORY':
                    tail_io = open(str(tailpath), 'rb')

        if not head_io is None:
            datasize += self.read_io(head_io, headpath, shm_name, ishead=True)
            # delete head file if type was memory 
            if (headpath.stat().st_size > 1) & (self.type == 'DISK'):
                head_io.close()
                mtime = headpath.stat().st_mtime
                with open(headpath, 'wb') as f:                            
                    f.write(b'\x00')
                os.utime(headpath, (mtime, mtime))


        if not tail_io is None:
            datasize += self.read_io(tail_io, tailpath, shm_name, ishead=False)
            # delete tail file if type was memory 
            if (tailpath.stat().st_size > 1) & (self.type == 'DISK'):
                tail_io.close()
                mtime = tailpath.stat().st_mtime
                with open(tailpath, 'wb') as f:                            
                    f.write(b'\x00')
                os.utime(tailpath, (mtime, mtime))

        te = time.time()-tini+0.000001
        datasize = datasize/(1024*1024)
        Logger.log.debug('read %s/%s %.2fMB in %.2fs %.2fMBps ' %
                         (self.source, self.period, datasize, te, datasize/te))

    def read_io(self, io_obj, path, shm_name, ishead=True):
        """
        '''
        Reads and verifies timeseries data from a binary I/O object, validates its integrity using an MD5 hash, and loads the data into the object's tags as either disk-backed or in-memory timeseries.
        
        Parameters:
            io_obj (io.BufferedIOBase): A binary I/O object containing the serialized timeseries data.
            path (str): The file path or identifier associated with the data (not used directly in this method).
            shm_name (str): Name of the shared memory segment used for logging and verification messages.
            ishead (bool, optional): Indicates if the data being read is the initial header load. Defaults to True.
        
        Returns:
            int: The size in bytes of the timeseries data read (excluding the trailing 24 bytes used for hash and metadata).
        
        Raises:
            Exception: If the MD5 hash verification fails, indicating data corruption.
        
        Behavior:
        - Reads the entire content of io_obj, excluding the last 24 bytes which contain metadata and an MD5 hash.
        - Computes the MD5 hash of the data, using a progress bar if the data size exceeds 100 MB.
        - Compares the computed hash with the stored hash to verify data integrity.
        - Parses the data in chunks, each preceded by a separator and header describing the tag,
        """
        datasize = 0
        # read
        io_obj.seek(0)
        io_data = io_obj.read()
        _io_data = io_data[:-24]
        datasize = len(_io_data)
        datasizemb = datasize/(1024*1024)
        if datasizemb > 100:
            message = 'Verifying:%iMB %s' % (datasizemb, shm_name)
            block_size = 100 * 1024 * 1024  # or any other block size that you prefer
            nb_total = datasize
            read_bytes = 0
            _m = hashlib.md5()
            # Use a with block to manage the progress bar
            with tqdm(total=nb_total, unit='B', unit_scale=True, desc=message) as pbar:
                # Loop until we have read all the data
                while read_bytes < nb_total:
                    # Read a block of data
                    chunk_size = min(block_size, nb_total-read_bytes)
                    # Update the shared memory buffer with the newly read data
                    _m.update(_io_data[read_bytes:read_bytes+chunk_size])
                    read_bytes += chunk_size  # update the total number of bytes read so far
                    # Update the progress bar
                    pbar.update(chunk_size)
            _m = _m.digest()
        else:
            _m = hashlib.md5(io_data[:-24]).digest()
        # _m = hashlib.md5(io_data[:-24]).digest()
        m = io_data[-16:]
        if not self.compare_hash(m,_m):
            Logger.log.error('Timeseries file %s corrupted!' % (shm_name))
            raise Exception('Timeseries file %s corrupted!' % (shm_name))
        io_obj.seek(0)
        separator = np.frombuffer(io_obj.read(8), dtype=np.int64)[0]
        while (separator == 1):
            _header = np.frombuffer(io_obj.read(40), dtype=np.int64)
            _tag_b = io_obj.read(int(_header[0]))
            _tag = _tag_b.decode(encoding='UTF-8', errors='ignore')
            _idx_b = io_obj.read(int(_header[1]))
            _idx = pd.to_datetime(np.frombuffer(_idx_b, dtype=np.int64))
            _colscsv_b = io_obj.read(int(_header[2]))
            _colscsv = _colscsv_b.decode(encoding='UTF-8', errors='ignore')
            _cols = _colscsv.split(',')
            r = _header[3]
            c = _header[4]
            total_bytes = int(r*c*8)
            _data = np.frombuffer(io_obj.read(total_bytes),
                                  dtype=np.float64).reshape((r, c))
            df = pd.DataFrame(_data, index=_idx, columns=_cols)
            if self.type == 'DISK':
                if ishead:
                    self.tags[_tag] = TimeSeriesDisk(self.shareddata, self, self.database,
                                                    self.period, self.source, tag=_tag, value=df, user=self.user, overwrite=True)
                else:
                    if not _tag in self.tags.keys():
                        self.tags[_tag] = TimeSeriesDisk(self.shareddata, self, self.database,
                                                    self.period, self.source, tag=_tag, value=df, user=self.user, overwrite=True)
                    else:
                        data = self.tags[_tag].data
                        iidx = df.index.intersection(data.index)
                        icol = df.columns.intersection(data.columns)
                        data.loc[iidx, icol] = df.loc[iidx, icol].copy()
                        
            elif self.type == 'MEMORY':
                if not _tag in self.tags.keys():
                    self.tags[_tag] = TimeSeriesMemory(self.shareddata, self, self.database,
                                                self.period, self.source, tag=_tag, value=df, user=self.user, overwrite=True)
                else:
                    data = self.tags[_tag].data
                    iidx = df.index.intersection(data.index)
                    icol = df.columns.intersection(data.columns)
                    data.loc[iidx, icol] = df.loc[iidx, icol].copy()
            separator = np.frombuffer(io_obj.read(8), dtype=np.int64)[0]
        io_obj.close()

        return datasize

    def compare_hash(self,h1,h2):
        """
        Compares two hash strings up to the length of the shorter one.
        
        Parameters:
            h1 (str): The first hash string.
            h2 (str): The second hash string.
        
        Returns:
            bool: True if the prefixes of both hashes up to the length of the shorter hash are equal, False otherwise.
        """
        l1 = len(h1)
        l2 = len(h2)
        l = min(l1,l2)
        return h1[:l]==h2[:l]

    # WRITE
    def flush(self):
        """
        Flushes the buffered data for all tags if the object's type is 'DISK'.
        
        Iterates over each tag in the `tags` dictionary and calls the `flush` method
        on the `shf` attribute of each tag to ensure all data is written out.
        """
        if self.type == 'DISK':
            for tag in self.tags:
                self.tags[tag].shf.flush()

    def write(self, startDate=None):
        """
        Writes data to a file or shared memory segment, optionally starting from a specified date.
        
        Parameters:
            startDate (pd.Timestamp or None): Optional start date to determine the writing range.
                If provided and earlier than the start of the current year, the header is written
                starting from this date; otherwise, writing begins from the start of the current year.
        
        Behavior:
            - Retrieves the file path and shared memory name.
            - Sets the modification time to the current timestamp.
            - Defines the partition date as January 1st of the current year.
            - Determines the first date to write from, defaulting to '1970-01-01' if no startDate is given.
            - Writes the header if the first date is before the partition date.
            - Writes the tail data.
            - Flushes the output to ensure all data is written.
        """
        path, shm_name = self.get_path()
        mtime = datetime.now().timestamp()
        partdate = pd.Timestamp(datetime(datetime.now().year, 1, 1))
        firstdate = pd.Timestamp('1970-01-01')
        if not startDate is None:
            firstdate = startDate
        if firstdate < partdate:
            self.write_head(path, partdate, mtime, shm_name)
        self.write_tail(path, partdate, mtime, shm_name)
        self.flush()

    def write_head(self, path, partdate, mtime, shm_name):
        """
        Compresses and uploads a header file related to the given path and partition date.
        
        Creates a header IO object for the specified partition date, compresses it using gzip,
        and uploads the compressed data to S3 asynchronously using a separate thread.
        If the instance type is 'DISK', it also creates a placeholder header file on disk
        and sets its modification time.
        
        Args:
            path (str or Path): The base path for the header file.
            partdate (Any): The partition date used to create the header IO object.
            mtime (float): The modification time to set on the local header file if type is 'DISK'.
            shm_name (str): Shared memory name (not used directly in this method).
        """
        io_obj = self.create_head_io(partdate)

        threads = []    
        io_obj.seek(0)
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            shutil.copyfileobj(io_obj, gz)
        threads = [*threads, Thread(target=S3Upload,
                                    args=(gzip_io, str(path)+'_head.bin.gzip', mtime))]

        if self.type == 'DISK':
            with open(str(path)+'_head.bin', 'wb') as f:
                f.write(b'\x00')
            os.utime(str(path)+'_head.bin', (mtime, mtime))

        for i in range(len(threads)):
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

    def create_head_io(self, partdate):
        """
        Create a binary I/O stream containing serialized data frames for each tag up to a specified date.
        
        Parameters:
            partdate (Timestamp): The cutoff date (exclusive) for selecting data from each tag's DataFrame.
        
        Returns:
            io.BytesIO: A BytesIO object containing the binary representation of the data, including:
                - A header with metadata (version, lengths, and shape information)
                - Encoded tag name
                - Encoded index values as int64 timestamps
                - Encoded column names as CSV string
                - The DataFrame values as a contiguous array of float64
                - A terminating int64 zero followed by an MD5 hash of the preceding data for integrity verification.
        """
        io_obj = io.BytesIO()
        for tag in self.tags.keys():            
            dftag = self.tags[tag].data.loc[:partdate-BDay(1)]
            # create binary df
            df = dftag.dropna(how='all', axis=0).copy()
            r, c = df.shape
            tag_b = str.encode(tag, encoding='UTF-8', errors='ignore')
            idx = (df.index.astype(np.int64))
            idx_b = idx.values.tobytes()
            cols = df.columns.values
            colscsv = ','.join(cols)
            colscsv_b = str.encode(colscsv, encoding='UTF-8', errors='ignore')
            nbtag = len(tag_b)
            nbidx = len(idx_b)
            nbcols = len(colscsv_b)
            header = np.array([1, nbtag, nbidx, nbcols, r, c]).astype(np.int64)
            io_obj.write(header)
            io_obj.write(tag_b)
            io_obj.write(idx_b)
            io_obj.write(colscsv_b)
            io_obj.write(np.ascontiguousarray(df.values.astype(np.float64)))

        m = hashlib.md5(io_obj.getvalue()).digest()
        io_obj.write(np.array([0]).astype(np.int64))
        io_obj.write(m)
        return io_obj

    def write_tail(self, path, partdate, mtime, shm_name):
        """
        Compresses and uploads the tail data of a partition to S3, and optionally writes a placeholder tail file on disk.
        
        Parameters:
            path (str or Path): The base file path for the tail files.
            partdate (datetime or similar): The partition date used to create the tail IO object.
            mtime (float): The modification time to set on the local tail file if applicable.
            shm_name (str): Shared memory name (not used directly in this method).
        
        Behavior:
        - Creates a tail IO object for the given partition date.
        - Compresses the tail data using gzip with compression level 1.
        - Starts a thread to upload the compressed tail data to S3 with a filename suffix '_tail.bin.gzip'.
        - If the instance type is 'DISK', writes a single null byte to a local tail file and sets its modification time.
        - Waits for all upload threads to complete before returning.
        """
        io_obj = self.create_tail_io(partdate)

        threads = []        
        io_obj.seek(0)
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            shutil.copyfileobj(io_obj, gz)
        threads = [*threads, Thread(target=S3Upload,
                                    args=(gzip_io, str(path)+'_tail.bin.gzip', mtime))]
        
        if self.type == 'DISK':
            with open(str(path)+'_tail.bin', 'wb') as f:
                f.write(b'\x00')
            os.utime(str(path)+'_tail.bin', (mtime, mtime))

        for i in range(len(threads)):
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

    def create_tail_io(self, partdate):
        """
        Create a binary in-memory stream containing serialized data frames from the object's tags starting from a specified date.
        
        For each tag in `self.tags`, the method optionally flushes the associated file handle if the type is 'DISK', then extracts the data frame from `partdate` onwards, drops rows with all NaN values, and serializes the tag name, index, column names, and data values into a binary format written to a `BytesIO` object. After processing all tags, it appends a zero marker and an MD5 checksum of the written content for integrity verification.
        
        Parameters:
            partdate (Timestamp or compatible): The starting date from which to include data in the serialization.
        
        Returns:
            io.BytesIO: An in-memory binary stream containing the serialized data frames and checksum.
        """
        io_obj = io.BytesIO()
        for tag in self.tags.keys():
            if self.type == 'DISK':
                self.tags[tag].shf.flush()
            dftag = self.tags[tag].data.loc[partdate:]
            # create binary df
            df = dftag.dropna(how='all', axis=0)
            r, c = df.shape
            tag_b = str.encode(tag, encoding='UTF-8', errors='ignore')
            idx = (df.index.astype(np.int64))
            idx_b = idx.values.tobytes()
            cols = df.columns.values
            colscsv = ','.join(cols)
            colscsv_b = str.encode(colscsv, encoding='UTF-8', errors='ignore')
            nbtag = len(tag_b)
            nbidx = len(idx_b)
            nbcols = len(colscsv_b)
            header = np.array([1, nbtag, nbidx, nbcols, r, c]).astype(np.int64)
            io_obj.write(header)
            io_obj.write(tag_b)
            io_obj.write(idx_b)
            io_obj.write(colscsv_b)
            io_obj.write(np.ascontiguousarray(df.values.astype(np.float64)))

        m = hashlib.md5(io_obj.getvalue()).digest()
        io_obj.write(np.array([0]).astype(np.int64))
        io_obj.write(m)
        return io_obj

    @staticmethod
    def write_file(io_obj, path, mtime, shm_name):
        """
        Writes the contents of a BytesIO-like object to a file at the specified path, optionally displaying a progress bar for large files, and sets the file's modification time.
        
        Parameters:
            io_obj (io.BytesIO): An in-memory bytes buffer containing the data to write.
            path (str): The file system path where the data should be written.
            mtime (float): The modification time to set on the written file (as a Unix timestamp).
            shm_name (str): A name used in the progress bar description when writing large files.
        
        Behavior:
            - If the size of the data exceeds 100 MB, writes the file in 100 MB chunks while displaying a tqdm progress bar.
            - Otherwise, writes the entire buffer at once.
            - After writing, flushes the file and updates its modification time to `mtime`.
        """
        with open(path, 'wb') as f:
            nb = len(io_obj.getbuffer())
            size_mb = nb / (1024*1024)
            if size_mb > 100:
                blocksize = 1024*1024*100
                descr = 'Writing:%iMB %s' % (size_mb, shm_name)
                with tqdm(total=nb, unit='B', unit_scale=True, desc=descr) as pbar:
                    written = 0
                    while written < nb:
                        # write in chunks of max 100 MB size
                        chunk_size = min(blocksize, nb-written)
                        f.write(io_obj.getbuffer()[written:written+chunk_size])
                        written += chunk_size
                        pbar.update(chunk_size)
            else:
                f.write(io_obj.getbuffer())
            f.flush()
        os.utime(path, (mtime, mtime))

    def free(self):
        """
        Frees resources associated with the current object's tags and removes the corresponding timeseries data from shared storage.
        
        This method performs the following actions:
        1. Iterates over all tags in the object's `tags` dictionary and calls their `free()` method.
        2. Constructs a path string based on the object's `user`, `database`, `period`, and `source` attributes.
        3. Checks if this path exists as a key in the `shareddata.data` dictionary and deletes it if present.
        
        This helps in cleaning up memory and shared data related to the object's timeseries.
        """
        _tags = list(self.tags.keys())
        for tag in _tags:
            self.tags[tag].free()
        path = f'{self.user}/{self.database}/{self.period}/{self.source}/timeseries'
        if path in self.shareddata.data.keys():
            del self.shareddata.data[path]
        

    # GETTER AND SETTER
    def __getitem__(self, key):
        """
        Retrieve the data associated with the given tag key.
        
        Parameters:
            key (str): The tag key to look up.
        
        Returns:
            The data corresponding to the specified tag key.
        
        Raises:
            Exception: If the tag key is not found in the tags dictionary, with a message indicating the missing tag and its context (database, period, source).
        """
        if key in self.tags.keys():
            return self.tags[key].data
        else:
            raise Exception('Tag %s not found in %s/%s/%s' %
                    (key, self.database, self.period, self.source))
        
    def __setitem__(self, key, value):
        """
        Sets the value of an existing tag identified by `key`.
        
        If the `key` exists in the `tags` dictionary, its value is updated to `value`.
        If the `key` does not exist, raises an Exception indicating the tag was not found,
        including the database, period, and source context in the error message.
        
        Parameters:
            key: The tag key to be updated.
            value: The new value to assign to the tag.
        
        Raises:
            Exception: If the tag `key` is not found in the current tags.
        """
        if key in self.tags.keys():
            self.tags[key] = value
        else:
            raise Exception('Tag %s not found in %s/%s/%s' %
                    (key, self.database, self.period, self.source))