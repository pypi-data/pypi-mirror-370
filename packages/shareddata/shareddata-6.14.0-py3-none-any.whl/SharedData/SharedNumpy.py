import pandas as pd
import numpy as np
import time
from datetime import datetime
from tqdm import tqdm
import os

from SharedData.Logger import Logger
from SharedData.TableIndexJit import get_date_loc_jit, get_date_loc_gte_jit, get_date_loc_lte_jit,get_date_loc_gte_lte_jit
from SharedData.TableIndexJit import get_symbol_loc_jit, get_portfolio_loc_jit, get_tag_loc_jit
from SharedData.Utils import mmaparray2df
from SharedData.Database import STRING_FIELDS
       
class SharedNumpy(np.ndarray):

    """
    A subclass of numpy.ndarray designed to represent and manage shared data tables with support for both in-memory and disk-backed storage.
    
    This class integrates tightly with a backing 'table' object that manages metadata, indexing, and persistence. It provides methods for inserting, extending, and upserting records, as well as querying by primary key, date, symbol, portfolio, and tags. It supports synchronization features such as subscribing and publishing data streams.
    
    Key features:
    - Supports two types of storage: 'MEMORY' (in-memory ndarray) and 'DISK' (memory-mapped file).
    - Automatic handling of record metadata such as modification time.
    - Index management and fast lookup operations on primary keys and other indexed fields.
    - Conversion utilities between numpy structured arrays and pandas DataFrames.
    - Methods to manage memory mapping and file resizing for disk-backed tables.
    - Stream reading and synchronization capabilities for real-time data updates.
    - Properties to access and modify table metadata like count, record size, modification time, and indexes.
    
    Intended for use in high-performance data applications requiring efficient storage, indexing, and querying of large structured datasets.
    """
    def __new__(cls, type, *args, **kwargs):
        """
        Create a new instance of the class based on the specified type.
        
        Parameters:
            cls (type): The class to instantiate.
            type (str): The type of instance to create. Must be either 'MEMORY' or 'DISK'.
            *args: Additional positional arguments passed to the underlying ndarray or memmap.
            **kwargs: Additional keyword arguments passed to the underlying ndarray.
        
        Returns:
            instance: A new instance of the class, either a standard ndarray subclass ('MEMORY') or a memmap-backed subclass ('DISK').
        
        Raises:
            Exception: If the provided type is not 'MEMORY' or 'DISK'.
        """
        if type == 'MEMORY':
            obj = np.ndarray.__new__(cls, *args, **kwargs)
            obj.table = None
            return obj
        elif type == 'DISK':
            memmap = args[0]
            obj = memmap.view(cls)
            obj.memmap = memmap
            obj.table = None
            obj._df = None
            return obj
        else:
            raise Exception('Unknown type %s!' % (type))

    def free(self):
        """
        Releases the resources held by the table.
        
        Calls the `free` method on the `table` attribute to free up any allocated resources.
        """
        self.table.free()

    def trim(self):
        """
        Calls the trim method on the internal table attribute to optimize its storage or remove unused elements.
        """
        self.table.trim()

    def write(self,force_write=False):
        """
        Writes the table data to storage, optionally forcing the write operation.
        
        If the table has an index (`hasindex` is 1) and the index is not sorted (`isidxsorted` is 0),
        the index is sorted before writing. The write operation is then performed on the table,
        with the option to force the write regardless of internal conditions.
        
        Parameters:
            force_write (bool): If True, forces the write operation even if not necessary. Defaults to False.
        """
        if self.table.hdr['hasindex']==1 and self.table.hdr['isidxsorted']==0:
            self.sort_index()
        self.table.write(force_write)
        
    def rememmap(self):
        """
        Create and return a memory-mapped view of the table's records.
        
        This method creates a numpy memmap object for the table's data file with the appropriate dtype and shape,
        then creates a new instance of the current class viewing this memmap. It sets the table and memmap attributes
        on the new instance, updates the table's records reference to this new instance, and returns it.
        
        Returns:
            An instance of the current class that provides a memory-mapped view of the table's records.
        """
        memmap = np.memmap(self.table.filepath, self.table.recdtype, 'r+', self.table.hdr.dtype.itemsize, (self.recordssize,))
        new_instance = memmap.view(self.__class__)
        new_instance.table = self.table
        new_instance.memmap = memmap
        self.table.records = new_instance
        return new_instance
    
    def reload(self):
        """
        Reloads the data in the table by invoking the table's reload method.
        
        Returns:
            The result of the table's reload operation.
        """
        return self.table.reload()
    
    ################################# SYNC TABLE ########################################
    def subscribe(self, host, port=None, lookbacklines=1000, lookbackdate=None, method='websocket', snapshot=False, bandwidth=1e6, protocol='http'):
        """
        Subscribe to a data source with specified connection parameters.
        
        Parameters:
            host (str): The hostname or IP address of the data source.
            port (int, optional): The port number to connect to. Defaults to None.
            lookbacklines (int, optional): Number of lines to look back from the data source. Defaults to 1000.
            lookbackdate (str or datetime, optional): Specific date to look back to. Defaults to None.
            method (str, optional): Connection method to use (e.g., 'websocket'). Defaults to 'websocket'.
            snapshot (bool, optional): Whether to take a snapshot of the data upon subscription. Defaults to False.
            bandwidth (float, optional): Bandwidth limit in bits per second. Defaults to 1e6.
            protocol (str, optional): Protocol to use for the connection (e.g., 'http'). Defaults to 'http'.
        
        This method delegates the subscription request to the underlying table object's subscribe method.
        """
        self.table.subscribe(host, port, lookbacklines,
                             lookbackdate, method, snapshot, bandwidth,protocol)
        
    def publish(self, host, port=None, lookbacklines=1000, lookbackdate=None, method='websocket', snapshot=False, bandwidth=1e6, protocol='http'):
        """
        Publish the table data to a specified host and port using the given parameters.
        
        Parameters:
            host (str): The hostname or IP address to publish to.
            port (int, optional): The port number to use for publishing. Defaults to None.
            lookbacklines (int, optional): Number of lines to look back for data. Defaults to 1000.
            lookbackdate (str or datetime, optional): Date to look back from for data. Defaults to None.
            method (str, optional): The method of publishing, e.g., 'websocket'. Defaults to 'websocket'.
            snapshot (bool, optional): Whether to publish a snapshot of the data. Defaults to False.
            bandwidth (float, optional): Bandwidth limit in bits per second. Defaults to 1e6.
            protocol (str, optional): Protocol to use for publishing, e.g., 'http'. Defaults to 'http'.
        
        Returns:
            None
        """
        self.table.publish(host, port, lookbacklines,
                             lookbackdate, method, snapshot, bandwidth,protocol)
    
    def read_stream(self, buffer):
        
        """
        Reads and processes complete records from the given byte buffer.
        
        This method checks if the buffer contains enough bytes to form at least one complete record
        based on the predefined item size. It extracts all complete records from the buffer, converts
        them into a NumPy array of the specified data type, and then either upserts or extends these
        records into the associated table depending on whether the table has an index. The processed
        bytes are removed from the buffer.
        
        Parameters:
            buffer (bytearray): The byte buffer containing raw data to be read and processed.
        
        Returns:
            bytearray: The remaining buffer after extracting and processing complete records.
        """
        if len(buffer) >= self.itemsize:
            # Determine how many complete records are in the buffer
            num_records = len(buffer) // self.itemsize
            # Take the first num_records worth of bytes
            record_data = buffer[:num_records * self.itemsize]
            # And remove them from the buffer
            del buffer[:num_records * self.itemsize]
            # Convert the bytes to a NumPy array of records
            rec = np.frombuffer(
                record_data, dtype=self.dtype)
            
            if self.table.hasindex:
                # Upsert all records at once
                self.upsert(rec)
            else:
                # Extend all records at once
                self.extend(rec)

        return buffer

    ############################## KEYLESS OPERATIONS ########################################

    def insert(self, new_records, acquire=True):
        """
        Insert new records into the table, optionally acquiring a lock during the operation.
        
        Parameters:
            new_records (numpy.ndarray): Array of new records to be inserted.
            acquire (bool, optional): Whether to acquire the table lock before insertion. Defaults to True.
        
        Raises:
            Exception: If the table's maximum size is exceeded or if any error occurs during insertion.
        
        Behavior:
            - Acquires the table lock if `acquire` is True.
            - Checks if there is enough space to insert the new records.
            - Converts `new_records` to the table's dtype if necessary.
            - Updates any 'mtime' fields with NaT values to the current time in nanoseconds.
            - Inserts the new records into the table's underlying array.
            - Updates the record count and modification time.
            - Releases the table lock if it was acquired.
            - Logs errors and raises exceptions on failure.
        """
        errmsg = ''
        try:
            if acquire:
                self.table.acquire()

            nrec = new_records.size
            _count = self.count
            if (_count + nrec <= self.size):
                # convert new_records
                if (self.dtype != new_records.dtype):
                    new_records = self.convert(new_records)
                # fill mtime
                nidx = np.isnat(new_records['mtime'])
                if nidx.any():
                    new_records['mtime'][nidx] = time.time_ns()

                arr = super().__getitem__(slice(0, self.size))
                arr[_count:_count+nrec] = new_records
                self.count = _count + nrec
                self.mtime = datetime.now().timestamp()
            else:
                errmsg = 'Table max size reached!'
                Logger.log.error(errmsg)
        except Exception as e:
            errmsg = 'Error inserting %s!\n%s' % (self.table.relpath, str(e))
            Logger.log.error(errmsg)
        finally:
            if acquire:
                self.table.release()
            if errmsg:
                raise Exception(errmsg)

    def extend(self, new_records, acquire=True):
        """
        '''
        Extend the underlying table by appending new records.
        
        This method attempts to add new_records to the table's data storage, handling file resizing and memory mapping as needed. It performs several checks and operations:
        
        - Raises an exception if the table is in-memory or has an index, as extending is not supported in these cases.
        - Optionally acquires a lock on the table before modification.
        - If the current allocated record size is insufficient, extends the file size by approximately 100MB (aligned to page size) to accommodate new records.
        - Uses memory mapping to remap the extended file region.
        - Converts new_records to the appropriate dtype if necessary.
        - Fills missing modification times ('mtime') in new_records with the current time in nanoseconds.
        - Inserts the new_records into the table without acquiring the lock again.
        - Releases the lock if it was acquired.
        - Logs and raises exceptions encountered during the process.
        
        Parameters:
            new_records (numpy.ndarray): Array of new records to append to the table.
            acquire (bool, optional): Whether to acquire the table lock during the operation. Defaults to True.
        
        Returns:
            SharedNumpy: The updated records object of the table after extension.
        
        Raises:
            Exception: If the table is in-memory, has an index
        """
        errmsg = ''
        if self.table.type == 'MEMORY':
                raise Exception(
                    'Table %s is in memory, extend not supported!' % (self.table.relpath))

        if self.table.hdr['hasindex'] == 1:
            raise Exception(
                'Table %s has index, extend not supported!' % (self.table.relpath))
        
        try:            
            if acquire:
                self.table.acquire()
            
            if self.size < self.recordssize:
                self = self.rememmap()

            nrec = new_records.size
            _count = self.count.copy()
            
            if (_count + nrec > self.recordssize):
                # extend table by 10MB
                rec = self.table.records
                page_size = 4096
                extend_size = int(np.round(100 * 1024 * 1024 / page_size) * page_size)
                new_rows = int(np.floor(extend_size/rec.dtype.itemsize))
                new_rows = max(new_rows, nrec)

                new_recordssize = rec.size + new_rows
                hdr_bytes = self.table.hdr.dtype.itemsize
                rec_bytes = rec.dtype.itemsize * rec.size                
                totalbytes = hdr_bytes + rec_bytes + rec.dtype.itemsize*new_rows
                
                with open(self.table.filepath, 'ab+') as f:
                    # Seek to the end of the file
                    f.seek(totalbytes-1)
                    # Write a single null byte to the end of the file
                    f.write(b'\x00')
                    if os.name == 'posix':
                        os.posix_fallocate(f.fileno(), 0, totalbytes)
                    elif os.name == 'nt':
                        pass  # TODO: implement preallocation for windows in pyd

                # remap extended file
                if self.table.shf_data is not None:
                    self.table.shf_data.flush()
                self.table.shf_data = np.memmap(
                    self.table.filepath,rec.dtype,'r+',
                    hdr_bytes,(new_recordssize,) )
                self.table.records = SharedNumpy('DISK', self.table.shf_data)
                self.table.records.table = self.table                
                self.recordssize = new_recordssize

            # convert new_records
            if (self.dtype != new_records.dtype):
                new_records = self.convert(new_records)
            # fill mtime
            nidx = np.isnat(new_records['mtime'])
            if nidx.any():
                new_records['mtime'][nidx] = time.time_ns()
            # insert data
            self.table.records.insert(new_records, acquire=False)
            
            return self.table.records
        

        except Exception as e:
            errmsg = 'Error extending %s!\n%s' % (self.table.relpath, str(e))
            Logger.log.error(errmsg)
        finally:
            if acquire:
                self.table.release()
            if errmsg:
                raise Exception(errmsg)

    ############################## PRIMARY KEY OPERATIONS ########################################
    @property
    def loc(self):
        """
        Provides a location-based indexer for selecting data by label.
        
        Returns an instance of the _LocIndexer class initialized with the current object,
        enabling label-based indexing and slicing operations.
        """
        return _LocIndexer(self)

    def upsert(self, new_records, acquire=True):
        # TODO: check if index variables are valid
        """
        Upserts new records into the table, updating existing entries or inserting new ones as needed.
        
        Parameters:
            new_records (np.ndarray or pd.DataFrame): The records to be upserted. Can be a numpy structured array or a pandas DataFrame.
            acquire (bool, optional): Whether to acquire a lock on the table during the operation. Defaults to True.
        
        Returns:
            int: The minimum change ID (minchgid) if upsert occurs, otherwise the current count of records.
        
        Raises:
            Exception: If the table has no index, if an error occurs during upsert, or if the table is full.
        
        Notes:
            - Validates and converts input records to the appropriate dtype.
            - Updates 'mtime' field to current UTC time if missing or invalid.
            - Filters out records with invalid or out-of-range dates (except for tables named 'Symbols').
            - Ensures the index is created and valid before upserting.
            - Handles concurrency by optionally acquiring and releasing a table lock.
            - Logs warnings for invalid mtimes and critical errors if the table is full.
        """
        if self.table.hdr['hasindex'] == 0:
            raise Exception('Table %s has no index!' % (self.table.relpath))

        if new_records.size > 0:

            # convert to same dtype record
            if isinstance(new_records, pd.DataFrame):
                new_records = self.table.df2records(new_records)
            elif (self.dtype != new_records.dtype):
                new_records = self.convert(new_records)

            utcnow = np.datetime64(time.time_ns(), 'ns') # add 1 second tolerance
            # fill mtime
            nidx = np.isnat(new_records['mtime'])
            if nidx.any():
                new_records['mtime'][nidx] = utcnow

            # remove invalid mtime
            invalididx = new_records['mtime'].astype(np.int64) > utcnow.astype(np.int64) + 1000000000
            if invalididx.any():
                new_records[invalididx]['mtime'] = utcnow
                Logger.log.warning('%s: %d records with invalid mtime check your system clock!' \
                                   % (self.table.relpath, invalididx.sum()))

            # check for null date
            if self.table.database!='Symbols':
                invalididx = np.isnat(new_records['date'])
                invalididx = invalididx | (new_records['date'] < self.table.mindate)
                invalididx = invalididx | (new_records['date'] >= self.table.maxdate)
                if invalididx.any():
                    new_records = new_records[~invalididx]
                # round date to period
                new_records['date'] = (new_records['date'].astype(np.int64) // self.table.periodns) * self.table.periodns

            if new_records.size > 0:
                # single record to array
                if new_records.shape == ():
                    new_records = np.array([new_records])

                try:
                    success = True
                    if acquire:
                        self.table.acquire()

                    # check if index is created & valid
                    if self.table.hdr['isidxcreated'] == 0:
                        self.index.create_index(self, self.pkey)

                    # upsert
                    minchgid = self.count
                    arr = super().__getitem__(slice(0, self.size))

                    self.table.hdr['isidxcreated'] == 0

                    self.count, minchgid, isidxsorted = self.index.upsert_func(
                        arr, self.count, new_records, self.pkey,
                        self.index.datelastidx, self.index.dateprevidx,
                        self.table.mindate, self.table.periodns,
                        self.index.portlastidx, self.index.portprevidx,
                        self.index.symbollastidx, self.index.symbolprevidx)

                    self.table.hdr['isidxsorted'] == 1 if isidxsorted else 0
                    self.table.hdr['isidxcreated'] == 1
                    minchgid = int(minchgid)
                    self.minchgid = minchgid
                    self.mtime = datetime.now().timestamp()

                except Exception as e:
                    Logger.log.error('Error upserting %s!\n%s' %
                                     (self.table.relpath, str(e)))
                    success = False
                finally:
                    if acquire:
                        self.table.release()
                    # table full
                    if self.count == self.size:
                        Logger.log.critical('Table %s is full!' %
                                           (self.table.relpath))
                    if not success:
                        raise Exception('Error upserting %s!' %
                                        (self.table.relpath))
                return minchgid

        return self.count

    def sort_index(self, start=0):
        """
        Sorts the index of the object starting from the specified position.
        
        Parameters:
            start (int): The position from which to start sorting the index. Defaults to 0.
        
        Note:
            This method calls the `sort_index` method of the `index` attribute, passing the current object and the start position.
        """
        self.index.sort_index(self, start)

    def get_loc(self, keys, acquire=True):
        """
        Retrieve the location(s) of the given key(s) in the indexed table.
        
        Parameters:
            keys (array-like): The key or keys to locate in the table index.
            acquire (bool, optional): Whether to acquire and release the table lock during the operation. Defaults to True.
        
        Returns:
            numpy.ndarray: An array of integer locations corresponding to the provided keys.
        
        Raises:
            Exception: If the table does not have an index, if there is an error during location retrieval,
                       or if the index is not properly created and cannot be generated.
        """
        success = False
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        
        try:
            if acquire:
                self.table.acquire()

            # check if index is created & valid
            if self.table.hdr['isidxcreated'] == 0:
                self.index.create_index(self, self.pkey)

            loc = self.index.get_loc_func(
                self[:], self.pkey, keys).astype(np.int64)
            success = True
        except Exception as e:
            Logger.log.error('Error getting loc for %s!\n%s' %
                             (self.table.relpath, str(e)))
            loc = np.array([])
        finally:
            if acquire:
                self.table.release()
            if not success:
                raise Exception('Error getting loc for %s!' %
                                (self.table.relpath))
        return loc

    def get_date_loc(self, date, maxids=0):
        """
        Retrieve the location indices corresponding to a given date within the table's index.
        
        Parameters:
            date (pd.Timestamp or np.datetime64): The date for which to find location indices.
            maxids (int, optional): Maximum number of indices to return. Defaults to 0 (no limit).
        
        Returns:
            np.ndarray: An array of location indices matching the given date. Returns an empty array if the date is out of range.
        
        Raises:
            Exception: If the table does not have an index or if there is an error during the retrieval process.
        """
        success = False
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        try:
            self.table.acquire()

            # check if index is created & valid
            if self.table.hdr['isidxcreated'] == 0:
                self.index.create_index(self, self.pkey)
            
            if isinstance(date, pd.Timestamp):
                date = np.datetime64(date,'ns')

            datelastidx = self.table.index.datelastidx
            dateprevidx = self.table.index.dateprevidx            
            mindate = self.table.mindate
            periodns = self.table.periodns
            if (date < mindate) | (date >= self.table.maxdate):
                loc = np.array([])                
            else:                            
                loc = get_date_loc_jit(date, datelastidx, dateprevidx, mindate, periodns, maxids)
            
            success = True
        except Exception as e:
            Logger.log.error('Error getting date_loc for %s!\n%s' %
                             (self.table.relpath, str(e)))
        finally:
            self.table.release()
            if not success:
                raise Exception('Error getting date_loc for %s!' %
                                (self.table.relpath))
        return loc

    # get date loc greater than or equal to startdate
    def get_date_loc_gte(self, startdate, maxids=0):
        """
        Retrieve the indices of records with dates greater than or equal to a specified start date.
        
        This method returns a NumPy array of record indexes where the date is greater than or equal to `startdate`.
        It utilizes a Just-In-Time (JIT) compiled function for fast execution. The table must have an index
        available, otherwise an exception is raised.
        
        Parameters:
            startdate (pd.Timestamp or np.datetime64): The start date to compare against.
            maxids (int, optional): Maximum number of record indexes to return. Defaults to 0 (no limit).
        
        Returns:
            np.ndarray: Array of record indexes with dates >= `startdate`.
        
        Raises:
            Exception: If the table does not have an index.
        """
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        if isinstance(startdate, pd.Timestamp):
            startdate = np.datetime64(startdate, 'ns')

        datelastidx = self.table.index.datelastidx
        dateprevidx = self.table.index.dateprevidx
        mindate = self.table.mindate
        periodns = self.table.periodns

        return get_date_loc_gte_jit(startdate, datelastidx, dateprevidx, mindate, periodns, maxids)
    
    # get date loc less than or equal to enddate
    def get_date_loc_lte(self, enddate, maxids=0):
        """
        Retrieve the indices of records with dates less than or equal to a specified end date.
        
        This method returns a NumPy array of record indexes where the record dates are less than or equal to the given `enddate`. It uses a Just-In-Time (JIT) compiled function for fast execution. The method requires the underlying table to have an index; otherwise, it raises an exception.
        
        Parameters:
            enddate (pd.Timestamp or np.datetime64): The end date to compare against record dates.
            maxids (int, optional): Maximum number of record indexes to return. Defaults to 0 (no limit).
        
        Returns:
            np.ndarray: Array of record indexes with dates <= `enddate`.
        
        Raises:
            Exception: If the table does not have an index.
        """
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        if isinstance(enddate, pd.Timestamp):
            enddate = np.datetime64(enddate, 'ns')

        datelastidx = self.table.index.datelastidx
        dateprevidx = self.table.index.dateprevidx
        mindate = self.table.mindate
        periodns = self.table.periodns

        return get_date_loc_lte_jit(enddate, datelastidx, dateprevidx, mindate, periodns, maxids)
    
    # get date loc greater than or equal to startdate
    def get_date_loc_gte_lte(self, startdate, enddate, maxids=0):
        """
        Retrieve the indices of records within the specified date range [startdate, enddate].
        
        This method returns a NumPy array of record indexes where the record dates satisfy the condition:
        startdate <= date <= enddate. It uses a Just-In-Time (JIT) compiled function for fast execution.
        
        Parameters:
            startdate (pd.Timestamp or np.datetime64): The start date of the range (inclusive).
            enddate (pd.Timestamp or np.datetime64): The end date of the range (inclusive).
            maxids (int, optional): Maximum number of record indexes to return. Defaults to 0 (no limit).
        
        Returns:
            np.ndarray: Array of record indexes matching the date range criteria.
        
        Raises:
            Exception: If the underlying table does not have an index.
        """
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        if isinstance(startdate, pd.Timestamp):
            startdate = np.datetime64(startdate, 'ns')
        if isinstance(enddate, pd.Timestamp):
            enddate = np.datetime64(enddate, 'ns')

        datelastidx = self.table.index.datelastidx
        dateprevidx = self.table.index.dateprevidx
        mindate = self.table.mindate
        periodns = self.table.periodns

        return get_date_loc_gte_lte_jit(startdate, enddate, datelastidx, dateprevidx, mindate, periodns, maxids)

    def get_symbol_loc(self, symbol, maxids=0):
        """
        Retrieve the location index of a given symbol within the table's indexed data.
        
        This method ensures that the table has an index, creates the index if it is not already created,
        and then searches for the symbol's location using a JIT-compiled helper function. The symbol can be
        provided as a string or bytes; if a string is given, it is encoded to UTF-8 bytes before searching.
        
        Parameters:
            symbol (str or bytes): The symbol to locate in the table.
            maxids (int, optional): A parameter to limit the search range or number of IDs considered. Defaults to 0.
        
        Returns:
            int: The location index of the symbol within the table.
        
        Raises:
            Exception: If the table does not have an index or if there is an error during the symbol location retrieval.
        """
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        success = False
        try:
            self.table.acquire()
            # check if index is created & valid
            if self.table.hdr['isidxcreated'] == 0:
                self.index.create_index(self, self.pkey)

            if not isinstance(symbol, bytes):
                symbol = symbol.encode('utf-8')
            
            _rec = np.full((1,),np.nan,dtype=self.dtype)
            _rec['symbol'] = symbol
            loc = get_symbol_loc_jit(self[:], self.index.symbollastidx,
                                 self.index.symbolprevidx, _rec, maxids)
            success = True
        except Exception as e:
            Logger.log.error('Error getting symbol_loc for %s!\n%s' %
                             (self.table.relpath, str(e)))
        finally:
            self.table.release()
            if not success:
                raise Exception('Error getting symbol_loc for %s!' %
                                (self.table.relpath))
        return loc

    def get_portfolio_loc(self, portfolio, maxids=0):
        """
        Retrieve the location(s) of a given portfolio within the table using the index.
        
        Parameters:
            portfolio (str or bytes): The portfolio identifier to locate. If a string is provided, it will be encoded to bytes.
            maxids (int, optional): The maximum number of IDs to retrieve. Defaults to 0.
        
        Returns:
            loc: The location(s) of the portfolio in the table as determined by the index.
        
        Raises:
            Exception: If the table does not have an index or if there is an error during the retrieval process.
        
        Notes:
            - The method ensures the index is created and valid before searching.
            - The table is locked during the operation to prevent concurrent modifications.
        """
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        success = False
        try:
            self.table.acquire()
            # check if index is created & valid
            if self.table.hdr['isidxcreated'] == 0:
                self.index.create_index(self, self.pkey)

            if not isinstance(portfolio, bytes):
                portfolio = portfolio.encode('utf-8')
            
            _rec = np.full((1,),np.nan,dtype=self.dtype)
            _rec['portfolio'] = portfolio
            loc = get_portfolio_loc_jit(
                self[:], self.index.portlastidx, self.index.portprevidx, _rec, maxids)
            success = True
        except Exception as e:
            Logger.log.error('Error getting portfolio_loc for %s!\n%s' %
                             (self.table.relpath, str(e)))
        finally:
            self.table.release()
            if not success:
                raise Exception('Error getting portfolio_loc for %s!' %
                                (self.table.relpath))
        return loc

    def get_tag_loc(self, tag, maxids=0):
        """
        Retrieve the location index of a given tag within the table's indexed data.
        
        This method checks if the table has an index and creates one if it does not exist.
        It then encodes the tag to bytes if necessary, constructs a record with the tag,
        and uses a JIT-compiled function to find the location of the tag in the index.
        
        Parameters:
            tag (str or bytes): The tag to locate in the table index.
            maxids (int, optional): Maximum number of IDs to consider. Defaults to 0.
        
        Returns:
            int: The location index of the tag in the table.
        
        Raises:
            Exception: If the table does not have an index or if there is an error during the lookup process.
        """
        if self.table.hdr['hasindex'] != 1:
            raise Exception(f'Table {self.table.relpath} does not have index!')
        success = False
        try:
            self.table.acquire()
            # check if index is created & valid
            if self.table.hdr['isidxcreated'] == 0:
                self.index.create_index(self, self.pkey)

            if not isinstance(tag, bytes):
                tag = tag.encode('utf-8')

            _rec = np.full((1,),np.nan,dtype=self.dtype)
            _rec['tag'] = tag

            loc = get_tag_loc_jit(
                self[:], self.index.portlastidx, self.index.portprevidx, _rec, maxids)
            success = True
        except Exception as e:
            Logger.log.error('Error getting tag_loc for %s!\n%s' %
                             (self.table.relpath, str(e)))
        finally:
            self.table.release()
            if not success:
                raise Exception('Error getting tag_loc for %s!' %
                                (self.table.relpath))
        return loc

    ############################## CONVERSION ##############################
    @property
    def df(self):
        """
        Lazily loads and returns a DataFrame representation of the data.
        
        If the internal DataFrame (`self._df`) is not set or its number of rows is less than the expected count,
        the method reloads the DataFrame from the underlying data source using memory mapping for efficiency.
        The DataFrame is constructed with the appropriate index columns based on the table's primary key columns.
        
        Returns:
            pandas.DataFrame: The DataFrame containing the data.
        """
        mmap_df = False
        if self._df is not None:
            if self._df.shape[0] < self.count:
                mmap_df = True
        else:
            mmap_df = True
            
        if mmap_df:
            indexcols = len(self.table.index.pkeycolumns)
            self._df = mmaparray2df(self[:], indexcols)            

        return self._df
                    
    def records2df(self, records):
        """
        Convert a list of records into a pandas DataFrame using the associated table's method.
        
        Parameters:
            records (list): A list of records to be converted.
        
        Returns:
            pandas.DataFrame: DataFrame representation of the input records.
        """
        return self.table.records2df(records)

    def df2records(self, df):
        """
        Convert a DataFrame into a list of records using the associated table's conversion method.
        
        Parameters:
            df (pandas.DataFrame): The DataFrame to be converted.
        
        Returns:
            list: A list of records derived from the DataFrame.
        """
        return self.table.df2records(df)

    def convert(self, new_records):
        """
        Converts fields of a structured NumPy array `new_records` to match the data types defined in `self.dtype`.
        
        For each column in `self.dtype.names` that exists in `new_records.dtype.names`, attempts to:
        - Replace byte-string representations of 'nan' with 0 for integer fields.
        - Replace byte-string 'True' with 1 and 'False' with 0 for integer fields.
        - Cast the column data to the corresponding dtype in `self.dtype`.
        
        If conversion fails for any column, logs an error message.
        
        Parameters:
            new_records (np.ndarray): Structured NumPy array with new data to convert.
        
        Returns:
            np.ndarray: Structured array with the same shape as `new_records` and dtype `self.dtype`,
                        containing the converted data.
        """
        rec = np.full((new_records.size,), fill_value=np.nan, dtype=self.dtype)
        for col in self.dtype.names:
            if col in new_records.dtype.names:
                try:
                    if np.issubdtype(self.dtype[col], np.integer):
                        nanidx = new_records[col] == b'nan'
                        new_records[col][nanidx] = 0
                        trueidx = new_records[col] == b'True'
                        new_records[col][trueidx] = 1
                        falseidx = new_records[col] == b'False'
                        new_records[col][falseidx] = 0
                    rec[col] = new_records[col].astype(self.dtype[col])
                except Exception as e:
                    Logger.log.error(f'SharedNumpy.convert(): Could not convert {col} on {self.table.relpath}: {str(e)}!')
        return rec

    def tags2df(self, dt, seltags, datetags=None):
        """
        Convert selected tags' records at a given datetime into two DataFrames.
        
        Parameters:
            dt (datetime-like): The datetime index to select records from.
            seltags (list of str): List of tags to extract data for.
            datetags (list of str, optional): Subset of tags whose 'value' should be converted from timestamps to pandas Timestamps.
        
        Returns:
            tuple:
                - df (pd.DataFrame): DataFrame indexed by the union of all record indices, containing the 'value' for each selected tag.
                - dfmtime (pd.DataFrame): DataFrame with the same index as df, containing the modification time ('mtime') for each selected tag.
        
        Notes:
            - If a tag is in datetags, its 'value' entries are converted from UNIX timestamps to pandas Timestamps.
            - Errors during data retrieval for any tag are logged but do not interrupt processing.
        """
        idx = pd.Index([])
        df = pd.DataFrame(columns=seltags)
        dfmtime = pd.DataFrame(columns=seltags)
        tag = seltags[0]        
        for tag in seltags:
            try:
                rec = self.loc[dt,tag]
                if len(rec)>0:            
                    values = self.records2df(rec).loc[dt].droplevel(0)
                    idx = idx.union(values.index)
                    df = df.reindex(idx)    
                    if not datetags is None:
                        if tag in datetags:
                            values['value'] = values['value'].apply(lambda x: pd.Timestamp.fromtimestamp(x))
                    df[tag] = values['value']
                    dfmtime[tag] = values['mtime']
            except Exception as e:
                Logger.log.error('Could not get %s %s!' % (tag,e))
        return df, dfmtime


    ############################## GETTERS / SETTERS ##############################    

    def __getitem__(self, key):
        """
        Retrieve item(s) from the object using the given key.
        
        If the object has a 'table' attribute and its size is less than 'recordssize',
        it remaps itself by calling 'rememmap()'. Then, it obtains a sliced array of
        elements up to 'count' using the superclass's __getitem__ method. If 'count'
        is greater than zero, it returns the item(s) at the specified key from this
        sliced array; otherwise, it returns the entire sliced array.
        
        If the object does not have a 'table' attribute, it directly returns the item(s)
        from the superclass's __getitem__ method using the provided key.
        
        Parameters:
            key (int, slice, or other): The index or slice to retrieve from the object.
        
        Returns:
            The item(s) corresponding to the key from the internal data structure.
        """
        if hasattr(self, 'table'):
            if self.size < self.recordssize:
                self = self.rememmap()

            arr = super().__getitem__(slice(0, self.count))  # slice arr
            if self.count > 0:
                return arr.__getitem__(key)
            else:
                return arr
        else:
            return super().__getitem__(key)
    
    def get_exists_remote(self):
        """
        Returns the result of the `get_exists_remote` method from the `table` attribute.
        
        This method acts as a proxy to check if a remote resource or entry exists by delegating the call to the `table` object's `get_exists_remote` method.
        
        Returns:
            The value returned by `self.table.get_exists_remote()`.
        """
        return self.table.get_exists_remote()

    @property
    def records(self):
        """
        Returns a slice of the underlying data from the start up to the current size.
        
        This property retrieves the first `size` elements by calling the superclass's
        `__getitem__` method with a slice from index 0 to `self.size`.
        
        Returns:
            A subset of the data containing elements from index 0 up to (but not including) `self.size`.
        """
        return super().__getitem__(slice(0, self.size))

    @property
    def count(self):
        return self.table.hdr['count']

    @count.setter
    def count(self, value):
        """
        Setter method for the 'count' property. Updates the 'count' value in the 'hdr' dictionary of the 'table' attribute.
        """
        self.table.hdr['count'] = value

    @property
    def recordssize(self):
        return self.table.hdr['recordssize']

    @recordssize.setter
    def recordssize(self, value):
        """
        Set the 'recordssize' field in the table header to the given value.
        
        Parameters:
            value (int): The new size of the records to be set in the header.
        """
        self.table.hdr['recordssize'] = value

    @property
    def mtime(self):
        return self.table.hdr['mtime']

    @mtime.setter
    def mtime(self, value):
        """
        Set the modification time in the table header.
        
        Parameters:
            value (int or float): The new modification time to be set.
        """
        self.table.hdr['mtime'] = value

    @property
    def minchgid(self):
        return self.table.hdr['minchgid']

    @minchgid.setter
    def minchgid(self, value):
        """
        Set the 'minchgid' header value to the given value or the current header value, whichever is smaller.
        
        Parameters:
            value (int): The new minimum change ID to set.
        
        This setter ensures that the 'minchgid' header in the table is never increased by limiting it to the minimum of the current and new values.
        """
        value = min(value, self.table.hdr['minchgid'])
        self.table.hdr['minchgid'] = value

    @property
    def index(self):
        return self.table.index

    @index.setter
    def index(self, value):
        """
        Set the index of the internal table to the specified value.
        
        Parameters:
            value: The new index to be assigned to the table.
        """
        self.table.index = value

    @property
    def pkey(self):
        return self.table.index.pkey

    @pkey.setter
    def pkey(self, value):
        """
        Set the primary key of the table's index.
        
        Parameters:
            value: The new primary key to be assigned to the table's index.
        """
        self.table.index.pkey = value

class _LocIndexer:
    """
    .loc indexer for SharedNumpy data structures, enabling advanced row- and column-wise selection.
    
    Supports selection by primary and secondary keys such as 'symbol', 'tag', and 'portfolio', including:
    - Access by string keys to filter rows matching the key.
    - Multi-key tuple indexing with support for date ranges, slices, and lists/arrays of string keys.
    - Column selection via single column names or lists of columns.
    - Handling of MultiIndex row selections.
    - Read-only enforcement on assignment attempts.
    
    This indexer is designed to work with tables that have a multi-level index with primary key columns,
    including special handling when the first primary key is a date.
    
    Raises:
        Exception: If an attempt is made to assign values via .loc (readonly).
    
    Returns:
        Subsets of the underlying data array or numpy arrays depending on the indexing operation.
    """
    def __init__(self, data):
        """
        Initializes the instance with the provided data.
        
        Parameters:
            data: The data to be stored in the instance.
        """
        self.data = data

    def __setitem__(self, key, value):
        """
        Prevent setting an item in the object, as it is read-only.
        
        Logs an error message and raises an Exception whenever an attempt is made to set an item using the subscript notation.
        
        Parameters:
            key: The key/index at which the value is attempted to be set.
            value: The value attempted to be assigned.
        
        Raises:
            Exception: Always raised to indicate that the object is read-only.
        """
        errmsg = "Error: loc is readonly!"
        Logger.log.error(errmsg)
        raise Exception(errmsg)

    def __getitem__(self, index):
         # --- Multi-secondary-key support  ---
        """
        Retrieve data using complex indexing with support for multi-secondary keys, slices, tuples, and string keys.
        
        Parameters:
            index (int, slice, str, tuple, or pd.Timestamp): The indexer used to select data. Supports:
                - Single integer or slice for row selection.
                - String keys corresponding to secondary indices like 'symbol', 'tag', or 'portfolio'.
                - Tuples combining row and column selectors, including multi-key tuples matching primary key columns.
                - pd.Timestamp or numpy datetime64 for date-based selection.
                - MultiIndex objects for advanced indexing.
        
        Returns:
            numpy.ndarray or structured array subset corresponding to the requested index.
        
        Behavior:
            - Supports fast access when indexing with tuples containing secondary keys.
            - Handles string keys by mapping them to appropriate secondary index lookup functions.
            - Applies date range filtering when 'date' is part of the primary key columns.
            - Supports boolean masking for multi-key tuple indexing.
            - Allows column selection via list, tuple, or single column name.
            - Handles MultiIndex and fallback cases gracefully.
            - Raises IndexError if a requested key is not found in certain cases.
        """
        pkeycolumns = getattr(self.data.table.index, "pkeycolumns", [])

        # Fast path for index = (row, col) tuple and [:, [sec_key,...]]
        if isinstance(index, tuple):
            row_index, col_index = self._parse_index(index)
            if (
                isinstance(row_index, (type(None), slice))
                and isinstance(col_index, (list, np.ndarray, pd.Index))
                and len(pkeycolumns) >= 2
                and pkeycolumns[1] in {'symbol', 'tag', 'portfolio'}
            ):
                idx_type = pkeycolumns[1]
                get_func = {
                    'symbol': self.data.get_symbol_loc,
                    'tag': self.data.get_tag_loc,
                    'portfolio': self.data.get_portfolio_loc
                }[idx_type]
                locs = np.concatenate([
                    get_func(val) for val in col_index
                ]) if len(col_index) else np.array([], dtype=int)
                locs = np.unique(locs)
                if 'date' in pkeycolumns:
                    # If date is the first primary key, sort by date
                    locs = np.array(locs, dtype=int)
                    locs = locs[np.argsort(self.data[locs]['date'])]
                    if isinstance(row_index, slice):
                        start = row_index.start
                        stop = row_index.stop
                        if start is None:
                            start = self.data.table.mindate
                        if stop is None:
                            stop = self.data.table.maxdate
                        locidx = (self.data[locs]['date'] >= start) & (self.data[locs]['date'] <= stop)
                        locs = locs[locidx]

                return self.data[locs] if len(locs) else np.array([], dtype=self.data.dtype)

        # Secondary-key-only (e.g. tbl.loc["AAPL"])
        if isinstance(index, str):
            if pkeycolumns:
                if pkeycolumns == ["symbol"]:
                    buffer = np.full((1,), dtype=self.data.dtype, fill_value=np.nan)
                    buffer['symbol'] = index
                    locs = self.data.get_loc(buffer)
                    if locs[0] != -1:
                        return self.data[locs[0]]                    
                    return np.array([], dtype=self.data.dtype)
                
                primary_string_keys = [k for k in pkeycolumns if k in STRING_FIELDS]
                if primary_string_keys:
                    key = primary_string_keys[0]
                    method = {
                        'symbol': self.data.get_symbol_loc,
                        'tag': self.data.get_tag_loc,
                        'portfolio': self.data.get_portfolio_loc,
                    }.get(key)
                    if method is not None:
                        if pkeycolumns[0] == "date":
                            # restrict to mindate... for date-ordered                            
                            key_locs = method(index)
                            key_locs = np.array(key_locs, dtype=int)
                            key_locs = key_locs[np.argsort(self.data[key_locs]['date'])]
                            return self.data[key_locs] if len(key_locs) else np.array([], dtype=self.data.dtype)
                        else:
                            # secondary-only
                            locs = method(index)
                            return self.data[locs] if len(locs) else np.array([], dtype=self.data.dtype)

        # Fully general multi-key/pkey access (including date, symbol, ... multi-columns)
        if (
            isinstance(index, tuple)
            and (1 <= len(index) <= len(pkeycolumns) + 1)
            and any(pkey == "date" for pkey in pkeycolumns)
        ):
            row_keys = index[:len(pkeycolumns)]
            col_selector = index[len(pkeycolumns):]
            col_selector = col_selector[0] if col_selector else None

            # Build a filter list - always use get_date_loc* for date!
            sort_by_date = False
            row_locs_list = []
            for val, pkey in zip(row_keys, pkeycolumns):
                if pkey == "date":
                    # --- Use date indexers for date portions ---
                    if isinstance(val, slice):
                        start = val.start
                        stop = val.stop
                        if not start and not stop:
                            sort_by_date = True
                            continue  # Empty slice, skip
                        else:
                            start = (np.datetime64(pd.Timestamp(start), 'ns') if start is not None 
                                    else self.data.table.mindate)
                            stop = (np.datetime64(pd.Timestamp(stop), 'ns') if stop is not None 
                                    else self.data.table.maxdate)
                            locs = self.data.get_date_loc_gte_lte(start, stop)
                    elif isinstance(val, (pd.Timestamp, np.datetime64, str)):
                        dt = pd.Timestamp(val) if isinstance(val, str) else val
                        dt = np.datetime64(dt, 'ns')
                        locs = self.data.get_date_loc(dt)
                    elif val is None:
                        locs = np.arange(self.data.count)
                    else:
                        locs = np.array([], dtype=int)                    
                    row_locs_list.append(locs)
                elif pkey in STRING_FIELDS:
                    # --- Use existing secondary key indexers ---
                    if isinstance(val, (list, tuple, np.ndarray, pd.Index)):
                        arr = np.concatenate([
                            getattr(self.data, f"get_{pkey}_loc")(v) for v in val
                        ]) if len(val) else np.array([], dtype=int)
                        arr = np.unique(arr)
                        row_locs_list.append(arr)
                    elif isinstance(val, (str, bytes)):
                        arr = getattr(self.data, f"get_{pkey}_loc")(val)
                        row_locs_list.append(arr)
                    elif val is None:
                        continue
                    else:
                        continue
                else:
                    # For classic non-string non-date fields, fall back to boolean masking (rare)
                    # This can be optimized only if you add an integer-index.
                    # For now, do standard comparison on all records:
                    records = self.data[:self.data.count]
                    if val is not None:
                        mask = (records[pkey] == val)
                        arr = np.flatnonzero(mask)
                        row_locs_list.append(arr)
                        
            # Intersect all location arrays, preserving order by the first.
            if row_locs_list:
                result_locs = row_locs_list[0]
                for other in row_locs_list[1:]:
                    result_locs = np.intersect1d(result_locs, other, assume_unique=True)
            else:
                result_locs = np.arange(self.data.count)                

            if sort_by_date and len(result_locs) > 0:
                # If we are sorting by date, we need to sort the result_locs by the date column
                result_locs = np.array(result_locs, dtype=int)
                result_locs = result_locs[np.argsort(self.data[result_locs]['date'])]

            selected = self.data[result_locs]
            # Robust column selection: list/tuple/Index or single column
            if col_selector is not None:
                if isinstance(col_selector, (list, tuple, pd.Index)):
                    return selected[list(col_selector)]
                else:
                    return selected[col_selector]
            else:
                return selected
                

        # MultiIndex rows
        row_index, col_index = self._parse_index(index)
        if isinstance(row_index, pd.MultiIndex):
            return self._multiindex_locs(row_index, col_index)

        # Tuple as (slice/Timestamp/int, key)
        if isinstance(row_index, tuple):
            row_part, key_part = row_index
            if isinstance(row_part, slice) and isinstance(key_part, str):
                start, stop, step = self._slice_to_bounds(row_part)
                locs = self._secondary_index_locs(row_key=key_part)
                if locs.size:
                    result = locs[(locs >= start) & (locs < stop)]
                    return self.data[result]
                else:
                    return np.array([], dtype=self.data.dtype)
            elif row_part is None:
                return self.data[..., col_index]
            else:
                raise NotImplementedError("Tuple with this signature in .loc not handled.")

        # Integer row index
        if isinstance(row_index, int):
            if isinstance(col_index, str) and col_index not in self.data.dtype.names:
                locs = self._secondary_index_locs(row_key=col_index)
                if locs.size:
                    return self.data[locs[row_index % len(locs)]]
                else:
                    raise IndexError(f"No entry for key '{col_index}'")
            return self.data[row_index][col_index]

        # Timestamp row index (date lookup)
        if isinstance(row_index, pd.Timestamp) or np.issubdtype(type(row_index), np.datetime64):
            row_index = np.datetime64(row_index, 'ns')
            locs = self.data.get_date_loc(row_index)
            if not isinstance(locs, np.ndarray):
                locs = np.array(locs)
            if isinstance(col_index, str) and col_index not in self.data.dtype.names:
                key_locs = self._secondary_index_locs(row_key=col_index)
                if key_locs.size and locs.size:
                    result = np.intersect1d(locs, key_locs, assume_unique=True)
                    return self.data[result]
                return np.array([], dtype=self.data.dtype)
            if isinstance(col_index, pd.Index):
                idxname = self.data.table.index.pkeycolumns[1]
                all_locs = []
                for key in col_index:
                    sec_locs = self._secondary_index_locs(row_key=key)
                    all_locs.extend(np.intersect1d(locs, sec_locs, assume_unique=True))
                return self.data[np.sort(np.unique(all_locs))]
            return self.data[locs][col_index] if locs.size else np.array([], dtype=self.data.dtype)

        # Fallback
        return self.data[row_index][col_index]

    def _parse_index(self, index):
        """
        Parses the given index used in .loc[] calls and returns a tuple of (row_index, col_index).
        
        Handles various types of indices including tuples, MultiIndex, slices, and strings,
        providing appropriate defaults for missing row or column indices.
        
        Parameters:
            index: The index used in a .loc[] call, which can be a tuple, MultiIndex, slice, string, or other types.
        
        Returns:
            tuple: A tuple containing (row_index, col_index), where each can be an index, slice, or None.
        """
        if isinstance(index, tuple):
            if len(index) == 2:
                return index
            elif len(index) == 1:
                return index[0], slice(None)
        elif isinstance(index, pd.MultiIndex):
            return index, slice(None)
        elif isinstance(index, slice):
            return index, slice(None)
        elif isinstance(index, str):
            return None, index
        return index, slice(None)

    def _slice_to_bounds(self, s: slice):
        """
        Convert a slice object with possible timestamp bounds into integer index bounds.
        
        Parameters:
            s (slice): A slice object where start and stop can be integers, None, or pd.Timestamp.
        
        Returns:
            tuple: A tuple (start, stop, step) where start and stop are integer indices corresponding
                   to the slice bounds, and step is the slice step (defaulting to 1 if not specified).
        
        Notes:
            - If start or stop is None, they default to 0 and the length of the data, respectively.
            - If start or stop is a pd.Timestamp, it is converted to the corresponding integer index
              using the data's date location method.
        """
        def bound(val, fallback):
            """
            Returns a bounded value based on the input `val`. If `val` is `None`, returns the provided `fallback`. If `val` is a `pandas.Timestamp`, attempts to locate its position in `self.data` using `get_date_loc` and returns the first matching index if found; otherwise, returns `fallback`. For all other types, returns `val` unchanged.
            """
            if val is None:
                return fallback
            if isinstance(val, pd.Timestamp):
                arr = self.data.get_date_loc(np.datetime64(val, 'ns'))
                return arr[0] if len(arr) > 0 else fallback
            return val
        start = bound(s.start, 0)
        stop = bound(s.stop, self.data.count)
        step = s.step if s.step is not None else 1
        return start, stop, step

    def _secondary_index_locs(self, row_key: str):
        """
        Retrieve the indices corresponding to a secondary key type (symbol, tag, or portfolio) for a given row key.
        
        This method checks the secondary key type from the table's primary key columns and uses the appropriate
        lookup function to find the indices associated with the provided row key. If the secondary key type is
        not recognized or there are insufficient primary key columns, it returns an empty integer array.
        
        Parameters:
            row_key (str): The key value to look up in the secondary index.
        
        Returns:
            np.ndarray: An array of integer indices corresponding to the row_key for the secondary key type.
            Returns an empty array if the secondary key type is not supported or not present.
        """
        pkeycolumns = getattr(self.data.table.index, 'pkeycolumns', [])
        if len(pkeycolumns) < 2:
            return np.array([], dtype=int)
        idx_type = pkeycolumns[1]
        get_func = {
            'symbol': self.data.get_symbol_loc,
            'tag': self.data.get_tag_loc,
            'portfolio': self.data.get_portfolio_loc,
        }.get(idx_type)
        if get_func is None:
            return np.array([], dtype=int)
        out = get_func(row_key)
        if not isinstance(out, np.ndarray):
            out = np.array(out, dtype=int)
        return out

    def _multiindex_locs(self, row_index: pd.MultiIndex, col_index):
        """
        Retrieve data locations for specified MultiIndex rows and column index.
        
        Parameters:
            row_index (pd.MultiIndex): MultiIndex object specifying the rows to locate.
            col_index: Column index or label(s) to select from the located rows.
        
        Returns:
            Selected data corresponding to the provided MultiIndex rows and column index.
        
        This method converts the MultiIndex rows into a structured numpy array with appropriate dtypes,
        finds their locations within the underlying data, filters out invalid locations, and returns
        the data at those locations for the specified columns.
        """
        dtype = np.dtype([(x, row_index.get_level_values(x).dtype) for x in row_index.names])
        record_keys = np.array([tuple(x) for x in row_index.values], dtype=dtype)
        record_keys = self.data.convert(record_keys)
        locs = self.data.get_loc(record_keys)
        locs = np.array(locs)
        locs = locs[locs >= 0]
        return self.data[locs][col_index]