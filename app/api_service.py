from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import sqlite3
from sqlalchemy import create_engine, text
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cloud-Native Data Platform API",
    description="REST API for accessing analytics and metrics from the data platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')

class DatabaseConnection:
    def __init__(self):
        self.engine = None
        self.setup_connection()
    
    def setup_connection(self):
        try:
            self.engine = create_engine('sqlite:///dataplatform.db')
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.engine = None
    
    def get_connection(self):
        if self.engine:
            return self.engine
        else:
            raise HTTPException(status_code=500, detail="Database connection not available")

db = DatabaseConnection()

class MetricsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: Optional[str] = None

class ChurnMetrics(BaseModel):
    churn_rate: float
    at_risk_customers: int
    churned_customers: int
    total_customers: int

class CustomerSegment(BaseModel):
    segment: str
    customer_count: int
    avg_revenue: float
    percentage: float

@app.middleware("http")
async def track_requests(request, call_next):
    start_time = datetime.now()
    
    response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds()
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

def load_data():
    """Load data from CSV files or database"""
    try:
        data_path = '../data/raw/'
        datasets = {}
        
        csv_files = ['customers.csv', 'transactions.csv', 'events.csv', 'products.csv']
        
        for file in csv_files:
            file_path = os.path.join(data_path, file)
            if os.path.exists(file_path):
                dataset_name = file.replace('.csv', '')
                datasets[dataset_name] = pd.read_csv(file_path)
        
        if not datasets:
            logger.error("No data files found")
            return None
        
        datasets['transactions']['transaction_date'] = pd.to_datetime(datasets['transactions']['transaction_date'])
        datasets['customers']['registration_date'] = pd.to_datetime(datasets['customers']['registration_date'])
        
        return datasets
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

data = load_data()

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Cloud-Native Data Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "database": "connected" if db.engine else "disconnected",
        "data_loaded": "yes" if data else "no",
        "timestamp": datetime.now().isoformat()
    }
    
    if not data:
        raise HTTPException(status_code=503, detail="Data not available")
    
    return health_status

@app.get("/metrics/churn", response_model=MetricsResponse)
async def get_churn_metrics():
    """Get customer churn metrics"""
    if not data:
        raise HTTPException(status_code=503, detail="Data not available")
    
    try:
        customers_df = data['customers']
        transactions_df = data['transactions']
        
        current_date = datetime.now()
        last_transaction = transactions_df.groupby('customer_id')['transaction_date'].max()
        
        days_since_last = (current_date - last_transaction).dt.days
        
        churn_threshold = 90
        at_risk_threshold = 60
        
        churned = (days_since_last > churn_threshold).sum()
        at_risk = ((days_since_last > at_risk_threshold) & (days_since_last <= churn_threshold)).sum()
        total_customers = len(customers_df)
        churn_rate = (churned / total_customers) * 100 if total_customers > 0 else 0
        
        churn_data = {
            "churn_rate": round(churn_rate, 2),
            "churned_customers": int(churned),
            "at_risk_customers": int(at_risk),
            "total_customers": total_customers,
            "active_customers": total_customers - churned,
            "churn_threshold_days": churn_threshold
        }
        
        return MetricsResponse(
            success=True,
            data=churn_data,
            timestamp=datetime.now().isoformat(),
            message="Churn metrics calculated successfully"
        )
    except Exception as e:
        logger.error(f"Error calculating churn metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/anomalies", response_model=MetricsResponse)
async def get_anomaly_metrics():
    """Get transaction anomalies"""
    if not data:
        raise HTTPException(status_code=503, detail="Data not available")
    
    try:
        transactions_df = data['transactions']
        
        mean_amount = transactions_df['amount'].mean()
        std_amount = transactions_df['amount'].std()
        
        threshold = mean_amount + (3 * std_amount)
        
        anomalous_transactions = transactions_df[transactions_df['amount'] > threshold]
        
        daily_counts = transactions_df.groupby(transactions_df['transaction_date'].dt.date).size()
        daily_mean = daily_counts.mean()
        daily_std = daily_counts.std()
        
        daily_threshold_upper = daily_mean + (2 * daily_std)
        daily_threshold_lower = max(0, daily_mean - (2 * daily_std))
        
        anomalous_days = daily_counts[
            (daily_counts > daily_threshold_upper) | (daily_counts < daily_threshold_lower)
        ]
        
        anomaly_data = {
            "large_transactions": {
                "count": len(anomalous_transactions),
                "threshold": round(threshold, 2),
                "total_value": round(anomalous_transactions['amount'].sum(), 2),
                "avg_amount": round(anomalous_transactions['amount'].mean(), 2) if len(anomalous_transactions) > 0 else 0
            },
            "daily_volume_anomalies": {
                "anomalous_days": len(anomalous_days),
                "upper_threshold": round(daily_threshold_upper, 2),
                "lower_threshold": round(daily_threshold_lower, 2),
                "normal_daily_range": f"{daily_mean - daily_std:.0f} - {daily_mean + daily_std:.0f}"
            },
            "recent_anomalies": anomalous_transactions.tail(10)[
                ['transaction_id', 'customer_id', 'amount', 'transaction_date']
            ].to_dict('records') if len(anomalous_transactions) > 0 else []
        }
        
        return MetricsResponse(
            success=True,
            data=anomaly_data,
            timestamp=datetime.now().isoformat(),
            message="Anomaly metrics calculated successfully"
        )
    except Exception as e:
        logger.error(f"Error calculating anomaly metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/segments/high_value", response_model=MetricsResponse)
