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
    
    table = dynamodb.Table(DYNAMO_DB_TABLE)
    
    # Set to track already processed transaction IDs
    processed_transactions = set()

    try:
        print("Scanning DynamoDB table for fraud detected accounts...")

        # Paginated scan
        last_evaluated_key = None
        while True:
            # Scan the table, but limit to fraud detected transactions (is_fraud_detected = 1)
            scan_params = {}
            if last_evaluated_key:
                scan_params['ExclusiveStartKey'] = last_evaluated_key

            response = table.scan(**scan_params)

            for item in response.get('Items', []):
                transaction_id = item.get('transaction_id')  # Updated field name
                is_fraud_detected = int(item.get('is_fraud_detected', 0))
                
                if is_fraud_detected == 1 and transaction_id not in processed_transactions:
                    # Extract relevant fields for fraud alert
                    amount = float(item.get('amount', 0))  
                    location = str(item.get('location', 'N/A'))
                    day = item.get('day', 'N/A')
                    month = item.get('month', 'N/A')
                    year = item.get('year', 'N/A')

                    location_address = LOCATIONS_TABLE.get(location, "Unknown Location")

                    transaction_date = f"{year}-{month}-{day}"

                    confirm_url = f"{API_BASE_URL}?action=confirm&transaction_id={urllib.parse.quote(transaction_id)}"
                    deny_url = f"{API_BASE_URL}?action=deny&transaction_id={urllib.parse.quote(transaction_id)}"

                    fraud_message = (
                        f"Fraud Alert - Account ID: {transaction_id}\n\n"
                        f"Amount: ${round(amount, 2)}\n"  # Rounded amount to 2 decimal places
                        f"Location: {location_address}\n"
                        f"Transaction Date: {transaction_date}\n"
                        f"Please confirm if this transaction is fraudulent:\n"
                        f"Confirm: {confirm_url}\n"
                        f"Deny: {deny_url}\n"
                    )

                    sns.publish(
                        TopicArn=topic_arn,
                        Message=fraud_message,
                        Subject=f'Fraud Alert - Account {transaction_id}'
                    )

                    processed_transactions.add(transaction_id)

            last_evaluated_key = response.get('LastEvaluatedKey', None)
            if not last_evaluated_key:
                break
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Fraud alert emails sent for all detected accounts.'})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
