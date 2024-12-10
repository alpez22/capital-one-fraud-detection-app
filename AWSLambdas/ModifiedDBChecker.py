import boto3
import json
import urllib.parse

sns = boto3.client('sns')

TOPIC_ARN = 'arn:aws:sns:us-east-1:624438129884:tempemail'
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

API_BASE_URL = 'https://mx2rbjpzug.execute-api.us-east-1.amazonaws.com/prod/confirmFraud'

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            print(f"Processing record: {json.dumps(record)}")  # Log the entire record for debugging
            
            if record['eventName'] == 'MODIFY': 
                new_image = record['dynamodb'].get('NewImage', {})
                old_image = record['dynamodb'].get('OldImage', {})
                
                #print(f"Old Image: {json.dumps(old_image)}")  # Log old image
                #print(f"New Image: {json.dumps(new_image)}")  # Log new image

                # Check if is_fraud_detected transitioned to 1
                new_is_fraud_detected = new_image.get('is_fraud_detected', {}).get('S', '0')
                old_is_fraud_detected = old_image.get('is_fraud_detected', {}).get('S', '0')

                #print(f"Old is_fraud_detected: {old_is_fraud_detected}, New is_fraud_detected: {new_is_fraud_detected}")  # Log fraud detection status
                
                if old_is_fraud_detected == '0' and new_is_fraud_detected == '1':
                    # Extract details from the new image
                    transaction_id = new_image.get('transaction_id', {}).get('S', 'Unknown')
                    amount = float(new_image.get('amount', {}).get('S', 0))  # Make sure amount is extracted as a float
                    location = new_image.get('location', {}).get('S', 'N/A')
                    day = new_image.get('day', {}).get('S', 'N/A')
                    month = new_image.get('month', {}).get('S', 'N/A')
                    year = new_image.get('year', {}).get('S', 'N/A')

                    location_address = LOCATIONS_TABLE.get(location, "Unknown Location")
                    transaction_date = f"{year}-{month}-{day}"

                    confirm_url = f"{API_BASE_URL}?action=confirm&transaction_id={urllib.parse.quote(transaction_id)}"
                    deny_url = f"{API_BASE_URL}?action=deny&transaction_id={urllib.parse.quote(transaction_id)}"

                    fraud_message = (
                        f"Fraud Alert - Account ID: {transaction_id}\n\n"
                        f"Amount: ${round(amount, 2)}\n"
                        f"Location: {location_address}\n"
                        f"Transaction Date: {transaction_date}\n"
                        f"Please confirm if this transaction is fraudulent:\n"
                        f"Confirm: {confirm_url}\n"
                        f"Deny: {deny_url}\n"
                    )

                    #print(f"Fraud message: {fraud_message}")  # Log the fraud message being sent
                    
                    # Publish to SNS
                    response = sns.publish(
                        TopicArn=TOPIC_ARN,
                        Message=fraud_message,
                        Subject=f'Fraud Alert - Account {transaction_id}'
                    )
                    
                    #print(f"SNS response: {json.dumps(response)}")  # Log SNS response
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processed DynamoDB stream records successfully.'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")  # Log any error that occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
