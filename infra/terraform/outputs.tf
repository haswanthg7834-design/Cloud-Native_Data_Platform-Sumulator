# Outputs for the Cloud-Native Data Platform Infrastructure

output "cluster_name" {
  description = "GKE Cluster Name"
  value       = google_container_cluster.dataplatform.name
}

output "cluster_endpoint" {
  description = "GKE Cluster Endpoint"
  value       = google_container_cluster.dataplatform.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE Cluster CA Certificate"
  value       = google_container_cluster.dataplatform.master_auth.0.cluster_ca_certificate
  sensitive   = true
}

output "data_lake_bucket" {
  description = "Data Lake Storage Bucket"
  value       = google_storage_bucket.data_lake.name
}

output "bigquery_dataset" {
  description = "BigQuery Analytics Dataset"
  value       = google_bigquery_dataset.analytics.dataset_id
}

output "postgres_instance_name" {
  description = "Cloud SQL PostgreSQL Instance Name"
  value       = google_sql_database_instance.postgres.name
}

output "postgres_connection_name" {
  description = "Cloud SQL PostgreSQL Connection Name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "postgres_ip_address" {
  description = "Cloud SQL PostgreSQL IP Address"
  value       = google_sql_database_instance.postgres.ip_address.0.ip_address
}

output "vpc_network" {
  description = "VPC Network Name"
  value       = google_compute_network.vpc.name
}

output "subnet_name" {
  description = "Subnet Name"
  value       = google_compute_subnetwork.subnet.name
}

output "service_account_email" {
  description = "GKE Service Account Email"
  value       = google_service_account.gke_service_account.email
}

output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.dataplatform.name} --zone ${google_container_cluster.dataplatform.location} --project ${var.project_id}"
}

output "data_lake_url" {
  description = "Data Lake Storage URL"
  value       = "gs://${google_storage_bucket.data_lake.name}"
}

output "bigquery_tables" {
  description = "BigQuery Tables Created"
  value = {
    customers    = "${google_bigquery_dataset.analytics.dataset_id}.${google_bigquery_table.customers.table_id}"
    transactions = "${google_bigquery_dataset.analytics.dataset_id}.${google_bigquery_table.transactions.table_id}"
  }
}

output "database_connection_string" {
  description = "Database Connection String"
  value       = "postgresql://datauser:datapass123@${google_sql_database_instance.postgres.ip_address.0.ip_address}:5432/dataplatform"
  sensitive   = true
}