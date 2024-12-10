import boto3
import json

dynamodb = boto3.resource('dynamodb')
DYNAMO_DB_TABLE = 'synthetic_transactions'  # Updated table name

def lambda_handler(event, context):
    # Extract parameters from the query string
    action = event['queryStringParameters'].get('action')
    transaction_id = event['queryStringParameters'].get('transaction_id')  # Updated to transaction_id

    # Validate input
    if action not in ['confirm', 'deny'] or not transaction_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request parameters'})
        }
    
    table = dynamodb.Table(DYNAMO_DB_TABLE)
    
    # Determine fraud status based on the action
    is_fraud_detected = 1 if action == 'confirm' else 0

    try:
        # Update the record in DynamoDB
        response = table.update_item(
            Key={'transaction_id': transaction_id},  # Use transaction_id as the primary key
            UpdateExpression="set is_fraud_detected = :val",  # Update the fraud detection flag
            ExpressionAttributeValues={':val': is_fraud_detected},
            ReturnValues="UPDATED_NEW"
        )
        
        # Return a success message
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Transaction {transaction_id} marked as {"fraudulent" if is_fraud_detected else "not fraudulent"}.'})
        }
    except Exception as e:
        # Return error message in case of failure
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
