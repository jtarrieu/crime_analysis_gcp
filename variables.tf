# Provider
variable "gcp_svc_key_path" {
  type = string
}
variable "gcp_project" {
  type = string
}
variable "gcp_region" {
  type = string
}
variable "service_account_email" {
  type = string
}

# Functions
variable "functions_runtime" {
  type = string
}
variable "extract_transform_function_name" {
  type = string
}
variable "load_function_name" {
  type = string
}
variable "start_processing_pipeline_name" {
  type = string
}

# Paths and filenames
variable "functions_source_dir" {
  type = string
}
variable "functions_output_path" {
  type = string
}
variable "data_source_dir" {
  type = string
}
variable "data_output_path" {
  type = string
}
variable "data_file_name" {
  type = string
}
variable "job_source_dir" {
  type = string
}
variable "job_file_name" {
  type = string
}

# Permissions
variable "permission_function" {
  type = string
}

# Pubsub
variable "pubsub_topic_extract_transform_name" {
  type = string
}
variable "pubsub_topic_load_name" {
  type = string
}

# BigQuery
variable "bigquery_crimes_dataset_id" {
  type = string
}

# Dataproc
variable "dataproc_cluster_name" {
  type = string
}