import sys
from datetime import datetime
import io
from zipfile import ZipFile
from google.cloud import storage
from google.cloud import pubsub_v1
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

def get_config()->tuple:
    if len(sys.argv) != 3:
        print("Error: missing arguments\nUsage: python script_name.py <DATA_BUCKET_NAME> <DATA_FILE_NAME>")
        sys.exit(1)
    DATA_BUCKET_NAME = sys.argv[1]
    DATA_FILE_NAME   = sys.argv[2]    
    print(f"Data bucket name: {DATA_BUCKET_NAME}")
    print(f"Data file name:   {DATA_FILE_NAME}")
    return DATA_BUCKET_NAME, DATA_FILE_NAME

def unzip_files(bucket_name, file_name):

    # Initialize a Google Cloud Storage client
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket(bucket_name)
    # adding file extensions

    zip_file = f'{file_name}.zip'
    print(f'python job file name : {file_name}')
    print(f'zipped python job file name : {zip_file}')

    print(f"Searching for '{file_name}' in gs://{bucket_name}")
    # Check if the original file exists in the bucket
    original_blob = bucket.blob(file_name)
    if original_blob.exists():
        print(f"File '{file_name}' found in the bucket.")
    else:
        # If the original file is not found, try finding and unzipping a file with .zip extension
        print(f"'{file_name}' not found in gs://{bucket_name}")
        zip_blob = bucket.blob(zip_file)

        if zip_blob.exists():
            print(f"Zip file '{zip_file}' found in the bucket. Unzipping...")

            # Download the zip file as bytes
            zip_file_content = io.BytesIO()
            zip_blob.download_to_file(zip_file_content)

            # Unzip the file in memory
            with ZipFile(zip_file_content, "r") as zip_ref:
                # Assume the unzipped file has the same name as the original file
                unzipped_file_name = file_name

                # Read the unzipped file content
                unzipped_file_content = zip_ref.read(unzipped_file_name)

                # Upload the unzipped file back to the bucket
                unzipped_blob = bucket.blob(unzipped_file_name)
                unzipped_blob.upload_from_string(unzipped_file_content, content_type="application/octet-stream")

                print(f"Unzipped file '{unzipped_file_name}' uploaded to the bucket.")

                # delete the zip file
                zip_blob.delete()

                print(f"Deleting zip file '{zip_file}'")
        else:
            print(f"Neither file '{file_name}' nor zip file '{zip_file}' found. Running target function...")

def pull_gcs_csv_to_df(bucket:str, file_name:str)->DataFrame:
    print('Building spark session ...')
    spark = SparkSession.builder.appName("CrimeDataAnalysis").getOrCreate()
    print('Spark session built.')
    gcs_input_path = f'gs://{bucket}/{file_name}'
    print(f'Downloading {gcs_input_path}')
    return spark.read.csv(gcs_input_path, header=True, inferSchema=True)

def load_df_to_gcs_csv(df:DataFrame, bucket:str, name:str)->None:
    print(f"Uploading csv result of '{name}' processing into gs://{bucket}/{name}'.")
    output_gcs_path = f'gs://{bucket}/{name}'
    df.coalesce(1).write.csv(output_gcs_path, mode="overwrite", header=True)
    print('File uploaded.')

def load_df_to_gcs_parquet(df:DataFrame, bucket:str, name:str)->None:
    print(f"Uploading result of '{name}' processing into gs://{bucket}/{name}.")
    output_gcs_path = f'gs://{bucket}/{name}'
    df.repartition(1).write.parquet(output_gcs_path, mode="overwrite")

def get_current_year()->int:
    return datetime.now().year

def add_3y(df: DataFrame) -> DataFrame:
    # Format the date and add 3 years to all the dates
    df = df.withColumn("Date", F.expr("date_add(to_timestamp(Date, 'MM/dd/yyyy hh:mm:ss a'), 3 * 365)"))
    # Update/Create the Year, Month, and Hour
    df = df.withColumn("Year", F.year("Date"))
    df = df.withColumn("Month", F.month("Date"))
    df = df.withColumn("Hour", F.hour("Date"))

    return df

