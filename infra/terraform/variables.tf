# Variables for Cloud-Native Data Platform Infrastructure

variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
  validation {
    condition     = length(var.project_id) > 0
    error_message = "Project ID cannot be empty."
  }
}

variable "region" {
  description = "The Google Cloud region for resources"
  type        = string
  default     = "us-central1"
  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]+$", var.region))
    error_message = "Region must be a valid Google Cloud region format."
  }
}

variable "zone" {
  description = "The Google Cloud zone for zonal resources"
  type        = string
  default     = "us-central1-a"
  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]+-[a-z]$", var.zone))
    error_message = "Zone must be a valid Google Cloud zone format."
  }
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "dataplatform-cluster"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.cluster_name))
    error_message = "Cluster name must start with a letter, contain only lowercase letters, numbers, and hyphens, and end with a letter or number."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "node_count" {
  description = "Number of nodes in the GKE node pool"
  type        = number
  default     = 2
  validation {
    condition     = var.node_count >= 1 && var.node_count <= 10
    error_message = "Node count must be between 1 and 10."
  }
}

variable "machine_type" {
  description = "Machine type for GKE nodes"
  type        = string
  default     = "e2-medium"
  validation {
    condition = contains([
      "e2-micro", "e2-small", "e2-medium", "e2-standard-2", "e2-standard-4",
      "n1-standard-1", "n1-standard-2", "n1-standard-4", "n1-highmem-2"
    ], var.machine_type)
    error_message = "Machine type must be a valid Google Cloud machine type."
  }
}

variable "preemptible" {
  description = "Whether to use preemptible nodes"
  type        = bool
  default     = true
}

variable "auto_scaling_min" {
  description = "Minimum number of nodes for auto-scaling"
  type        = number
  default     = 1
  validation {
    condition     = var.auto_scaling_min >= 0 && var.auto_scaling_min <= 5
    error_message = "Auto-scaling minimum must be between 0 and 5."
  }
}

variable "auto_scaling_max" {
  description = "Maximum number of nodes for auto-scaling"
  type        = number
  default     = 5
  validation {
    condition     = var.auto_scaling_max >= 1 && var.auto_scaling_max <= 20
    error_message = "Auto-scaling maximum must be between 1 and 20."
  }
}

variable "database_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
  validation {
    condition = contains([
      "db-f1-micro", "db-g1-small", "db-n1-standard-1", "db-n1-standard-2"
    ], var.database_tier)
    error_message = "Database tier must be a valid Cloud SQL tier."
  }
}

variable "enable_backup" {
  description = "Enable automated backups for Cloud SQL"
  type        = bool
  default     = true
}

variable "backup_start_time" {
  description = "Start time for automated backups (HH:MM format)"
  type        = string
  default     = "03:00"
  validation {
    condition     = can(regex("^[0-2][0-9]:[0-5][0-9]$", var.backup_start_time))
    error_message = "Backup start time must be in HH:MM format (24-hour)."
  }
}

variable "maintenance_start_time" {
  description = "Start time for maintenance window (HH:MM format)"
  type        = string
  default     = "03:00"
  validation {
    condition     = can(regex("^[0-2][0-9]:[0-5][0-9]$", var.maintenance_start_time))
    error_message = "Maintenance start time must be in HH:MM format (24-hour)."
  }
}

variable "storage_bucket_location" {
  description = "Location for the data lake storage bucket"
  type        = string
  default     = "US"
  validation {
    condition = contains([
      "US", "EU", "ASIA", "us-central1", "us-east1", "europe-west1", "asia-southeast1"
    ], var.storage_bucket_location)
    error_message = "Storage bucket location must be a valid Google Cloud Storage location."
  }
}

variable "data_retention_days" {
  description = "Number of days to retain data in storage bucket"
  type        = number
  default     = 30
  validation {
    condition     = var.data_retention_days >= 1 && var.data_retention_days <= 365
    error_message = "Data retention days must be between 1 and 365."
  }
}

variable "enable_private_cluster" {
  description = "Enable private cluster configuration"
  type        = bool
  default     = true
}

variable "enable_network_policy" {
  description = "Enable network policy for the cluster"
  type        = bool
  default     = true
}

variable "enable_workload_identity" {
  description = "Enable Workload Identity for the cluster"
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "dataplatform"
    managed_by  = "terraform"
  }
}

# Local values for computed variables
locals {
  cluster_full_name = "${var.cluster_name}-${var.environment}"
  
  common_labels = merge(var.labels, {
    environment = var.environment
    cluster     = var.cluster_name
  })
  
  # Network CIDR ranges
  subnet_cidr      = "10.0.0.0/24"
  pod_cidr         = "10.1.0.0/16"
  service_cidr     = "10.2.0.0/16"
  master_cidr      = "172.16.0.0/28"
}