async def get_high_value_customers():
    """Get high-value customer segments"""
    if not data:
        raise HTTPException(status_code=503, detail="Data not available")
    
    try:
        customers_df = data['customers']
        transactions_df = data['transactions']
        
        customer_spending = transactions_df.groupby('customer_id').agg({
            'amount': ['count', 'sum', 'mean'],
            'transaction_date': ['min', 'max']
        }).round(2)
        
        customer_spending.columns = ['transaction_count', 'total_spent', 'avg_order_value', 'first_purchase', 'last_purchase']
        customer_spending = customer_spending.reset_index()
        
        high_value_threshold = customer_spending['total_spent'].quantile(0.8)
        
        high_value_customers = customer_spending[
            customer_spending['total_spent'] >= high_value_threshold
        ].sort_values('total_spent', ascending=False)
        
        customer_segments = []
        
        spending_percentiles = [0.95, 0.8, 0.6, 0.4]
        segment_names = ['Platinum', 'Gold', 'Silver', 'Bronze']
        
        for i, (percentile, name) in enumerate(zip(spending_percentiles, segment_names)):
            if i == 0:
                segment_customers = customer_spending[
                    customer_spending['total_spent'] >= customer_spending['total_spent'].quantile(percentile)
                ]
            else:
                prev_percentile = spending_percentiles[i-1]
                segment_customers = customer_spending[
                    (customer_spending['total_spent'] >= customer_spending['total_spent'].quantile(percentile)) &
                    (customer_spending['total_spent'] < customer_spending['total_spent'].quantile(prev_percentile))
                ]
            
            if len(segment_customers) > 0:
                customer_segments.append({
                    "segment": name,
                    "customer_count": len(segment_customers),
                    "avg_revenue": round(segment_customers['total_spent'].mean(), 2),
                    "total_revenue": round(segment_customers['total_spent'].sum(), 2),
                    "percentage": round((len(segment_customers) / len(customer_spending)) * 100, 2),
                    "min_spend": round(segment_customers['total_spent'].min(), 2),
                    "max_spend": round(segment_customers['total_spent'].max(), 2)
                })
        
        segment_data = {
            "high_value_threshold": round(high_value_threshold, 2),
            "total_high_value_customers": len(high_value_customers),
            "customer_segments": customer_segments,
            "top_10_customers": high_value_customers.head(10).to_dict('records')
        }
        
        return MetricsResponse(
            success=True,
            data=segment_data,
            timestamp=datetime.now().isoformat(),
            message="Customer segments calculated successfully"
        )
    except Exception as e:
        logger.error(f"Error calculating customer segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/revenue", response_model=MetricsResponse)
