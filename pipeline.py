from apache_beam.io.filesystems import FileSystems
from apache_beam.options.pipeline_options import PipelineOptions
from typing import Optional
import apache_beam as beam
import argparse
import etl
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger(__name__)


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
            >> beam.ParDo(etl.extract.ExtractFn()).with_outputs(
                etl.util.SUCCESS_TAG, etl.util.FAILURE_TAG
            )
        )

        transformed = extracted[etl.util.SUCCESS_TAG] | "Transform" >> beam.ParDo(
            etl.transform.TransformFn()
        ).with_outputs(etl.util.SUCCESS_TAG, etl.util.FAILURE_TAG)

        transformed[
            etl.util.SUCCESS_TAG
        ]  # | "Print" >> beam.Map(lambda record: print(json.dumps(record, indent=4)))


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
