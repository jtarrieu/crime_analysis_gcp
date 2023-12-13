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

# STORAGE MODULE
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
}
 
# FUNCTIONS MODULE
module "functions" {
  source = "./functions"

  gcp_project = var.gcp_project
  gcp_region = var.gcp_region

  runtime = var.functions_runtime
  functions_bucket_name = module.storage.functions_bucket_name
  functions_zip_file_name = module.storage.functions_zip_file_name

  data_bucket_name = module.storage.data_bucket_name
  data_file_name = var.data_file_name
  data_zip_file_name = module.storage.data_zip_file_name

  job_bucket_name = module.storage.job_bucket_name
  job_file_name = var.job_file_name
}

# IAM MODULE
module "iam" {
  source = "./iam"

  gcp_project = var.gcp_project
  gcp_region = var.gcp_region

  function = module.functions.function

  permission_function = var.permission_function
}