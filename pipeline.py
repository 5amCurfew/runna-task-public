import apache_beam as beam
from apache_beam.io.filesystems import FileSystems
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from models import Activity
import argparse
import datetime
import etl
import os
from typing import Optional

SUCCESS_TAG = 'SUCCESS'
FAILURE_TAG = 'FAILURE'

class ExtractFn(beam.DoFn):
    def process(self, file_path):
        data, error = etl.extract(file_path)
        if error:
            # Yield to failure side output
            yield beam.pvalue.TaggedOutput(FAILURE_TAG, (file_path, error))
        else:
            # Yield to the main (success) output
            yield beam.pvalue.TaggedOutput(SUCCESS_TAG, data)

class TransformFn(beam.DoFn):
    def process(self, activity):
        try:
            act = Activity(**activity)  # Instantiate Activity class
        except Exception as e:
            # Yield to failure side output if Activity instantiation fails
            yield beam.pvalue.TaggedOutput(FAILURE_TAG, (activity, str(e)))

        result = {}
        # List of transformation method names
        transformations = [
            'fct__activities',
            'dim__plans',
            'dim__workouts',
            'bdg__activity_to_laps',
            'bdg__workout_to_steps'
        ]

        for method in transformations:
            try:
                # Dynamically call the method on the Activity object
                result[method] = getattr(act, f"transform__{method}")()
            except Exception as e:
                # If an error occurs, set the result to None
                result[method] = None

        yield result



class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--batch_date', type=str, help='Batch date in YYYY-MM-DD format')

# Apache Beam Pipeline
def execute(pipeline_options: Optional[PipelineOptions] = None):
    with beam.Pipeline(options=pipeline_options) as p:
        custom_options = pipeline_options.view_as(CustomOptions)
        batch_date = custom_options.batch_date
        
        # Use Beam's FileSystems to list files in the directory
        directory_pattern = f"data/{batch_date}/*.json"  # Match all files in the directory
        activity_paths = FileSystems.match([directory_pattern])[0].metadata_list
        file_paths = [file.path for file in activity_paths]
        
        parsed = (
            p
            | 'Find activities for batch' >> beam.Create(['data/2024-10-01/take-home-example-activity-1.json'])
            | 'Extract Data with Tagged Output' >> beam.ParDo(ExtractFn()).with_outputs(
                SUCCESS_TAG, FAILURE_TAG
            )
        )

        # Printing only the successful outputs
        activities = parsed[SUCCESS_TAG] | beam.ParDo(TransformFn()) | beam.Map(print)

        # Optional: Print or handle failures (for debugging purposes)
        #parsed[FAILURE_TAG] | "Print Failure" >> beam.Map(print)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process activity files for a specific batch date')
    parser.add_argument('--batch_date', type=str, help='Batch date in YYYY-MM-DD format')
    args, pipeline_args = parser.parse_known_args()

    options = PipelineOptions(pipeline_args)
    options.view_as(SetupOptions).save_main_session = True  # Ensures that the main session state is accessible

    # Define PipelineOptions
    options = PipelineOptions(
        project='runna-task-public',
        batch_date=args.batch_date,
        runner='DirectRunner'  # Or DataflowRunner for GCP Dataflow
    )

    execute(pipeline_options=options)
