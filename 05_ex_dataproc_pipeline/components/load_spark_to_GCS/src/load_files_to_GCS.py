# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Load a file to GCS


import argparse
import os

from google.cloud import storage
from pathlib import PurePath


def uplaod_file_to_gcs(local_path: str, gcs_path: str) -> str:

    filename = os.path.basename(local_path)
    pure_path = PurePath(gcs_path)
    gcs_bucket = pure_path.parts[1]
    gcs_blob = '/'.join(pure_path.parts[2:] + (filename, ))
    client = storage.Client()
    bucket = client.get_bucket(gcs_bucket)
    blob = bucket.blob(gcs_blob)
    blob.upload_from_filename(local_path)

    return '/'.join((gcs_path, filename))


def dump_file(path: str, content: str):
    """Dumps string into local file.

    Args:
        path: the local path to the file.
        content: the string content to dump.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif os.path.exists(path):
        logging.warning('The file {} will be overwritten.'.format(path))
    with open(path, 'w') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description='Load a file to GCS')

    parser.add_argument(
        '--gcs-path',
        type=str,
        required=True,
        help='GCS path to where load the local file excluding file name'
    )

    known_args, _ = parser.parse_known_args()
    transform_run_path = uplaod_file_to_gcs(
        '/pipelines/component/src/spark_files/transform_run.py', known_args.gcs_path)

    dump_file('/tmp/kfp/output/pyspark/transform_run.txt', transform_run_path)

    jar_path = uplaod_file_to_gcs(
        '/pipelines/component/src/spark_files/sparkicson-0.1-dependencies.jar', known_args.gcs_path)

    dump_file('/tmp/kfp/output/pyspark/jar_path.txt', jar_path)

if __name__ == '__main__':
    main()