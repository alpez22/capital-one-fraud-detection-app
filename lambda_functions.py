import boto3
import csv
import io

# Initialize DynamoDB and S3 clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Define your DynamoDB table
table_name = 'YourDynamoDBTable'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # Get the bucket and file information from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    csv_file_key = event['Records'][0]['s3']['object']['key']
    
    # Fetch the CSV file from S3
    csv_file_obj = s3_client.get_object(Bucket=bucket_name, Key=csv_file_key)
    
    # Read the CSV content
    csv_file_content = csv_file_obj['Body'].read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_file_content))
    
    # Stream the CSV data to DynamoDB
    for row in csv_reader:
        try:
            # Put each row into DynamoDB (assuming each row has a 'PrimaryKey' field for the partition key)
            table.put_item(Item=row)
        except Exception as e:
            print(f"Error inserting row {row}: {e}")
    
    return {
        'statusCode': 200,
        'body': 'CSV data processed and uploaded to DynamoDB successfully!'
    }
