import boto3
import json

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
DYNAMO_DB_TABLE = 'Transactions'

def lambda_handler(event, context):
    topic_arn = 'arn:aws:sns:us-east-1:624438129884:FraudAlertEmail'
    
    account_id = event.get('accountId', None)

    if account_id is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'accountId is required'})
        }

    table = dynamodb.Table(DYNAMO_DB_TABLE)

    try:
        print(f"Fetching item with accountId: {account_id}")

        response = table.get_item(
            Key={
                'accountId': account_id  
            }
        )

        # Make sure the item exists
        if 'Item' in response:
            item = response['Item']
            is_fraud_detected = item.get('is_fraud_detected', 0)  
            
            if is_fraud_detected == 1:
                amount = item.get('amount', 0)  
                transaction_date = item.get('transactionDate', 'N/A')
                transaction_location = item.get('transactionLocation', 'N/A')

                # Message sent
                message = (f"Fraud detected for the following transaction:\n"
                           f"Account ID: {account_id}\n"
                           f"Amount: {amount}\n"
                           f"Transaction Date: {transaction_date}\n"
                           f"Transaction Location: {transaction_location}")
                
                # Send an email notification 
                sns.publish(
                    TopicArn=topic_arn,
                    Message=message,
                    Subject='Fraud Alert Notification'
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
