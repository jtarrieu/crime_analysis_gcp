# PROVIDER
variable "gcp_project" {
  type = string
}
variable "gcp_region" {
  type = string
}

# RUNTIME
variable "runtime" {
  type = string
}

# BUCKET NAMES
variable "functions_bucket_name" {
  type = string
}
variable "data_bucket_name" {
  type = string
}
variable "job_bucket_name" {
  type = string
}

# BUCKET OBJECTS
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
