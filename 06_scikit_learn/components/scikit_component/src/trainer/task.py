import logging
import sys

import argparse
import model
import utils
import metadata
import time
import os
from sklearn import model_selection
from pathlib import Path

def get_args():
    
    parser = argparse.ArgumentParser(
        description="ArgeParser"
        )

    parser.add_argument('--pathdata', 
                        help="Path to where the raw data is",
                        type=str,
                        required=False,
                        default=1
                        )

    parser.add_argument('--storage', 
                        help="Where your data is stored: BQ or GCS",
                        type=str,
                        required=True,
                        default=1
                        )

    parser.add_argument('--pathoutput', 
                        help="GCS Bucket to output the trained model as model.joblib",
                        required=True,
                        type=str,
                        default=1
                        )

    parser.add_argument('--pathoutputfile', 
                        help="Where to write the data that needs to be passed to next component",
                        required=True,
                        type=str,
                        default=1
                        )                    

    parser.add_argument('--bqtable', 
                        help="Full path to the BigQuery table: yourproject.dataset.table",
                        type=str,
                        required=False,
                        default=1
                        )

    arguments = parser.parse_args()

    return arguments

def main():

    args = get_args()

    path_data = args.pathdata

    output_bucket = args.pathoutput

    storage = args.storage

    full_table_path = args.bqtable

    if storage in ['BQ', 'bq' 'bigquery', 'BigQuery', 'bigQuery', 'Bigquery', 'Bq']:
      dataset = utils.read_df_from_bigquery(full_table_path)
    else:
      dataset = utils.get_data_from_gcs(path_data)

    x_train, y_train, x_val, y_val = utils.data_train_test_split(dataset)

    pipeline = model.get_pipeline()
   
    pipeline.fit(x_train, y_train)

    scores = model_selection.cross_val_score(pipeline, x_val, y_val, cv=3)

    print("model score: %.3f" % pipeline.score(x_val, y_val))
    print('pipeline run done :)')

    model_output_path = os.path.join(
      output_bucket,'model/', metadata.MODEL_FILE_NAME)

    metric_output_path = os.path.join(
      output_bucket, 'experiment', metadata.METRIC_FILE_NAME)

    utils.dump_object(pipeline, model_output_path)
    utils.dump_object(scores, metric_output_path)

    joblib_output_path = os.path.join(
      output_bucket)

    Path(args.pathoutputfile).parent.mkdir(parents=True, exist_ok=True)
    Path(args.pathoutputfile).write_text(joblib_output_path)

if __name__ == '__main__':
    main()

    