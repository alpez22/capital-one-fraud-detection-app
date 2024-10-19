import json
import boto3
import random
import uuid
from decimal import Decimal  # To handle float conversion

# Initialize boto3 clients for SQS and DynamoDB
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

# Define the SQS Queue URL and DynamoDB Table Name
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/624438129884/data_ingestion_pipeline_queue'
DYNAMODB_TABLE_NAME = 'Transactions'

def convert_floats_to_decimal(data):
    """Recursively convert float values to Decimal for DynamoDB."""
    if isinstance(data, dict):
        return {k: convert_floats_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimal(i) for i in data]
    elif isinstance(data, float):  # Convert float to Decimal
        return Decimal(str(data))  # Use str to preserve precision
    return data

def lambda_handler(event, context):
    # Get the DynamoDB Table
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    # Poll the message from SQS
    response = sqs.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=1,  # Poll only one message at a time
        WaitTimeSeconds=10
    )
    
    # Check if any messages were received
    if 'Messages' in response:
        for message in response['Messages']:
            # Get the message body and convert it to JSON
            message_body = json.loads(message['Body'])
            
            # Modify the record by adding the 'is_fraud_detected' column
            message_body['is_fraud_detected'] = random.randint(0, 1)  # 0 for False, 1 for True
            
            # Add a unique identifier for DynamoDB (assuming no identifier was present)
            message_body['RecordId'] = message_body.get('recordId', str(uuid.uuid4()))  # Default to 'recordId' or new UUID
            
            # Ensure the accountId is converted to string (as DynamoDB expects it to be a string)
            if 'accountId' in message_body:
                message_body['accountId'] = str(message_body['accountId'])  # Convert accountId to string
            
            # Convert all float values in the message_body to Decimal
            message_body = convert_floats_to_decimal(message_body)

            # Write the record to DynamoDB
            table.put_item(Item=message_body)
            
            # Delete the message from SQS after successful processing
            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps('Record processed and written to DynamoDB')
            }
    
    return {
        'statusCode': 204,
        'body': json.dumps('No messages to process')
    }
