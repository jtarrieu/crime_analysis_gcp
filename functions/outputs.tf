# Function object
output "function" {
  description = "processing function name"
  value = google_cloudfunctions_function.function.name
}

# http trigger url
output "function_url" {
  description = "link to trigger processing function"
  value = google_cloudfunctions_function.function.https_trigger_url
}

# output "create_dataproc_cluster_function" {
#   description = "Create dataproc cluster function name"
#   value = google_cloudfunctions_function.create_dataproc_cluster.name
# }
# output "delete_dataproc_cluster_function" {
#   description = "Create dataproc cluster function name"
#   value = google_cloudfunctions_function.create_dataproc_cluster.name
# }

# output "create_dataproc_cluster_url" {
#   description = "link to create the dataproc cluster"
#   value = google_cloudfunctions_function.create_dataproc_cluster.https_trigger_url
# }
# output "delete_dataproc_cluster_url" {
#   description = "link to delete the dataproc cluster"
#   value = google_cloudfunctions_function.delete_dataproc_cluster.https_trigger_url
# }