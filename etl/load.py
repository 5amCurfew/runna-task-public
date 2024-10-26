import apache_beam as beam
import etl.util as util
import logging


class LoadFn(beam.DoFn):
    def process(self, record):
        for model in util.transformations:
            if not record[model]:
                continue
            try:
                # load(model, record[model])
                yield f"{record['sourcePath']} loaded"
            except Exception as e:
                logging.warning(f"{record['sourcePath']}:{model}: {e} - skipping...")
                continue
