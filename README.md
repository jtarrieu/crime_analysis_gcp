# crime analysis gcp ETL pipeline
## Introduction
This code provide a **ETL** architecture on **Google Cloud Platform** using *Cloud functions*, *DataProc cluster* and *job*, *Pub/Sub*, *BigQuery*. It processes a 1,7Gb csv file into 5 BigQuery tables that answer specific questions.

The **infrastructure** is mainly configured and deployed via **terraform** to make the processing environment easily reproductible and versatile.

The **processing** is made via a **pySpark** code running on a **Dataproc Cluster**.

## Providing the infrastructure : Terraform
Terraform is a IAS(Infra As Code) language that allows us to create, configure and destroy infrastructure. The infra of this project uses **4 modules**:
- **storage**: instanciate 3 Google Cloud Storage buckets. The buckets have a same unique identifier that is generated each time the infrastructure is provided. See the GCS good uses for naming the buckets:
  - **functions**: contains the GCF .zip code
  - **data**: contains the raw csv file zipped.
  - **job**: contains the pySprak job code
- **functions**: instanciates Google Cloud functions. It is linked to the src/funcitons/ dir containing the (main.py + requirements.txt) code for the functions. There are two functions:
  - **extract_and_load**: is extracting the data (taking it from a Google Cloud Storage) and launching the dataprocessing pySpark job inside a cluster (Dataproc). It has a HTTP trigger that is the starting point of the pipeline.
  - **load_and_clean** is loading the processed data located in a Google Cloud Storage bucket into BigQuery tables. It has a PubSub subscription trigger that is activated at the end of the pySpark job. It is destroying the dataproc cluster at the end of the job to avoid unecessary costs.
- **pubsub**: creates a pubsub topic that links the end of the pySpark job to the load_and_clean function. The job is sending a json file that contains information about the transformed tables (name, column names & types).
- **iam**: this module contains ressources that specifies the access rights and authorisations of the other ressources defines in the modules.

## Triggering the pipeline: Cloud Function
The pipeline starts when a cloud function is triggered. This function is checking if a dataproc cluster already exists if not it creates it. Then it is submitting the processing pyspark job to the cluster. The function ends when the job is sumbitted (before the job starts) and returns the links of the function logs and the job logs.

## Processing data: Dataproc cluster & job
The job running inside the dataproc cluster is doing the following tasks:
  - Check if the data file inside the data bucket is zipped and unzip it if so.
  - Load the file as a Spark df.
  - Creates 5 new df based on the first one answering certain questions.
  - Uploads the new df inside the data bucket as csv files.
  - Creates a json containing description of the new csv files.
  - Send the json into the pubsub topic and trigger the loading_and_extract function.

## Loading the data: PubSub & BigQuery
