import boto3
import json
import urllib.parse

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
DYNAMO_DB_TABLE = 'Transactions'

API_BASE_URL = 'https://mx2rbjpzug.execute-api.us-east-1.amazonaws.com/prod/confirmFraud'

def lambda_handler(event, context):
    topic_arn = 'arn:aws:sns:us-east-1:624438129884:FraudAlertEmail'
    
    # Scan the DynamoDB table for all items where fraud is detected
    table = dynamodb.Table(DYNAMO_DB_TABLE)
    
    try:
        print("Scanning DynamoDB table for fraud detected accounts...")

        # Scan the table to get all items (may be large data, use pagination if needed)
        response = table.scan()

        # List to keep track of fraud detected account names
        fraud_account_details = []

        # Loop through each item in the response
        for item in response.get('Items', []):
            account_id = item.get('accountId')
            is_fraud_detected = item.get('is_fraud_detected', 0)  # Default to 0 if not found
            
            if is_fraud_detected == 1:
                # Collect details for fraud detected accounts
                amount = item.get('amount', 0)  
                transaction_date = item.get('transactionDate', 'N/A')
                transaction_location = item.get('transactionLocation', 'N/A')

                # URL encode the account ID and other params
                confirm_url = f"{API_BASE_URL}?action=confirm&accountId={urllib.parse.quote(account_id)}"
                deny_url = f"{API_BASE_URL}?action=deny&accountId={urllib.parse.quote(account_id)}"

                fraud_account_details.append(
                    {
                        "account_id": account_id,
                        "amount": amount,
                        "transaction_date": transaction_date,
                        "transaction_location": transaction_location,
                        "confirm_url": confirm_url,
                        "deny_url": deny_url
                    }
                )
        
        if not fraud_account_details:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No fraud detected for any accounts.'})
            }
        
        # Build a message listing all the accounts with fraud detected
        fraud_message = "The following accounts have fraud detected:\n\n"
        for fraud in fraud_account_details:
            fraud_message += (f"Account ID: {fraud['account_id']}\n"
                              f"Amount: {fraud['amount']}\n"
                              f"Transaction Date: {fraud['transaction_date']}\n"
                              f"Transaction Location: {fraud['transaction_location']}\n"
                              f"Please confirm if this transaction is fraudulent:\n"
                              f"Confirm: {fraud['confirm_url']}\n"
                              f"Deny: {fraud['deny_url']}\n\n")
        
        # Send an email notification with the fraud details
        sns.publish(
            TopicArn=topic_arn,
            Message=fraud_message,
            Subject='Fraud Alert - Accounts Detected'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Fraud alert email sent with detected account details.'})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
