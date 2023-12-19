# Provider
gcp_svc_key_path = "../service_acount_key.json"
gcp_project = "jerem-est-pauvre"
gcp_region = "europe-west2"
service_account_email = "terraform@jerem-est-pauvre.iam.gserviceaccount.com"

# Functions
functions_runtime = "python38"
extract_transform_function_name = "extract_transform"
load_function_name = "load"
start_processing_pipeline_name = "start_processing_pipeline"

# Paths and filenames
functions_source_dir = "../src/functions"
functions_output_path = "../tmp/functions.zip"
data_source_dir = "../data"
data_output_path = "../tmp/data.zip"
data_file_name = "Crimes_-_2001_to_Present.csv"
job_source_dir = "../src/job/"
job_file_name = "job.py"

# Permissions
permission_function = "allUsers"

# PubSub
pubsub_topic_extract_transform_name = "extract_transform"
pubsub_topic_load_name = "load"

# Big Query
bigquery_crimes_dataset_id = "crimes"

# Dataproc
dataproc_cluster_name = "dataproc-cluster"