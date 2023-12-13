# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker_function" {
  project        = var.gcp_project
  region         = var.gcp_region
  cloud_function = var.function

  role   = "roles/cloudfunctions.invoker"
  member = var.permission_function
}
