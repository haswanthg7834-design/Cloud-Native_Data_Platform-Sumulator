import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

def generate_customers(num_customers=1000):
    """Generate sample customer data"""
    np.random.seed(42)
    random.seed(42)
    
    customers = []
    for i in range(num_customers):
        customer = {
            'customer_id': f'CUST_{i+1:06d}',
            'first_name': random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa']),
            'last_name': random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']),
            'email': f'customer{i+1}@email.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'registration_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'age': random.randint(18, 80),
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']),
            'state': random.choice(['CA', 'TX', 'NY', 'FL', 'IL', 'PA', 'OH', 'GA']),
            'segment': random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
            'is_active': random.choices([True, False], weights=[0.8, 0.2])[0]
        }
        customers.append(customer)
    
    return pd.DataFrame(customers)

def generate_transactions(num_transactions=10000):
    """Generate sample transaction data"""
    np.random.seed(42)
    random.seed(42)
    
    transactions = []
    for i in range(num_transactions):
        transaction = {
            'transaction_id': f'TXN_{i+1:08d}',
            'customer_id': f'CUST_{random.randint(1, 1000):06d}',
            'transaction_date': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S'),
            'amount': round(random.uniform(10, 1000), 2),
            'currency': random.choices(['USD', 'EUR', 'GBP'], weights=[0.7, 0.2, 0.1])[0],
            'transaction_type': random.choice(['purchase', 'refund', 'transfer', 'deposit']),
            'merchant': random.choice(['Amazon', 'Walmart', 'Target', 'Best Buy', 'Costco', 'Home Depot', 'Starbucks', 'McDonald\'s']),
            'category': random.choice(['retail', 'food', 'entertainment', 'utilities', 'healthcare', 'transportation']),
            'payment_method': random.choice(['credit_card', 'debit_card', 'paypal', 'bank_transfer']),
            'status': random.choices(['completed', 'pending', 'failed'], weights=[0.85, 0.1, 0.05])[0]
        }
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)

def generate_events(num_events=5000):
    """Generate sample event data for user behavior tracking"""
    np.random.seed(42)
    random.seed(42)
    
    events = []
    for i in range(num_events):
        event = {
            'event_id': f'EVT_{i+1:08d}',
            'customer_id': f'CUST_{random.randint(1, 1000):06d}',
            'timestamp': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d %H:%M:%S'),
            'event_type': random.choice(['login', 'logout', 'page_view', 'click', 'purchase_start', 'purchase_complete', 'search']),
            'page_url': f'/page/{random.randint(1, 50)}',
            'session_id': f'SESS_{random.randint(1, 2000):06d}',
            'device_type': random.choices(['desktop', 'mobile', 'tablet'], weights=[0.5, 0.4, 0.1])[0],
            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
            'ip_address': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'user_agent': 'Mozilla/5.0 (compatible)'
        }
        events.append(event)
    
    return pd.DataFrame(events)

def generate_products(num_products=500):
    """Generate sample product catalog data"""
    np.random.seed(42)
    random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Health & Beauty']
    
    products = []
    for i in range(num_products):
        category = random.choice(categories)
        product = {
            'product_id': f'PROD_{i+1:06d}',
            'name': f'{category} Product {i+1}',
            'category': category,
            'subcategory': f'{category} Sub {random.randint(1, 5)}',
            'price': round(random.uniform(10, 500), 2),
            'cost': round(random.uniform(5, 300), 2),
            'stock_quantity': random.randint(0, 1000),
            'supplier': f'Supplier {random.randint(1, 20)}',
            'created_date': (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
            'is_active': random.choices([True, False], weights=[0.9, 0.1])[0],
            'weight_kg': round(random.uniform(0.1, 10), 2),
            'dimensions': f'{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)} cm'
        }
        products.append(product)
    
    return pd.DataFrame(products)

if __name__ == "__main__":
    # Generate all datasets
    print("Generating sample datasets...")
    
    customers_df = generate_customers()
    transactions_df = generate_transactions()
    events_df = generate_events()
    products_df = generate_products()
    
    # Save to CSV files
    customers_df.to_csv('customers.csv', index=False)
    transactions_df.to_csv('transactions.csv', index=False)
    events_df.to_csv('events.csv', index=False)
    products_df.to_csv('products.csv', index=False)
    
    # Also save some data as JSON for API simulation
    sample_customers = customers_df.head(10).to_dict('records')
    with open('sample_customers.json', 'w') as f:
        json.dump(sample_customers, f, indent=2)
    
    print("Sample data generated successfully!")
    print(f"- Customers: {len(customers_df)} records")
    print(f"- Transactions: {len(transactions_df)} records")
    print(f"- Events: {len(events_df)} records")
    print(f"- Products: {len(products_df)} records")