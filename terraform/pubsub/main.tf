resource "google_pubsub_topic" "pubsub_extract_transform_pipeline" {
  name = var.pubsub_topic_start_pipeline_name
  project = var.gcp_project
}
resource "google_pubsub_topic" "pubsub_topic_load_clean_ended" {
  name = var.pubsub_topic_job_ended_name
  project = var.gcp_project
}
