from flask import Flask, Response, g
from flask import request
from flask import jsonify
from flask import make_response
from flasgger import Swagger, swag_from
import bson
from bson import json_util
from bson.objectid import ObjectId
import pymongo
import os
import datetime
import gzip
import json
import time
import lz4.frame as lz4f
import pandas as pd
import numpy as np
from collections import defaultdict
import threading
from pathlib import Path
from werkzeug.middleware.proxy_fix import ProxyFix
import random

from SharedData.SharedData import SharedData
shdata = SharedData('SharedData.IO.ServerAPI', user='master',quiet=True)
from SharedData.Logger import Logger
from SharedData.Database import *
from SharedData.IO.MongoDBClient import MongoDBClient
from SharedData.CollectionMongoDB import CollectionMongoDB
from SharedData.Routines.WorkerPool import WorkerPool

MAX_RESPONSE_SIZE_BYTES = int(20*1024*1024)

app = Flask(__name__)
app.config['APP_NAME'] = 'SharedData API'
app.config['FLASK_ENV'] = 'production'
app.config['FLASK_DEBUG'] = '0'
if not 'SHAREDDATA_SECRET_KEY' in os.environ:
    raise Exception('SHAREDDATA_SECRET_KEY environment variable not set')
if not 'SHAREDDATA_TOKEN' in os.environ:
    raise Exception('SHAREDDATA_TOKEN environment variable not set')

app.config['SECRET_KEY'] = os.environ['SHAREDDATA_SECRET_KEY']
app.config['SWAGGER'] = {
    'title': 'SharedData API',
    'uiversion': 3
}
docspath = 'ServerAPIDocs.yml'
swagger = Swagger(app, template_file=docspath)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Thread-safe in-memory storage for traffic statistics
traffic_stats = {
    'total_requests': 0,
    'endpoints': defaultdict(lambda: {
        'requests': 0,
        'total_response_time': 0.0,
        'status_codes': defaultdict(int),
        'total_bytes_sent': 0,
        'total_bytes_received': 0  
    })
}

traffic_rates = {
    'last_total_requests': 0,
    'last_total_bytes_sent': 0,
    'last_total_bytes_received': 0,  
    'last_timestamp': time.time()
}

# Lock for thread-safe updates to traffic_stats
stats_lock = threading.Lock()

# Lock for updating users data
users_lock = threading.Lock()
users = {}

# User dictionary to store user data by token
with users_lock:
    if users == {}:
        user_collection = shdata.collection('Symbols', 'D1', 'AUTH', 'USERS', user='SharedData')
        _users = list(user_collection.find({}))  # Ensure we can iterate multiple times
        new_tokens = {user['token'] for user in _users}
        # Add or update users
        for user in _users:
            if user['token'] not in users:
                users[user['token']] = user
            else:
                users[user['token']].update(user)
        # Remove users not present in the new list
        tokens_to_delete = [token for token in users if token not in new_tokens]
        for token in tokens_to_delete:
            del users[token]        

@staticmethod
def check_permissions(reqpath: list[str], permissions: dict, method: str) -> bool:
    """
    Iteratively check if given path and method are permitted.
    Faster than a classical recursive approach for deep trees.
    """    
    node = permissions
    for segment in reqpath:
        if segment in node:
            node = node[segment]
        elif '*' in node:
            node = node['*']
        else:
            return False
        # If leaf is not dict (wildcard or method list)
        if not isinstance(node, dict):
            if '*' in node or (isinstance(node, list) and method in node):
                return True
            return False
    # At the end, check at current node
    if '*' in node:
        return True
    if method in node:
        return True
    return False

@staticmethod
def authenticate(request):    
    """
    Authenticate a request using a token provided either as a query parameter or in a custom header.
    
    The function attempts to retrieve the token from the 'token' query parameter. If not found, it looks for the token in the 'X-Custom-Authorization' header. It then compares the token against the expected token stored in the environment variable 'SHAREDDATA_TOKEN'. If the tokens do not match, the function waits for 3 seconds before returning False to mitigate brute-force attacks. If the token matches, it returns True. Any exceptions during the process result in a False return value.
    
    Parameters:
        request (flask.Request): The incoming HTTP request object.
    
    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    try:
        token = request.args.get('token')  # Not Optional
        if not token:
            token = request.headers.get('X-Custom-Authorization')
        if not token:
            token = request.headers.get('x-api-key')
        
        if not token in users:
            time.sleep(3)
            return False
       
        userdata = users[token]
        
        reqpath = str(request.path).split('/')[1:]
        user = request.args.get('user','master')        
        if user:
            reqpath = [user] + reqpath

        tablesubfolder = request.args.get('tablesubfolder')
        if tablesubfolder:
            reqpath = reqpath + [tablesubfolder]

        if not check_permissions(reqpath, userdata['permissions'], request.method):
            time.sleep(3)
            return False
                                            
        return True
    except:
        return False

@app.before_request
def start_timer():
    # Store the start time of the request
    """
    Initialize timing and request size tracking before processing each request.
    
    This function records the current time as the start time of the request and attempts to determine the size of the inbound request in bytes. It first tries to read the 'Content-Length' header; if that is not available or invalid, it falls back to measuring the length of the request data. The results are stored in the Flask `g` context for use during the request lifecycle.
    """
    g.start_time = time.time()
    # Store the inbound request size (if available)
    content_length = request.headers.get('Content-Length', 0)
    try:
        g.request_bytes = int(content_length)
    except ValueError:
        g.request_bytes = len(request.get_data()) if request.data else 0

@app.after_request
def log_request(response):
    # Calculate response time
    """
    Logs details of each HTTP request after it is processed, including response time, request method and endpoint, bytes sent and received, and updates aggregated traffic statistics in a thread-safe manner.
    
    Parameters:
        response (flask.Response): The HTTP response object to be sent to the client.
    
    Returns:
        flask.Response: The same response object passed in, unmodified.
    
    This function is intended to be used as a Flask after_request handler. It calculates the time taken to process the request, determines the number of bytes sent and received, and updates global traffic statistics including counts of requests, response times, status codes, and data transfer metrics per endpoint and HTTP method.
    """    
    response_time = time.time() - g.start_time    
    response.headers['Server'] = 'SharedData'    
    response.headers['X-Response-Time'] = f"{response_time * 1000:.2f}ms"

    # Get endpoint and method
    endpoint = request.endpoint or request.path
    method = request.method

    # Calculate bytes sent (outbound)
    content_length = response.headers.get('Content-Length', 0)
    try:
        bytes_sent = int(content_length)
    except ValueError:
        bytes_sent = len(response.get_data()) if response.data else 0

    # Get bytes received (inbound) from before_request
    bytes_received = g.request_bytes

    # Update statistics in a thread-safe manner
    with stats_lock:
        traffic_stats['total_requests'] += 1
        endpoint_stats = traffic_stats['endpoints'][f"{method} {endpoint}"]
        endpoint_stats['requests'] += 1
        endpoint_stats['total_response_time'] += response_time
        endpoint_stats['status_codes'][response.status_code] += 1
        endpoint_stats['total_bytes_sent'] += bytes_sent
        endpoint_stats['total_bytes_received'] += bytes_received  # Track inbound traffic

    return response

@app.route('/api/installworker')
def installworker():
    """
    Generate and return a shell script to install and configure the SharedData worker service on the client machine.
    
    This endpoint requires authentication via the `authenticate` function. It accepts the following query parameters:
    - `token` (str): Authentication token to be embedded in the environment file.
    - `batchjobs` (int, optional): Number of batch jobs to run; defaults to 0 if not provided.
    
    The generated script performs the following actions:
    - Creates an environment file with SharedData and Git configuration variables.
    - Installs necessary system dependencies including OpenJDK 21, Git, Python 3, and related development packages.
    - Configures Git with user credentials and disables pull rebase.
    - Sets up a Python virtual environment and installs the SharedData Python package.
    - Creates and enables a systemd service to run the SharedData worker with the specified batch jobs.
    - Starts the service and tails its logs.
    
    Returns:
        Response: A Flask Response object containing the shell script with MIME type 'text/x-sh' on success,
                  or a JSON error message with status 401 if unauthorized,
                  or status 500 if an exception occurs.
    """
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401        
        token = request.args.get('token')
        batchjobs = int(request.args.get('batchjobs', '0'))
        endpoint = str('https://'+request.host).rstrip('/')
        

        script = f"""\
