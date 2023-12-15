# Function name
output "start_processing_pipeline_name" {
  description = "processing function name"
  value = google_cloudfunctions_function.start_processing_pipeline.name
}

# http trigger url
output "start_processing_pipeline_url" {
  description = "link to trigger processing function"
  value = google_cloudfunctions_function.start_processing_pipeline.https_trigger_url
}
