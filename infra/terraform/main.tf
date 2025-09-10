# Cloud-Native Data Platform Infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "us-central1-a"
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
  default     = "dataplatform-cluster"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Google Cloud Storage Bucket for Data Lake
resource "google_storage_bucket" "data_lake" {
  name          = "${var.project_id}-dataplatform-datalake"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    component   = "data-lake"
  }
}

# BigQuery Dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id  = "dataplatform_analytics"
  description = "Analytics dataset for data platform"
  location    = var.region

  labels = {
    environment = var.environment
    component   = "analytics"
  }
}

# BigQuery Tables
resource "google_bigquery_table" "customers" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "customers"

  schema = jsonencode([
    {
      name = "customer_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "first_name"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "last_name"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "email"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "registration_date"
      type = "TIMESTAMP"
      mode = "NULLABLE"
    },
    {
      name = "segment"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "is_active"
      type = "BOOLEAN"
      mode = "NULLABLE"
    }
  ])

  labels = {
    environment = var.environment
  }
}

resource "google_bigquery_table" "transactions" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "transactions"

  schema = jsonencode([
    {
      name = "transaction_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "customer_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "transaction_date"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "amount"
      type = "NUMERIC"
      mode = "REQUIRED"
    },
    {
      name = "currency"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "category"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "status"
      type = "STRING"
      mode = "NULLABLE"
    }
  ])

  labels = {
    environment = var.environment
  }
}

# Google Kubernetes Engine Cluster
resource "google_container_cluster" "dataplatform" {
  name     = var.cluster_name
  location = var.zone

  # We can't create a cluster without a default pool, so we create the smallest possible default pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Network Policy
  network_policy {
    enabled = true
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "k8s-pod-range"
    services_secondary_range_name = "k8s-service-range"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  labels = {
    environment = var.environment
  }
}

# Separately Managed Node Pool
resource "google_container_node_pool" "dataplatform_nodes" {
  name       = "${var.cluster_name}-node-pool"
  location   = var.zone
  cluster    = google_container_cluster.dataplatform.name
  node_count = 2

  node_config {
    preemptible  = true
    machine_type = "e2-medium"

    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = google_service_account.gke_service_account.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      env = var.environment
    }

    tags = ["gke-node", "${var.cluster_name}-node"]

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  # Auto-scaling
  autoscaling {
    min_node_count = 1
    max_node_count = 5
  }

  # Auto-repair and auto-upgrade
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.cluster_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.name

  secondary_ip_range {
    range_name    = "k8s-pod-range"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "k8s-service-range"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Service Account for GKE
resource "google_service_account" "gke_service_account" {
  account_id   = "gke-service-account"
  display_name = "GKE Service Account"
}

# IAM Roles for GKE Service Account
resource "google_project_iam_member" "gke_sa_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_project_iam_member" "gke_sa_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.gke_service_account.email}"
}

# Cloud SQL Instance
resource "google_sql_database_instance" "postgres" {
  name             = "${var.cluster_name}-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
}

# Cloud SQL Database
resource "google_sql_database" "dataplatform" {
  name     = "dataplatform"
  instance = google_sql_database_instance.postgres.name
}

# Cloud SQL User
resource "google_sql_user" "datauser" {
  name     = "datauser"
  instance = google_sql_database_instance.postgres.name
  password = "datapass123"
}

# Firewall Rules
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal"
  network = google_compute_network.vpc.name

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = ["10.0.0.0/24", "10.1.0.0/16", "10.2.0.0/16"]
}

# Cloud NAT for private cluster
resource "google_compute_router" "router" {
  name    = "${var.cluster_name}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "${var.cluster_name}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}