import apache_beam as beam
import etl.util as util
import logging


class TransformFn(beam.DoFn):
    def process(self, activity):
        logging.info(f"transforming {activity.source_path}")

        record = {"source_path": activity.source_path}
        for model in util.models:
            try:
                record[model] = getattr(activity, f"transform__{model}_record")()
                yield beam.pvalue.TaggedOutput(util.SUCCESS_TAG, record)
            except Exception as e:
                logging.warning(
                    f"{record['source_path']}:{model}: failed transform {e} skipping..."
                )
                record[model] = None
                yield beam.pvalue.TaggedOutput(util.FAILURE_TAG, record)
