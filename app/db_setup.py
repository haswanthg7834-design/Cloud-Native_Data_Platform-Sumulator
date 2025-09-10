import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, Float, DateTime, Boolean
import os
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, db_type='sqlite', connection_string=None):
        self.db_type = db_type
        self.connection_string = connection_string or 'sqlite:///dataplatform.db'
        self.engine = None
        self.setup_connection()
    
    def setup_connection(self):
        """Setup database connection"""
        try:
            self.engine = create_engine(self.connection_string, echo=False)
            logger.info(f"Database connection established: {self.db_type}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def create_tables(self):
        """Create database tables with proper schemas"""
        try:
            metadata = MetaData()
            
            customers_table = Table(
                'customers', metadata,
                Column('customer_id', String(20), primary_key=True),
                Column('first_name', String(50)),
                Column('last_name', String(50)),
                Column('email', String(100)),
                Column('phone', String(20)),
                Column('registration_date', DateTime),
                Column('age', Integer),
                Column('city', String(50)),
                Column('state', String(10)),
                Column('segment', String(20)),
                Column('is_active', Boolean)
            )
            
            transactions_table = Table(
                'transactions', metadata,
                Column('transaction_id', String(20), primary_key=True),
                Column('customer_id', String(20)),
                Column('transaction_date', DateTime),
                Column('amount', Float),
                Column('currency', String(5)),
                Column('transaction_type', String(20)),
                Column('merchant', String(50)),
                Column('category', String(30)),
                Column('payment_method', String(20)),
                Column('status', String(20))
            )
            
            events_table = Table(
                'events', metadata,
                Column('event_id', String(20), primary_key=True),
                Column('customer_id', String(20)),
                Column('timestamp', DateTime),
                Column('event_type', String(30)),
                Column('page_url', String(100)),
                Column('session_id', String(20)),
                Column('device_type', String(20)),
                Column('browser', String(20)),
                Column('ip_address', String(15)),
                Column('user_agent', String(200))
            )
            
            products_table = Table(
                'products', metadata,
                Column('product_id', String(20), primary_key=True),
                Column('name', String(100)),
                Column('category', String(30)),
                Column('subcategory', String(50)),
                Column('price', Float),
                Column('cost', Float),
                Column('stock_quantity', Integer),
                Column('supplier', String(50)),
                Column('created_date', DateTime),
                Column('is_active', Boolean),
                Column('weight_kg', Float),
                Column('dimensions', String(50))
            )
            
            metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def load_csv_to_database(self, csv_path, table_name, if_exists='replace'):
        """Load CSV data into database table"""
        try:
            df = pd.read_csv(csv_path)
            
            if table_name == 'customers':
                df['registration_date'] = pd.to_datetime(df['registration_date'])
                df['is_active'] = df['is_active'].astype(bool)
            elif table_name == 'transactions':
                df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            elif table_name == 'events':
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            elif table_name == 'products':
                df['created_date'] = pd.to_datetime(df['created_date'])
                df['is_active'] = df['is_active'].astype(bool)
            
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(f"Loaded {len(df)} records into {table_name} table")
            
        except Exception as e:
            logger.error(f"Error loading {csv_path} to {table_name}: {e}")
            raise
    
    def load_all_data(self, data_path='../data/raw/'):
        """Load all CSV files into database"""
        csv_files = {
            'customers.csv': 'customers',
            'transactions.csv': 'transactions', 
            'events.csv': 'events',
            'products.csv': 'products'
        }
        
        for csv_file, table_name in csv_files.items():
            file_path = os.path.join(data_path, csv_file)
            if os.path.exists(file_path):
                self.load_csv_to_database(file_path, table_name)
            else:
                logger.warning(f"File not found: {file_path}")
    
    def create_views(self):
        """Create useful database views for analytics"""
        try:
            views = {
                'customer_summary': '''
                    CREATE VIEW IF NOT EXISTS customer_summary AS
                    SELECT 
                        c.customer_id,
                        c.first_name,
                        c.last_name,
                        c.segment,
                        c.registration_date,
                        COUNT(t.transaction_id) as total_transactions,
                        COALESCE(SUM(t.amount), 0) as total_spent,
                        COALESCE(AVG(t.amount), 0) as avg_order_value,
                        MIN(t.transaction_date) as first_purchase,
                        MAX(t.transaction_date) as last_purchase
                    FROM customers c
                    LEFT JOIN transactions t ON c.customer_id = t.customer_id
                    GROUP BY c.customer_id, c.first_name, c.last_name, c.segment, c.registration_date
                ''',
                
                'daily_metrics': '''
                    CREATE VIEW IF NOT EXISTS daily_metrics AS
                    SELECT 
                        DATE(transaction_date) as date,
                        COUNT(*) as daily_transactions,
                        SUM(amount) as daily_revenue,
                        AVG(amount) as avg_transaction_value,
                        COUNT(DISTINCT customer_id) as unique_customers
                    FROM transactions
                    WHERE status = 'completed'
                    GROUP BY DATE(transaction_date)
                    ORDER BY date
                ''',
                
                'monthly_trends': '''
                    CREATE VIEW IF NOT EXISTS monthly_trends AS
                    SELECT 
                        strftime('%Y-%m', transaction_date) as month,
                        COUNT(*) as monthly_transactions,
                        SUM(amount) as monthly_revenue,
                        COUNT(DISTINCT customer_id) as unique_customers,
                        AVG(amount) as avg_order_value
                    FROM transactions
                    WHERE status = 'completed'
                    GROUP BY strftime('%Y-%m', transaction_date)
                    ORDER BY month
                '''
            }
            
            with self.engine.connect() as conn:
                for view_name, view_sql in views.items():
                    conn.execute(text(view_sql))
                    conn.commit()
                    logger.info(f"Created view: {view_name}")
                    
        except Exception as e:
            logger.error(f"Error creating views: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)",
                "CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(segment)",
                "CREATE INDEX IF NOT EXISTS idx_events_customer_id ON events(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)"
            ]
            
            with self.engine.connect() as conn:
                for index_sql in indexes:
                    conn.execute(text(index_sql))
                    conn.commit()
                    
            logger.info("Database indexes created successfully")
                    
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise
    
    def validate_data_quality(self):
        """Validate data quality in database"""
        try:
            quality_checks = {}
            
            with self.engine.connect() as conn:
                tables_to_check = ['customers', 'transactions', 'events', 'products']
                
                for table in tables_to_check:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    quality_checks[f"{table}_count"] = count
                    
                    if table == 'transactions':
                        result = conn.execute(text("SELECT COUNT(*) FROM transactions WHERE amount < 0"))
                        negative_amounts = result.scalar()
                        quality_checks["negative_amounts"] = negative_amounts
                        
                        result = conn.execute(text("SELECT COUNT(*) FROM transactions WHERE customer_id IS NULL"))
                        null_customers = result.scalar()
                        quality_checks["null_customer_ids"] = null_customers
                    
                    if table == 'customers':
                        result = conn.execute(text("SELECT COUNT(*) FROM customers WHERE email IS NULL OR email = ''"))
                        null_emails = result.scalar()
                        quality_checks["null_emails"] = null_emails
                
                logger.info("Data quality validation completed")
                return quality_checks
                
        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            raise
    
    def export_sample_queries(self):
        """Export sample SQL queries for common analytics"""
        queries = {
            "top_customers_by_revenue": '''
                SELECT customer_id, total_spent, total_transactions
                FROM customer_summary
                ORDER BY total_spent DESC
                LIMIT 10;
            ''',
            
            "monthly_revenue_growth": '''
                SELECT 
                    month,
                    monthly_revenue,
                    LAG(monthly_revenue) OVER (ORDER BY month) as prev_month_revenue,
                    ROUND(
                        ((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month)) / 
                         LAG(monthly_revenue) OVER (ORDER BY month)) * 100, 2
                    ) as growth_percentage
                FROM monthly_trends
                ORDER BY month;
            ''',
            
            "customer_churn_analysis": '''
                SELECT 
                    segment,
                    COUNT(*) as total_customers,
                    COUNT(CASE WHEN julianday('now') - julianday(last_purchase) > 90 THEN 1 END) as churned,
                    ROUND(
                        COUNT(CASE WHEN julianday('now') - julianday(last_purchase) > 90 THEN 1 END) * 100.0 / COUNT(*), 2
                    ) as churn_rate
                FROM customer_summary
                WHERE total_transactions > 0
                GROUP BY segment;
            ''',
            
            "product_performance": '''
                SELECT 
                    p.category,
                    COUNT(DISTINCT t.transaction_id) as transactions,
                    SUM(t.amount) as revenue,
                    AVG(t.amount) as avg_transaction_value
                FROM products p
                LEFT JOIN transactions t ON p.category = t.category
                GROUP BY p.category
                ORDER BY revenue DESC;
            '''
        }
        
        queries_path = '../app/queries.sql'
        with open(queries_path, 'w') as f:
            f.write("-- Sample Analytics Queries for Cloud-Native Data Platform\\n\\n")
            for query_name, query_sql in queries.items():
                f.write(f"-- {query_name.replace('_', ' ').title()}\\n")
                f.write(f"{query_sql}\\n\\n")
        
        logger.info(f"Sample queries exported to {queries_path}")
        
        return queries
    
    def setup_database(self, data_path='../data/raw/'):
        """Complete database setup process"""
        try:
            logger.info("Starting database setup...")
            
            self.create_tables()
            self.load_all_data(data_path)
            self.create_views()
            self.create_indexes()
            
            quality_report = self.validate_data_quality()
            logger.info(f"Data quality report: {quality_report}")
            
            self.export_sample_queries()
            
            setup_summary = {
                "setup_completed": datetime.now().isoformat(),
                "database_type": self.db_type,
                "connection_string": self.connection_string,
                "data_quality": quality_report,
                "status": "success"
            }
            
            with open('../app/db_setup_log.json', 'w') as f:
                json.dump(setup_summary, f, indent=2)
            
            logger.info("Database setup completed successfully!")
            return setup_summary
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

def main():
    """Main function to run database setup"""
    try:
        db_setup = DatabaseSetup()
        summary = db_setup.setup_database()
        
        print("\\n" + "="*50)
        print("DATABASE SETUP COMPLETED")
        print("="*50)
        print(f"Database: {summary['database_type']}")
        print(f"Status: {summary['status']}")
        print(f"Completed: {summary['setup_completed']}")
        print("\\nData Quality Summary:")
        for key, value in summary['data_quality'].items():
            print(f"  {key}: {value}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()