#!/bin/bash
USERNAME=$(whoami)

cd /home/$USERNAME

# CREATE ENVIRONMENT FILE
cat > /home/$USERNAME/shareddata-worker.env <<EOF
SHAREDDATA_TOKEN={token}
SHAREDDATA_ENDPOINT={endpoint}
GIT_USER={os.environ['GIT_USER']}
GIT_EMAIL={os.environ['GIT_EMAIL']}
GIT_TOKEN={os.environ['GIT_TOKEN']}
GIT_ACRONYM={os.environ['GIT_ACRONYM']}
GIT_SERVER={os.environ['GIT_SERVER']}
GIT_PROTOCOL={os.environ['GIT_PROTOCOL']}
EOF

export GIT_USER="{os.environ['GIT_USER']}"
export GIT_EMAIL="{os.environ['GIT_EMAIL']}"
export GIT_TOKEN="{os.environ['GIT_TOKEN']}"

# INSTALL DEPENDENCIES
sudo apt update -y
sudo apt install openjdk-21-jre-headless -y

# INSTALL GIT
sudo apt install git -y
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"
git config --global credential.helper "!f() {{ echo username=\\$GIT_USER; echo password=\\$GIT_TOKEN; }};f"
git config --global pull.rebase false

# INSTALL PYTHON DEPENDENCIES
sudo apt install python-is-python3 -y
sudo apt install python3-venv -y
sudo apt-get install python3-dev -y
sudo apt-get install build-essential -y
sudo apt-get install libffi-dev -y
sudo apt-get install -y libxml2-dev libxslt-dev

# CREATE SOURCE FOLDER
SOURCE_FOLDER="${{SOURCE_FOLDER:-$HOME/src}}"
mkdir -p "$SOURCE_FOLDER"
cd "$SOURCE_FOLDER"

# Setup Python virtual environment
python -m venv venv
. venv/bin/activate
pip install shareddata --upgrade

# CREATE SYSTEMD SERVICE
sudo bash -c 'cat > /etc/systemd/system/shareddata-worker.service <<EOF
[Unit]
Description=SharedData Worker
After=network.target

