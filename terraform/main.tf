# Local Backend (it would be better to have it hosted on a bucket)
terraform {
  backend "local" {}
}

# Provider GCP
provider "google" {
  credentials = file(var.gcp_svc_key_path)
  project     = var.gcp_project
  region      = var.gcp_region
}

# MODULES

# Storage
module "storage" {
  source = "./storage"

  gcp_region = var.gcp_region

  functions_source_dir = var.functions_source_dir
  functions_output_path = var.functions_output_path

  data_source_dir = var.data_source_dir
  data_output_path = var.data_output_path
  data_file_name = var.data_file_name

  job_file_name = var.job_file_name
  job_source_dir = var.job_source_dir

  pubsub_topic_extract_transform_name = var.pubsub_topic_extract_transform_name
  pubsub_topic_load_name = var.pubsub_topic_load_name
}

# Functions
module "functions" {
  source = "./functions"

  gcp_project = var.gcp_project
  gcp_region = var.gcp_region
  service_account_email = var.service_account_email

  runtime = var.functions_runtime
  extract_transform_function_name = var.extract_transform_function_name
  load_function_name = var.load_function_name
  start_processing_pipeline_name = var.start_processing_pipeline_name
  functions_bucket_name = module.storage.functions_bucket_name
  functions_zip_file_name = module.storage.functions_zip_file_name

  data_bucket_name = module.storage.data_bucket_name
  data_file_name = var.data_file_name
  data_zip_file_name = module.storage.data_zip_file_name

  job_bucket_name = module.storage.job_bucket_name
  job_file_name = var.job_file_name

  pubsub_topic_extract_transform_name = var.pubsub_topic_extract_transform_name
  pubsub_topic_load_name = var.pubsub_topic_load_name

  bigquery_crimes_dataset_id = var.bigquery_crimes_dataset_id

  dataproc_cluster_name = var.dataproc_cluster_name
}

# I.A.M
module "iam" {
  source = "./iam"

  gcp_project = var.gcp_project
  gcp_region = var.gcp_region
  service_account_email = var.service_account_email

  function_name = module.functions.start_processing_pipeline_name

  permission_function = var.permission_function
}

# Pub Sub
module "pubsub" {
  source = "./pubsub"

  pubsub_topic_start_pipeline_name = var.pubsub_topic_extract_transform_name
  pubsub_topic_job_ended_name = var.pubsub_topic_load_name
  gcp_project = var.gcp_project
}

# Big Query
module "bigquery" {
  source = "./bigquery"
  
  gcp_project = var.gcp_project
  crimes_dataset_id = var.bigquery_crimes_dataset_id
}
