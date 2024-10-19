import boto3
import pandas as pd
import io
import json

# Initialize the SQS client
sqs = boto3.client('sqs')
s3 = boto3.client('s3')

def stream_csv_from_s3(bucket_name, key, chunk_size=1000):
    """Generator to stream a CSV file from S3 in chunks."""
    response = s3.get_object(Bucket=bucket_name, Key=key)
    for chunk in pd.read_csv(io.BytesIO(response['Body'].read()), chunksize=chunk_size):
        yield chunk

def send_message_to_sqs(queue_url, message):
    """Send a message to SQS."""
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

def lambda_handler(event, context):
    """Lambda function to stream data from S3 and send to SQS."""
    bucket_name = event['bucket_name']
    transactions_key = event['transactions_key']
    sqs_url = event['sqs_url']

    # Stream and send messages to SQS
    for transactions_chunk in stream_csv_from_s3(bucket_name, transactions_key):
        for _, row in transactions_chunk.iterrows():
            send_message_to_sqs(sqs_url, row.to_dict())

    return {
        'statusCode': 200,
        'body': 'Messages sent to SQS successfully.'
    }