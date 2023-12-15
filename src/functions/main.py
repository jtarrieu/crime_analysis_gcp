from os import getenv
from google.cloud import dataproc_v1 as dataproc
from google.cloud import pubsub_v1 as pubsub
from google.cloud import bigquery
from google.cloud import storage
import base64
from ast import literal_eval

# Configuration
def get_config()->dict:
    """Return the main configuration dict. Extract the provided environement variable stored in the terraform.tfvars.

    Returns:
        dict: main configuration dict
    """
    config = {
        'project_id': getenv('PROJECT'),
        'region': getenv('REGION'),
        'cluster_name': getenv('CLUSTER_NAME'),
        'job_bucket_name': getenv('JOB_BUCKET_NAME'),
        'job_file_name': getenv('JOB_FILE_NAME'),
        'data_bucket_name': getenv('DATA_BUCKET_NAME'),
        'data_zip_file_name': getenv('DATA_ZIP_FILE_NAME'),
        'data_file_name': getenv('DATA_FILE_NAME'),
        'extract_transform_topic_name': getenv('EXTRACT_TRANSFORM_TOPIC'),
        'load_topic_name': getenv('LOAD_TRANSFORM_TOPIC'),
        'extract_transform_function_name': getenv('EXTRACT_TRANFORM_FUNC_NAME'),
        'load_function_name': getenv('LOAD_FUNC_NAME'),
        'dataset_id': getenv('DATASET_ID')
    }
    print(config)
    return config

def get_cluster_config(config:dict) -> dict:
    """Return the dataproc cluster configuration.

    Args:
        config (dict): main configuration file

    Returns:
        dict: dataproc cluster configuration
    """
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

def get_job_config(config:dict)->dict:
    """Return the dataproc cluster job configuration.

    Args:
        config (dict): main configuration dict

    Returns:
        dict: dataproc cluster job configuration
    """
    cluster_name     = config['cluster_name']
    job_bucket_name  = config['job_bucket_name']
    job_file_name    = config['job_file_name']
    data_bucket_name = config['data_bucket_name']
    data_file_name   = config['data_file_name']
    project_id       = config['project_id']
    topic_name       = config['load_topic_name']

    print('Creating job Config.')
    config = {
        "placement": {"cluster_name": cluster_name},
        "pyspark_job": {
            "main_python_file_uri": f"gs://{job_bucket_name}/{job_file_name}",
            "args": [data_bucket_name, data_file_name, project_id, topic_name]
            }
    }
    return config

def get_bigquery_job_config()->bigquery.LoadJobConfig:
    """Return a basic Big Query job configuration. The job erases the previous table. the inserted data come from a parquet file.

    Returns:
        bigquery.LoadJobConfig: configuration
    """
    return bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # rewrite the table
        source_format=bigquery.SourceFormat.PARQUET, # parquet file
    )

# Clients
def create_cluster_client(config:dict)->dataproc.ClusterControllerClient:
    """Create a dataproc cluster client.

    Args:
        config (dict): main configuration dict

    Returns:
        dataproc.ClusterControllerClient: cluster controller client
    """
    region = config['region']
    print('Creating a ClusterControllerClient.')
    return dataproc.ClusterControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

def create_job_client(config:dict)->dataproc.JobControllerClient:
    """Create a cluster job client.

    Args:
        config (dict): main configuration dict

    Returns:
        dataproc.JobControllerClient: job controller client
    """
    region = config['region']
    print('Creating a JobControllerClient')
    return dataproc.JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
        )

def create_bucket_client(config:dict)->storage.Client:
    """Create a Google Cloud Storage bucket client.

    Args:
        config (dict): main configuration dict

    Returns:
        storage.Client: Google Cloud Storage Bucket client
    """
    project = config['project_id']
    bucket_name = config['data_bucket_name']
    storage_client = storage.Client(project=project)
    bucket_client = storage.Bucket(storage_client, bucket_name)
    return bucket_client

def create_biquery_client(config:dict)->bigquery.client:
    """Create a big Query client.

    Args:
        config (dict): main configuration dict

    Returns:
        bigquery.client: Big Query client
    """
    project = config['project_id']
    client = bigquery.Client(project=project)
    return client