def total_crimes_past_5y_per_month(df:DataFrame)->DataFrame:
    current_year = get_current_year()
    # Filter data for the past 5 years
    df = df.filter((F.col("Year") >= current_year - 5) & (F.col("Year") <= current_year))
    # Group by month and count the number of crimes for each month
    df = df.groupBy("Month").count().orderBy("Month")
    
    name = 'total_crimes_during_the_past_5_years_per_month'

    return df, name

def top_10_theft_crimes_location_past_3y(df:DataFrame)->DataFrame:
    current_year = get_current_year()
    # Filter data for the past 3 years and for "THEFT" crimes
    df = df.filter((F.col("Year") >= current_year - 3) & (F.col("Year") <= current_year) & (F.col("Primary Type") == "THEFT"))

    # Group by 'Location Description' and count the number of thefts for each location
    location_counts = df.groupBy("Location Description").count()

    # Create a window specification to rank locations based on the count
    window_spec = Window.orderBy(F.desc("count"))

    # Add a rank column to the DataFrame based on the count
    ranked_locations = location_counts.withColumn("rank", F.rank().over(window_spec))

    # Filter the top 10 locations for each year
    top_10_locations = ranked_locations.filter(F.col("rank") <= 10)

    name = 'top_10_theft_crimes_location_past_3y'

    return top_10_locations, name

def total_crimes_per_year(df:DataFrame)->DataFrame:
    # Group by year and count the total number of crimes for each year
    total_crimes_per_year = df.groupBy("Year").count().orderBy("Year")

    name = 'total_crimes_per_year'
    return total_crimes_per_year, name

def safest_locations_4pm_to_10pm(df:DataFrame)->DataFrame:
    # Filter data for the time range between 10 pm and 4 am
    nighttime_df = df.filter((F.col("Hour") >= 22) | (F.col("Hour") <= 4))

    # Group by 'Location Description' and count the number of crimes for each location
    location_counts = nighttime_df.groupBy("Location Description").count()

    # Rank locations based on the count in ascending order
    ranked_locations = location_counts.orderBy("count").filter((F.col("count") == 1))

    name = 'safest_locations_4pm_to_10pm'

    return ranked_locations, name

def types_of_crimes_most_arrested_2016_to_2019(df:DataFrame)->DataFrame:
    # Filter data for the time range between 2016 and 2019 and where arrests occurred
    arrested_df = df.filter((F.col("Year") >= 2016) & (F.col("Year") <= 2019) & (F.col("Arrest") == "true"))

    # Group by 'Primary Type' and count the number of arrests for each crime type
    crime_counts = arrested_df.groupBy("Primary Type").count()

    # Rank crime types based on the count in descending order
    ranked_crimes = crime_counts.orderBy(F.desc("count")).limit(15)

    name = 'types_of_crimes_most_arrested_from_2016_to_2019'

    return ranked_crimes, name

def task_finished(project_id:str, topic_name:str, message:str):
    print(f"Creating a publisher client with topic '{topic_name}'.")
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    message_data = message

    future = publisher.publish(topic_path, data=message_data.encode("utf-8"))
    future.result()
    print(f"Message '{message}'sent to topic '{topic_name}'.")

    return True

def main():
    print('Starting processign job.')
    DATA_BUCKET_NAME, DATA_FILE_NAME = get_config()
    PROJECT_ID = 'tarrieu'
    TOPIC_NAME = "processing_job_ended"

    unzip_files(DATA_BUCKET_NAME, DATA_FILE_NAME)

    df_raw = pull_gcs_csv_to_df(DATA_BUCKET_NAME, DATA_FILE_NAME)
    df_0 = add_3y(df_raw)

    processing_function_list = [
        total_crimes_past_5y_per_month,
        top_10_theft_crimes_location_past_3y,
        total_crimes_per_year,
        safest_locations_4pm_to_10pm,
        types_of_crimes_most_arrested_2016_to_2019
    ]

    for index, func in enumerate(processing_function_list, start=1):
        print(f'Starting job n°{index}.')
        print('Computing ...')
        df, name = func(df_0)
        print('Computing ended.')
        load_df_to_gcs_csv(df, DATA_BUCKET_NAME, name)
        print(f'Ended job n°{index}.')

    task_finished(PROJECT_ID, TOPIC_NAME, 'job_finished')

if __name__ == '__main__':
    main()