[Service]
User={os.environ['USER']}
WorkingDirectory={os.environ.get('SOURCE_FOLDER', '$HOME/src')}
ExecStart={os.environ.get('SOURCE_FOLDER', '$HOME/src')}/venv/bin/python -m SharedData.Routines.Worker --batchjobs {batchjobs}
EnvironmentFile=/home/{os.environ['USER']}/shareddata-worker.env
LimitNOFILE=65536
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable shareddata-worker
sudo systemctl restart shareddata-worker
sudo journalctl -f -u shareddata-worker
"""
        return Response(script, mimetype='text/x-sh')
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/traffic_stats', methods=['GET'])
def get_traffic_stats():
    """
    Handle GET requests to the '/api/traffic_stats' endpoint, returning aggregated traffic statistics in JSON format.
    
    This function performs authentication, then safely accesses shared traffic statistics data protected by a threading lock.
    It compiles a summary including total requests, per-endpoint request counts, average response times, status code distributions,
    and total bytes sent and received. The response includes appropriate headers and handles errors by returning a JSON error message
    with a 500 status code.
    
    Returns:
        Response: A Flask Response object containing JSON-encoded traffic statistics or an error message.
    """
    try:
        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        # Prepare statistics for response in a thread-safe manner
        stats_response = {
            'total_requests': 0,
            'endpoints': {}
        }

        with stats_lock:
            stats_response['total_requests'] = traffic_stats['total_requests']
            for endpoint, data in traffic_stats['endpoints'].items():
                stats_response['endpoints'][endpoint] = {
                    'requests': data['requests'],
                    'average_response_time': data['total_response_time'] / data['requests'] if data['requests'] > 0 else 0,
                    'status_codes': dict(data['status_codes']),
                    'total_bytes_sent': data['total_bytes_sent'],
                    'total_bytes_received': data['total_bytes_received']  # Add inbound stats
                }

        response_data = json.dumps(stats_response).encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    
@app.route('/api/heartbeat', methods=['GET', 'POST'])
def heartbeat():
    """
    Endpoint to check the server heartbeat.
    
    Handles GET and POST requests by pausing for 3 seconds before responding with a JSON object indicating the server is alive. Returns a 200 OK response with a JSON payload `{"heartbeat": true}` and sets the appropriate Content-Length header.
    """
    time.sleep(3)
    response_data = json.dumps({'heartbeat': True}).encode('utf-8')
    response = Response(response_data, status=200, mimetype='application/json')
    response.headers['Content-Length'] = len(response_data)
    return response

@app.route('/api/auth', methods=['GET', 'POST'])
def auth():
    """
    Handle authentication requests via GET or POST methods.
    
    This endpoint checks for a valid authentication token in the request headers using the `authenticate` function.
    - If authentication fails, it returns a 401 Unauthorized response with an error message.
    - If authentication succeeds, it returns a 200 OK response with a JSON payload indicating successful authentication.
    - In case of any exceptions during processing, it returns a 500 Internal Server Error with the error details.
    
    Returns:
        Response: A Flask Response object containing JSON data and appropriate HTTP status codes.
    """
    try:
        # Check for the token in the header        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        response_data = json.dumps({'authenticated': True}).encode('utf-8')
        response = Response(response_data, status=200, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        error_message = json.dumps({"type": "InternalServerError", "message": str(e)})
        response = Response(error_message, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_message)
        return response

@app.route('/api/subscribe/table/<database>/<period>/<source>/<tablename>', methods=['GET'])
def subscribe_table(database, period, source, tablename):
    """
    Handle GET requests to subscribe to data updates from a specified table.
    
    This endpoint streams data from a table identified by the given database, period, source, and tablename parameters.
    Optional query parameters allow filtering and pagination of the data returned:
    
    - tablesubfolder: str (optional) - Subfolder appended to the tablename.
    - lookbacklines: int (optional, default=1000) - Number of recent lines to retrieve.
    - lookbackdate: str (optional) - ISO format date string to filter rows from this date onwards.
    - mtime: str (optional) - ISO format timestamp to filter rows modified after this time.
    - count: int (optional) - Client's current row count to fetch new rows beyond this count.
    - page: int (optional, default=1) - Page number for paginated responses.
    
    The response returns compressed (lz4) binary data of the requested rows with appropriate headers for encoding, length, and pagination.
    If no new data is available, responds with HTTP 204 No Content.
    If authentication fails, responds with HTTP 401 Unauthorized.
    On errors, responds with HTTP 500 and a JSON error message.
    
    Returns:
        Response: Flask Response object containing compressed binary data or error/status information.
    """
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        if tablesubfolder is not None:
            table = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            table = shdata.table(database, period, source, tablename)

        if table.table.hasindex:
            lookbacklines = request.args.get('lookbacklines', default=1000, type=int)  # Optional
            lookbackid = table.count - lookbacklines
            if 'lookbackdate' in request.args:
                lookbackdate = pd.Timestamp(request.args.get('lookbackdate'))                
                loc = table.get_date_loc_gte(lookbackdate)
                if len(loc)>0:
                    lookbackid = min(loc)
            if lookbackid < 0:
                lookbackid = 0

            ids2send = np.arange(lookbackid, table.count)
            if 'mtime' in request.args:
                mtime = pd.Timestamp(request.args.get('mtime'))
                newids = lookbackid + np.where(table['mtime'][ids2send] >= mtime)[0]
                ids2send = np.intersect1d(ids2send, newids)
        else:
            clientcount = request.args.get('count', default=0, type=int)  # Optional
            if clientcount < table.count:
                ids2send = np.arange(clientcount, table.count-1)
            else:
                ids2send = np.array([])
        
        rows2send = len(ids2send)
        if rows2send == 0:
            response = Response(status=204)
            response.headers['Content-Length'] = 0
            return response
        
        # Compress & paginate the response                
        maxrows = np.floor(MAX_RESPONSE_SIZE_BYTES/table.itemsize)
        if rows2send > maxrows:
            # paginate
            page = request.args.get('page', default=1, type=int)
            ids2send = ids2send[int((page-1)*maxrows):int(page*maxrows)]

        compressed = lz4f.compress(table[ids2send].tobytes())
        responsebytes = len(compressed)
        response = Response(compressed, mimetype='application/octet-stream')
        response.headers['Content-Encoding'] = 'lz4'
        response.headers['Content-Length'] = responsebytes        
        response.headers['Content-Pages'] = int(np.ceil(rows2send/maxrows))
        return response
    
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    
@app.route('/api/publish/table/<database>/<period>/<source>/<tablename>', methods=['GET'])
def publish_table_get(database, period, source, tablename):
    """
    Handle GET requests to publish metadata about a specified table in the database.
    
    This endpoint returns JSON containing the count of records in the specified table and, if the table has an index, the latest modification time (mtime) within an optional lookback window.
    
    URL Parameters:
    - database (str): The database name.
    - period (str): The period identifier.
    - source (str): The data source name.
    - tablename (str): The table name, optionally combined with a subfolder.
    
    Query Parameters:
    - tablesubfolder (str, optional): Subfolder within the table path.
    - lookbacklines (int, optional): Number of recent lines to consider for mtime calculation (default is 1000).
    - lookbackdate (str, optional): ISO format date string to specify the earliest date for lookback filtering.
    
    Authentication:
    - Requires successful authentication via the `authenticate` function; returns 401 Unauthorized if authentication fails.
    
    Returns:
    - JSON response with:
      - 'count': Total number of records in the table.
      - 'mtime' (optional): ISO formatted timestamp of the latest modification time within the lookback window if the table has an index.
    
    Error Handling:
    - Returns a JSON error message with status code 500 if an exception occurs.
    """
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
                
        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        if tablesubfolder is not None:
            table = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            table = shdata.table(database, period, source, tablename)

        msg = {'count': int(table.count)}

        if table.table.hasindex:
            lookbacklines = request.args.get('lookbacklines', default=1000, type=int)  # Optional
            lookbackid = table.count - lookbacklines
            if 'lookbackdate' in request.args:
                lookbackdate = pd.Timestamp(request.args.get('lookbackdate'))                
                loc = table.get_date_loc_gte(lookbackdate)
                if len(loc)>0:
                    lookbackid = min(loc)
            if lookbackid < 0:
                lookbackid = 0

            ids2send = np.arange(lookbackid, table.count)
            if len(ids2send) == 0:
                msg['mtime'] = pd.Timestamp(np.datetime64('1970-01-01')).isoformat()    
            else:
                msg['mtime'] = pd.Timestamp(np.datetime64(np.max(table['mtime'][ids2send]))).isoformat()

        response_data = json.dumps(msg).encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/publish/table/<database>/<period>/<source>/<tablename>', methods=['POST'])
def publish_table_post(database, period, source, tablename):
    """
    Handle POST requests to publish data to a specified table within a database.
    
    This endpoint accepts compressed binary data, decompresses it using lz4f, and writes the data to the specified table. It supports an optional subfolder within the table path.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier.
    - source (str): The data source identifier.
    - tablename (str): The name of the table to publish data to.
    
    Query Parameters:
    - tablesubfolder (str, optional): An optional subfolder within the table path.
    
    Behavior:
    - Authenticates the request; returns 401 Unauthorized if authentication fails.
    - Decompresses the request body using lz4f.
    - Converts decompressed data into records matching the table's dtype.
    - If the table has an index, performs an upsert of all records.
    - Otherwise, extends the table with the new records.
    - Returns HTTP 200 with empty body if data was processed.
    - Returns HTTP 204 No Content if no complete records were found in the data.
    - Returns HTTP 500 with error details if an exception occurs.
    """
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
                
        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        if tablesubfolder is not None:
            table = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            table = shdata.table(database, period, source, tablename)
        
        data = lz4f.decompress(request.data)
        buffer = bytearray()
        buffer.extend(data)
        if len(buffer) >= table.itemsize:
            # Determine how many complete records are in the buffer
            num_records = len(buffer) // table.itemsize
            # Take the first num_records worth of bytes
            record_data = buffer[:num_records * table.itemsize]
            # And remove them from the buffer
            del buffer[:num_records * table.itemsize]
            # Convert the bytes to a NumPy array of records
            rec = np.frombuffer(record_data, dtype=table.dtype)
                
            if table.table.hasindex:
                # Upsert all records at once
                table.upsert(rec)
            else:
                # Extend all records at once
                table.extend(rec)
            
            response = Response(status=200)
            response.headers['Content-Length'] = 0
            return response        
        
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/tables', methods=['GET'])
def list_tables() -> Response:
    """
    Endpoint to list all tables.
    Query params:
        - keyword: (optional) a keyword to filter table names.
        - user: (optional) user name, default 'master'.
    Response: JSON list of table names and info.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        keyword = request.args.get('keyword', '')
        user = request.args.get('user', 'master')

        tables = shdata.list_tables(keyword=keyword, user=user)
        if tables.empty:
            return Response(status=204)
        tables = tables.reset_index().to_dict('records')        
        tables = CollectionMongoDB.serialize(tables, iso_dates=True)
        response_data = json.dumps(tables).encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response

    except Exception as e:
        response = Response(status=500)
        error_data = json.dumps({'error': str(e).replace('\n', ' ')}).encode('utf-8')
        response.headers['Error-Message'] = error_data
        return response

