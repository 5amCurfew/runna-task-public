from models.activity import Activity
import apache_beam as beam
import etl.util as util
import logging


class TransformFn(beam.DoFn):
    def process(self, activity):
        logging.info(f"transforming {activity['sourcePath']}")

        try:
            act = Activity.from_json(activity)
        except Exception as e:
            logging.warning(f"{activity['sourcePath']}: {e} skipping...")
            yield beam.pvalue.TaggedOutput(
                util.FAILURE_TAG, (activity["sourcePath"], str(e))
            )
            return

        record = {"source_path": act.source_path}
        for model in util.transformations:
            try:
                record[model] = getattr(act, f"transform__{model}_record")()
            except Exception as e:
                logging.warning(
                    f"{record['source_path']}:{model}: failed transform {e} skipping..."
                )
                record[model] = None

        logging.info(f"transformed {record['source_path']}")
        yield beam.pvalue.TaggedOutput(util.SUCCESS_TAG, record)
