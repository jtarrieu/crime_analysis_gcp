resource "google_cloudfunctions_function" "start_processing_pipeline" {
    name                  = var.start_processing_pipeline_name
    runtime               = var.runtime
    region                = var.gcp_region
    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = var.functions_bucket_name
    source_archive_object = var.functions_zip_file_name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = var.start_processing_pipeline_name

    # Time after wich the response wont be available
    timeout               = 540

    # Set the trigger to HTTP
    trigger_http          = true

    environment_variables = {
      PROJECT                    = var.gcp_project
      REGION                     = var.gcp_region
      CLUSTER_NAME               = var.dataproc_cluster_name
      JOB_BUCKET_NAME            = var.job_bucket_name
      JOB_FILE_NAME              = var.job_file_name
      DATA_BUCKET_NAME           = var.data_bucket_name
      DATA_FILE_NAME             = var.data_file_name
      DATA_ZIP_FILE_NAME         = var.data_zip_file_name
      EXTRACT_TRANSFORM_TOPIC    = var.pubsub_topic_extract_transform_name
      LOAD_TRANSFORM_TOPIC       = var.pubsub_topic_load_name
      EXTRACT_TRANFORM_FUNC_NAME = var.extract_transform_function_name
      LOAD_FUNC_NAME       = var.load_function_name
      DATASET_ID                 = var.bigquery_crimes_dataset_id
    }

  service_account_email = var.service_account_email
}

resource "google_cloudfunctions_function" "extract_transform_function" {
  name                  = var.extract_transform_function_name
  description           = "Extract and transform data (ETL) via dataproc pyspark cluster"
  runtime               = var.runtime
  source_archive_bucket = var.functions_bucket_name
  source_archive_object = var.functions_zip_file_name
  entry_point           = var.extract_transform_function_name
  region                = var.gcp_region
  timeout               = 540

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = var.pubsub_topic_extract_transform_name
  }

    environment_variables = {
      PROJECT                    = var.gcp_project
      REGION                     = var.gcp_region
      CLUSTER_NAME               = var.dataproc_cluster_name
      JOB_BUCKET_NAME            = var.job_bucket_name
      JOB_FILE_NAME              = var.job_file_name
      DATA_BUCKET_NAME           = var.data_bucket_name
      DATA_FILE_NAME             = var.data_file_name
      DATA_ZIP_FILE_NAME         = var.data_zip_file_name
      EXTRACT_TRANSFORM_TOPIC    = var.pubsub_topic_extract_transform_name
      LOAD_TRANSFORM_TOPIC       = var.pubsub_topic_load_name
      EXTRACT_TRANFORM_FUNC_NAME = var.extract_transform_function_name
      LOAD_FUNC_NAME       = var.load_function_name
      DATASET_ID                 = var.bigquery_crimes_dataset_id
    }

  service_account_email = var.service_account_email
}

resource "google_cloudfunctions_function" "load_and_function" {
  name                  = var.load_function_name
  description           = "loading data from GCS to big query (ETL)"
  runtime               = var.runtime
  source_archive_bucket = var.functions_bucket_name
  source_archive_object = var.functions_zip_file_name
  entry_point           = var.load_function_name
  region                = var.gcp_region
  timeout               = 540
  # Additional Cloud Function settings (e.g., memory, timeout, etc.)

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = var.pubsub_topic_load_name
  }

    environment_variables = {
      PROJECT                    = var.gcp_project
      REGION                     = var.gcp_region
      CLUSTER_NAME               = var.dataproc_cluster_name
      JOB_BUCKET_NAME            = var.job_bucket_name
      JOB_FILE_NAME              = var.job_file_name
      DATA_BUCKET_NAME           = var.data_bucket_name
      DATA_FILE_NAME             = var.data_file_name
      DATA_ZIP_FILE_NAME         = var.data_zip_file_name
      EXTRACT_TRANSFORM_TOPIC    = var.pubsub_topic_extract_transform_name
      LOAD_TRANSFORM_TOPIC       = var.pubsub_topic_load_name
      EXTRACT_TRANFORM_FUNC_NAME = var.extract_transform_function_name
      LOAD_FUNC_NAME             = var.load_function_name
      DATASET_ID                 = var.bigquery_crimes_dataset_id
    }

  service_account_email = var.service_account_email
}