@app.route('/api/table/<database>/<period>/<source>/<tablename>', methods=['HEAD', 'GET', 'POST', 'DELETE'])
@swag_from(docspath)
def table(database, period, source, tablename):
    """
    Handle CRUD operations on a specified table within a database for a given period and source.
    
    Supports GET, POST, and DELETE HTTP methods:
    - GET: Retrieve data from the specified table.
    - POST: Insert or update data in the specified table.
    - DELETE: Remove data from the specified table.
    
    Authentication is required for all requests. Returns appropriate JSON responses and HTTP status codes:
    - 401 Unauthorized if authentication fails.
    - 405 Method Not Allowed for unsupported HTTP methods.
    - 500 Internal Server Error for unexpected exceptions.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The time period related to the data.
    - source (str): The data source identifier.
    - tablename (str): The name of the table to operate on.
    
    Returns:
    - JSON response with data or error message and corresponding HTTP status code.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        if request.method == 'HEAD':
            return head_table(database, period, source, tablename, request)                
        elif request.method == 'GET':
            return get_table(database, period, source, tablename, request)        
        elif request.method == 'POST':
            return post_table(database, period, source, tablename, request)
        elif request.method == 'DELETE':
            return delete_table(database, period, source, tablename, request)
        else:
            return jsonify({'error': 'method not allowed'}), 405
        
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error                
        response = Response(status=500)                
        response.headers['Error-Message'] = str(e).replace('\n', ' ')
        return response

def head_table(database, period, source, tablename, request):
    tablesubfolder = request.args.get('tablesubfolder')    
    user = request.args.get('user', default='master')
    
    if tablesubfolder is not None:
        tbl = shdata.table(database, period, source, tablename+'/'+tablesubfolder, user=user)
    else:
        tbl = shdata.table(database, period, source, tablename, user=user)
    hdr = tbl.table.hdr    
    hdrdict = {name: hdr[name].item() if hasattr(hdr[name], 'item') else hdr[name]
               for name in hdr.dtype.names}
    response = Response(200)    
    for key, value in hdrdict.items():
        response.headers['Table-'+key] = value    
    return response

def get_table(database, period, source, tablename, request):
    """
    '''
    Retrieve and filter data from a specified table in the database based on HTTP request parameters, then return the data in the requested format.
    
    Parameters:
        database (str): The name of the database.
        period (str): The period identifier for the data.
        source (str): The data source identifier.
        tablename (str): The name of the table to query.
        request (flask.Request): The HTTP request object containing query parameters and headers.
    
    Query Parameters (all optional):
        tablesubfolder (str): Subfolder within the table to query.
        startdate (str): Start date filter in a format parseable by pandas.Timestamp.
        enddate (str): End date filter in a format parseable by pandas.Timestamp.
        symbols (str): Comma-separated list of symbols to filter.
        portfolios (str): Comma-separated list of portfolios to filter.
        tags (str): Comma-separated list of tags to filter.
        page (int): Page number for pagination (default is 1).
        per_page (int): Number of records per page (default is 0, meaning no limit).
        format (str): Output format, one of 'json' (default), 'csv', or 'bin'.
        query (str):
    """
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    startdate = request.args.get('startdate')  # Optional
    enddate = request.args.get('enddate')  # Optional
    symbols = request.args.get('symbols')  # Optional
    portfolios = request.args.get('portfolios')  # Optional
    tags = request.args.get('tags')  # Optional
    page = request.args.get('page', default='1')
    page = int(float(page))
    per_page = request.args.get('per_page', default='0')
    per_page = int(float(per_page))
    output_format = request.args.get('format', 'json').lower()  # 'json' by default, can be 'csv' and 'bin'        
    query = request.args.get('query')
    user = request.args.get('user', default='master')

    if query:
        query = json.loads(query)  # Optional
    else:
        query = {}

    if tablesubfolder is not None:
        tbl = shdata.table(database, period, source, tablename+'/'+tablesubfolder, user=user)
    else:
        tbl = shdata.table(database, period, source, tablename, user=user)
    
    loc = None

    if startdate is not None and enddate is not None:
        startdate = pd.Timestamp(startdate)
        enddate = pd.Timestamp(enddate)
        loc = tbl.get_date_loc_gte_lte(startdate, enddate)

    elif startdate is not None:
        startdate = pd.Timestamp(startdate)
        loc = tbl.get_date_loc_gte(startdate)            

    elif enddate is not None:
        enddate = pd.Timestamp(enddate)
        loc = tbl.get_date_loc_lte(enddate)        
    
    else:
        loc = np.arange(tbl.count)

    if len(loc) == 0:
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response
    
    # filter data by symbols    
    if symbols is not None:
        symbols = symbols.split(',')
        symbolloc = []
        for symbol in symbols:
            symbolloc.extend(tbl.get_symbol_loc(symbol))
        symbolloc = np.array(symbolloc)
        if len(symbolloc) > 0:
            loc = np.intersect1d(loc, symbolloc)
        else:
            loc = np.array([])

    # filter data by portfolios
    if portfolios is not None:
        portfolios = portfolios.split(',')
        portloc = []
        for port in portfolios:
            portloc.extend(tbl.get_portfolio_loc(port))
        portloc = np.array(portloc)
        if len(portloc) > 0:
            loc = np.intersect1d(loc, portloc)
        else:
            loc = np.array([])

    # filter data by tags
    if tags is not None:
        tags = tags.split(',')
        tagloc = []
        for tag in tags:
            tagloc.extend(tbl.get_tag_loc(tag))
        tagloc = np.array(tagloc)
        if len(tagloc) > 0:
            loc = np.intersect1d(loc, tagloc)
        else:
            loc = np.array([])
    
    if not loc is None:
        loc = np.array(loc)
    # cycle query keys
    if query.keys() is not None:        
        for key in query.keys():            
            if pd.api.types.is_string_dtype(tbl[key]):
                idx = tbl[loc][key] == query[key].encode()
            elif pd.api.types.is_datetime64_any_dtype(tbl[key]):
                idx = tbl[loc][key] == pd.Timestamp(query[key])
            else:                    
                idx = tbl[loc][key] == query[key]
            loc = loc[idx]
    
    if len(loc) == 0:
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response
    
    
    # filter columns
    pkey = DATABASE_PKEYS[database]
    columns = request.args.get('columns')  # Optional
    if columns:
        columns = columns.split(',')
        columns = np.array([c for c in columns if not c in pkey])
        columns = pkey + list(np.unique(columns))
        names = columns
        formats = [tbl.dtype.fields[name][0].str for name in names]
        dtype = np.dtype(list(zip(names, formats)))
        # Apply pagination    
        maxrows = int(np.floor(MAX_RESPONSE_SIZE_BYTES/dtype.itemsize))
        maxrows = min(maxrows,len(loc))
        if (per_page > maxrows) | (per_page == 0):
            per_page = maxrows        
        startpage = (page - 1) * per_page
        endpage = startpage + per_page        
        content_pages = int(np.ceil(len(loc) / per_page))
        recs2send = tbl[loc[startpage:endpage]]
        # Create new array
        arrays = [recs2send[field] for field in columns]
        recs2send = np.rec.fromarrays(arrays, dtype=dtype)
    else:
        # Apply pagination    
        maxrows = int(np.floor(MAX_RESPONSE_SIZE_BYTES/tbl.itemsize))
        maxrows = min(maxrows,len(loc))
        if (per_page > maxrows) | (per_page == 0):
            per_page = maxrows
        startpage = (page - 1) * per_page
        endpage = startpage + per_page        
        content_pages = int(np.ceil(len(loc) / per_page))
        recs2send = tbl[loc[startpage:endpage]]    
    
    # send response
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if output_format == 'csv':
        # Return CSV
        df = tbl.records2df(recs2send)
        df = df.reset_index()
        csv_data = df.to_csv(index=False)
        if 'gzip' in accept_encoding:
            response_csv = csv_data.encode('utf-8')
            response_compressed = gzip.compress(response_csv, compresslevel=1)
            response = Response(response_compressed, mimetype='text/csv')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            response.headers['Content-Pages'] = content_pages
            return response
        else:
            response_data = csv_data.encode('utf-8')
            response = Response(response_data, mimetype='text/csv')
            response.headers['Content-Length'] = len(response_data)
            return response
    elif output_format == 'json':
        # Return JSON
        df = tbl.records2df(recs2send)
        pkey = df.index.names
        df = df.reset_index()
        df = df.applymap(lambda x: x.isoformat() if isinstance(x, datetime.datetime) else x)
        response_data = {
            'page': page,
            'per_page': per_page,
            'total': len(loc),
            'pkey': pkey,
            'data': df.to_dict(orient='records')
        }
        if 'gzip' in accept_encoding:
            response_json = json.dumps(response_data).encode('utf-8')
            response_compressed = gzip.compress(response_json, compresslevel=1)
            response = Response(response_compressed, mimetype='application/json')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            response.headers['Content-Pages'] = content_pages
            return response
        else:
            response_data_json = json.dumps(response_data).encode('utf-8')
            response = Response(response_data_json, mimetype='application/json')
            response.headers['Content-Length'] = len(response_data_json)
            return response
    else:  # output_format=='bin'
        names = list(recs2send.dtype.names)
        formats = [recs2send.dtype.fields[name][0].str for name in names]
        json_payload = {
            'names': names,
            'formats': formats,
            'pkey': DATABASE_PKEYS[database],
            'data': recs2send.tobytes()

        }
        bson_payload = bson.BSON.encode(json_payload)
        compressed = lz4f.compress(bson_payload)
        
        response = Response(compressed, mimetype='application/octet-stream')
        response.headers['Content-Encoding'] = 'lz4'        
        response.headers['Content-Pages'] = content_pages        
        return response

def post_table(database, period, source, tablename, request):
    """
    '''
    Handles a POST request to create or update a table in the specified database.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier for the table.
    - source (str): The data source identifier.
    - tablename (str): The name of the table to create or update.
    - request (flask.Request): The HTTP request object containing data and query parameters.
    
    Query Parameters (all optional):
    - tablesubfolder (str): Subfolder to append to the table name.
    - names (str): JSON-encoded list of field names.
    - formats (str): JSON-encoded list of field formats.
    - size (int): Size parameter for the table.
    - overwrite (bool): Whether to overwrite existing data (default False).
    - user (str): User performing the operation (default 'master').
    - hasindex (str): Whether the data has an index (default 'True').
    
    Request Data:
    - If Content-Encoding is 'lz4', decompresses binary data and interprets it using provided metadata.
    - Otherwise, expects JSON data representing a DataFrame.
    
    Behavior:
    - Parses and validates primary key columns.
    - Creates or updates the table using the provided data.
    - Supports upsert if data has an index, otherwise
    """
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    overwrite = request.args.get('overwrite', 'False')  # Optional
    overwrite = overwrite=='True'
    user = request.args.get('user', 'master')  # Optional
    hasindex = request.args.get('hasindex', 'True')    
    hasindex = hasindex=='True'
    
    value = None
    if not request.data:
        raise Exception('No data provided')
    
    content_encoding = request.headers.get('Content-Encoding', "")
    if content_encoding != 'lz4':
        raise Exception('Content-Encoding must be lz4')
    
    data = lz4f.decompress(request.data)
    json_payload = bson.decode(data)
    names = None
    if 'names' in json_payload:
        names = json_payload['names']
    formats = None
    if 'formats' in json_payload:
        formats = json_payload['formats']
    size = None
    if 'size' in json_payload:
        size = json_payload['size']
        
    value = None
    if 'data' in json_payload:
        meta_names = json_payload['meta_names']
        meta_formats = json_payload['meta_formats']
        dtype = np.dtype(list(zip(meta_names, meta_formats)))        
        value = np.frombuffer(json_payload['data'], dtype=dtype).copy()
                
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
            
    tbl = shdata.table(database, period, source, tablename,
                       names=names, formats=formats, size=size,
                       overwrite=overwrite, user=user, value=value, hasindex=hasindex)
    
    if size is not None:
        if tbl.size < size:
            tbl.free()
            tbl = shdata.table(database, period, source, tablename,
                names=names, formats=formats, size=size,
                overwrite=overwrite, user=user, value=value, hasindex=hasindex)

    if value is not None:
        if hasindex:
            tbl.upsert(value)
        else:
            tbl.append(value)
            
    response = Response(status=201)
    response.headers['Content-Length'] = 0
    return response

def delete_table(database, period, source, tablename, request):
    """
    Deletes a specified table from the given database, period, and source.
    
    Parameters:
        database (str): The name of the database.
        period (str): The time period associated with the table.
        source (str): The source identifier of the table.
        tablename (str): The name of the table to delete.
        request (flask.Request): The HTTP request object containing optional query parameters.
    
    Optional Query Parameters in request.args:
        tablesubfolder (str): An optional subfolder appended to the tablename.
        user (str): The user performing the deletion; defaults to 'master' if not provided.
    
    Returns:
        flask.Response: HTTP 204 No Content if deletion is successful,
                        HTTP 404 Not Found if the table does not exist or deletion fails.
    """
    tablesubfolder = request.args.get('tablesubfolder')  # Optional    
    user = request.args.get('user', 'master')  # Optional
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
    success = shdata.delete_table(database, period, source, tablename, user=user)
    if success:
        return Response(status=204)
    else:
        return Response(status=404)
    
@app.route('/api/collections', methods=['GET'])
def list_collections():
    """
    Endpoint to list all collections.
    Query params:
        - keyword: (optional) a keyword to filter collection names.
        - user: (optional) user name, default 'master'.
    Response: JSON list of collection names and info.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        keyword = request.args.get('keyword', '')
        user = request.args.get('user', 'master')
        collections = shdata.list_collections(keyword=keyword, user=user)
        if collections.empty:
            return Response(status=204)
        collections = collections.reset_index().to_dict('records')
        collections = CollectionMongoDB.serialize(collections,iso_dates=True)
        response_data = json.dumps(collections).encode('utf-8')
        response = Response(response_data, mimetype='application/json')        
        return response
    except Exception as e:        
        response = Response(status=500)
        error_data = json.dumps({'error': str(e).replace('\n', ' ')}).encode('utf-8')
        response.headers['Error-Message'] = error_data
        return response

