# Provider
variable "gcp_project" {
  type = string
}
variable "gcp_region" {
  type = string
}

# Runtime
variable "runtime" {
  type = string
}

# Names
variable "extract_transform_function_name" {
  type = string
}
variable "load_function_name" {
  type = string
}
variable "start_processing_pipeline_name" {
  type = string
}

# Bucket names
variable "functions_bucket_name" {
  type = string
}
variable "data_bucket_name" {
  type = string
}
variable "job_bucket_name" {
  type = string
}

# Bucket Objects
variable "functions_zip_file_name" {
  type = string
}
variable "data_file_name" {
  type = string
}
variable "data_zip_file_name" {
  type = string
}
variable "job_file_name" {
  type = string
}

variable "service_account_email" {
  type = string
}

# Pub Sub
variable "pubsub_topic_extract_transform_name" {
  type = string
}
variable "pubsub_topic_load_name" {
  type = string
}

# Big Query
variable "bigquery_crimes_dataset_id" {
  type = string
}

# Dataproc Cluster
variable "dataproc_cluster_name" {
  type = string
}
