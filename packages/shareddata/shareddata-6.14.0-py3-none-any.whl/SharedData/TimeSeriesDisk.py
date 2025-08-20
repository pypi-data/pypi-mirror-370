# TimeSeriesDisk.py
# This file is part of the SharedData package.
# It manages time series data stored on disk using memory-mapped files for efficient access and modification

# THIRD PARTY LIBS
import os
import pandas as pd
import numpy as np
import time
from numba import jit
from pathlib import Path

from SharedData.Logger import Logger


class TimeSeriesDisk:

    """
    '''
    Manages time series data stored on disk using memory-mapped files for efficient access and modification.
    
    This class provides functionality to create, map, and manipulate large time series datasets stored as binary files on disk. It supports initializing from existing data, creating new datasets, and updating values with fast memory mapping techniques. The data is organized by user, database, period, source, and tag, and indexed by timestamps with associated columns representing different symbols or variables.
    
    Key features:
    - Initializes time series data from disk or creates new storage if not present or if overwrite is requested.
    - Uses numpy memmap for memory-efficient file access and pandas DataFrame for convenient data manipulation.
    - Supports fast lookup of symbol and timestamp indices with JIT-compiled helper functions.
    - Handles file path creation and directory management based on environment and input parameters.
    - Provides methods to allocate and map shared memory segments for inter-process data sharing.
    - Ensures data consistency by verifying columns and index alignment when loading existing data.
    - Includes error handling and logging for robust operation.
    
    Parameters:
    - shareddata: Shared memory manager object for allocating and managing shared memory segments.
    - container: Container object providing period duration, start date, and time indexing utilities.
    - database: String identifier for the database name.
    - period: String
    """
    def __init__(self, shareddata, container, database, period, source, tag,
             value=None, columns=None, user='master',overwrite=False):

        """
        '''
        Initialize an instance managing shared memory data storage and retrieval.
        
        Parameters:
            shareddata: Shared data object used for synchronization or shared state.
            container: Container object providing metadata such as periodseconds, startDate, and indexing methods.
            database: Identifier or connection for the database associated with the data.
            period: Time period for the data.
            source: Source identifier for the data.
            tag: String tag identifying the dataset; leading slashes are removed if present.
            value (optional): DataFrame containing initial data values to populate the shared memory.
            columns (optional): Columns to be used for the data; if None and value is provided, columns are inferred from value.
            user (optional): User identifier, default is 'master'.
            overwrite (optional): Boolean flag indicating whether to overwrite existing data; default is False.
        
        Behavior:
        - Sets up internal attributes including period, source, tag, and indexing based on the container.
        - Determines columns and symbol indices from provided columns or value.
        - Attempts to locate existing shared memory file; if found and not overwriting, maps it into memory.
        - Validates that existing data columns and index match expected columns and index; if not, copies and recreates shared memory.
        - If no existing data or overwrite
        """
        self.shareddata = shareddata
        self.container = container
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tag = tag[1:] if tag[0]=="\\" or tag[0]=="/" else tag
        
        self.periodseconds = container.periodseconds
        self.startDate = self.container.startDate
        self.index = self.container.getTimeIndex(self.startDate)
        self.ctimeidx = self.container.getContinousTimeIndex(self.startDate)
        
        self.columns = None
        if not columns is None:
            self.columns = columns
            self.symbolidx = {}
            for i in range(len(self.columns)):
                self.symbolidx[self.columns.values[i]] = i
        elif not value is None:
            self.columns = value.columns
            self.symbolidx = {}
            for i in range(len(self.columns)):
                self.symbolidx[self.columns.values[i]] = i

        self.path, self.shm_name = self.get_path()
        self.exists = os.path.isfile(self.path)                        
                    
        self.data = None        
                        
        self.init_time = time.time()
        try:            
            copy = False
            if (self.exists) & (not overwrite):
                _data = self.malloc_map()
                
                if not self.columns is None:
                    if not _data.columns.equals(self.columns):
                        copy = True

                if not self.index.equals(_data.index):
                    copy = True

                if not copy:
                    self.data = _data
                    if self.columns is None:
                        self.columns = self.data.columns
                        self.symbolidx = {}
                        for i in range(len(self.columns)):
                            self.symbolidx[self.columns.values[i]] = i
                else:
                    _data = _data.copy(deep=True)                    
                    del self.shf
                    self.columns = _data.columns
                    self.symbolidx = {}
                    for i in range(len(self.columns)):
                        self.symbolidx[self.columns.values[i]] = i
                    self.malloc_create()
                    sidx = np.array([self.get_loc_symbol(s)
                                for s in self.columns])
                    ts = _data.index.values.astype(np.int64)/10**9  # seconds
                    tidx = self.get_loc_timestamp(ts)
                    self.setValuesJit(self.data.values, tidx,
                                        sidx, _data.values)
                    del _data
                                
            elif (not self.exists) | (overwrite):
                # create new empty file
                self.malloc_create()

            if (not value is None):
                sidx = np.array([self.get_loc_symbol(s)
                                for s in self.columns])
                ts = value.index.values.astype(np.int64)/10**9  # seconds
                tidx = self.get_loc_timestamp(ts)
                self.setValuesJit(self.data.values, tidx,
                                    sidx, value.values)
                self.shf.flush()
                        
        except Exception as e:            
            errmsg = 'Error initalizing %s!\n%s' % (self.shm_name, str(e))
            Logger.log.error(errmsg)
            raise Exception(errmsg)

        self.init_time = time.time() - self.init_time

    def get_path(self):
        """
        Constructs and returns the file system path and shared memory name for a timeseries data file.
        
        The method builds a hierarchical path based on the instance attributes: user, database, period, source, and tag.
        It ensures the directory structure exists under the base directory specified by the 'DATABASE_FOLDER' environment variable.
        The returned path points to a binary file named after the tag with a '.bin' extension.
        The shared memory name is a string composed of the same attributes separated by slashes, with path separators adjusted for POSIX systems.
        
        Returns:
            tuple: A tuple containing:
                - path (Path): The full Path object to the binary timeseries file.
                - shm_name (str): The shared memory name string with appropriate path separators.
        """
        shm_name = self.user + '/' + self.database + '/' \
            + self.period + '/' + self.source + '/timeseries/' + self.tag
        if os.name == 'posix':
            shm_name = shm_name.replace('/', '\\')

        path = Path(os.environ['DATABASE_FOLDER'])
        path = path / self.user
        path = path / self.database
        path = path / self.period
        path = path / self.source
        path = path / 'timeseries'
        path = path / (self.tag+'.bin')
        path = Path(str(path).replace('\\', '/'))
        os.makedirs(path.parent, exist_ok=True)
        
        return path, shm_name

    def malloc_create(self):
        """
        Creates or expands a memory-mapped file to store a DataFrame's data with preallocated space.
        
        This method performs the following steps:
        - Calculates the required file size based on the DataFrame's index and columns.
        - Creates the file and necessary directories if they do not exist.
        - Preallocates disk space for the file to improve write performance (using posix_fallocate on POSIX systems).
        - Writes a custom header containing metadata (number of rows, columns, and byte sizes).
        - Writes the column names and index values as bytes.
        - Initializes a numpy memmap with the specified shape and data type (float64), filled with NaNs.
        - Creates a pandas DataFrame backed by the memmap for efficient data access and modification.
        
        Returns:
            bool: True if the file was successfully created or expanded and initialized.
        
        Raises:
            Exception: If any error occurs during file creation, preallocation, or writing, the exception is logged and re-raised.
        """
        filepath = self.path
                            
        try:  # try create file
                                    
            idx_b = self.index.astype(np.int64).values.tobytes()
            nb_idx = len(idx_b)
            r = len(self.index)

            colscsv_b = str.encode(','.join(self.columns),
                                   encoding='UTF-8', errors='ignore')            
            nb_cols = len(colscsv_b)
            c = len(self.columns)
            
            nb_data = int(r*c*8)
            
            header_b = np.array([r, c, nb_cols, nb_idx, nb_data]).astype(
                np.int64).tobytes()
            nb_header = len(header_b)

            nb_total = nb_header+nb_cols+nb_idx+nb_data
            nb_offset = nb_header+nb_cols+nb_idx

            totalbytes = int(nb_total)
            if not Path(filepath).is_file():
                # create folders
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    # Seek to the end of the file
                    f.seek(totalbytes-1)
                    # Write a single null byte to the end of the file
                    f.write(b'\x00')
                    if os.name == 'posix':
                        os.posix_fallocate(f.fileno(), 0, totalbytes)
                    elif os.name == 'nt':
                        pass  # TODO: implement preallocation for windows in pyd
            elif (Path(filepath).stat().st_size < totalbytes):
                with open(filepath, 'ab') as f:
                    # Seek to the end of the file
                    f.seek(totalbytes-1)
                    # Write a single null byte to the end of the file
                    f.write(b'\x00')
                    if os.name == 'posix':
                        os.posix_fallocate(f.fileno(), 0, totalbytes)
                    elif os.name == 'nt':
                        pass  # TODO: implement preallocation for windows in pyd

            # write data
            with open(filepath, 'rb+') as f:
                f.seek(0)
                f.write(header_b)
                f.write(colscsv_b)
                f.write(idx_b)                

            
            self.shf = np.memmap(filepath,'<f8','r+',nb_offset,(r,c))
            self.shf[:] = np.nan
            self.shf.flush()
            self.data = pd.DataFrame(self.shf,                                     
                                     index=self.index,
                                     columns=self.columns,
                                     copy=False)
            self.data.index.name = 'date'            
            

            return True
        except Exception as e:
            Logger.log.error('Failed to malloc_create\n%s' % str(e))
            raise Exception('Failed to malloc_create\n%s' % str(e))            

    def malloc_map(self):        
        """
        Memory-maps a binary file containing a structured dataset and returns it as a pandas DataFrame.
        
        The binary file is expected to have a specific format:
        - The first 40 bytes contain a header with five int64 values representing:
          number of rows (r), number of columns (c), number of bytes for column names (nb_cols),
          number of bytes for index data (nb_idx), and number of bytes for data (nb_data).
        - Following the header, the column names are stored as a UTF-8 encoded comma-separated string.
        - Next, the index data is stored as int64 timestamps, which are converted to pandas datetime index.
        - The remaining data is memory-mapped as a 2D float64 array with shape (r, c).
        
        Returns:
            pd.DataFrame: A DataFrame with the memory-mapped data, indexed by datetime and labeled with column names.
        """
        filepath = self.path
        
        with open(filepath, 'rb') as f:
            nb_header = 40
            header = np.frombuffer(f.read(nb_header), dtype=np.int64)            
            r = header[0]
            c = header[1]
            nb_cols = header[2]
            nb_idx = header[3]
            nb_data = header[4]
            
            cols_b = f.read(nb_cols)
            _columns = cols_b.decode(
                encoding='UTF-8', errors='ignore').split(',')
            _columns = pd.Index(_columns)

            idx_b = f.read(nb_idx)
            _index = pd.to_datetime(np.frombuffer(idx_b, dtype=np.int64))
                                                
            nb_offset = nb_header+nb_cols+nb_idx
            self.shf = np.memmap(filepath,'<f8','r+',nb_offset,(r,c))

            _data = pd.DataFrame(self.shf,
                                index=_index,
                                columns=_columns,
                                copy=False)
            _data.index.name = 'date'
            
        return _data

    # get / set
    def get_loc_symbol(self, symbol):
        """
        Retrieve the location index associated with the given symbol.
        
        Parameters:
            symbol (hashable): The symbol to look up in the symbol index.
        
        Returns:
            int or float: The location index corresponding to the symbol if found;
                          otherwise, returns numpy.nan.
        """
        if symbol in self.symbolidx.keys():
            return self.symbolidx[symbol]
        else:
            return np.nan

    def get_loc_timestamp(self, ts):
        """
        Convert a given timestamp or array of timestamps to corresponding location indices based on the object's start date and period.
        
        Parameters:
            ts (scalar or array-like): Timestamp(s) in seconds to be converted.
        
        Returns:
            int, numpy.ndarray, or float: Location index or array of indices corresponding to the input timestamp(s). Returns np.nan if the timestamp is out of range.
        """
        istartdate = self.startDate.timestamp()  # seconds
        if not np.isscalar(ts):
            tidx = self.get_loc_timestamp_Jit(ts, istartdate,
                                              self.periodseconds, self.ctimeidx)
            return tidx
        else:
            tids = np.int64(ts)  # seconds
            tids = np.int64(tids - istartdate)
            tids = np.int64(tids/self.periodseconds)
            if tids < self.ctimeidx.shape[0]:
                tidx = self.ctimeidx[tids]
                return tidx
            else:
                return np.nan

    @staticmethod
    @jit(nopython=True, nogil=True, cache=True)
    def get_loc_timestamp_Jit(ts, istartdate, periodseconds, ctimeidx):
        """
        Convert an array of timestamps into localized timestamps based on a start date and period, using a precomputed index array.
        
        Parameters:
            ts (np.ndarray): Array of timestamps to be converted.
            istartdate (int): The start date timestamp used as a reference point.
            periodseconds (int): The length of each period in seconds.
            ctimeidx (np.ndarray): Array of precomputed localized timestamps indexed by period.
        
        Returns:
            np.ndarray: Array of localized timestamps corresponding to input timestamps. If a timestamp falls outside the range of ctimeidx, the result is NaN.
        
        Notes:
            This function is optimized with Numba JIT compilation for performance, running without Python's GIL and caching the compiled function.
        """
        tidx = np.empty(ts.shape, dtype=np.float64)
        len_ctimeidx = len(ctimeidx)
        for i in range(len(tidx)):
            tid = np.int64(ts[i])
            tid = np.int64(tid-istartdate)
            tid = np.int64(tid/periodseconds)
            if tid < len_ctimeidx:
                tidx[i] = ctimeidx[tid]
            else:
                tidx[i] = np.nan
        return tidx

    @staticmethod
    @jit(nopython=True, nogil=True, cache=True)
    def setValuesSymbolJit(values, tidx, sidx, arr):
        """
        Set values in a 2D array at specified indices using JIT compilation for performance.
        
        Parameters:
            values (np.ndarray): A 2D numpy array to be updated.
            tidx (array-like): An iterable of indices for the first dimension of `values`.
            sidx (float or int): Index for the second dimension of `values`. If NaN, no update occurs.
            arr (array-like): Values to assign at the specified indices.
        
        Notes:
            - Only updates `values` where `tidx` elements are not NaN.
            - Converts indices to int64 before assignment.
            - Uses Numba JIT compilation with no Python overhead and releases the GIL.
        """
        if not np.isnan(sidx):
            s = np.int64(sidx)
            i = 0
            for t in tidx:
                if not np.isnan(t):
                    values[np.int64(t), s] = arr[i]
                i = i+1

    @staticmethod
    @jit(nopython=True, nogil=True, cache=True)
    def setValuesJit(values, tidx, sidx, arr):
        """
        Set values in a 2D array at specified indices using JIT compilation for performance.
        
        Parameters:
        values : numpy.ndarray
            The 2D array in which values will be set.
        tidx : array-like
            Array of row indices where values should be assigned. NaN entries are ignored.
        sidx : array-like
            Array of column indices where values should be assigned. NaN entries are ignored.
        arr : numpy.ndarray
            2D array of values to assign to `values` at positions defined by `tidx` and `sidx`.
        
        Notes:
        - Indices in `tidx` and `sidx` are converted to int64 before assignment.
        - Entries in `tidx` or `sidx` that are NaN are skipped.
        - This function is optimized with Numba's JIT for speed and releases the GIL.
        """
        i = 0
        for t in tidx:
            if not np.isnan(t):
                j = 0
                for s in sidx:
                    if not np.isnan(s):
                        values[np.int64(t), np.int64(s)] = arr[i, j]
                    j = j+1
            i = i+1

    # C R U D
    def malloc(self, value=None):
        """
        Allocate or map a shared memory block for storing a DataFrame with specified index and columns.
        
        If the shared memory segment does not exist, it creates a new one, initializes it with the provided DataFrame values or NaNs, and stores metadata (shape, index, columns) in the shared memory header. If the shared memory segment already exists, it maps to the existing memory, reconstructs the DataFrame metadata, and updates the data with any overlapping values from the provided DataFrame.
        
        Returns:
            bool: True if a new shared memory segment was created, False if an existing segment was mapped.
        
        Parameters:
            value (pd.DataFrame, optional): DataFrame whose values are used to initialize or update the shared memory array. If None, the memory is initialized with NaNs.
        
        Side Effects:
            - Updates self.shm with the shared memory object.
            - Updates self.shmarr with a numpy ndarray view of the shared memory buffer.
            - Updates self.data with a pandas DataFrame backed by the shared memory.
            - Updates self.index and self.columns based on the stored metadata.
            - Sets self.create_map to 'create' or 'map' depending on the operation performed.
        """
        tini = time.time()

        # Create write ndarray
        path, shm_name = self.get_path()

        if os.environ['LOG_LEVEL'] == 'DEBUG':
            Logger.log.debug('malloc %s ...%.2f%% ' % (shm_name, 0.0))

        try:  # try create memory file
            r = len(self.index)
            c = len(self.columns)

            idx_b = self.index.astype(np.int64).values.tobytes()
            colscsv_b = str.encode(','.join(self.columns.values),
                                   encoding='UTF-8', errors='ignore')
            nb_idx = len(idx_b)
            nb_cols = len(colscsv_b)
            nb_data = int(r*c*8)
            header_b = np.array([r, c, nb_idx, nb_cols, nb_data]).astype(
                np.int64).tobytes()
            nb_header = len(header_b)

            nb_buf = nb_header+nb_idx+nb_cols+nb_data
            nb_offset = nb_header+nb_idx+nb_cols

            [self.shm, ismalloc] = self.shareddata.malloc(
                shm_name, create=True, size=nb_buf)

            i = 0
            self.shm.buf[i:nb_header] = header_b
            i = i + nb_header
            self.shm.buf[i:i+nb_idx] = idx_b
            i = i + nb_idx
            self.shm.buf[i:i+nb_cols] = colscsv_b

            self.shmarr = np.ndarray((r, c),
                                     dtype=np.float64, buffer=self.shm.buf, offset=nb_offset)

            if not value is None:
                self.shmarr[:] = value.values.copy()
            else:
                self.shmarr[:] = np.nan

            self.data = pd.DataFrame(self.shmarr,
                                     index=self.index,
                                     columns=self.columns,
                                     copy=False)

            if not value is None:
                value = self.data

            if os.environ['LOG_LEVEL'] == 'DEBUG':
                Logger.log.debug('malloc create %s ...%.2f%% %.2f sec! ' %
                                 (shm_name, 100, time.time()-tini))
            self.create_map = 'create'
            return True
        except Exception as e:
            pass

        # map memory file
        [self.shm, ismalloc] = self.shareddata.malloc(shm_name)

        i = 0
        nb_header = 40
        header = np.frombuffer(self.shm.buf[i:nb_header], dtype=np.int64)
        i = i + nb_header
        nb_idx = header[2]
        idx_b = bytes(self.shm.buf[i:i+nb_idx])
        self.index = pd.to_datetime(np.frombuffer(idx_b, dtype=np.int64))
        i = i + nb_idx
        nb_cols = header[3]
        cols_b = bytes(self.shm.buf[i:i+nb_cols])
        self.columns = cols_b.decode(
            encoding='UTF-8', errors='ignore').split(',')

        r = header[0]
        c = header[1]
        nb_data = header[4]
        nb_offset = nb_header+nb_idx+nb_cols

        self.shmarr = np.ndarray((r, c), dtype=np.float64,
                                 buffer=self.shm.buf, offset=nb_offset)

        self.data = pd.DataFrame(self.shmarr,
                                 index=self.index,
                                 columns=self.columns,
                                 copy=False)

        if not value is None:
            iidx = value.index.intersection(self.data.index)
            icol = value.columns.intersection(self.data.columns)
            self.data.loc[iidx, icol] = value.loc[iidx, icol]

        if os.environ['LOG_LEVEL'] == 'DEBUG':
            Logger.log.debug('malloc map %s/%s/%s ...%.2f%% %.2f sec! ' %
                             (self.source, self.period, self.tag, 100, time.time()-tini))
        self.create_map = 'map'
        return False

    def free(self):
        """
        Releases resources associated with the object by flushing and deleting the memory-mapped file and its related DataFrame if they exist. Additionally, removes the corresponding tag from the shared data dictionary based on the constructed path.
        
        This method ensures that all changes are saved and that memory is freed by deleting references to large data structures.
        """
        if hasattr(self, 'shf'):
            self.shf.flush()  # Ensure all changes are written back to the file
            del self.shf  # Delete the memmap object
            if hasattr(self, 'data'):
                del self.data  # Ensure DataFrame is also deleted if it exists
            
        path = f'{self.user}/{self.database}/{self.period}/{self.source}/timeseries'
        if path in self.shareddata.data.keys():
            del self.shareddata.data[path].tags[self.tag]
            