import apache_beam as beam
import etl.util as util
import json
import logging


class ExtractFn(beam.DoFn):
    def process(self, file_path):
        logging.info(f"extracting {file_path}")

        activity, error = extract(file_path)
        if error:
            logging.warning(f"{file_path}: {error} skipping...")
            yield beam.pvalue.TaggedOutput(util.FAILURE_TAG, (file_path, error))
        else:
            logging.info(f"extracted {file_path}")
            yield beam.pvalue.TaggedOutput(util.SUCCESS_TAG, activity)


def extract(path: str) -> tuple[dict, str]:
    """
    Extracts activity data from a given JSON file
    """
    try:
        with open(path, "r") as file:
            data = json.load(file)
            data["sourcePath"] = path
            return data, None
    except FileNotFoundError as e:
        return None, str(f"FileNotFoundError: {e}: {path}")
    except json.JSONDecodeError as e:
        return None, str(f"JSONDecodeError: {e}: {path}")
