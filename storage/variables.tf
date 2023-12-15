# PROVIDER REGION
variable "gcp_region" {
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
  type = 	string
}
variable "data_output_path" {
  type = string
}
variable "data_file_name" {
  type = string
}
variable "job_file_name" {
  type = string
}
variable "job_source_dir" {
  type = string
}

# Pub Sub topic names
variable "pubsub_topic_extract_transform_name" {
  type = string
}
variable "pubsub_topic_load_name" {
  type = string
}

