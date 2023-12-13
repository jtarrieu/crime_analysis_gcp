output "functions_bucket_name" {
  description = "functions_bucket name"
  value = google_storage_bucket.functions_bucket.name
}

output "data_bucket_name" {
  description = "data_bucket name"
  value = google_storage_bucket.data_bucket.name
}

output "job_bucket_name" {
  description = "jobs_bucket name"
  value = google_storage_bucket.job_bucket.name
}

output "functions_zip_file_name" {
  description = "functions_bucket zip object"
  value = google_storage_bucket_object.functions_zip.name
}

output "data_zip_file_name" {
 description = "data zip file name"
 value = google_storage_bucket_object.data_zip.name
}

output "job_zip_file_name" {
  description = "pyspark job zip file name"
  value = google_storage_bucket_object.job_zip.name
}