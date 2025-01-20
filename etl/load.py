import apache_beam as beam
import etl.util as util
import logging


class LoadFn(beam.DoFn):
    def process(self, record):
        for model in util.models:
            if model not in record:
                continue
            try:
                logging.info(f"{record['source_path']}:{model} successfully loaded")
            except Exception as e:
                logging.warning(
                    f"{record['source_path']}:{model}: failed load {e} - skipping..."
                )
                yield beam.pvalue.TaggedOutput(
                    util.FAILURE_TAG, (record["source_path"], model, str(e))
                )
