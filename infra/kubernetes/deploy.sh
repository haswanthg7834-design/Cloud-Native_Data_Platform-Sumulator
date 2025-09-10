#!/bin/bash

# Cloud-Native Data Platform Kubernetes Deployment Script

echo "Starting Kubernetes deployment for Cloud-Native Data Platform..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    echo "Please ensure your kubectl context is set correctly"
    exit 1
fi

# Create namespace
echo "Creating namespace..."
kubectl apply -f namespace.yaml

# Wait for namespace to be created
kubectl wait --for=condition=Active --timeout=30s namespace/dataplatform

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f postgres-deployment.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n dataplatform

# Deploy API service
echo "Deploying API service..."
kubectl apply -f api-deployment.yaml

# Wait for API service to be ready
echo "Waiting for API service to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/api-service -n dataplatform

# Deploy Jupyter
echo "Deploying Jupyter..."
kubectl apply -f jupyter-deployment.yaml

# Wait for Jupyter to be ready
echo "Waiting for Jupyter to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/jupyter -n dataplatform

# Deploy monitoring stack
echo "Deploying monitoring stack (Prometheus & Grafana)..."
kubectl apply -f monitoring-deployment.yaml

# Wait for monitoring stack to be ready
echo "Waiting for monitoring stack to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n dataplatform
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n dataplatform

# Display deployment status
echo ""
echo "Deployment Status:"
echo "=================="
kubectl get deployments -n dataplatform
echo ""
echo "Services:"
echo "========="
kubectl get services -n dataplatform
echo ""
echo "Ingress:"
echo "========"
kubectl get ingress -n dataplatform

# Display access information
echo ""
echo "Access Information:"
echo "==================="
echo "API Service: http://api.dataplatform.local"
echo "Jupyter Lab: http://jupyter.dataplatform.local"
echo "Prometheus: kubectl port-forward service/prometheus-service 9090:9090 -n dataplatform"
echo "Grafana: kubectl port-forward service/grafana-service 3000:3000 -n dataplatform"
echo ""
echo "To access services locally, add these entries to your /etc/hosts file:"
echo "127.0.0.1 api.dataplatform.local"
echo "127.0.0.1 jupyter.dataplatform.local"
echo ""
echo "Deployment completed successfully!"

# Optional: Port forward for local development
read -p "Do you want to set up port forwarding for local development? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up port forwarding..."
    kubectl port-forward service/api-service 8000:8000 -n dataplatform &
    kubectl port-forward service/jupyter-service 8888:8888 -n dataplatform &
    kubectl port-forward service/prometheus-service 9090:9090 -n dataplatform &
    kubectl port-forward service/grafana-service 3000:3000 -n dataplatform &
    
    echo "Port forwarding active:"
    echo "- API: http://localhost:8000"
    echo "- Jupyter: http://localhost:8888"
    echo "- Prometheus: http://localhost:9090"
    echo "- Grafana: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop port forwarding"
    wait
fi