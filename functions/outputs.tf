# Function object
output "extrac_transform_function_name" {
  description = "processing function name"
  value = google_cloudfunctions_function.extract_transform_function.name
}

# http trigger url
output "extract_transform_function_url" {
  description = "link to trigger processing function"
  value = google_cloudfunctions_function.extract_transform_function.https_trigger_url
}
