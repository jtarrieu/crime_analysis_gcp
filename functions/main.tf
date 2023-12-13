# DEPLOY THE PROCESSING FUNCTION
resource "google_cloudfunctions_function" "extract_transform_function" {
    name                  = "extract_and_transform"
    description           = "Extract and transform data (ETL) via dataproc pyspark cluster"
    runtime               = var.runtime

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = var.functions_bucket_name
    source_archive_object = var.functions_zip_file_name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "extract_and_transform_with_dataproc"

    # Time after wich the response wont be available
    timeout               = 540

    # Set the trigger to HTTP
    trigger_http          = true

    environment_variables = {
      PROJECT            = var.gcp_project
      REGION             = var.gcp_region
      JOB_BUCKET_NAME    = var.job_bucket_name
      JOB_FILE_NAME      = var.job_file_name
      DATA_BUCKET_NAME   = var.data_bucket_name
      DATA_FILE_NAME     = var.data_file_name
      DATA_ZIP_FILE_NAME = var.data_zip_file_name
  }

  service_account_email = "compte-service-tarrieu@tarrieu.iam.gserviceaccount.com"
}

resource "google_cloudfunctions_function" "load_and_clean_function" {
  name        = "load_and_clean"
  description = "loading data to big query"
  runtime     = var.runtime
  source_archive_bucket = var.functions_bucket_name
  source_archive_object = var.functions_zip_file_name
  entry_point = "load_to_bigquery"

  # Additional Cloud Function settings (e.g., memory, timeout, etc.)

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "processing_job_ended"
  }

  environment_variables = {
    PROJECT            = var.gcp_project
    REGION             = var.gcp_region
    JOB_BUCKET_NAME    = var.job_bucket_name
    JOB_FILE_NAME      = var.job_file_name
    DATA_BUCKET_NAME   = var.data_bucket_name
    DATA_FILE_NAME     = var.data_file_name
    DATA_ZIP_FILE_NAME = var.data_zip_file_name
  }

  service_account_email = "compte-service-tarrieu@tarrieu.iam.gserviceaccount.com"
}