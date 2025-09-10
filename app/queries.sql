-- Sample Analytics Queries for Cloud-Native Data Platform

-- Top Customers By Revenue
SELECT 
    customer_id, 
    total_spent, 
    total_transactions,
    avg_order_value,
    first_purchase,
    last_purchase
FROM customer_summary
ORDER BY total_spent DESC
LIMIT 10;

-- Monthly Revenue Growth
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

-- Customer Churn Analysis By Segment
SELECT 
    segment,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN julianday('now') - julianday(last_purchase) > 90 THEN 1 END) as churned,
    COUNT(CASE WHEN julianday('now') - julianday(last_purchase) BETWEEN 60 AND 90 THEN 1 END) as at_risk,
    ROUND(
        COUNT(CASE WHEN julianday('now') - julianday(last_purchase) > 90 THEN 1 END) * 100.0 / COUNT(*), 2
    ) as churn_rate_percentage
FROM customer_summary
WHERE total_transactions > 0
GROUP BY segment
ORDER BY churn_rate_percentage DESC;

-- Daily Transaction Volume Trends
SELECT 
    date,
    daily_transactions,
    daily_revenue,
    avg_transaction_value,
    unique_customers,
    ROUND(daily_revenue / unique_customers, 2) as revenue_per_customer
FROM daily_metrics
ORDER BY date DESC
LIMIT 30;

-- Large Transaction Anomalies
SELECT 
    transaction_id,
    customer_id,
    amount,
    transaction_date,
    merchant,
    category
FROM transactions
WHERE amount > (
    SELECT AVG(amount) + (3 * 
        (SELECT 
            SQRT(AVG((amount - avg_amount) * (amount - avg_amount))) 
            FROM (SELECT amount, AVG(amount) OVER() as avg_amount FROM transactions)
        )
    ) FROM transactions
)
ORDER BY amount DESC;

-- Customer Lifetime Value Analysis
SELECT 
    segment,
    COUNT(*) as customers,
    AVG(total_spent) as avg_clv,
    MIN(total_spent) as min_clv,
    MAX(total_spent) as max_clv,
    AVG(total_transactions) as avg_frequency,
    AVG(avg_order_value) as avg_order_value
FROM customer_summary
WHERE total_transactions > 0
GROUP BY segment
ORDER BY avg_clv DESC;

-- Weekly Active Users and Retention
SELECT 
    strftime('%Y-W%W', timestamp) as week,
    COUNT(DISTINCT customer_id) as weekly_active_users,
    COUNT(DISTINCT session_id) as total_sessions,
    ROUND(COUNT(*) / COUNT(DISTINCT session_id), 2) as avg_events_per_session
FROM events
GROUP BY strftime('%Y-W%W', timestamp)
ORDER BY week DESC;

-- Payment Method Performance
SELECT 
    payment_method,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction_amount,
    ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM transactions), 2) as revenue_share_percentage
FROM transactions
WHERE status = 'completed'
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- Customer Acquisition by Month
SELECT 
    strftime('%Y-%m', registration_date) as month,
    COUNT(*) as new_customers,
    SUM(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', registration_date)) as cumulative_customers
FROM customers
GROUP BY strftime('%Y-%m', registration_date)
ORDER BY month;

-- Product Category Revenue Analysis
SELECT 
    category,
    COUNT(*) as transactions,
    SUM(amount) as revenue,
    AVG(amount) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(SUM(amount) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
FROM transactions
WHERE status = 'completed'
GROUP BY category
ORDER BY revenue DESC;

-- High-Value Customer Segments (RFM-like Analysis)
SELECT 
    customer_id,
    total_spent,
    total_transactions,
    julianday('now') - julianday(last_purchase) as days_since_last_purchase,
    CASE 
        WHEN total_spent >= 1000 AND total_transactions >= 10 AND julianday('now') - julianday(last_purchase) <= 30 THEN 'Champions'
        WHEN total_spent >= 500 AND total_transactions >= 5 AND julianday('now') - julianday(last_purchase) <= 60 THEN 'Loyal Customers'
        WHEN total_spent >= 200 AND julianday('now') - julianday(last_purchase) <= 30 THEN 'Potential Loyalists'
        WHEN julianday('now') - julianday(last_purchase) > 90 THEN 'At Risk'
        ELSE 'Others'
    END as customer_segment
FROM customer_summary
WHERE total_transactions > 0
ORDER BY total_spent DESC;

-- Fraud Detection - Unusual Transaction Patterns
SELECT 
    customer_id,
    COUNT(*) as transactions_today,
    SUM(amount) as total_amount_today,
    AVG(amount) as avg_amount_today,
    transaction_date
FROM transactions
WHERE DATE(transaction_date) = DATE('now')
    AND customer_id IN (
        SELECT customer_id
        FROM transactions
        WHERE DATE(transaction_date) = DATE('now')
        GROUP BY customer_id
        HAVING COUNT(*) > 10 OR SUM(amount) > 5000
    )
GROUP BY customer_id, DATE(transaction_date)
ORDER BY total_amount_today DESC;

-- Cohort Analysis - Customer Retention by Registration Month
WITH cohort_data AS (
    SELECT 
        strftime('%Y-%m', c.registration_date) as cohort_month,
        c.customer_id,
        strftime('%Y-%m', t.transaction_date) as transaction_month,
        (strftime('%Y', t.transaction_date) - strftime('%Y', c.registration_date)) * 12 + 
        (strftime('%m', t.transaction_date) - strftime('%m', c.registration_date)) as period_number
    FROM customers c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    WHERE t.transaction_date IS NOT NULL
)
SELECT 
    cohort_month,
    period_number,
    COUNT(DISTINCT customer_id) as customers
FROM cohort_data
WHERE period_number >= 0
GROUP BY cohort_month, period_number
ORDER BY cohort_month, period_number;