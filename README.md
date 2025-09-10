# Cloud-Native Data Platform Simulator

A comprehensive, production-ready data platform demonstrating modern cloud-native architecture with data ingestion, transformation, analytics, and deployment capabilities.

![Data Platform Architecture](architecture.png)

## 🚀 Features

- **Data Ingestion**: Automated CSV and API data ingestion pipelines
- **Data Transformation**: ETL/ELT pipelines with data quality validation
- **Analytics Engine**: Business intelligence with customer analytics, churn analysis, and anomaly detection
- **REST API**: FastAPI service exposing analytics endpoints
- **Cloud-Native**: Containerized with Docker and Kubernetes deployment
- **Infrastructure as Code**: Terraform scripts for Google Cloud Platform
- **Monitoring**: Prometheus and Grafana observability stack
- **Scalable**: Auto-scaling Kubernetes cluster with load balancing

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Local Development](#-local-development)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Monitoring](#-monitoring)
- [Data Pipeline](#-data-pipeline)
- [Contributing](#-contributing)

## 🏗️ Architecture

The platform follows a microservices architecture with the following components:

### Core Services
- **API Service**: FastAPI application serving analytics data
- **Database**: PostgreSQL for structured data storage
- **Data Lake**: Google Cloud Storage for raw data
- **Analytics DB**: BigQuery for large-scale analytics
- **Cache**: Redis for performance optimization

### Infrastructure
- **Container Platform**: Kubernetes (GKE)
- **Service Mesh**: Nginx ingress controller
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions (optional)
- **IaC**: Terraform for cloud resources

### Data Flow
1. **Ingestion** → Raw data from CSVs/APIs
2. **Validation** → Data quality checks
3. **Transformation** → ETL pipelines with PySpark
4. **Storage** → PostgreSQL + BigQuery + GCS
5. **Analytics** → Business intelligence metrics
6. **API** → RESTful endpoints for consumption
7. **Visualization** → Grafana dashboards

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- kubectl (for Kubernetes)
- Terraform (for cloud deployment)
- Google Cloud SDK (for GCP deployment)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd cloud-native-data-platform-simulator
pip install -r requirements.txt
```

### 2. Generate Sample Data
```bash
cd data/raw
python generate_sample_data.py
```

### 3. Start with Docker Compose
```bash
cd infra/docker
docker-compose up -d
```

### 4. Access Services
- **API**: http://localhost:8000
- **Jupyter**: http://localhost:8888
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 💻 Local Development

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
```bash
cd app
python db_setup.py
```

### Run API Service
```bash
cd app
uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
```

### Run Jupyter Notebooks
```bash
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
```

### Data Pipeline Execution
```bash
# Run data ingestion
jupyter nbconvert --execute notebooks/01_data_ingestion.ipynb

# Run transformation
jupyter nbconvert --execute notebooks/02_data_transformation.ipynb

# Generate analytics
jupyter nbconvert --execute notebooks/03_analytics_and_metrics.ipynb
```

## 🚀 Deployment

### Docker Deployment
```bash
cd infra/docker
docker-compose up -d
```

### Kubernetes Deployment
```bash
# Local Kubernetes (minikube/kind)
cd infra/kubernetes
./deploy.sh

# Or manual deployment
kubectl apply -f namespace.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f monitoring-deployment.yaml
kubectl apply -f jupyter-deployment.yaml
```

### Cloud Deployment (GCP)
```bash
# Configure Terraform variables
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your GCP project details

# Deploy infrastructure
./deploy.sh
```

## 📊 API Documentation

The API provides comprehensive analytics endpoints:

### Health Check
```bash
GET /health
```

### Analytics Endpoints

#### Customer Churn Metrics
```bash
GET /metrics/churn
```
Response:
```json
{
  "success": true,
  "data": {
    "churn_rate": 12.5,
    "churned_customers": 125,
    "at_risk_customers": 87,
    "total_customers": 1000
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

#### Anomaly Detection
```bash
GET /metrics/anomalies
```

#### High-Value Customer Segments
```bash
GET /segments/high_value
```

#### Revenue Analytics
```bash
GET /analytics/revenue?period=daily
```

#### Customer Analytics
```bash
GET /analytics/customers
```

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📈 Monitoring

### Prometheus Metrics
- API request rates and latency
- System resource usage (CPU, memory, disk)
- Database connection pools
- Business metrics (churn rate, revenue, etc.)
- Custom application metrics

### Grafana Dashboards
- **Main Dashboard**: System and business metrics overview
- **API Performance**: Request rates, response times, error rates
- **Infrastructure**: CPU, memory, disk, network metrics
- **Business Intelligence**: Customer analytics, revenue trends

### Alerts
Configured alerts for:
- Service downtime
- High error rates
- Resource exhaustion
- Data quality issues
- Business metric thresholds

## 🔄 Data Pipeline

### 1. Data Ingestion (`01_data_ingestion.ipynb`)
- **CSV Import**: Customer, transaction, event, and product data
- **API Simulation**: External data source integration
- **Data Validation**: Schema and quality checks
- **Storage**: Raw data persistence to database/data lake

### 2. Data Transformation (`02_data_transformation.ipynb`)
- **Cleaning**: Handle missing values, standardize formats
- **Feature Engineering**: Create derived metrics and segments
- **Integration**: Join tables for comprehensive datasets
- **Validation**: Ensure data quality post-transformation

### 3. Analytics & Metrics (`03_analytics_and_metrics.ipynb`)
- **Customer Analytics**: Lifetime value, segmentation, behavior
- **Churn Analysis**: Identify at-risk customers
- **Anomaly Detection**: Unusual transaction patterns
- **Business Intelligence**: Revenue trends, KPIs
- **Reporting**: Export results for API consumption

### Data Quality Framework
- **Completeness**: Missing value detection
- **Validity**: Data type and range validation
- **Consistency**: Cross-table relationship checks
- **Accuracy**: Business rule validation
- **Timeliness**: Data freshness monitoring

## 🛠️ Technology Stack

### Backend
- **Python 3.11**: Core programming language
- **FastAPI**: Modern REST API framework
- **SQLAlchemy**: Database ORM
- **Pandas**: Data manipulation and analysis
- **PySpark**: Big data processing (optional)
- **Scikit-learn**: Machine learning

### Database
- **PostgreSQL**: Primary transactional database
- **BigQuery**: Data warehouse for analytics
- **Redis**: Caching layer
- **Google Cloud Storage**: Data lake

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Nginx**: Reverse proxy and load balancer
- **Terraform**: Infrastructure as Code
- **Google Cloud Platform**: Cloud provider

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert management

### Development
- **Jupyter**: Interactive development environment
- **pytest**: Testing framework
- **Black**: Code formatting
- **pre-commit**: Code quality hooks

## 📊 Sample Queries

### SQL Analytics Queries
```sql
-- Top customers by revenue
SELECT customer_id, total_spent, total_transactions
FROM customer_summary
ORDER BY total_spent DESC
LIMIT 10;

-- Monthly revenue growth
SELECT 
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY month) as prev_month,
    ((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month)) / 
     LAG(monthly_revenue) OVER (ORDER BY month)) * 100 as growth_pct
FROM monthly_trends;

-- Customer churn analysis
SELECT 
    segment,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN julianday('now') - julianday(last_purchase) > 90 THEN 1 END) as churned,
    ROUND(COUNT(CASE WHEN julianday('now') - julianday(last_purchase) > 90 THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
FROM customer_summary
WHERE total_transactions > 0
GROUP BY segment;
```

### API Usage Examples
```python
import requests

# Get churn metrics
response = requests.get('http://localhost:8000/metrics/churn')
churn_data = response.json()

# Get high-value customer segments
response = requests.get('http://localhost:8000/segments/high_value')
segments = response.json()

# Get daily revenue analytics
response = requests.get('http://localhost:8000/analytics/revenue?period=daily')
revenue_data = response.json()
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dataplatform

# API
API_HOST=0.0.0.0
API_PORT=8000

# Monitoring
PROMETHEUS_ENDPOINT=http://prometheus:9090
GRAFANA_ADMIN_PASSWORD=admin

# Cloud (for GCP deployment)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
```

### Configuration Files
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Container orchestration
- `terraform.tfvars`: Infrastructure variables
- `prometheus.yml`: Monitoring configuration

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/

# API tests
pytest tests/test_api.py

# Data pipeline tests
pytest tests/test_pipeline.py

# Integration tests
pytest tests/test_integration.py
```

### Load Testing
```bash
# API load testing with locust
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📋 Maintenance

### Regular Tasks
- **Data Backup**: Automated daily backups of PostgreSQL
- **Log Rotation**: Automated log cleanup
- **Security Updates**: Regular container image updates
- **Performance Tuning**: Query optimization and indexing
- **Monitoring Review**: Alert threshold adjustments

### Scaling Considerations
- **Horizontal Scaling**: Kubernetes auto-scaling for API pods
- **Database Scaling**: Read replicas for PostgreSQL
- **Data Partitioning**: Time-based partitioning for large tables
- **Caching Strategy**: Redis for frequently accessed data
- **CDN Integration**: For static assets and reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Create Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Include unit tests for new features
- Update documentation for changes
- Use semantic versioning for releases

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Submit bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions
- **Email**: Contact maintainers for enterprise support

## 🎯 Roadmap

### Upcoming Features
- [ ] Real-time streaming data ingestion with Apache Kafka
- [ ] Machine learning model deployment with MLflow
- [ ] Advanced analytics with time series forecasting
- [ ] Multi-cloud deployment support (AWS, Azure)
- [ ] Enhanced security with OAuth2 and RBAC
- [ ] Data catalog and lineage tracking
- [ ] Advanced alerting with Slack/Email integration
- [ ] Performance optimization with query caching

---

**Built with ❤️ for modern data engineering**