async def get_revenue_analytics(
    period: str = Query("daily", description="Period for revenue analysis: daily, weekly, monthly")
):
    """Get revenue analytics by period"""
    if not data:
        raise HTTPException(status_code=503, detail="Data not available")
    
    try:
        transactions_df = data['transactions']
        
        if period == "daily":
            revenue_data = transactions_df.groupby(transactions_df['transaction_date'].dt.date).agg({
                'amount': ['count', 'sum', 'mean'],
                'customer_id': 'nunique'
            }).round(2)
            revenue_data.columns = ['transactions', 'revenue', 'avg_order_value', 'unique_customers']
        elif period == "weekly":
            revenue_data = transactions_df.groupby(transactions_df['transaction_date'].dt.to_period('W')).agg({
                'amount': ['count', 'sum', 'mean'],
                'customer_id': 'nunique'
            }).round(2)
            revenue_data.columns = ['transactions', 'revenue', 'avg_order_value', 'unique_customers']
        elif period == "monthly":
            revenue_data = transactions_df.groupby(transactions_df['transaction_date'].dt.to_period('M')).agg({
                'amount': ['count', 'sum', 'mean'],
                'customer_id': 'nunique'
            }).round(2)
            revenue_data.columns = ['transactions', 'revenue', 'avg_order_value', 'unique_customers']
        else:
            raise HTTPException(status_code=400, detail="Invalid period. Use: daily, weekly, or monthly")
        
        revenue_data = revenue_data.reset_index()
        revenue_data.iloc[:, 0] = revenue_data.iloc[:, 0].astype(str)
        
        total_revenue = transactions_df['amount'].sum()
        total_transactions = len(transactions_df)
        
        analytics_data = {
            "period": period,
            "total_revenue": round(total_revenue, 2),
            "total_transactions": total_transactions,
            "data_points": len(revenue_data),
            "revenue_trends": revenue_data.to_dict('records'),
            "summary": {
                "avg_daily_revenue": round(revenue_data['revenue'].mean(), 2),
                "peak_revenue_day": revenue_data.loc[revenue_data['revenue'].idxmax()].to_dict(),
                "revenue_growth": round(((revenue_data['revenue'].iloc[-1] / revenue_data['revenue'].iloc[0]) - 1) * 100, 2) if len(revenue_data) > 1 else 0
            }
        }
        
        return MetricsResponse(
            success=True,
            data=analytics_data,
            timestamp=datetime.now().isoformat(),
            message=f"Revenue analytics calculated for {period} period"
        )
    except Exception as e:
        logger.error(f"Error calculating revenue analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/customers", response_model=MetricsResponse)
async def get_customer_analytics():
    """Get comprehensive customer analytics"""
    if not data:
        raise HTTPException(status_code=503, detail="Data not available")
    
    try:
        customers_df = data['customers']
        transactions_df = data['transactions']
        
        customer_metrics = transactions_df.groupby('customer_id').agg({
            'amount': ['count', 'sum', 'mean'],
            'transaction_date': ['min', 'max']
        }).round(2)
        
        customer_metrics.columns = ['transaction_count', 'total_spent', 'avg_order_value', 'first_purchase', 'last_purchase']
        
        current_date = datetime.now()
        customer_metrics['days_since_last_purchase'] = (
            current_date - pd.to_datetime(customer_metrics['last_purchase'])
        ).dt.days
        
        age_groups = customers_df['age'].value_counts().sort_index() if 'age' in customers_df.columns else {}
        
        analytics_data = {
            "total_customers": len(customers_df),
            "customers_with_purchases": len(customer_metrics),
            "customer_lifetime_value": {
                "mean": round(customer_metrics['total_spent'].mean(), 2),
                "median": round(customer_metrics['total_spent'].median(), 2),
                "percentile_75": round(customer_metrics['total_spent'].quantile(0.75), 2),
                "percentile_95": round(customer_metrics['total_spent'].quantile(0.95), 2)
            },
            "purchase_frequency": {
                "mean": round(customer_metrics['transaction_count'].mean(), 2),
                "median": round(customer_metrics['transaction_count'].median(), 2),
                "one_time_buyers": int((customer_metrics['transaction_count'] == 1).sum()),
                "repeat_customers": int((customer_metrics['transaction_count'] > 1).sum())
            },
            "customer_acquisition": customers_df.groupby(
                pd.to_datetime(customers_df['registration_date']).dt.to_period('M')
            ).size().tail(12).to_dict()
        }
        
        return MetricsResponse(
            success=True,
            data=analytics_data,
            timestamp=datetime.now().isoformat(),
            message="Customer analytics calculated successfully"
        )
    except Exception as e:
        logger.error(f"Error calculating customer analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prometheus/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/status")
async def api_status():
    """API status and statistics"""
    try:
        status_info = {
            "api_version": "1.0.0",
            "uptime": datetime.now().isoformat(),
            "database_status": "connected" if db.engine else "disconnected",
            "data_status": "loaded" if data else "not_loaded",
            "available_endpoints": [
                "/metrics/churn",
                "/metrics/anomalies", 
                "/segments/high_value",
                "/analytics/revenue",
                "/analytics/customers"
            ],
            "data_summary": {}
        }
        
        if data:
            status_info["data_summary"] = {
                "customers": len(data['customers']),
                "transactions": len(data['transactions']),
                "events": len(data.get('events', [])),
                "products": len(data.get('products', []))
            }
        
        return status_info
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )