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

# Functions
variable "functions_runtime" {
  type = string
}
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
variable "permission_function" {
  type = string
}