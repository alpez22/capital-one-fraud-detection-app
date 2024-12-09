from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import boto3
import io

# Initialize Flask app and S3 client
app = Flask(__name__)
app.secret_key = 'J31p3u8tO4UHfJMuJbXlyqScqhWprv/49wltSGyG'
s3 = boto3.client('s3')

# Set S3 bucket name and the CSV key
BUCKET_NAME = 'c1-fraud-detection-data'
CSV_KEY = 'synthetic_transactions.csv'

def fetch_transactions_from_s3():
    """Fetch the transactions from the CSV file in S3, or create a new DataFrame if it doesn't exist."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_KEY)
        return pd.read_csv(io.BytesIO(response['Body'].read()))
    except s3.exceptions.NoSuchKey:
        # If the file doesn't exist, return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['amount', 'transaction_time', 
                                     'location', 'location_id', 'merchant_id', 'device_id',
                                     'customer_age', 'num_prev_transactions', 'credit_score', 'year', 
                                     'month', 'day', 'transaction_id'])

def upload_transactions_to_s3(df):
    """Upload the updated DataFrame back to the S3 bucket."""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=BUCKET_NAME, Key=CSV_KEY, Body=csv_buffer.getvalue())

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get form data
        amount = float(request.form['amount'])
        transaction_time = request.form['transactionTime']
        location = request.form['location']
        location_id = request.form['locationId']
        merchant_id = request.form['merchantId']
        device_id = request.form['deviceId']
        customer_age = int(request.form['customerAge'])
        num_prev_transactions = int(request.form['numPrevTransactions'])
        credit_score = int(request.form['creditScore'])
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        transaction_id = request.form['transaction_id']

        # Fetch the current transactions, append new entry, and upload back to S3
        df = fetch_transactions_from_s3()
        new_transaction = pd.DataFrame([{
            'amount': amount,
            'transaction_time': transaction_time,
            'location': location,
            'location_id': location_id,
            'merchant_id': merchant_id,
            'device_id': device_id,
            'customer_age': customer_age,
            'num_prev_transactions': num_prev_transactions,
            'credit_score': credit_score,
            'year': year,
            'month': month,
            'day': day,
            'transaction_id': transaction_id
        }])
        updated_df = pd.concat([df, new_transaction], ignore_index=True)
        upload_transactions_to_s3(updated_df)
        
        # Redirect to the home page after submission
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('home'))

    # Render the form to input transactions
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
