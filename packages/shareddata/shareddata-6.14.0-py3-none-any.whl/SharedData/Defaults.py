import os
from dotenv import load_dotenv
import socket

load_dotenv()  # take environment variables from .env.

if not 'SHAREDDATA_SERVER' in os.environ:
    os.environ['SHAREDDATA_SERVER'] = 'False'

if 'AWS_PROFILE' in os.environ:
    if not 'S3_AWS_PROFILE' in os.environ:
        os.environ['S3_AWS_PROFILE'] = os.environ['AWS_PROFILE']
    if not 'KINESIS_AWS_PROFILE' in os.environ:
        os.environ['KINESIS_AWS_PROFILE'] = os.environ['AWS_PROFILE']
else:    
    if (not 'AWS_ACCESS_KEY_ID' in os.environ)\
        or (not 'AWS_SECRET_ACCESS_KEY' in os.environ):
                
        if os.environ['SHAREDDATA_SERVER'] == 'True':
            raise Exception('Missing AWS login credentials environment variable!')

if not 'DATABASE_FOLDER' in os.environ:
    os.environ['DATABASE_FOLDER'] = os.path.expanduser("~")+'/db'

if not 'S3_BUCKET' in os.environ:
    os.environ['S3_BUCKET'] = 's3://shareddata'

if not 'LOG_API' in os.environ:
    os.environ['LOG_API'] = 'True'

if not 'LOG_FILE' in os.environ:
    os.environ['LOG_FILE'] = 'False'

if not 'LOG_KINESIS' in os.environ:
    os.environ['LOG_KINESIS'] = 'False'

if not 'LOG_STREAMNAME' in os.environ:
    os.environ['LOG_STREAMNAME'] = 'shareddata-logs'

if not 'WORKERPOOL_STREAM' in os.environ:
    os.environ['WORKERPOOL_STREAM'] = 'shareddata-workerpool'

if not 'USERNAME' in os.environ:        
    if 'USER' in os.environ:
        os.environ['USERNAME'] = os.environ['USER']
                    
if not 'COMPUTERNAME' in os.environ:
    os.environ['COMPUTERNAME'] = socket.gethostname().upper()

if not 'USER_COMPUTER' in os.environ:    
    os.environ['USER_COMPUTER'] = os.environ['USERNAME'] + \
        '@'+os.environ['COMPUTERNAME']

if not 'LOG_LEVEL' in os.environ:
    os.environ['LOG_LEVEL'] = 'INFO'

if not 'SAVE_LOCAL' in os.environ:
    os.environ['SAVE_LOCAL'] = 'True'

if not 'GIT_PROTOCOL' in os.environ:
    os.environ['GIT_PROTOCOL'] = 'https'

if not 'GIT_SERVER' in os.environ:
    os.environ['GIT_SERVER'] = 'github.com'

if not 'SOURCE_FOLDER' in os.environ:
    if 'USERPROFILE' in os.environ:
        os.environ['SOURCE_FOLDER'] = os.environ['USERPROFILE']+'/src/'
    elif 'HOME' in os.environ:
        os.environ['SOURCE_FOLDER'] = os.environ['HOME']+'/src/'

if not 'SLEEP_TIME' in os.environ:
    os.environ['SLEEP_TIME'] = '2'

if not 'KAFKA_RETENTION' in os.environ:
    os.environ['KAFKA_RETENTION'] = '84600000'  # 1 days

if not 'KAFKA_PARTITIONS' in os.environ:
    os.environ['KAFKA_PARTITIONS'] = '1'

if not 'KAFKA_REPLICATION' in os.environ:
    os.environ['KAFKA_REPLICATION'] = '3'


loaded = True
