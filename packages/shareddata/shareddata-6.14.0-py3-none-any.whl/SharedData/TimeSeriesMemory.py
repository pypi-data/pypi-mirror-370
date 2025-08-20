# THIRD PARTY LIBS
import os
import pandas as pd
import numpy as np
import time
from numba import jit
from pathlib import Path

from SharedData.Logger import Logger


class TimeSeriesMemory:

    """
    '''
    Manages shared memory for time series data, enabling creation, mapping, and manipulation of time-indexed data frames stored in shared memory.
    
    This class supports initializing a shared memory segment for time series data either by creating a new segment or mapping an existing one. It handles indexing by timestamps and symbols, and provides efficient read/write access to the underlying data using numpy arrays backed by shared memory buffers.
    
    Attributes:
        shareddata: Shared memory manager instance used for allocating and freeing shared memory.
        container: Container object providing period length and time index utilities.
        database: Name of the database.
        period: Time period string (e.g., '1min', '5min').
        source: Data source identifier.
        tag: Tag identifying the specific time series.
        user: User identifier for namespacing shared memory.
        periodseconds: Length of the period in seconds.
        create_map: Indicates whether to create ('create') or map ('map') shared memory.
        init_time: Initialization duration in seconds.
        download_time: Timestamp of last download (initially NaT).
        last_update: Timestamp of last update (initially NaT).
        first_update: Timestamp of first update (initially NaT).
        data: Pandas DataFrame backed by shared
    """
    def __init__(self, shareddata, container, database, period, source, tag,
                 value=None, startDate=None, columns=None, user='master'):

        """
        '''
        Initialize the shared memory time series object.
        
        Parameters:
            shareddata: Shared data manager or handler.
            container: Container object providing periodseconds and data reading capabilities.
            database: Database identifier or connection.
            period: Time period for the time series data.
            source: Source identifier for the data.
            tag: Tag identifier for the data.
            value (optional): Initial data as a pandas DataFrame to populate the shared memory.
            startDate (optional): Start date for the time series if creating new shared memory without initial data.
            columns (optional): Column names for the time series data.
            user (str, optional): User identifier, default is 'master'.
        
        Behavior:
            - Checks if shared memory already exists; decides to create or map accordingly.
            - If creating new shared memory:
                - Initializes empty shared memory if startDate is provided without value.
                - Initializes shared memory with provided value DataFrame.
                - Logs error if neither startDate nor value is provided.
            - If mapping existing shared memory:
                - Maps the shared memory and updates data if value is provided.
            - Handles exceptions by logging errors and freeing resources.
        
        Attributes initialized:
            shareddata, container, user, database, period, source, tag,
            period
        """
        self.shareddata = shareddata
        self.container = container
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tag = tag

        self.periodseconds = container.periodseconds

        # test if shared memory already exists
        if self.ismalloc():
            self.create_map = 'map'
        else:
            self.create_map = 'create'
            
        self.init_time = time.time()
        self.download_time = pd.NaT
        self.last_update = pd.NaT
        self.first_update = pd.NaT

        # Time series dataframe
        self.data = pd.DataFrame()
        self.index = pd.Index([])
        self.columns = pd.Index([])

        # initalize
        try:
            if self.create_map == 'create':
                if (not startDate is None) & (value is None):
                    # create new shared memory empty
                    self.startDate = startDate
                    self.columns = columns
                    self.malloc_create()

                elif (not value is None):
                    # create new shared memory with value
                    self.startDate = value.index[0]
                    self.columns = value.columns
                    self.malloc_create()
                    sidx = np.array([self.get_loc_symbol(s)
                                    for s in self.columns])
                    ts = value.index.values.astype(np.int64)/10**9  # seconds
                    tidx = self.get_loc_timestamp(ts)
                    self.setValuesJit(self.data.values, tidx,
                                      sidx, value.values)

                elif (value is None):
                    Logger.log.error('Tag %s/%s not mapped!' %
                                     (self.source, self.tag))
                    # read & allocate data
                    tini = time.time()
                    datasize = self.container.read()
                    datasize /= (1024*1024)
                    te = time.time()-tini+0.000001
                    Logger.log.debug('read %s/%s %.2fMB in %.2fs %.2fMBps ' %
                                     (self.source, self.tag, datasize, te, datasize/te))

            elif self.create_map == 'map':
                # map existing shared memory
                self.malloc_map()
                if (not value is None):
                    iidx = value.index.intersection(self.data.index)
                    icol = value.columns.intersection(self.data.columns)
                    self.data.loc[iidx, icol] = value.loc[iidx, icol].copy()
        except Exception as e:
            path, shm_name = self.get_path()
            Logger.log.error('Error initalizing %s!\n%s' % (shm_name, str(e)))
            self.free()

        self.init_time = time.time() - self.init_time

    def get_path(self):
        """
        Constructs and returns the filesystem path and shared memory name for the timeseries data.
        
        The method builds a path based on the instance attributes: user, database, period, source, and tag.
        It returns a tuple containing:
        - path: a pathlib.Path object representing the full path within the DATABASE_FOLDER environment variable.
        - shm_name: a string representing the shared memory name, with directory separators adjusted based on the operating system.
        
        Returns:
            tuple[pathlib.Path, str]: A tuple containing the constructed path and shared memory name.
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
        path = path / self.tag
        path = Path(str(path).replace('\\', '/'))
        
        return path, shm_name

    def ismalloc(self):
        """
        Allocates shared memory for the object using a shared memory manager.
        
        Retrieves the shared memory path and name, then attempts to allocate the shared memory segment
        via the shareddata manager. Updates the object's shared memory reference and returns whether
        the allocation was successful.
        
        Returns:
            bool: True if the shared memory was successfully allocated, False otherwise.
        """
        path, shm_name = self.get_path()
        [self.shm, ismalloc] = self.shareddata.malloc(shm_name)
        return ismalloc

    def malloc_create(self):
        """
        Create a shared memory block to store a DataFrame with specified columns and time index.
        
        This method initializes shared memory for a DataFrame based on the time index and columns obtained from the container.
        It sets up the shared memory buffer with a header containing metadata, the time index, column names, and a data array initialized with NaNs.
        The shared memory is mapped to a NumPy ndarray and then wrapped in a pandas DataFrame for easy access.
        
        Returns:
            bool: True if the shared memory allocation and DataFrame creation succeed.
        
        Raises:
            Exception: If any error occurs during the shared memory allocation or DataFrame setup, the exception is logged and re-raised.
        """
        path, shm_name = self.get_path()
        self.symbolidx = {}
        for i in range(len(self.columns)):
            self.symbolidx[self.columns.values[i]] = i
        self.index = self.container.getTimeIndex(self.startDate)
        self.ctimeidx = self.container.getContinousTimeIndex(self.startDate)
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

            self.shmarr[:] = np.nan

            self.data = pd.DataFrame(self.shmarr,
                                     index=self.index,
                                     columns=self.columns,
                                     copy=False)

            return True
        except Exception as e:
            Logger.log.error('Failed to malloc_create\n%s' % str(e))
            raise Exception('Failed to malloc_create\n%s' % str(e))            

    def malloc_map(self):
        """
        Allocate and map a shared memory segment to a pandas DataFrame.
        
        This method attempts to create or access a shared memory block using a name obtained from `get_path()`. It reads a header from the shared memory buffer to extract metadata including the number of rows, columns, and index size. It then reconstructs the DataFrame's index and columns from the shared memory, and creates a NumPy ndarray view of the data buffer. Finally, it constructs a pandas DataFrame using this ndarray, index, and columns without copying the data.
        
        Returns:
            bool: True if the shared memory mapping and DataFrame creation succeed, False otherwise.
        """
        try:  # try map memory file
            path, shm_name = self.get_path()
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

            return True
        except Exception as e:
            Logger.log.error('Failed to malloc_map\n%s' % str(e))
            return False

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
            int, np.ndarray, or float: Location index or array of indices corresponding to the input timestamp(s). Returns np.nan if the timestamp is out of range.
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
        Convert an array of timestamps to localized timestamps using a reference start date, period length, and a mapping index array.
        
        Parameters:
            ts (np.ndarray): Array of timestamps to be converted.
            istartdate (int): Reference start date timestamp.
            periodseconds (int): Length of each period in seconds.
            ctimeidx (np.ndarray): Array mapping period indices to localized timestamps.
        
        Returns:
            np.ndarray: Array of localized timestamps corresponding to input timestamps. If a timestamp falls outside the range of ctimeidx, the result is NaN for that entry.
        
        Notes:
            This function is JIT-compiled with Numba for performance optimization.
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
            values (np.ndarray): A 2D NumPy array to be updated.
            tidx (array-like): An iterable of indices for the first dimension of `values`.
            sidx (float or int): An index for the second dimension of `values`. If NaN, no update is performed.
            arr (array-like): An iterable of values to assign to `values` at positions defined by `tidx` and `sidx`.
        
        Notes:
            - The function skips any NaN values in `tidx` and does not update `values` if `sidx` is NaN.
            - Uses Numba's JIT compilation with `nopython=True` and `nogil=True` for optimized performance.
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
        values (np.ndarray): The 2D array to be updated.
        tidx (array-like): Array of row indices where values will be set; NaN entries are ignored.
        sidx (array-like): Array of column indices where values will be set; NaN entries are ignored.
        arr (np.ndarray): 2D array of values to assign at the specified indices.
        
        This function iterates over the provided row and column indices, skipping any NaN values,
        and assigns corresponding values from 'arr' to 'values' at the specified positions.
        The function is optimized with Numba's JIT decorator for faster execution.
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
        Allocate or map a shared memory block for storing a DataFrame with the given index and columns.
        
        If the shared memory segment does not exist, it creates a new one, initializes it with the provided DataFrame values or NaNs, and stores metadata (shape, index, columns) in the shared memory header. If the shared memory segment already exists, it maps to the existing memory, reconstructs the DataFrame metadata, and updates the data with any overlapping values from the provided DataFrame.
        
        Returns:
            bool: True if a new shared memory segment was created, False if an existing segment was mapped.
        
        Parameters:
            value (pd.DataFrame or None): Optional DataFrame to initialize or update the shared memory data.
        
        Side Effects:
            - Updates self.shm with the shared memory object.
            - Updates self.shmarr with the numpy ndarray view of the shared memory buffer.
            - Updates self.data with the pandas DataFrame backed by shared memory.
            - Updates self.index and self.columns based on stored metadata.
            - Sets self.create_map to 'create' if new memory was allocated, or 'map' if existing memory was mapped.
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
        Releases the shared memory resource associated with the current instance.
        
        This method retrieves the shared memory path and name using `get_path()`
        and then frees the shared memory segment identified by `shm_name` via
        the `shareddata.free()` method.
        """
        path, shm_name = self.get_path()
        self.shareddata.free(shm_name)