# Dataproc control
def cluster_exists(cluster_client:dataproc.ClusterControllerClient,
                   project_id:str,
                   region:str,
                   cluster_name:str)->bool:
    """Check if a cluster exist.

    Args:
        cluster_client (dataproc.ClusterControllerClient): cluster controller client
        project_id (str): project id
        region (str): region
        cluster_name (str): cluster name

    Returns:
        bool: _description_
    """
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

def create_dataproc_cluster(cluster_client, config:dict)->bool:
    """Create a dataproc cluster.

    Args:
        cluster_client (dataproc.ClusterControllerClient): cluster controller client
        config (dict): main configuration dict

    Returns:
        bool: _description_
    """
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

        print(f"Creating cluster '{cluster_name}' ... (~ 4 minutes)")
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

def delete_dataproc_cluster(cluster_client:dataproc.ClusterControllerClient,
                            config:dict)->bool:
    """Delete a dataproc cluster.

    Args:
        cluster_client (dataproc.ClusterControllerClient): cluster controller client
        config (dict): main configuration dict

    Returns:
        bool: True if deleted, False if an error occured
    """
    project_id = config['project_id']
    region = config['region']
    cluster_name = config['cluster_name']
    print('Starting dataproc cluster deletion procedure.')

    try:
        # Delete the cluster
        print(f"Deleting cluster '{cluster_name}' ... (~ 2 minutes)")
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
    
def submit_job_to_cluster(job_client:dataproc.JobControllerClient, config:dict)->bool:
    """Submit a job to a cluster.

    Args:
        job_client (dataproc.JobControllerClient): job controller client
        config (dict): _description_

    Returns:
        bool: _description_
    """
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
        # the job id to the config
        config['job_id'] = job_id
        print(f'Submitted job ID "{job_id}" to cluster "{cluster_name}".')
        return True
    except Exception as e:
        print(f"Failed to submit the job. Error: {e}")
        return False

# Generate log links
def get_cloud_function_logs_link(config:dict, function_name:str)->str:
    """Create the link to access the logs of a function.

    Args:
        config (dict): main configuration dict
        funciton_name (str): function name

    Returns:
        str: link of the function logs
    """
    region     = config['region']
    project_id = config['project_id']
    url = f'https://console.cloud.google.com/functions/details/{region}/{function_name}?env=gen1&hl=fr&project={project_id}&tab=logs'
    html = f'<a href="{url}">Here</a>'
    return html

def get_job_logs_link(config:dict)->str:
    """Create the link to access the logs of a job.

    Args:
        config (dict): main configuration dict

    Returns:
        str: link of the job logs submitted to the cluster or "" if not submitted
    """
    region     = config['region']
    project_id = config['project_id']
    cluster_name = config['cluster_name']

    if config['job_id']:
        job_id = config['job_id']
        url = f'https://console.cloud.google.com/dataproc/jobs/{job_id}/monitoring?region={region}&hl=fr&project={project_id}'
        html = f'<a href="{url}">job logs</a>'
        return url
    url = f'https://console.cloud.google.com/dataproc/clusters/{cluster_name}/jobs?region={region}&hl=fr&project={project_id}'
    html = f'<a href="{url}">cluster jobs</a>'
    return url

# Pub Sub
def publish_message_in_topic(project_id:str, topic:str, message:str)->None:
    """Publish a message into a Pub Sub topic.

    Args:
        project_id (str): project id 
        topic (str): topic name
        message (str): message
    """
    print(f"Creating a publisher client for topic '{topic}'.")
    publisher = pubsub.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic)
    message_data = message

    future = publisher.publish(topic_path, data=message_data.encode("utf-8"))
    future.result()
    print(f"Message '{message}'sent to topic '{topic}'.")

def response_to_dict(event=None)->dict:
    """Extracts the dict sent by the job via the pubsub.

    Args:
        event (, optional): event object. Defaults to None.

    Returns:
        dict: job dict
    """
    # loading the triger message
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    # turing it into a dict
    content = literal_eval(pubsub_message)
    print(f'Received : {content}')
    return content

