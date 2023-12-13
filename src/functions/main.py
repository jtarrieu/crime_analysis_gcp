from os import getenv
from google.cloud import dataproc_v1 as dataproc
import base64

def get_config()->tuple:
    config = {
        'project_id': getenv('PROJECT'),
        'region': getenv('REGION'),
        'cluster_name': "dataproc-cluster",
        'job_bucket_name': getenv('JOB_BUCKET_NAME'),
        'job_file_name': getenv('JOB_FILE_NAME'),
        'data_bucket_name': getenv('DATA_BUCKET_NAME'),
        'data_zip_file_name': getenv('DATA_ZIP_FILE_NAME'),
        'data_file_name': getenv('DATA_FILE_NAME'),
        'job_ended_topic_name': 'processing_job_ended'
    }
    print(config)
    return config

def create_cluster_client(config:dict):
    region = config['region']
    print('Creating a ClusterControllerClient.')
    return dataproc.ClusterControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

def create_job_client(config:dict):
    region = config['region']
    print('Creating a JobControllerClient')
    return dataproc.JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
        )

def get_cluster_config(config:dict) -> dict:
    project_id, cluster_name = config['project_id'], config['cluster_name']
    # Create the cluster config with 30GB memory for both master and worker nodes.
    cluster_config = {
        "project_id": project_id,
        "cluster_name": cluster_name,
        "config": {
            "software_config": {"image_version": "2.1.33-debian11"},
            "master_config": {
                "num_instances": 1,
                "machine_type_uri": "n1-standard-4",
                "disk_config": {
                    "boot_disk_size_gb": 40
                }
            },
            "worker_config": {
                "num_instances": 2,
                "machine_type_uri": "n1-standard-4",
                "disk_config": {
                    "boot_disk_size_gb":40
                }
            }
        },
    }

    print(f'Creating cluster configuration: {cluster_config}.')
    return cluster_config

def get_job_config(config:dict):
    cluster_name     = config['cluster_name']
    job_bucket_name  = config['job_bucket_name']
    job_file_name    = config['job_file_name']
    data_bucket_name = config['data_bucket_name']
    data_file_name   = config['data_file_name']

    print('Creating job Config.')
    config = {
        "placement": {"cluster_name": cluster_name},
        "pyspark_job": {
            "main_python_file_uri": f"gs://{job_bucket_name}/{job_file_name}",
            "args": [data_bucket_name, data_file_name]
            }
    }
    return config

def cluster_exists(cluster_client, project_id, region, cluster_name):
    print('Checking if the cluster exist or not.')
    try:
        # Attempt to get information about the cluster
        cluster_client.get_cluster(
            project_id=project_id,
            region=region,
            cluster_name=cluster_name
        )
        return True  # Cluster exists
    except Exception as e:
        print(f'Cluster not found: {e}.')
        return False # Cluster doesn't exist

def create_dataproc_cluster(cluster_client, config:dict):
    project_id       = config['project_id']
    region           = config['region']
    cluster_name     = config['cluster_name']

    print('Starting dataproc cluster creation precedure.')

    # Check if the cluster already exists
    if cluster_exists(cluster_client, project_id, region, cluster_name):
        print(f"Cluster '{cluster_name}' already exists. Skipping creation.")
        return True
    print(f"Cluster '{cluster_name}' does not exists. Starting creation.")
    try:
        # Create the cluster config with 50GB memory for both master and worker nodes.
        cluster = get_cluster_config(config)

        print(f"Creating cluster '{cluster_name}'.")
        # Create the cluster.
        operation = cluster_client.create_cluster(
            request={"project_id": project_id, "region": region, "cluster": cluster}
        )
        result = operation.result()

        # Output a success message.
        print(f"Cluster created successfully: {result.cluster_name}")
        return True
    except Exception as e:
        print(f"Failed to create the cluster: {cluster_name}. Error: {e}")
        return False

def delete_dataproc_cluster(cluster_client, config:dict):
    project_id = config['project_id']
    region = config['region']
    cluster_name = config['cluster_name']
    print('Starting dataproc cluster deletion procedure.')

    try:
        # Delete the cluster
        operation = cluster_client.delete_cluster(
            project_id=project_id,
            region=region,
            cluster_name=cluster_name
        )
        operation.result()  # Wait for the operation to complete
        print(f"Cluster '{cluster_name}' deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting cluster: '{cluster_name}'.Error: {e}")
        return False
    
def submit_job_to_cluster(job_client, config:dict):
    project_id       = config['project_id']
    region           = config['region']
    cluster_name     = config['cluster_name']
    print('Starting submitting job to clutser procedure.')
    try:
        # Submit the job to the cluster

        # Create the job config.
        job = get_job_config(config)

        print('Submitting job to cluster.')
        operation = job_client.submit_job(
            request={"project_id": project_id, "region": region, "job": job}
        )

        job_id = operation.reference.job_id

        print(f'Submitted job ID "{job_id}" to cluster "{cluster_name}".')
        return True
    except Exception as e:
        print(f"Failed to submit the job. Error: {e}")
        return False

def extract_and_transform_with_dataproc(request):

    config         = get_config()
    cluster_client = create_cluster_client(config)
    job_client     = create_job_client(config)

    create_dataproc_cluster(cluster_client, config)
    # unzip_data(config)
    submit_job_to_cluster(job_client, config)
    # delete_dataproc_cluster(cluster_client, config)

    return 'Extract transform ended'

def load_to_bigquery(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    return pubsub_message