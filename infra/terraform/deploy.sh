#!/bin/bash

# Terraform Deployment Script for Cloud-Native Data Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Cloud-Native Data Platform - Terraform Deployment${NC}"
echo "=================================================="

# Check if required tools are installed
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    if ! command -v terraform &> /dev/null; then
        echo -e "${RED}Error: Terraform is not installed${NC}"
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}Error: Google Cloud SDK is not installed${NC}"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites are installed${NC}"
}

# Initialize Terraform
init_terraform() {
    echo -e "${YELLOW}Initializing Terraform...${NC}"
    terraform init
    echo -e "${GREEN}✓ Terraform initialized${NC}"
}

# Validate Terraform configuration
validate_terraform() {
    echo -e "${YELLOW}Validating Terraform configuration...${NC}"
    terraform validate
    echo -e "${GREEN}✓ Terraform configuration is valid${NC}"
}

# Plan Terraform deployment
plan_terraform() {
    echo -e "${YELLOW}Planning Terraform deployment...${NC}"
    terraform plan -out=tfplan
    echo -e "${GREEN}✓ Terraform plan created${NC}"
}

# Apply Terraform deployment
apply_terraform() {
    echo -e "${YELLOW}Applying Terraform deployment...${NC}"
    terraform apply tfplan
    echo -e "${GREEN}✓ Infrastructure deployed successfully${NC}"
}

# Configure kubectl
configure_kubectl() {
    echo -e "${YELLOW}Configuring kubectl...${NC}"
    
    CLUSTER_NAME=$(terraform output -raw cluster_name)
    PROJECT_ID=$(terraform output -raw project_id 2>/dev/null || echo "")
    ZONE=$(terraform show -json | jq -r '.values.root_module.resources[] | select(.type=="google_container_cluster") | .values.location')
    
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project)
    fi
    
    gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE --project $PROJECT_ID
    echo -e "${GREEN}✓ kubectl configured for cluster: $CLUSTER_NAME${NC}"
}

# Display deployment information
show_deployment_info() {
    echo -e "${GREEN}Deployment Information:${NC}"
    echo "======================="
    
    echo -e "${YELLOW}Cluster Information:${NC}"
    echo "Cluster Name: $(terraform output -raw cluster_name)"
    echo "Cluster Endpoint: $(terraform output -raw cluster_endpoint)"
    
    echo -e "${YELLOW}Storage:${NC}"
    echo "Data Lake Bucket: $(terraform output -raw data_lake_bucket)"
    echo "BigQuery Dataset: $(terraform output -raw bigquery_dataset)"
    
    echo -e "${YELLOW}Database:${NC}"
    echo "PostgreSQL Instance: $(terraform output -raw postgres_instance_name)"
    echo "PostgreSQL IP: $(terraform output -raw postgres_ip_address)"
    
    echo -e "${YELLOW}Network:${NC}"
    echo "VPC Network: $(terraform output -raw vpc_network)"
    echo "Subnet: $(terraform output -raw subnet_name)"
    
    echo -e "${YELLOW}kubectl Configuration:${NC}"
    echo "$(terraform output -raw kubectl_config_command)"
}

# Clean up function
cleanup() {
    if [ -f "tfplan" ]; then
        rm tfplan
        echo -e "${YELLOW}Cleaned up temporary files${NC}"
    fi
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        echo -e "${RED}Error: terraform.tfvars file not found${NC}"
        echo "Please copy terraform.tfvars.example to terraform.tfvars and update with your values"
        exit 1
    fi
    
    # Run deployment steps
    check_prerequisites
    init_terraform
    validate_terraform
    plan_terraform
    
    # Ask for confirmation before applying
    echo -e "${YELLOW}Review the plan above. Do you want to proceed with deployment? (y/n):${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        apply_terraform
        configure_kubectl
        show_deployment_info
        echo -e "${GREEN}Deployment completed successfully!${NC}"
    else
        echo -e "${YELLOW}Deployment cancelled${NC}"
        cleanup
        exit 0
    fi
    
    cleanup
}

# Destroy infrastructure function
destroy() {
    echo -e "${RED}WARNING: This will destroy all infrastructure!${NC}"
    echo -e "${YELLOW}Are you sure you want to proceed? (type 'yes' to confirm):${NC}"
    read -r response
    if [[ "$response" == "yes" ]]; then
        terraform destroy
        echo -e "${GREEN}Infrastructure destroyed${NC}"
    else
        echo -e "${YELLOW}Destroy cancelled${NC}"
    fi
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "destroy")
        destroy
        ;;
    "plan")
        check_prerequisites
        init_terraform
        validate_terraform
        plan_terraform
        ;;
    "init")
        check_prerequisites
        init_terraform
        ;;
    "validate")
        validate_terraform
        ;;
    *)
        echo "Usage: $0 {deploy|destroy|plan|init|validate}"
        echo ""
        echo "Commands:"
        echo "  deploy    - Deploy the complete infrastructure (default)"
        echo "  destroy   - Destroy all infrastructure"
        echo "  plan      - Show what will be deployed"
        echo "  init      - Initialize Terraform"
        echo "  validate  - Validate Terraform configuration"
        exit 1
        ;;
esac