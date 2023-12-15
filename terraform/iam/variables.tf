# PROVIDER
variable "gcp_project" {
  type = string
}
variable "gcp_region" {
  type = string
}
variable "service_account_email" {
  type = string
}

# FUNCTIONS
variable "function_name" {
  type = string
}

# PERMISSIONS
variable "permission_function" {
  type = string  
}