def parse_json_query(query: dict) -> dict:
    """
    Recursively parse a Mongo-like query dict converting string '_id' to ObjectId
    and string 'date' fields to pandas.Timestamp.
    """
    for key in list(query.keys()):
        value = query[key]
        if key == '_id':
            if isinstance(value, dict):
                # Handle MongoDB operators like $gte, $lte, $in, etc.
                for op_key, op_value in value.items():
                    if op_key.startswith('$'):
                        try:
                            if op_key == '$in' and isinstance(op_value, list):
                                # Handle $in operator with list of _id values
                                value[op_key] = [ObjectId(str(item)) for item in op_value]
                            else:
                                # Handle other operators like $gte, $lte, $ne, etc.
                                value[op_key] = ObjectId(str(op_value))
                        except Exception:
                            pass
                    elif isinstance(op_value, dict):
                        value[op_key] = parse_json_query({op_key: op_value})[op_key]
            else:
                query[key] = ObjectId(str(value))
        elif key == 'date':
            if isinstance(value, dict):
                # Handle MongoDB operators like $gte, $lte, etc.
                for op_key, op_value in value.items():
                    if op_key.startswith('$'):
                        try:
                            value[op_key] = pd.Timestamp(op_value)
                        except Exception:
                            pass
                    elif isinstance(op_value, dict):
                        value[op_key] = parse_json_query({op_key: op_value})[op_key]
            else:
                try:
                    query[key] = pd.Timestamp(value)
                except Exception:
                    pass
        elif isinstance(value, dict):
            query[key] = parse_json_query(value)
    return query

