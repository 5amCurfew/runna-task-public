import apache_beam as beam
from apache_beam.io.filesystems import FileSystems
from apache_beam.options.pipeline_options import PipelineOptions
from models.Activity import Activity
import argparse
import datetime
import etl
import logging
from typing import Optional

logging.getLogger().setLevel(logging.INFO)

SUCCESS_TAG = "SUCCESS"
FAILURE_TAG = "FAILURE"

transformations = [
    "fct__activities",
    #'dim__plans',
    #'dim__workouts',
    #'bdg__activity_to_laps',
    "bdg__workout_to_steps",
]


# ########################
# ETL Fns
# ########################
class ExtractFn(beam.DoFn):
    def process(self, file_path):
        logging.info(f"extracting {file_path} at {datetime.datetime.now()}...")

        activity, error = etl.extract(file_path)
        if error:
            logging.warning(f"{file_path}: {error} skipping...")
            yield beam.pvalue.TaggedOutput(FAILURE_TAG, (file_path, error))
        else:
            logging.info(f"extracted {file_path} at {datetime.datetime.now()}")
            yield beam.pvalue.TaggedOutput(SUCCESS_TAG, activity)


class TransformFn(beam.DoFn):
    def process(self, activity):
        logging.info(
            f"transforming {activity['sourcePath']} at {datetime.datetime.now()}"
        )

        try:
            act = Activity.from_json(activity)
        except Exception as e:
            logging.warning(f"{activity['sourcePath']}: {e} skipping...")
            yield beam.pvalue.TaggedOutput(
                FAILURE_TAG, (activity["sourcePath"], str(e))
            )
            return

        record = {"source_path": act.source_path}
        for model in transformations:
            try:
                record[model] = getattr(act, f"transform__{model}_record")()
            except Exception as e:
                logging.warning(
                    f"{record['source_path']}:{model}: failed transformation {e} - setting to NULL..."
                )
                record[model] = None

        logging.info(
            f"transformed {record['source_path']} at {datetime.datetime.now()}"
        )
        yield beam.pvalue.TaggedOutput(SUCCESS_TAG, record)


class LoadFn(beam.DoFn):
    def process(self, record):
        for model in transformations:
            if not record[model]:
                continue
            try:
                etl.load(model, record[model])
                yield f"{record['sourcePath']} loaded at {datetime.datetime.now()}"
            except Exception as e:
                logging.warning(f"{record['sourcePath']}:{model}: {e} - skipping...")
                continue


# ########################
# Apache Beam Pipeline
# ########################
class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            "--batch_date", type=str, help="Batch date in YYYY-MM-DD format"
        )


def execute(pipeline_options: Optional[PipelineOptions] = None):
    with beam.Pipeline(options=pipeline_options) as p:
        custom_options = pipeline_options.view_as(CustomOptions)
        batch_date = custom_options.batch_date

        directory_pattern = f"data/{batch_date}/*.json"
        activity_paths = FileSystems.match([directory_pattern])[0].metadata_list
        file_paths = [file.path for file in activity_paths]
        if len(file_paths) == 0:
            raise ValueError(f"No files found for batch date {batch_date}")

        logging.info(f"files in batch: {', '.join(file_paths)}")

        extracted = (
            p
            | "Find activities for batch" >> beam.Create(file_paths)
            | "Extract"
            >> beam.ParDo(ExtractFn()).with_outputs(SUCCESS_TAG, FAILURE_TAG)
        )

        transformed = extracted[SUCCESS_TAG] | "Transform" >> beam.ParDo(
            TransformFn()
        ).with_outputs(SUCCESS_TAG, FAILURE_TAG)

        transformed[SUCCESS_TAG]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process activity files for a specific batch date"
    )
    parser.add_argument(
        "--batch_date", type=str, help="Batch date in YYYY-MM-DD format"
    )
    args, _ = parser.parse_known_args()

    # Define PipelineOptions
    options = PipelineOptions(
        runner="DirectRunner",
        direct_num_workers=3,
        save_main_session=True,
        batch_date=args.batch_date,
    )

    execute(pipeline_options=options)
