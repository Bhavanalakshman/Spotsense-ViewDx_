import boto3
import json
import os
from utils.constants import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION

# SET AWS CREDENTAILS AS OS ENVIRONMENTAL VARIABLES
os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_KEY
os.environ['AWS_DEFAULT_REGION'] = AWS_REGION

dynamo_client = boto3.client('dynamodb')
dynamo_db = boto3.resource('dynamodb')

REQ_TABLE = None

# GET EXACT Requisition TABLE NAME
for tableName in dynamo_client.list_tables()['TableNames']:
    if( tableName.split('-')[0] == 'Requisition'):
        REQ_TABLE = dynamo_db.Table(tableName)
print(REQ_TABLE)
