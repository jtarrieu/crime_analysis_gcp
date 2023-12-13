# PROVIDER REGION
variable "gcp_region" {
  type = string
}

# SOURCE & OUTPUT PATHS
#     FUNCTIONS
variable "functions_source_dir" {
  type = string
}
variable "functions_output_path" {
  type = string
}
#     DATA
variable "data_source_dir" {
  type = 	string
}
variable "data_output_path" {
  type = string
}
variable "data_file_name" {
  type = string
}
#     JOBS
variable "job_file_name" {
  type = string
}
variable "job_source_dir" {
  type = string
}