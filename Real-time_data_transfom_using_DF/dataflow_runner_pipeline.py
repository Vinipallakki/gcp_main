import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, GoogleCloudOptions
import json

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)  # Set to DEBUG for more detailed logs

# Project details
PROJECT_ID = "databricks-vini"
TOPIC_ID = "real-time-data"
SUBSCRIPTION_ID = "real-time-data-sub"

# Dataset and table names
DATASET_NAME = "sensor_data"
TABLE_NAME = "sensor_readings"

# Subscription path
input_subscription = f"projects/{PROJECT_ID}/subscriptions/{SUBSCRIPTION_ID}"
output_table = f"{PROJECT_ID}:{DATASET_NAME}.{TABLE_NAME}"

class ParseJson(beam.DoFn):
    def process(self, element):
        data = json.loads(element)
        return [data]

# Define PipelineOptions for DataflowRunner
options = PipelineOptions()
options.view_as(StandardOptions).runner = 'DataflowRunner'  # Use DataflowRunner
options.view_as(StandardOptions).streaming = True

# Set Google Cloud-specific options
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = PROJECT_ID
google_cloud_options.region = 'us-central1'  # Update with your desired region
google_cloud_options.temp_location = 'gs://garbage_dumps_1/temp/'  # Update with your GCS bucket and path
google_cloud_options.staging_location = 'gs://garbage_dumps_1/staging/'  # Update with your GCS bucket and path

p = beam.Pipeline(options=options)

# Define and run the pipeline
result = (p
 | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
 | "ParseJson" >> beam.ParDo(ParseJson())
 | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
        output_table,
        schema="sensor_id:INTEGER, temperature:FLOAT, humidity:FLOAT, timestamp:FLOAT",
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
    ))

# Run the pipeline and wait for it to finish
pipeline_result = p.run()
pipeline_result.wait_until_finish()