@app.route('/api/collection/<database>/<period>/<source>/<tablename>', methods=['HEAD','GET', 'POST', 'PATCH', 'DELETE'])
@swag_from(docspath)
def collection(database, period, source, tablename):
    """
    Handle CRUD operations on a specified collection within a database.
    
    This endpoint supports GET, POST, PATCH, DELETE, and HEAD HTTP methods to interact with a collection identified by the given database, period, source, and tablename parameters.
    
    Authentication is required for all requests. If authentication fails, a 401 Unauthorized response is returned.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier.
    - source (str): The source identifier.
    - tablename (str): The name of the table or collection.
    
    Returns:
    - JSON response with the result of the requested operation.
    - 401 Unauthorized if authentication fails.
    - 405 Method Not Allowed if the HTTP method is not supported.
    - 500 Internal Server Error with error details if an exception occurs.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        if request.method == 'HEAD':
            return head_collection(database, period, source, tablename, request)
        elif request.method == 'GET':
            return get_collection(database, period, source, tablename, request)
        elif request.method == 'POST':
            return post_collection(database, period, source, tablename, request)
        elif request.method == 'PATCH':
            return patch_collection(database, period, source, tablename, request)        
        elif request.method == 'DELETE':
            return delete_collection(database, period, source, tablename, request)
        else:
            return jsonify({'error': 'method not allowed'}), 405
        
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        response = Response(status=500)                
        response.headers['Error-Message'] = str(e).replace('\n', ' ')
        return response
    
def head_collection(database: str, period: str, source: str, tablename: str, request):
    """
    Respond to HTTP HEAD requests with metadata headers for a given collection.
    Uses MongoDB's $sample aggregation to fetch a random sample of fields.
    """
    user = request.args.get('user', 'master')
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    if tablesubfolder:
        tablename = f"{tablename}/{tablesubfolder}"

    collection = shdata.collection(database, period, source, tablename, user=user, create_if_not_exists=False)

    sample_size = 10000  # or any number you want
    # Get a random sample using $sample
    try:
        cursor = collection.collection.aggregate([{"$sample": {"size": sample_size}}])
    except Exception:
        # fallback in case $sample is not supported, e.g. very small collections
        cursor = collection.find({}, limit=sample_size)
    
    field_set = set()
    for doc in cursor:
        field_set.update(doc.keys())
    doc_fields = sorted(field_set)

    pkey = DATABASE_PKEYS[database] if database in DATABASE_PKEYS else []
    try:
        count = collection.collection.estimated_document_count()
    except Exception:
        # fallback to slow but accurate if estimate fails
        count = collection.collection.count_documents({})
    response = Response(status=200)
    response.headers["Collection-Count"] = str(count)
    response.headers["Collection-Fields"] = ",".join(doc_fields)
    response.headers["Collection-Pkey"] = ",".join(pkey)
    return response    

def get_collection(database, period, source, tablename, request):
    # Get the collection    
    """
    '''
    Retrieve and return a collection from the specified database with filtering, sorting, pagination, and formatting options.
    
    Parameters:
    - database (str): The name of the database to query.
    - period (str): The period or partition of the database.
    - source (str): The data source identifier.
    - tablename (str): The name of the table or collection to query.
    - request (flask.Request): The Flask request object containing query parameters and headers.
    
    Query Parameters (via request.args):
    - user (str, optional): User identifier for access control, defaults to 'master'.
    - tablesubfolder (str, optional): Subfolder appended to the tablename.
    - query (str, optional): JSON-encoded query filter for MongoDB.
    - sort (str, optional): JSON-encoded sort specification.
    - columns (str, optional): Comma-separated list of columns to include in the result.
    - page (int, optional): Page number for pagination, defaults to 1.
    - per_page (int, optional): Number of items per page, defaults to 10000.
    - format (str, optional): Output format, one of 'bson' (default), 'json', or 'csv'.
    
    Headers:
    - Accept-Encoding: Used to determine if gzip
    """
    user = request.args.get('user', 'master')  # Optional
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    query = request.args.get('query')
    if query:
        query = json_util.loads(query)  # Optional
    else:
        query = {}        
    sort = request.args.get('sort')  # Optional        
    if sort:
        sort = json_util.loads(sort)
    else:
        sort = {}
    columns = request.args.get('columns')  # Optional
    projection = None
    if columns:
        columns = json_util.loads(columns)
        projection = {f.strip(): 1 for f in columns.split(',')}
        for pkey in DATABASE_PKEYS[database]:
            projection[pkey] = 1

    page = request.args.get('page', default='1')
    page = int(float(page))
    per_page = request.args.get('per_page', default='10000')
    per_page = int(float(per_page))
    output_format = request.args.get('format', 'bson').lower()  # 'json' by default, can be 'csv'
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
    collection = shdata.collection(database, period, source, tablename, user=user,
                                   create_if_not_exists=False)

    query = parse_json_query(query)
    result = collection.find(query, sort=sort, limit=per_page, skip=(page-1)*per_page, projection=projection)
    if len(result) == 0:
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response
    
    if output_format == 'bson':
        bson_data = bson.encode({'data': list(result)})
        compressed_data = lz4f.compress(bson_data)

        response = Response(compressed_data, mimetype='application/octet-stream')
        response.headers['Content-Encoding'] = 'lz4'
        response.headers['Content-Length'] = len(compressed_data)
        response.headers['Content-Type'] = 'application/octet-stream'
        return response

    elif output_format == 'csv':
        # Return CSV
        df = collection.documents2df(result)
        csv_data = df.to_csv()
        if 'gzip' in accept_encoding:
            response_csv = csv_data.encode('utf-8')
            response_compressed = gzip.compress(response_csv, compresslevel=1)
            response = Response(response_compressed, mimetype='text/csv')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            return response
        else:
            response_data = csv_data.encode('utf-8')
            response = Response(response_data, mimetype='text/csv')
            response.headers['Content-Length'] = len(response_data)
            return response
    else:
        pkey = ''
        if database in DATABASE_PKEYS:
            pkey = DATABASE_PKEYS[database]
        # Return JSON
        response_data = {
            'page': page,
            'per_page': per_page,
            'total': len(result),
            'pkey': pkey,
            'data': collection.documents2json(result)
        }

        if 'gzip' in accept_encoding:
            response_json = json.dumps(response_data).encode('utf-8')
            response_compressed = gzip.compress(response_json, compresslevel=1)
            response = Response(response_compressed, mimetype='application/json')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            return response
        else:
            response_json = json.dumps(response_data).encode('utf-8')
            response = Response(response_json, mimetype='application/json')
            response.headers['Content-Length'] = len(response_json)
            return response

def post_collection(database, period, source, tablename, request):    
    # 1. Parse query parameters
    """
    '''
    Handle a POST request to insert or upsert a collection of documents into a specified database collection.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period or timeframe identifier.
    - source (str): The data source identifier.
    - tablename (str): The base name of the target table or collection.
    - request (flask.Request): The incoming HTTP request object containing query parameters, headers, and data.
    
    Behavior:
    1. Parses optional query parameters:
       - 'tablesubfolder' to append to the tablename.
       - 'user' with a default value of 'master'.
       - 'hasindex' indicating whether the collection has an index (default True).
    2. Acquires a collection object using the provided parameters.
    3. Validates that request data is present; returns HTTP 400 if missing.
    4. Handles input data which can be either:
       - lz4 compressed BSON binary data (with 'Content-Encoding' header set to 'lz4'), or
       - JSON formatted data.
    5. Validates that the decoded data is a list of documents; returns HTTP 400 if not.
    6. Inserts or upserts the documents into the collection depending on the 'hasindex' flag.
    7.
    """
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    user = request.args.get('user', 'master')            # Default to 'master'
    hasindex = request.args.get('hasindex', 'True')    
    hasindex = hasindex=='True'

    if tablesubfolder:
        tablename = f"{tablename}/{tablesubfolder}"

    # 2. Acquire collection object
    collection = shdata.collection(database, period, source, tablename, user=user,hasindex=hasindex)

    # 3. Ensure data is present
    if not request.data:
        Response({'message':'No data'}, status=400)
    
    # 4. Handle input data (lz4+BSON or JSON)
    # Check for binary, compressed upload
    if request.headers.get('Content-Encoding', '').lower() == 'lz4':
        decompressed = lz4f.decompress(request.data)
        documents = bson.decode(decompressed)['data']
    else:
        # fallback: assume JSON
        documents = json.loads(request.data)

    if not isinstance(documents, list):
        Response({'message':'Data must be a list'}, status=400)
    
    # 5. Insert/Upsert
    # (Assume upsert method supports list input)
    if hasindex:
        collection.upsert(documents)
    else:
        collection.extend(documents)

    # 6. Prepare and return response
    response_data = json.dumps({'status': 'success'}).encode('utf-8')
    response = Response(response_data, status=201, mimetype='application/json')
    response.headers['Content-Length'] = str(len(response_data))
    return response   

def patch_collection(database, period, source, tablename, request):
    # Get the collection    
    """
    '''
    Update a single document in a specified collection within the database based on a filter and update criteria provided via HTTP request parameters.
    
    Parameters:
    - database (str): Name of the database to access.
    - period (str): Time period identifier used to locate the collection.
    - source (str): Source identifier used to locate the collection.
    - tablename (str): Name of the table/collection to update.
    - request (flask.Request): Flask request object containing query parameters.
    
    Returns:
    - flask.Response: JSON response containing the updated document with primary key information if successful,
      a 400 error response if required parameters are missing or invalid,
      or a 204 No Content response if no matching document is found.
    
    Behavior:
    - Validates the existence of the database and retrieves its primary key.
    - Extracts optional parameters 'user' and 'tablesubfolder' from the request.
    - Parses and validates the 'filter' and 'update' JSON parameters from the request.
    - Converts '_id' fields to ObjectId and attempts to parse 'date' fields to timestamps.
    - Optionally parses a 'sort' parameter to determine update order.
    - Performs a find_one_and_update operation on the collection.
    - Formats datetime fields and ObjectId in the response document for JSON serialization.
    """
    pkey = ''
    if database in DATABASE_PKEYS:
        pkey = DATABASE_PKEYS[database]
    else:
        error_data = json.dumps({'error': 'database not found'}).encode('utf-8')
        response = Response(error_data, status=400, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    
    user = request.args.get('user', 'master')  # Optional    
    tablesubfolder = request.args.get('tablesubfolder', None)  # Optional
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
    collection = shdata.collection(database, period, source, tablename, user=user)
    
    filter = request.args.get('filter')
    if filter is None:
        error_data = json.dumps({'error': 'filter is required'}).encode('utf-8')
        response = Response(error_data, status=400, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response    
    filter = json.loads(filter)
    filter = parse_json_query(filter)
    update = request.args.get('update')
    if update is None:
        error_data = json.dumps({'error': 'update is required'}).encode('utf-8')
        response = Response(error_data, status=400, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    update = json.loads(update)

    sort = request.args.get('sort')    
    if sort:
        sort = json.loads(sort)
    else:
        sort = {}
    
    coll = collection.collection
    res = coll.find_one_and_update(
        filter=filter, 
        update=update, 
        sort=sort, 
        return_document=pymongo.ReturnDocument.AFTER)
    
    if res:
        if '_id' in res:
            res['_id'] = str(res['_id'])
        
        for key in res:
            if pd.api.types.is_datetime64_any_dtype(res[key]) or isinstance(res[key], datetime.datetime):
                res[key] = res[key].isoformat()
        # Return JSON
        response_data = {
            'pkey': pkey,
            'data': json.dumps(res),
        }
        response_json = json.dumps(response_data).encode('utf-8')
        response = Response(response_json, mimetype='application/json')
        response.headers['Content-Length'] = len(response_json)
        return response
    else:
        response = Response('', status=204)
        response.headers['Content-Length'] = 0
        return response

def delete_collection(database, period, source, tablename, request):
    # Get the collection    
    """
    Deletes a specific collection from the database based on the given parameters.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier for the collection.
    - source (str): The source identifier for the collection.
    - tablename (str): The base name of the table/collection to delete.
    - request (flask.Request): The Flask request object containing optional query parameters.
    
    Optional query parameters in the request:
    - user (str): The user performing the deletion. Defaults to 'master' if not provided.
    - tablesubfolder (str): An optional subfolder appended to the tablename.
    
    Returns:
    - flask.Response: HTTP 204 No Content if deletion is successful.
                      HTTP 404 Not Found if the collection does not exist or deletion fails.
    """
    user = request.args.get('user', 'master')  # Optional
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    if tablesubfolder is not None:
        tablename = tablename + '/' + tablesubfolder

    query = request.args.get('query')
    if query:        
        query = json.loads(query) 
        query = parse_json_query(query)
        collection = shdata.collection(database, period, source, tablename, user=user, create_if_not_exists=False)
        result = collection.collection.delete_many(query)
        if result.deleted_count > 0:
            return Response(status=204)
        else:
            return Response(status=404)
    else:
        # original: drop the whole collection
        success = shdata.delete_collection(database, period, source, tablename, user=user)
        if success:
            return Response(status=204)
        else:
            return Response(status=404)

@app.route('/api/logs', methods=['POST'])
def logs():
    """
    Handle POST requests to the '/api/logs' endpoint by authenticating the request, decompressing and parsing the incoming LZ4-compressed JSON log data, and enqueueing the log record for processing.
    
    Returns:
        - 201 Created on successful log receipt.
        - 401 Unauthorized if authentication fails.
        - 500 Internal Server Error with a JSON error message if an exception occurs during processing.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        data = lz4f.decompress(request.data)
        rec = json.loads(data.decode('utf-8'))
        with Logger.lock:
            if Logger.log_writer_thread is None:
                Logger.log_writer_thread = threading.Thread(
                    target=Logger.log_writer,args=(shdata,), daemon=True
                )
                Logger.log_writer_thread.start()
        Logger.log_queue.put(rec)
        
        return Response(status=201)

    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        response = Response(status=500)                
        response.headers['Error-Message'] = str(e).replace('\n', ' ')
        return response

@app.route('/api/workerpool', methods=['GET','POST'])
def workerpool():
    """
    Handle HTTP requests for the '/api/workerpool' endpoint supporting GET, POST.
    
    - POST: Calls post_workerpool(request) to create or update workerpool data.
    - GET: Calls get_workerpool(request) to retrieve workerpool data.    
    
    In case of any exceptions, returns a JSON-formatted 500 Internal Server Error response after a 1-second delay.
    """
    try:        
        if request.method == 'POST':
            return post_workerpool(request)
        elif request.method == 'GET':
            return get_workerpool(request)

    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        response = Response(status=500)                
        response.headers['Error-Message'] = str(e).replace('\n', ' ')
        return response

def get_workerpool(request):
    """
    Handles a request to retrieve jobs from the worker pool for a specified worker.
    
    Parameters:
        request (flask.Request): The incoming HTTP request object.
    
    Process:
        - Authenticates the request; returns 401 Unauthorized if authentication fails.
        - Extracts the 'workername' parameter from the query string; returns 400 Bad Request if missing.
        - Retrieves existing jobs for the worker from the worker pool.
        - Optionally fetches additional jobs if 'fetch_jobs' parameter is provided, extending the job list.
        - If no jobs are found, returns a 204 No Content response.
        - Otherwise, encodes the jobs in BSON format, compresses the data using LZ4, and returns it with appropriate headers.
    
    Returns:
        flask.Response: HTTP response containing compressed job data or an error/status code.
    """
    if not authenticate(request):
        return jsonify({'error': 'unauthorized'}), 401
    workername = request.args.get('workername')
    if workername is None:
        return jsonify({'error': 'workername is required'}), 400
    jobs = WorkerPool.get_jobs(workername)

    fetch_jobs = request.args.get('fetch_jobs')
    if fetch_jobs is not None:
        batch_jobs = WorkerPool.fetch_batch_job(workername, int(fetch_jobs))
        jobs.extend(batch_jobs)

    if len(jobs)==0:
        return Response(status=204)
    else:
        bson_data = bson.encode({'jobs':jobs})
        compressed = lz4f.compress(bson_data)
        return Response(
            compressed, 
            mimetype='application/octet-stream', 
            headers={'Content-Encoding': 'lz4'}
        )        

def post_workerpool(request):
    """
    Handles POST requests to create a new job in the worker pool.
    
    This function authenticates the incoming request, decompresses and decodes the BSON-encoded data,
    and attempts to add a new job to the worker pool. If authentication fails, it returns a 401 Unauthorized response.
    If the job is successfully added, it returns a 201 Created response.
    
    Args:
        request (flask.Request): The incoming HTTP request containing compressed BSON data.
    
    Returns:
        flask.Response: A response object indicating the result of the operation.
    """
    if not authenticate(request):
        return jsonify({'error': 'unauthorized'}), 401
    
    bson_data = lz4f.decompress(request.data)
    record = bson.decode(bson_data)
    
    if not 'sender' in record:
        raise Exception('sender not in record')
    if not 'target' in record:
        raise Exception('target not in record')
    if not 'job' in record:
        raise Exception('job not in record')
    
    record['target'] = str(record['target']).upper()
    if record['target'] == 'ALL':
        record['status'] = 'BROADCAST'
    else:
        record['status'] = 'NEW'
    
    if not 'date' in record:
        record['date'] = pd.Timestamp.utcnow().tz_localize(None)

    if not 'hash' in record:
        record['hash'] = CollectionMongoDB.get_hash(record)
                    
    record['mtime'] = pd.Timestamp.utcnow().tz_localize(None)

    coll = shdata.collection('Text','RT','WORKERPOOL','COMMANDS')
    coll.upsert(record)
    
    return Response(status=201)
 
@app.route('/api/webhooks', methods=['POST'])
def webhooks():
    """
    Handle POST requests to the '/api/webhooks' endpoint.
    
    Returns:
        - 201 Created on successful log receipt.
        - 401 Unauthorized if authentication fails.
        - 500 Internal Server Error with a JSON error message if an exception occurs during processing.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'invalid data'}), 400
        
        token = request.args.get('token')  # Not Optional
        if not token:
            token = request.headers.get('X-Custom-Authorization')
        if not token:
            token = request.headers.get('x-api-key')

        userdata = users[token]
        
        data['date'] = pd.Timestamp.utcnow()
        data['hash'] = userdata['email']
        
        coll = shdata.collection('Text','RT','WORKERPOOL','WEBHOOKS', hasindex=False)
        coll.extend(data)
        
        return Response(status=200)

    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        response = Response(status=500)
        return response

if __name__ == '__main__':
    from waitress import serve
    import logging
    # Suppress Waitress logs
    waitress_logger = logging.getLogger('waitress')
    waitress_logger.setLevel(logging.CRITICAL)
    waitress_logger.addHandler(logging.NullHandler())

    import threading
    import sys
    import time  
    import argparse
            
    parser = argparse.ArgumentParser(description="Server configuration")
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=8082, help='Server port number')
    parser.add_argument('--nthreads', type=int, default=8, help='Number of server threads')

    args = parser.parse_args()
    host = args.host
    port = args.port
    nthreads = args.nthreads    
        
    heartbeat_running = True  # Flag to control the heartbeat thread    
    def send_heartbeat():
        global heartbeat_running, traffic_rates
        heartbeat_interval = 15
        time.sleep(15)
        Logger.log.info('ROUTINE STARTED!')
        while heartbeat_running:
            current_time = time.time()
            with stats_lock:
                current_total_requests = traffic_stats['total_requests']
                current_total_bytes_sent = sum(ep['total_bytes_sent'] for ep in traffic_stats['endpoints'].values())
                current_total_bytes_received = sum(ep['total_bytes_received'] for ep in traffic_stats['endpoints'].values())
                
                # Calculate time elapsed since last heartbeat
                time_elapsed = current_time - traffic_rates['last_timestamp']
                if time_elapsed > 0:
                    # Calculate rates
                    requests_delta = current_total_requests - traffic_rates['last_total_requests']
                    bytes_sent_delta = current_total_bytes_sent - traffic_rates['last_total_bytes_sent']
                    bytes_received_delta = current_total_bytes_received - traffic_rates['last_total_bytes_received']
                    requests_per_sec = requests_delta / time_elapsed
                    bytes_sent_per_sec = bytes_sent_delta / time_elapsed
                    bytes_received_per_sec = bytes_received_delta / time_elapsed
                else:
                    requests_per_sec = 0.0
                    bytes_sent_per_sec = 0.0
                    bytes_received_per_sec = 0.0
                
                # Update the last values for the next iteration
                traffic_rates['last_total_requests'] = current_total_requests
                traffic_rates['last_total_bytes_sent'] = current_total_bytes_sent
                traffic_rates['last_total_bytes_received'] = current_total_bytes_received
                traffic_rates['last_timestamp'] = current_time

            # Log the heartbeat with rates
            Logger.log.debug('#heartbeat#host:%s,port:%i,reqs:%i,reqps:%.2f,download:%.2fMB/s,upload:%.2fMB/s' % 
                            (host, port, current_total_requests, requests_per_sec, 
                                bytes_received_per_sec/(1024**2), bytes_sent_per_sec/(1024**2)))
            time.sleep(heartbeat_interval)
            
    t = threading.Thread(target=send_heartbeat, args=(), daemon=True)
    t.start()    

    try:
        serve(
            app, 
            host=host, 
            port=port,  
            threads=nthreads,
            expose_tracebacks=False,
            asyncore_use_poll=True,
            _quiet=True,
            ident='SharedData'
        )
    except Exception as e:
        Logger.log.error(f"Waitress server encountered an error: {e}")
        heartbeat_running = False  # Stop the heartbeat thread
        t.join()  # Wait for the heartbeat thread to finish
        sys.exit(1)  # Exit the program with an error code
    finally:
        # This block will always execute, even if an exception occurs.
        # Useful for cleanup if needed.
        Logger.log.info("Server shutting down...")
        heartbeat_running = False  # Ensure heartbeat stops on normal shutdown
        t.join()  # Wait for heartbeat thread to finish
        Logger.log.info("Server shutdown complete.")