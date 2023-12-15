resource "google_bigquery_dataset" "crimes_dataset" {
  dataset_id = var.crimes_dataset_id
  project    = var.gcp_project
  delete_contents_on_destroy = true
}