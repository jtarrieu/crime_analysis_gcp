# DEPLOY THE PROCESSING FUNCTION
resource "google_cloudfunctions_function" "function" {
    name                  = "processing"
    runtime               = var.runtime

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = var.functions_bucket_name
    source_archive_object = var.functions_zip_file_name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "main"

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
}
