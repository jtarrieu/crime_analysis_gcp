# Random id to have a random name (gcp good use for naming buckets)
resource "random_id" "bucket_prefix" {
  byte_length = 8
}

# DATA
# Create the bucket
resource "google_storage_bucket" "data_bucket" {
    name     = "data-bucket-${random_id.bucket_prefix.hex}"
    location = var.gcp_region
}
# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "data_zip" {
    source       = "./tmp/data.zip"
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "${var.data_file_name}.zip"
    bucket       = google_storage_bucket.data_bucket.name
}

# FUNCTIONS
# Create the bucket
resource "google_storage_bucket" "functions_bucket" {
    name     = "functions-bucket-${random_id.bucket_prefix.hex}"
    location = var.gcp_region
}
# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "functions_source" {
    type        = "zip"
    source_dir  = var.functions_source_dir
    output_path = var.functions_output_path
}
# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "functions_zip" {
    source       = data.archive_file.functions_source.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "src-${data.archive_file.functions_source.output_md5}.zip"
    bucket       = google_storage_bucket.functions_bucket.name
}


# JOBS
# Create the bucket
resource "google_storage_bucket" "job_bucket" {
    name     = "jobs-bucket-${random_id.bucket_prefix.hex}"
    location = var.gcp_region
}
# # Generates an archive of the source code compressed as a .zip file.
# data "archive_file" "job_source" {
#     type        = "zip"
#     source_dir  = var.jobs_source_dir
#     output_path = var.jobs_output_path
# }
# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "job_zip" {
    source       = "${var.job_source_dir}${var.job_file_name}"
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    # name         = "src-${data.archive_file.job_source.output_md5}.zip"
    name         = var.job_file_name
    bucket       = google_storage_bucket.job_bucket.name
}

resource "google_storage_bucket_access_control" "data_bucket_access" {
  bucket = google_storage_bucket.data_bucket.name
  role   = "READER"
  entity = "allUsers"
}