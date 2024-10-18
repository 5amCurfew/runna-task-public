import apache_beam as beam
from apache_beam.io.filesystems import FileSystems
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from models import Activity
import argparse
import datetime
import etl
import logging
from typing import Optional

# ########################
# Apache Beam Pipeline
# ########################
SUCCESS_TAG = 'SUCCESS'
FAILURE_TAG = 'FAILURE'

transformations = [
    'fct__activities',
    'dim__plans',
    'dim__workouts',
    'bdg__activity_to_laps',
    'bdg__workout_to_steps'
]

# ########################
# ETL Fns
# ########################
class ExtractFn(beam.DoFn):
    def process(self, file_path):
        data, error = etl.extract(file_path)
        if error:
            # Yield to failure side output
            yield beam.pvalue.TaggedOutput(FAILURE_TAG, (file_path, error))
        else:
            yield beam.pvalue.TaggedOutput(SUCCESS_TAG, data)

class TransformFn(beam.DoFn):
    def process(self, activity):
        try:
            act = Activity(**activity)
        except Exception as e:
            yield beam.pvalue.TaggedOutput(FAILURE_TAG, (activity['sourcePath'], str(e)))
            return

        result = {'sourcePath': act.sourcePath}
        for model in transformations:
            try:
                result[model] = getattr(act, f"transform__{model}")()
            except Exception as e:
                # If an error occurs, set the result to None
                result[model] = None

        yield beam.pvalue.TaggedOutput(SUCCESS_TAG, result)

class LoadFn(beam.DoFn):
    def process(self, record):
        for model in transformations:
            try:
                etl.load(model, record[model], record['sourcePath'])
            except Exception as e:
                continue

        yield f"{record['sourcePath']} loaded at {datetime.datetime.now()}"


# ########################
# Apache Beam Pipeline
# ########################
class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--batch_date', type=str, help='Batch date in YYYY-MM-DD format')

def execute(pipeline_options: Optional[PipelineOptions] = None):
    with beam.Pipeline(options=pipeline_options) as p:
        custom_options = pipeline_options.view_as(CustomOptions)
        batch_date = custom_options.batch_date
        
        directory_pattern = f"data/{batch_date}/*.json"
        activity_paths = FileSystems.match([directory_pattern])[0].metadata_list
        file_paths = [file.path for file in activity_paths]
        
        extracted = (
            p
            | 'Find activities for batch' >> beam.Create(file_paths)
            | 'Extract' >> beam.ParDo(ExtractFn()).with_outputs(
                SUCCESS_TAG, FAILURE_TAG
            )
        )

        transformed = (
            extracted[SUCCESS_TAG]
            | "Transform" >> beam.ParDo(TransformFn()).with_outputs(
                SUCCESS_TAG, FAILURE_TAG
            )
        )

        loaded = (
            transformed[SUCCESS_TAG] 
            | beam.ParDo(LoadFn())
        )

        loaded | beam.Map(print)
        #transformed[FAILURE_TAG] | beam.Map(print)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process activity files for a specific batch date')
    parser.add_argument('--batch_date', type=str, help='Batch date in YYYY-MM-DD format')
    args, _ = parser.parse_known_args()

    # Define PipelineOptions
    options = PipelineOptions(
        runner='DirectRunner',
        direct_running_mode='multi_procssing',
        direct_num_workers=3,
        save_main_session=True,
        batch_date=args.batch_date
    )

    execute(pipeline_options=options)