# Storage
def find_parquet_file_in_bucket_dir(bucket_client, folder_name:str)->str:
    """Search for a parquet file inside a folder in a bucket.

    Args:
        bucket_client (): bucket client
        folder_name (str): folder name

    Returns:
        str: file path or "" if not found
    """
    blobs = bucket_client.list_blobs(prefix=folder_name)
    file_complete = False
    parquet_file_name = ""
    for blob in blobs:
        if '_SUCCESS' in blob.name:
            file_complete = True
        if '.parquet' in blob.name:
            parquet_file_name = blob.name
            print(f"parquet file found '{parquet_file_name}'.")
            return parquet_file_name

    if file_complete and parquet_file_name:
        return parquet_file_name
    return ""

def get_parquet_file_uri(bucket_name:str, file_path:str)->str:
    """Create a GCS file uri.

    Args:
        bucket_name (str): bucket name
        file_path (str): file path

    Returns:
        str: _description_
    """
    return f"gs://{bucket_name}/{file_path}"

# Big Query
def create_table_id(project_id:str, dataset_id:str, table_name:str)->str:
    """Create a bigQuery table id.

    Args:
        project_id (str): project id
        dataset_id (str): dataset id
        table_name (str): table name

    Returns:
        str: table id
    """
    table_id = f"{project_id}.{dataset_id}.{table_name}"
    return table_id

def load_to_bigquery(bucket_client, bigquery_client, tables:dict, config:dict):

    project_id = config['project_id']
    dataset_id = config['dataset_id']
    bucket_name = config['data_bucket_name']

    job_config = get_bigquery_job_config()

    # Creating a table for each parquet file
    for table in tables:
        table_name  = table['table_name']
        gcs_file_path   = find_parquet_file_in_bucket_dir(bucket_client, table_name)
        table_id    = create_table_id(project_id, dataset_id, table_name)
        uri         = get_parquet_file_uri(bucket_name, gcs_file_path)

        # loading parquet table into table
        load_job = bigquery_client.load_table_from_uri(
            uri,
            table_id,
            job_config=job_config
        )

        load_job.result()  # Waits for the job to complete.

        destination_table = bigquery_client.get_table(table_id)
        print("Loaded {} rows.".format(destination_table.num_rows))

    return True

# ETL
def extract_transform(event, context)->str:
    """Google Cloud Function.
    Extract data, create a dataproc cluster, submit the processing job.

    Args:
        event (): 
        context (): 

    Returns:
        str: return
    """
    config         = get_config()
    cluster_client = create_cluster_client(config)
    job_client     = create_job_client(config)

    if create_dataproc_cluster(cluster_client, config):
        submit_job_to_cluster(job_client, config)
        print(f"See the job's logs here : {get_job_logs_link(config)}")

    return 'end'

def load(event, context)->str:
    """Google Cloud Function. Load data from GCS to BigQuery

    Args:
        event (): 
        context (): 

    Returns:
        str: return
    """
    # retreiving the content of the pubsub message into a dict
    response = response_to_dict(event)

    # getting the project config
    config = get_config()

    # Creating a BigQuery, GCS bucket and Dataproc cluster client
    bigquery_client = create_biquery_client(config)
    bucket_client   = create_bucket_client(config)
    cluster_client  = create_cluster_client(config)

    # tables info
    tables = response['tables']


    if response['status'] == 'SUCCESS':
        load_to_bigquery(bucket_client, bigquery_client, tables, config)
        delete_dataproc_cluster(cluster_client, config)
        print('Loading ended successfully.')

    return ""

def start_processing_pipeline(request)->None:
    """Google Cloud Function.
    Start the data procecssing

    Args:
        request (): 

    """
    config = get_config()
    project_id = config['project_id']
    topic = config['extract_transform_topic_name']
    extract_transform_function_name = config['extract_transform_function_name']
    load_function_name = config['load_function_name']

    message = 'starting pipeline'
    publish_message_in_topic(project_id, topic, message)

    return f"See the extract and transform's logs {get_cloud_function_logs_link(config, extract_transform_function_name)}.\
        See the load's logs {get_cloud_function_logs_link(config, load_function_name)}."