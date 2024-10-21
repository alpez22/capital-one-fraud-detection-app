from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import boto3
import io

# Initialize Flask app and S3 client
app = Flask(__name__)
s3 = boto3.client('s3')

# Set S3 bucket name and the CSV key
BUCKET_NAME = 'c1-fraud-detection-data'
CSV_KEY = 'test-transaction.csv'

def fetch_transactions_from_s3():
    """Fetch the transactions from the CSV file in S3, or create a new DataFrame if it doesn't exist."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_KEY)
        return pd.read_csv(io.BytesIO(response['Body'].read()))
    except s3.exceptions.NoSuchKey:
        # If the file doesn't exist, return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['accountId', 'amount', 'vendorName', 
                                     'transactionLocation', 'transactionDate'])

def upload_transactions_to_s3(df):
    """Upload the updated DataFrame back to the S3 bucket."""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=BUCKET_NAME, Key=CSV_KEY, Body=csv_buffer.getvalue())

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get form data
        account_id = request.form['accountId']
        amount = float(request.form['amount'])
        vendor_name = request.form['vendorName']
        transaction_location = request.form['transactionLocation']
        transaction_date = request.form['transactionDate']

        # Fetch the current transactions, append new entry, and upload back to S3
        df = fetch_transactions_from_s3()
        new_transaction = pd.DataFrame([{
            'accountId': account_id,
            'amount': amount,
            'vendorName': vendor_name,
            'transactionLocation': transaction_location,
            'transactionDate': transaction_date
        }])
        updated_df = pd.concat([df, new_transaction], ignore_index=True)
        upload_transactions_to_s3(updated_df)

        # Redirect to the home page after submission
        return redirect(url_for('home'))

    # Render the form to input transactions
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
