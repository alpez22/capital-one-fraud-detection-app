import pandas as pd

# Load the customer data
df = pd.read_csv("customers.csv")

# Generate email addresses
def generate_email(first_name, last_name):
    email_domain = "example.com"  # Common domain for example purposes
    email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"
    return email

# Add a new column for email
df['email'] = df.apply(lambda row: generate_email(row['firstName'], row['lastName']), axis=1)

# Save the updated DataFrame to a new CSV
df.to_csv("customers_with_email.csv", index=False)

print("Updated CSV with emails saved as 'customers_with_email.csv'.")
