import boto3
import json
import urllib.parse

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
DYNAMO_DB_TABLE = 'synthetic_transactions'

API_BASE_URL = 'https://mx2rbjpzug.execute-api.us-east-1.amazonaws.com/prod/confirmFraud'

LOCATIONS_TABLE = {
    "0": "123 Elm Street, Springfield, IL",
    "1": "456 Oak Avenue, St. Louis, MO", 
    "2": "789 Pine Road, Miami, FL",
    "3": "321 Maple Lane, Madison, WI",    
    "4": "654 Birch Drive, Denver, CO",
    "5": "987 Cedar Court, Boston, MA",
    "6": "246 Aspen Way, Phoenix, AZ",
    "7": "135 Willow Street, Nashville, TN",
    "8": "864 Sycamore Boulevard, San Diego, CA",
    "9": "753 Redwood Circle, New York, NY"
}


def lambda_handler(event, context):
    topic_arn = 'arn:aws:sns:us-east-1:624438129884:tempemail'

    transaction_id = event.get('transaction_id', None)
    
    if transaction_id is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'transaction_id is required'})
        }

    table = dynamodb.Table(DYNAMO_DB_TABLE)

    try:
        print(f"Fetching item with transaction_id: {transaction_id}")

        response = table.get_item(
            Key={
                'transaction_id': transaction_id  
            }
        )

        if 'Item' in response:
            item = response['Item']
            is_fraud_detected = int(item.get('is_fraud_detected', 0))
            
            if is_fraud_detected == 1:
                amount = float(item.get('amount', 0))
                location = str(item.get('location', 'N/A'))
                day = item.get('day', 'N/A')
                month = item.get('month', 'N/A')
                year = item.get('year', 'N/A')
            
                location_address = LOCATIONS_TABLE.get(location, "Unknown Location")
            
                transaction_date = f"{year}-{month}-{day}"
            
                confirm_url = f"{API_BASE_URL}?action=confirm&transaction_id={urllib.parse.quote(transaction_id)}"
                deny_url = f"{API_BASE_URL}?action=deny&transaction_id={urllib.parse.quote(transaction_id)}"
            
                message = (f"Fraud detected for the following transaction:\n"
                           f"Account ID: {transaction_id}\n"
                           f"Amount: ${round(amount, 2)}\n"  
                           f"Location: {location_address}\n"
                           f"Transaction Time: {transaction_date}\n"
                           f"Please confirm if this transaction is fraudulent:\n"
                           f"Confirm: {confirm_url}\n"
                           f"Deny: {deny_url}")
                
                # Add transaction_id to the subject to personalize it
                subject = f"Fraud Alert for Account ID: {transaction_id}"

                sns.publish(
                    TopicArn=topic_arn,
                    Message=message,
                    Subject=subject
                )
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Fraud alert email sent!'})
                }
            else:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'No fraud detected for this transaction.'})
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transaction not found'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
