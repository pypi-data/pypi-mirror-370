import json
import bson
from bson import json_util
from bson.objectid import ObjectId
import requests
import os
import pandas as pd
import numpy as np
import time
import lz4.frame
import lz4.frame as lz4f
import math
import datetime
import os
import logging
import threading
from tqdm import tqdm


from SharedData.IO.SyncTable import SyncTable
from SharedData.Logger import Logger
from SharedData.Database import *

MAX_UPLOAD_SIZE_BYTES = int(20*1024*1024)

class ClientAPI:

    """
    '''
    ClientAPI provides a comprehensive interface for interacting with a remote data service via HTTP API calls. It supports operations for retrieving, publishing, subscribing, and patching tabular and collection-based data, with built-in handling for compression, pagination, and data serialization.
    
    Key functionalities include:
    - raise_for_status: Raises exceptions for HTTP client and server errors with detailed messages.
    - subscribe_table_thread: Continuously subscribes to updates on a specified table, decompressing and merging incoming data.
    - publish_table_thread: Continuously publishes local table updates to the remote API, respecting bandwidth and rate limits.
    - records2df / df2records: Convert between numpy structured arrays and pandas DataFrames, handling encoding and datetime conversions.
    - get_table / post_table: Retrieve and post tabular data with support for pagination, compression, and metadata handling.
    - serialize / is_empty: Recursively serialize Python objects to JSON-compatible structures, omitting empty or sentinel values.
    - flatten_dict / unflatten_dict: Utilities to flatten nested dictionaries into single-level dicts with compound keys and vice versa.
    - documents2df / df2documents: Convert between lists of documents (dicts) and pandas DataFrames, with optional flattening and empty field removal.
    - get_collection / post_collection / patch
    """
    @staticmethod
    def raise_for_status(response, quiet=False):
        """
        Checks the HTTP response status code and raises an exception for client or server errors.
        Prints detailed error diagnostics only if an error occurs and response body is not JSON.
        """
        status = response.status_code
        url = response.url

        if 400 <= status < 600:
            # Try to get a JSON error message, fallback to plain text, headers, etc.
            if 'Error-Message' in response.headers:
                error_message = response.headers['Error-Message']
                error_message = f"{error_message}\nError {status} for URL: {url}"
                try:
                    Logger.log.error(error_message)
                except:
                    pass
                raise Exception(error_message)
            
            error_details = []
            error_details.append(f"Status: {status}")
            error_details.append(f"Reason: {response.reason}")
            error_details.append(f"URL: {url}")
            error_details.append(f"Headers: {dict(response.headers)}")
            body = response.text.strip()
            if body:
                error_details.append(f"Body: {body}")
            else:
                error_details.append("Body: <empty>")                
            error_msg = "\n".join(error_details)

            if 400 <= status < 500:                
                errmsg = f"{status} Client Error: {error_msg} for url: {url}"                
                try:
                    if not quiet:
                        Logger.log.error(errmsg)
                except:
                    pass
                raise Exception(errmsg)
            else:
                errmsg = f"{status} Server Error: {error_msg} for url: {url}"
                try:
                    if not quiet:
                        Logger.log.error(errmsg)
                except:
                    pass
                raise Exception(errmsg)                
        # Else success: do nothing
        
    @staticmethod
    def records2df(records, pkey):
        """
        Convert a list of record dictionaries into a pandas DataFrame with a specified primary key index.
        
        Parameters:
            records (list of dict): List of records where each record is a dictionary representing a row.
            pkey (str or list): Column name(s) to set as the DataFrame index.
        
        Returns:
            pandas.DataFrame: DataFrame constructed from the records with the specified index set.
            Object and byte string columns are decoded to UTF-8 strings where possible.
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
        df = df.set_index(pkey)
        return df
    
    @staticmethod
    def df2records(df, pkeycolumns, recdtype=None):
        """
        Convert a pandas DataFrame into a numpy structured array (records) with optional custom record dtype.
        
        Parameters:
            df (pandas.DataFrame): The input DataFrame to convert.
            pkeycolumns (list of str): List of column names that must match the DataFrame's index names in order.
            recdtype (numpy.dtype or None): Optional numpy dtype for the output structured array. If None, dtype is inferred.
        
        Returns:
            numpy.ndarray: A numpy structured array representing the DataFrame records.
        
        Raises:
            Exception: If the DataFrame's index names do not match pkeycolumns.
            Exception: If conversion to binary format fails due to unsupported object types.
        
        Details:
        - Validates that the DataFrame's index names match the provided primary key columns.
        - Resets the DataFrame index before conversion.
        - Converts timezone-aware datetime columns to UTC naive datetime.
        - Converts object columns to UTF-8 encoded byte strings when recdtype is None.
        - When recdtype is provided, attempts to cast columns to the specified dtype, filling NaNs in integer columns with zero.
        - Logs errors encountered during type conversions but continues processing other columns.
        """
        check_pkey = True
        if len(pkeycolumns) == len(df.index.names):
            for k in range(len(pkeycolumns)):
                check_pkey = (check_pkey) & (
                    df.index.names[k] == pkeycolumns[k])
        else:
            check_pkey = False
        if not check_pkey:
            raise Exception('First columns must be %s!' % (pkeycolumns))
        
        if recdtype is None:
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
                    Logger.log.error(f'ClientAPI.df2records(): Could not convert {tag} : {str(e)}!')
                df[tag] = df[tag].astype('|S')
                
            rec = np.ascontiguousarray(df.to_records(index=False))
            type_descriptors = [field[1] for field in rec]
            if '|O' in type_descriptors:
                errmsg = 'ClientAPI.df2records(): Could not convert |O type to binary'
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
            
            dtypes = recdtype
            
            rec = np.full((df.shape[0],), fill_value=np.nan, dtype=dtypes)
            for col in dtypes.names:
                try:
                    if col in df.columns:
                        if pd.api.types.is_integer_dtype(dtypes[col])\
                            or pd.api.types.is_unsigned_integer_dtype(dtypes[col]):
                            df[col] = df[col].fillna(0)
                            
                        rec[col] = df[col].astype(dtypes[col])
                        
                except Exception as e:
                    Logger.log.error(f'Table.df2records(): Could not convert {col} : {str(e)}!')

            return rec

    @staticmethod
    def subscribe_table_thread(table, host, port,
            lookbacklines=1000, lookbackdate=None, snapshot=False,
            bandwidth=1e6, protocol='http'):

        """
        '''
        Subscribe to a data table and continuously fetch updates from a remote API endpoint.
        
        This static method establishes a subscription to a specified table on a remote server,
        retrieving historical data based on lookback parameters and then continuously polling
        for new records. Data is fetched in compressed form, decompressed, and integrated into
        the local table's records, either by upserting or extending depending on the table's index.
        
        Parameters:
            table (object): The table object containing metadata and records to update.
            host (str): The hostname or IP address of the API server.
            port (int): The port number of the API server.
            lookbacklines (int, optional): Number of past records to retrieve initially. Default is 1000.
            lookbackdate (str or datetime, optional): Specific date to start lookback from. Overrides lookbacklines if provided.
            snapshot (bool, optional): Whether to request a snapshot of the current data state. Default is False.
            bandwidth (float, optional): Bandwidth limit parameter for the API request. Default is 1e6.
            protocol (str, optional): Protocol to use for the API request ('http' or 'https'). Default is 'http'.
        
        Behavior:
            - Constructs the API URL based
        """
        apiurl = f"{protocol}://{host}:{port}"
        
        records = table.records
        
        params = {                    
            'token': os.environ['SHAREDDATA_TOKEN'],            
        }

        tablename = table.tablename
        tablesubfolder = None
        if '/' in table.tablename:
            tablename = table.tablename.split('/')[0]
            tablesubfolder = table.tablename.split('/')[1] 

        url = apiurl+f"/api/subscribe/table/{table.database}/{table.period}/{table.source}/{tablename}"
        
        lookbackid = records.count - lookbacklines
        if tablesubfolder:
            params['tablesubfolder'] = tablesubfolder        
        if lookbacklines:
            params['lookbacklines'] = lookbacklines
        if lookbackdate:
            params['lookbackdate'] = lookbackdate
            lookbackdate = pd.Timestamp(lookbackdate)            
            loc = records.get_date_loc_gte(lookbackdate)
            if len(loc)>0:
                lookbackid = min(loc)
        if bandwidth:
            params['bandwidth'] = bandwidth
                
        hasindex = records.table.hasindex           
        lastmtime = pd.Timestamp('1970-01-01')
        if hasindex:
            lastmtime = np.max(records[lookbackid:]['mtime'])
            lastmtime = pd.Timestamp(np.datetime64(lastmtime))
        while True:
            try:
                params['page'] = 1
                if hasindex:
                    params['mtime'] = lastmtime
                params['count'] = records.count
                params['snapshot'] = snapshot
                snapshot = False

                response = requests.get(url, params=params)
                if response.status_code != 200:
                    if response.status_code == 204:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception(response.status_code, response.text)
                
                data = lz4.frame.decompress(response.content)
                buffer = bytearray()
                buffer.extend(data)
                if len(buffer) >= records.itemsize:
                    # Determine how many complete records are in the buffer
                    num_records = len(buffer) // records.itemsize
                    # Take the first num_records worth of bytes
                    record_data = buffer[:num_records *
                                                records.itemsize]
                    # And remove them from the buffer
                    del buffer[:num_records *
                                        records.itemsize]
                    # Convert the bytes to a NumPy array of records
                    rec = np.frombuffer(
                        record_data, dtype=records.dtype)
                    if hasindex:
                        recmtime = pd.Timestamp(np.max(rec['mtime']))
                        if recmtime > lastmtime:
                            lastmtime = recmtime
                        
                    if records.table.hasindex:
                        # Upsert all records at once
                        records.upsert(rec)
                    else:
                        # Extend all records at once
                        records.extend(rec)

                pages = int(response.headers['Content-Pages'])
                if pages > 1:
                    # paginated response
                    for i in range(2, pages+1):
                        params['page'] = i                        
                        response = requests.get(url, params=params)
                        if response.status_code != 200:
                            raise Exception(response.status_code, response.text)
                        data = lz4.frame.decompress(response.content)
                        buffer = bytearray()
                        buffer.extend(data)
                        if len(buffer) >= records.itemsize:
                            # Determine how many complete records are in the buffer
                            num_records = len(buffer) // records.itemsize
                            # Take the first num_records worth of bytes
                            record_data = buffer[:num_records *
                                                        records.itemsize]
                            # And remove them from the buffer
                            del buffer[:num_records *
                                                records.itemsize]
                            # Convert the bytes to a NumPy array of records
                            rec = np.frombuffer(
                                record_data, dtype=records.dtype)
                            if hasindex:
                                recmtime = pd.Timestamp(np.max(rec['mtime']))
                                if recmtime > lastmtime:
                                    lastmtime = recmtime
                                
                            if records.table.hasindex:
                                # Upsert all records at once
                                records.upsert(rec)
                            else:
                                # Extend all records at once
                                records.extend(rec)
                        time.sleep(0.5)

                time.sleep(1)

            except Exception as e:
                msg = 'Retrying API subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    def publish_table_thread(table, host, port, lookbacklines, 
        lookbackdate, snapshot,bandwidth, protocol='http', max_requests_per_minute=100):

        """
        '''
        Continuously publishes data from a given table to a remote server via HTTP(S) API.
        
        This static method repeatedly checks for new records in the specified table and uploads them
        to a remote endpoint, handling rate limiting, compression, and retries on failure.
        
        Parameters:
            table (object): The table object containing records and metadata to publish.
            host (str): The hostname or IP address of the remote server.
            port (int or None): The port number of the remote server; if None, default protocol port is used.
            lookbacklines (int or None): Number of previous lines to include in the publish request.
            lookbackdate (str or pandas.Timestamp or None): Date string or timestamp to look back from.
            snapshot (bool): Flag indicating whether to publish a snapshot of the table.
            bandwidth (float or None): Maximum bandwidth in bytes per second for data transfer.
            protocol (str): Protocol to use for the connection ('http' or 'https'). Default is 'http'.
            max_requests_per_minute (int): Maximum number of API requests allowed per minute. Default is 100.
        
        Behavior:
            - Constructs the API URL based on the host, port, and protocol.
            - Retrieves remote table metadata (modification time and
        """
        if port is None:
            apiurl = f"{protocol}://{host}"
        else:
            apiurl = f"{protocol}://{host}:{port}"
        
        while True:
            try:
                records = table.records
                
                params = {                    
                    'token': os.environ['SHAREDDATA_TOKEN'],            
                }

                tablename = table.tablename
                tablesubfolder = None
                if '/' in table.tablename:
                    tablename = table.tablename.split('/')[0]
                    tablesubfolder = table.tablename.split('/')[1] 

                url = apiurl+f"/api/publish/table/{table.database}/{table.period}/{table.source}/{tablename}"
                                
                if tablesubfolder:
                    params['tablesubfolder'] = tablesubfolder        
                if lookbacklines:
                    params['lookbacklines'] = lookbacklines
                if lookbackdate:
                    params['lookbackdate'] = lookbackdate
                    lookbackdate = pd.Timestamp(lookbackdate)            
                if bandwidth:
                    params['bandwidth'] = bandwidth
                
                
                # ask for the remote table mtime and count

                response = requests.get(url, params=params)

                if response.status_code != 200:
                    raise Exception(response.status_code, response.text)

                response = response.json()
                remotemtime = None
                if 'mtime' in response:
                    remotemtime = pd.Timestamp(response['mtime']).replace(tzinfo=None)
                remotecount = response['count']

                client = {}
                client.update(params)
                if 'mtime' in response:
                    client['mtime'] = remotemtime.timestamp()
                client['count'] = remotecount
                client = SyncTable.init_client(client,table)

                while True:
                    try:
                        time.sleep(60/max_requests_per_minute)
                        
                        client, ids2send = SyncTable.get_ids2send(client)
                        if len(ids2send) == 0:
                            time.sleep(0.001)                            
                        else:
                            rows2send = len(ids2send)
                            sentrows = 0
                            msgsize = min(client['maxrows'], rows2send)
                            bandwidth = client['bandwidth']
                            tini = time.time_ns()
                            bytessent = 0
                            while sentrows < rows2send:
                                t = time.time_ns()
                                message = records[ids2send[sentrows:sentrows +
                                                        msgsize]].tobytes()
                                compressed = lz4f.compress(message)
                                msgbytes = len(compressed)
                                bytessent+=msgbytes                        
                                msgmintime = msgbytes/bandwidth                        
                                
                                # create a post request
                                response = requests.post(url, params=params, data=compressed)
                                if response.status_code != 200:
                                    raise Exception('Failed to publish data remote!=200 !')

                                sentrows += msgsize
                                msgtime = (time.time_ns()-t)*1e-9
                                ratelimtime = max(msgmintime-msgtime, 0)
                                if ratelimtime > 0:
                                    time.sleep(ratelimtime)

                            totalsize = (sentrows*records.itemsize)/1e6
                            totaltime = (time.time_ns()-tini)*1e-9
                            if totaltime > 0:
                                transfer_rate = totalsize/totaltime
                            else:
                                transfer_rate = 0
                            client['transfer_rate'] = transfer_rate
                            client['upload'] += msgbytes
                        
                    except:
                        break

            except Exception as e:
                msg = 'Retrying API publish %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                        table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    def list_tables(
        keyword: str = '', 
        user: str = 'master',
        endpoint: str = None, 
        token: str = None,
        output_dataframe: bool = True
    ):
        """
        List available tables from the server via /api/tables endpoint.

        Parameters:
            keyword (str): Optional filter by keyword.
            user (str): User name, default 'master'.
            endpoint (str, optional): API endpoint, default uses SHAREDDATA_ENDPOINT env.
            token (str, optional): API token; defaults to SHAREDDATA_TOKEN env.
            output_dataframe (bool): Return as DataFrame if True (default), else as list-of-dicts.

        Returns:
            pandas.DataFrame or list: Table info.
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint
        url += '/api/tables'
        params = {'keyword': keyword, 'user': user}
        
        if token is not None:
            params['token'] = token
        else:
            params['token'] = os.environ.get('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        headers = {'Accept': 'application/json'}

        response = requests.get(url, params=params, headers=headers)
        ClientAPI.raise_for_status(response)

        if response.status_code == 204:
            if output_dataframe:
                return pd.DataFrame()
            else:
                return []

        result = response.json()
        if output_dataframe:
            return pd.DataFrame(result) if isinstance(result, list) else pd.DataFrame(result.get('tables', []))
        return result

    @staticmethod
    def head_table(database, period, source, tablename, 
            endpoint=None, token=None, user=None):
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route
        
        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')
        
        if not user is None:
            params['user'] = user
        
        response = requests.head(url, params=params)
        ClientAPI.raise_for_status(response)                        
        return response.headers

    @staticmethod
    def get_table(database, period, source, tablename, 
            endpoint=None,
            startdate=None, enddate=None, 
            symbols=None, portfolios=None, tags=None, query=None,
            columns=None, output_dataframe=True,
            page=None, per_page=None, load_all_pages=False,
            token=None, user=None):
            
        """
        '''
        Fetches tabular data from a specified API endpoint, supporting pagination, filtering, and output formatting.
        
        Parameters:
            database (str): The database name to query.
            period (str): The period or timeframe for the data.
            source (str): The data source identifier.
            tablename (str): The name of the table to retrieve, optionally including a subfolder separated by '/'.
            endpoint (str, optional): Custom API endpoint URL. Defaults to environment variable 'SHAREDDATA_ENDPOINT' if not provided.
            startdate (str, optional): Filter data starting from this date (inclusive).
            enddate (str, optional): Filter data up to this date (inclusive).
            symbols (list or str, optional): Filter by one or more symbols.
            portfolios (list or str, optional): Filter by one or more portfolios.
            tags (list or str, optional): Filter by one or more tags.
            query (dict, optional): Additional query parameters as a dictionary, serialized to JSON.
            columns (list or str, optional): Specific columns to retrieve.
            output_dataframe (bool, optional): If True, returns a pandas DataFrame; otherwise returns a numpy structured array. Defaults to True.
            page (int, optional):
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route
        
        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if startdate:
            params['startdate'] = startdate
        if enddate:
            params['enddate'] = enddate
        if symbols:
            params['symbols'] = symbols
        if portfolios:
            params['portfolios'] = portfolios
        if tags:
            params['tags'] = tags
        if user:
            params['user'] = user
        if query:
            params['query'] = json.dumps(query)
        if per_page:
            params['per_page'] = per_page
        if page:
            params['page'] = page
        if columns:
            params['columns'] = columns
        
        params['format'] = 'bin'

        # Make the GET request
        # Request LZ4-encoded response
        headers = {
            'Accept-Encoding': 'lz4'
        }

        if load_all_pages:
            # Start with page 1 to get total pages from headers
            params['page'] = 1
            response = requests.get(url, params=params, headers=headers)
            ClientAPI.raise_for_status(response)
            
            if response.status_code == 204:
                return pd.DataFrame([])

            # Get total pages from headers
            total_pages = int(response.headers.get('Content-Pages', 1))
            
            # Process first page            
            bson_payload  = bson.BSON.decode(lz4f.decompress(response.content))
            pkey = bson_payload['pkey']
            dtype = np.dtype(list(zip(bson_payload['names'], bson_payload['formats'])))
            all_recs = np.frombuffer(bson_payload['data'], dtype=dtype)

            # Fetch remaining pages if there are more
            page_iter = (
                tqdm(range(2, total_pages + 1), desc="Downloading data:") if total_pages > 3
                else range(2, total_pages + 1)
            )
            for current_page in page_iter:
                params['page'] = current_page
                response = requests.get(url, params=params, headers=headers)
                ClientAPI.raise_for_status(response)
                
                if response.status_code != 204:
                    bson_payload  = bson.BSON.decode(lz4f.decompress(response.content))            
                    dtype = np.dtype(list(zip(bson_payload['names'], bson_payload['formats'])))
                    page_recs = np.frombuffer(bson_payload['data'], dtype=dtype)                                        
                    all_recs = np.concatenate((all_recs, page_recs))

            if not output_dataframe:
                return all_recs
                    
            # Convert combined records to DataFrame
            df = ClientAPI.records2df(all_recs, pkey)            
            return df.sort_index()
        else:
            # Original single page request logic
            response = requests.get(url, params=params, headers=headers)
            ClientAPI.raise_for_status(response)

            if response.status_code == 204: 
                return pd.DataFrame([])
                        
            bson_payload  = bson.BSON.decode(lz4f.decompress(response.content))
            pkey = bson_payload['pkey']
            dtype = np.dtype(list(zip(bson_payload['names'], bson_payload['formats'])))
            recs = np.frombuffer(bson_payload['data'], dtype=dtype)
            
            if not output_dataframe:
                return recs
                    
            # Convert to DataFrame
            df = ClientAPI.records2df(recs, pkey)
            return df.sort_index()

    @staticmethod
    def post_table(database, period, source, tablename, 
            endpoint=None, 
            names = None, formats=None, size=None,
            value=None, overwrite=False, hasindex=True,
            token=None, user=None):
            
        """
        '''
        Post data to a specified table in a remote database via an HTTP POST request.
        
        Parameters:
            database (str): The target database name.
            period (str): The period identifier for the data.
            source (str): The data source identifier.
            tablename (str): The target table name, optionally including a subfolder separated by '/'.
            endpoint (str, optional): The base URL endpoint for the API. Defaults to the environment variable 'SHAREDDATA_ENDPOINT'.
            names (list of str, optional): List of field names for the data schema.
            formats (list of str, optional): List of data formats corresponding to the field names.
            size (int, optional): Size parameter for the data.
            value (pandas.DataFrame or numpy.ndarray, optional): The data to post. If a DataFrame is provided, it is converted to a structured array.
            overwrite (bool, optional): Whether to overwrite existing data. Defaults to False.
            token (str, optional): Authentication token. If not provided, fetched from environment variable 'SHAREDDATA_TOKEN'.
            user (str, optional): User identifier for the request.
        
        Returns:
            int: HTTP status code of the POST request response.
        
        Raises:
            Exception: If
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint
        
        headers = {}
        headers['Content-Encoding'] = 'lz4'
        headers['Content-Type'] = 'application/octet-stream'        
        
        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route
        
        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')
        
        if user:
            params['user'] = user
        if overwrite:
            params['overwrite'] = 'True' if overwrite else 'False' 
        if hasindex:
            params['hasindex'] = 'True' if hasindex else 'False'
                
        json_payload = {}
        json_payload['pkey'] = json.dumps(DATABASE_PKEYS[database])
        if names:
            json_payload['names'] = names
        if formats:
            json_payload['formats'] = formats
        if size:
            json_payload['size'] = int(size)
                        
        if not value is None:
            if isinstance(value, pd.DataFrame):
                if names and formats:
                    hdrdtype = np.dtype({'names': names, 'formats': formats})
                    value = ClientAPI.df2records(value,DATABASE_PKEYS[database],recdtype=hdrdtype)
                else:
                    value = ClientAPI.df2records(value,DATABASE_PKEYS[database])
            elif isinstance(value, np.ndarray):
                pass
            else:
                raise Exception('value must be a pandas DataFrame')
                        
            json_payload['meta_names'] = list(value.dtype.names)
            json_payload['meta_formats'] = [value.dtype.fields[name][0].str 
                                            for name in json_payload['meta_names']]
            
            maxrows = int(MAX_UPLOAD_SIZE_BYTES / value.itemsize)
            if value.shape[0] > maxrows:
                nchunks = int(np.ceil(value.shape[0] / maxrows))
                chunk_iter = (
                    tqdm(range(nchunks), desc='Uploading data') if nchunks > 2
                    else range(nchunks)
                )
                for ichunk in chunk_iter:
                    chunk = value[ichunk*maxrows:(ichunk+1)*maxrows]
                    json_payload['data'] = chunk.tobytes()
                    trials = 0
                    while trials < 3:
                        if ClientAPI.try_post(url, headers, params, json_payload):
                            break
                        trials += 1
                        if trials == 3:
                            raise Exception('Failed to upload data after 3 attempts')
                return 201
            else:                            
                json_payload['data'] = value.tobytes()

        trials = 0
        while trials < 3:
            if ClientAPI.try_post(url, headers, params, json_payload):
                break
            trials += 1
            if trials == 3:
                raise Exception('Failed to upload data after 3 attempts')
        return 201
    
    @staticmethod
    def try_post(url, headers, params, json_payload=None, data=None,timeout=120):
        try:
            if json_payload is not None:
                bson_payload = bson.encode(json_payload)
                data = lz4f.compress(bson_payload)

            response = requests.post(
                url, 
                headers=headers, 
                params=params, 
                data=data, 
                timeout=timeout
            )
            ClientAPI.raise_for_status(response, quiet=True)
            return True
        except Exception as e:
            Logger.log.error(f'try_post:{str(e)}')
            return False

    @staticmethod
    def delete_table(database, period, source, tablename, 
            endpoint=None,token=None, user=None):
        
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')
        
        if not user is None:
            params['user'] = user
        
        response = requests.delete(url,params=params)
        ClientAPI.raise_for_status(response)
        return response.status_code

    @staticmethod
    def serialize(obj, iso_dates=False):
        """
        Recursively serialize a Python object into nested dictionaries and lists,
        omitting values considered "empty" as defined by the is_empty() method.
        
        Supports special handling for pandas Timestamps, datetime objects, dictionaries,
        pandas DataFrames, lists, tuples, sets, objects with __dict__, and ObjectId instances.
        
        Parameters:
            obj (any): The Python object to serialize.
            iso_dates (bool): If True, convert datetime and Timestamp objects to ISO 8601 strings.
        
        Returns:
            dict, list, str, or None: A serialized representation of the input object with empty values removed,
            or None if the object or its contents are empty.
        """

        # 1) Special-case Timestamps so they don't get recursed:
        if isinstance(obj, pd.Timestamp):
            # Return None if it's considered 'empty' (e.g. NaT),
            # otherwise treat it as a scalar (string, raw Timestamps, etc.)
            if iso_dates:
                return None if ClientAPI.is_empty(obj) else obj.isoformat()
            else:
                return None if ClientAPI.is_empty(obj) else obj

        # # Handle Python datetime.datetime objects
        if isinstance(obj, datetime.datetime):
            if iso_dates:        
                return None if ClientAPI.is_empty(obj) else obj.isoformat()
            else:
                return None if ClientAPI.is_empty(obj) else obj
        
        # 2) Dict
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                # Recurse
                serialized_v = ClientAPI.serialize(v, iso_dates)
                # Only keep non-empty values
                if serialized_v is not None and not ClientAPI.is_empty(serialized_v):
                    new_dict[k] = serialized_v

            # If the resulting dict is empty, return None instead of {}
            return new_dict if new_dict else None

        # 3) DataFrame
        if isinstance(obj, pd.DataFrame):
            records = obj.to_dict(orient='records')
            # Each record is a dict, so we re-serialize it
            return [
                r for r in (ClientAPI.serialize(rec, iso_dates) for rec in records)
                if r is not None and not ClientAPI.is_empty(r)
            ]

        # 4) List/tuple/set
        if isinstance(obj, (list, tuple, set)):
            new_list = [
                ClientAPI.serialize(item, iso_dates)
                for item in obj
                if not ClientAPI.is_empty(item)
            ]
            # If the list ends up empty, return None
            return new_list if new_list else None

        # 5) For other objects with __dict__, treat them like a dict
        if hasattr(obj, "__dict__"):
            return ClientAPI.serialize(vars(obj), iso_dates)
        
        # 6) Convert ObjectId to string for JSON serialization
        if isinstance(obj, ObjectId):
            return str(obj)

        # 7) Otherwise, just return the raw value if it's not "empty"
        return obj if not ClientAPI.is_empty(obj) else None

    EMPTY_VALUES = {
        str: ["", "1.7976931348623157E308", "nan", "NaN",],
        int: [2147483647],
        float: [1.7976931348623157e+308, np.nan, np.inf, -np.inf],
        datetime.datetime: [datetime.datetime(1, 1, 1, 0, 0)],
        # pd.Timestamp: [pd.Timestamp("1970-01-01 00:00:00")],
        pd.NaT: [pd.NaT],
        pd.Timedelta: [pd.Timedelta(0)],
        pd.Interval: [pd.Interval(0, 0)],
        type(None): [None],
        bool: [False],
    }

    @staticmethod
    def is_empty(value):
        """
        Determine if the given value should be considered empty or a sentinel.
        
        This method checks for various conditions that signify emptiness, including:
        - Floating point NaN, infinity, zero, and maximum float values.
        - Pandas Timestamp objects that are NaT.
        - Values contained in predefined empty sets specific to their type.
        - Empty containers such as lists, tuples, sets, and dictionaries.
        - Pandas NaTType instances.
        
        Parameters:
            value (any): The value to check for emptiness.
        
        Returns:
            bool: True if the value is considered empty or a sentinel, False otherwise.
        """
        # Special handling for floats
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return True
            if value == 1.7976931348623157e+308:
                return True

        # If it's a Timestamp and is NaT, treat as empty
        if isinstance(value, pd.Timestamp):
            if pd.isna(value):  # True for pd.NaT
                return True

        # Check if value is in our known empty sets
        value_type = type(value)
        if value_type in ClientAPI.EMPTY_VALUES:
            if value in ClientAPI.EMPTY_VALUES[value_type]:
                return True

        # Empty containers
        if isinstance(value, (list, tuple, set)) and len(value) == 0:
            return True
        if isinstance(value, dict) and len(value) == 0:
            return True
        if isinstance(value, pd._libs.tslibs.nattype.NaTType):
            return True

        return False

    @staticmethod
    def flatten_dict(d, parent_key='', sep='->'):
        """
        Recursively flattens a nested dictionary by concatenating keys.
        
        Parameters:
            d (dict): The dictionary to flatten.
            parent_key (str): The base key string to prepend to keys (used in recursion).
            sep (str): The separator between concatenated keys.
        
        Returns:
            dict: A new dictionary with nested keys flattened into single-level keys joined by the separator.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ClientAPI.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def unflatten_dict(d, sep='->'):
        """
        Convert a flat dictionary with compound keys into a nested dictionary.
        
        Each key in the input dictionary `d` is split by the specified separator `sep` to create a hierarchy of nested dictionaries. The values are assigned to the innermost keys.
        
        Parameters:
            d (dict): The flat dictionary with compound keys.
            sep (str): The separator string used to split keys into nested levels. Default is '->'.
        
        Returns:
            dict: A nested dictionary constructed from the flat dictionary.
        """
        result = {}
        for key, value in d.items():
            parts = key.split(sep)
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                    current = current[part]

                else:
                    if not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]
            current[parts[-1]] = value
        return result
            
    @staticmethod
    def documents2df(documents, database, flatten=True, drop_empty=True, serialize=True):
        """
        Convert a list of document dictionaries into a pandas DataFrame with optional serialization, flattening, and cleaning.
        
        Parameters:
            documents (list): A list of document dictionaries to convert.
            database (str): The name of the database, used to determine primary key columns.
            flatten (bool, optional): If True, flatten nested dictionaries in each document. Default is True.
            drop_empty (bool, optional): If True, drop columns that contain only None values. Default is True.
            serialize (bool, optional): If True, serialize ObjectId and datetime objects in the documents. Default is True.
        
        Returns:
            pandas.DataFrame: A DataFrame representation of the documents with the primary key columns set as the index if present.
        """
        if len(documents) == 0:
            return pd.DataFrame()
        # Serialize ObjectId and datetime objects
        if serialize:
            documents = ClientAPI.serialize(documents)
        # Flatten each document
        if flatten:
            documents = [ClientAPI.flatten_dict(doc) for doc in documents]
        
        # Convert the list of dictionaries into a DataFrame 
        df = pd.DataFrame(documents)
        
        if drop_empty:
            # Remove columns with all None values
            df = df.dropna(axis=1, how='all')
        
        # Set primary key as index        
        pkey_columns = DATABASE_PKEYS[database]
        if all(col in df.columns for col in pkey_columns):
            df.set_index(pkey_columns, inplace=True)

        return df
    
    @staticmethod
    def df2documents(df, database, unflatten=True, drop_empty=True):
        """
        Convert a pandas DataFrame into a list of dictionary documents suitable for database insertion.
        
        Parameters:
            df (pandas.DataFrame): The DataFrame to convert.
            database (str): The target database name, used to validate primary key columns.
            unflatten (bool, optional): If True, unflatten nested keys in the documents. Defaults to True.
            drop_empty (bool, optional): If True, drop rows and columns that are completely empty and remove empty fields from documents. Defaults to True.
        
        Returns:
            list of dict: A list of documents representing the DataFrame rows, with cleaned and optionally unflattened fields.
        
        Raises:
            ValueError: If the DataFrame's initial columns do not match the expected primary key columns for the specified database.
        """
        if df.empty:
            return []
        # Retrieve the expected primary key columns for this database
        pkey_columns = DATABASE_PKEYS[database]
        # Convert index to columns
        df = df.reset_index()
        if len(df.columns) >= len(pkey_columns):
            for icol, col in enumerate(pkey_columns):
                if df.columns[icol]!=pkey_columns[icol]:
                    raise ValueError(f"df2documents:Expected primary key column {pkey_columns}!")


        # MongoDB does not allow '.' in field names, so replace them with spaces
        df.columns = [str(s).replace('.','') for s in df.columns]

        # Drop rows and columns with all None/NaN values
        if drop_empty:
            df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')

        # Convert DataFrame to list of dictionaries
        documents = df.to_dict(orient='records')

        if drop_empty:
            # Remove empty fields in the documents
            for doc in documents:
                keys_to_remove = [key for key, value in doc.items() if ClientAPI.is_empty(value)]
                for key in keys_to_remove:
                    del doc[key]

        # Unflatten the documents if needed
        if unflatten:
            documents = [ClientAPI.unflatten_dict(doc) for doc in documents]

        return documents
    
    @staticmethod
    def list_collections(
        keyword: str = '',
        user: str = 'master',
        endpoint: str = None,
        token: str = None,
        output_dataframe: bool = True
    ):
        """
        List available collections from the server via /api/collections endpoint.

        Parameters:
            keyword (str): Optional filter by keyword.
            user (str): User name, default 'master'.
            endpoint (str, optional): API endpoint, default uses SHAREDDATA_ENDPOINT env.
            token (str, optional): API token; defaults to SHAREDDATA_TOKEN env.
            output_dataframe (bool): Return as DataFrame if True (default), else as list-of-dicts.

        Returns:
            pandas.DataFrame or list: Collections info.
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint
        url += '/api/collections'
        params = {'keyword': keyword, 'user': user}
        
        if token is not None:
            params['token'] = token
        else:
            params['token'] = os.environ.get('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        headers = {'Accept': 'application/json'}

        response = requests.get(url, params=params, headers=headers)
        ClientAPI.raise_for_status(response)

        if response.status_code == 204:
            if output_dataframe:
                return pd.DataFrame()
            else:
                return []

        result = response.json()
        if output_dataframe:
            return pd.DataFrame(result) if isinstance(result, list) else pd.DataFrame(result.get('collections', []))
        return result

    @staticmethod
    def head_collection(database, period, source, tablename, 
                        endpoint=None, token=None, user=None):
        """
        Sends a HEAD request to the collection API endpoint
        and returns response headers with collection metadata.

        Parameters:
            database (str): Database name.
            period (str): Period name.
            source (str): Source name.
            tablename (str): Table/collection name, can include a subfolder separated by '/'.
            endpoint (str, optional): API endpoint base URL.
            token (str, optional): API token (default: SHAREDDATA_TOKEN env).
            user (str, optional): User for access control.

        Returns:
            dict: Response headers containing metadata such as field names and estimated document count.
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if token is not None:
            params['token'] = token
        else:
            params['token'] = os.environ.get('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user is not None:
            params['user'] = user

        response = requests.head(url, params=params)
        ClientAPI.raise_for_status(response)
        return response.headers

    @staticmethod
    def get_collection(database, period, source, tablename, 
                        endpoint=None, query=None, sort=None,columns=None, 
                        page=None, per_page=None,load_all_pages=False,
                        output_dataframe=True, 
                        token=None, user=None):
        
        """
        '''
        Retrieve a collection of data from a specified database, period, source, and table via an API endpoint.
        
        Parameters:
        - database (str): The name of the database to query.
        - period (str): The time period for the data.
        - source (str): The data source identifier.
        - tablename (str): The name of the table to retrieve data from. Can include a subfolder separated by '/'.
        - endpoint (str, optional): Custom API endpoint URL. Defaults to environment variable 'SHAREDDATA_ENDPOINT' if not provided.
        - query (dict, optional): A query filter to apply to the data.
        - sort (dict, optional): Sorting instructions for the data.
        - columns (list, optional): List of columns to retrieve.
        - page (int, optional): Page number for paginated results.
        - per_page (int, optional): Number of records per page.
        - load_all_pages (bool, optional): If True, fetches all pages of data by iterating through pagination. Defaults to False.
        - output_dataframe (bool, optional): If True, returns the data as a pandas DataFrame; otherwise returns raw data list. Defaults to True.
        - token (str, optional): Authentication token. If not provided, attempts to use
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None:
            params['token'] = token
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user:
            params['user'] = user
        if sort:
            params['sort'] = json_util.dumps(sort)
        if query:
            params['query'] = json_util.dumps(query)
        if columns:
            params['columns'] = json_util.dumps(columns)

        if page:
            params['page'] = page
        if per_page:
            params['per_page'] = per_page  
        
        params['format'] = 'bson'
        if load_all_pages:
            all_data = []
            current_page = 1
            pbar = tqdm(total=0, desc="Downloading data:")
            while True:
                
                if not per_page:
                    per_page = 50000

                params['page'] = current_page
                params['per_page'] = per_page
                
                # Make the API request for the current page
                response = requests.get(url, params=params)
                ClientAPI.raise_for_status(response)

                if response.status_code == 204:
                    break

                decompressed_content = lz4f.decompress(response.content)
                bson_data = bson.BSON(decompressed_content).decode()
                data = bson_data.get('data', [])
                
                if not data:
                    break

                all_data.extend(data)

                # If less data than per_page is returned, we have reached the last page
                if len(data) < per_page:
                    break
                
                current_page += 1
                pbar.update(1)
            
            if not output_dataframe:
                return all_data
            
            return ClientAPI.documents2df(all_data, database)

        else:

            response = requests.get(url, params=params)
            ClientAPI.raise_for_status(response)

            if response.status_code == 204: 
                if not output_dataframe:
                    return []
                else:
                    return pd.DataFrame()
            
            decompressed_content = lz4f.decompress(response.content)
            bson_data = bson.BSON(decompressed_content).decode()  # Decode BSON to a dictionary

            data = bson_data.get('data', [])
            if not output_dataframe:
                return data
            
            df = ClientAPI.documents2df(data,database)
            return df

    @staticmethod
    def post_collection(database, period, source, tablename, 
            endpoint=None, 
            value=None, 
            token=None, user=None, hasindex=True):
            
        """
        Post a collection of data to a specified API endpoint.
        
        Parameters:
            database (str): The name of the database to post to.
            period (str): The period identifier for the data.
            source (str): The source identifier of the data.
            tablename (str): The name of the table to post data to. Can include a subfolder separated by '/'.
            endpoint (str, optional): The base URL of the API endpoint. Defaults to the environment variable 'SHAREDDATA_ENDPOINT' if not provided.
            value (pd.DataFrame or any): The data to be posted. If a DataFrame, it will be serialized after resetting its index.
            token (str, optional): Authentication token. Defaults to the environment variable 'SHAREDDATA_TOKEN' if not provided.
            user (str, optional): User identifier to include in the request parameters.
            hasindex (bool, optional): Indicates if the data includes an index. Defaults to True.
        
        Returns:
            dict: The JSON response from the API after posting the data.
        
        Raises:
            Exception: If no token is provided and 'SHAREDDATA_TOKEN' is not found in environment variables.
            HTTPError: If the HTTP request returns an unsuccessful status code.
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None:
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user:
            params['user'] = user

        params['hasindex'] = hasindex

        headers = {
            'Content-Encoding': 'lz4',
            'Content-Type': 'application/octet-stream'
        }

        # If input is a DataFrame, convert to serialized list of dicts
        if isinstance(value, pd.DataFrame):
            value = ClientAPI.serialize(value.reset_index())
        else:
            value = ClientAPI.serialize(value)

        # ... chunked upload logic ...
        if isinstance(value, list) and len(value) > 0:
            # Estimate BSON size of one document for proper chunking
            # Take one document, encode and compress
            try:
                test_bson = bson.encode({'data': [value[0]]})
                test_compressed = lz4f.compress(test_bson)
                approx_size = len(test_compressed)
            except Exception:
                approx_size = 1000  # fallback
            # Compute number per chunk (~20MB)
            max_per_chunk = max(1, MAX_UPLOAD_SIZE_BYTES // approx_size)
            nchunks = int(np.ceil(len(value) / max_per_chunk))
            chunk_iter = (
                tqdm(range(nchunks), desc='Uploading collection') if nchunks > 2
                else range(nchunks)
            )
            for ichunk in chunk_iter:            
                chunk = value[ichunk*max_per_chunk:(ichunk+1)*max_per_chunk]
                bson_data = bson.encode({'data': chunk})
                compressed_data = lz4f.compress(bson_data)
                trials = 0
                while trials < 3:
                    if ClientAPI.try_post(url, headers, params, data=compressed_data):
                        break
                    trials += 1
                    if trials == 3:
                        raise Exception('Failed to upload data after 3 attempts')
            return 201

        # Fallback: (original behavior for single document or empty)
        bson_data = bson.encode({'data': value})
        compressed_data = lz4f.compress(bson_data)
        trials = 0
        while trials < 3:
            if ClientAPI.try_post(url, headers, params, data=compressed_data):
                break
            trials += 1
            if trials == 3:
                raise Exception('Failed to upload data after 3 attempts')
        return 201
    
    @staticmethod
    def patch_collection(database, period, source, tablename, 
            filter, update, endpoint=None,
            token=None, user=None, sort=None):     
        
        """
        '''
        Patch documents in a specified collection of a remote database via an HTTP PATCH request.
        
        Parameters:
            database (str): The name of the database.
            period (str): The period identifier for the data.
            source (str): The data source name.
            tablename (str): The name of the table or collection to patch. Can include a subfolder separated by '/'.
            filter (dict): A dictionary specifying the filter criteria to select documents to update.
            update (dict): A dictionary specifying the update operations to apply to the filtered documents.
            endpoint (str, optional): The base URL of the API endpoint. Defaults to environment variable 'SHAREDDATA_ENDPOINT' if not provided.
            token (str, optional): Authentication token for the API. Defaults to environment variable 'SHAREDDATA_TOKEN' if not provided.
            user (str, optional): Username associated with the request.
            sort (dict, optional): Sorting criteria for the documents.
        
        Returns:
            pandas.DataFrame: A DataFrame containing the updated documents indexed by their primary key. Returns an empty DataFrame if no data is returned or if the response status is 204 (No Content).
        
        Raises:
            Exception: If the authentication token is not found or if the HTTP request fails
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user:
            params['user'] = user
        
        params['filter'] = json.dumps(filter)  # Convert filter to JSON string
        params['update'] = json.dumps(update)  # Convert update to JSON string
        if sort:
            params['sort'] = json.dumps(sort)  # Convert sort to JSON string

        try:
            response = requests.patch(url, params=params)
            ClientAPI.raise_for_status(response)  # Raise HTTPError for bad responses (4xx or 5xx)

            if response.status_code == 200:
                # Default to JSON
                rjson = json.loads(response.content)
                if not 'data' in rjson:
                    return pd.DataFrame([])
                df = pd.DataFrame([json.loads(rjson['data'])])
                if df.empty:
                    return df
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                pkey = rjson['pkey']
                df = df.set_index(pkey).sort_index()
                
                return df
            elif response.status_code == 204:
                return pd.DataFrame([])
        
        except Exception as e:
            Logger.log.error(f"ClientAPI patch_collection Error: {e}")
            raise e
    
    @staticmethod
    def delete_collection(
        database: str,
        period: str,
        source: str,
        tablename: str,
        endpoint: str = None,
        token: str = None,
        user: str = None,
        query: dict = None
    ) -> int:
        """
        Delete documents from a collection, or the entire collection if no filter is provided.

        Parameters:
            database (str): Database name.
            period (str): Period name.
            source (str): Source name.
            tablename (str): Table/collection name, can include subfolder as '/'.
            endpoint (str, optional): API endpoint base URL.
            token (str, optional): API auth token.
            user (str, optional): User for access control.
            tablesubfolder (str, optional): Subfolder for table (overrides '/' in tablename).
            filter (dict, optional): If provided, only documents matching this filter will be deleted.

        Returns:
            int: HTTP status code returned by the server.
        """
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        tn = tablename
        # Support subfolder via either explicit arg or slash in tablename        
        if '/' in tn:
            tn_parts = tn.split('/')
            tn = tn_parts[0]
            params['tablesubfolder'] = tn_parts[1]

        route = f'/api/collection/{database}/{period}/{source}/{tn}'
        url += route

        if token is not None:
            params['token'] = token
        else:
            params['token'] = os.environ.get('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')
        if user:
            params['user'] = user

        if query is not None:            
            params['query'] = json.dumps(ClientAPI.serialize(query, iso_dates=True))

        response = requests.delete(url, params=params)
        ClientAPI.raise_for_status(response)
        return response.status_code    

    @staticmethod
    def get_workerpool(fetch_jobs=0):
        """
        Consumes jobs from a remote worker pool API and appends them to the internal stream buffer.
        
        Attempts to acquire a lock before making a GET request to the worker pool endpoint, using
        environment variables for authentication and configuration. Optionally fetches a specified
        number of jobs if `fetch_jobs` is greater than zero. The response content is expected to be
        LZ4 compressed BSON data, which is decompressed and decoded before extending the internal
        `stream_buffer` with the retrieved jobs.
        
        Returns:
            bool: True if the request was successful and jobs were processed or no content was returned,
                  False otherwise.
        
        Parameters:
            fetch_jobs (int): Optional number of jobs to fetch from the worker pool. Defaults to 0.
        """        
        workername = os.environ['USER_COMPUTER']
        headers = {                
            'Accept-Encoding': 'lz4',                
            'X-Custom-Authorization': os.environ['SHAREDDATA_TOKEN'],
        }
        params = {
            'workername': workername,                
        }
        if fetch_jobs > 0:
            params['fetch_jobs'] = fetch_jobs
        response = requests.get(
            os.environ['SHAREDDATA_ENDPOINT']+'/api/workerpool',
            headers=headers,
            params=params,
            timeout=15
        )
        ClientAPI.raise_for_status(response)        
        if response.status_code == 204:
            return []
        response_data = lz4.frame.decompress(response.content)
        record = bson.decode(response_data)            
        return record['jobs']                        

    @staticmethod
    def post_workerpool(record):
        """
        Sends a compressed and encoded record to a remote server endpoint.
        
        The method validates that the record contains the required keys: 
        'sender', 'target', and 'job'. It then encodes the record using BSON,
        compresses it with LZ4, and sends it as a POST request to a predefined 
        server endpoint with appropriate headers, including an authorization 
        token retrieved from environment variables. 
        
        Args:
            record (dict): The data record to be sent. Must contain 'sender', 'target', and 'job' keys.
            partitionkey (optional): Not used in this implementation.
        
        Raises:
            Exception: If 'sender', 'target', or 'job' keys are missing in the record.
        """
        if not 'sender' in record:
            raise Exception('sender not in record')
        if not 'target' in record:
            raise Exception('target not in record')
        if not 'job' in record:
            raise Exception('job not in record')
                
        bson_data = bson.encode(record)
        compressed = lz4.frame.compress(bson_data)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Encoding': 'lz4',
            'X-Custom-Authorization': os.environ['SHAREDDATA_TOKEN'],
        }
        response = requests.post(
            os.environ['SHAREDDATA_ENDPOINT']+'/api/workerpool',
            headers=headers,
            data=compressed,
            timeout=15
        )
        ClientAPI.raise_for_status(response)
        
        return True
        

