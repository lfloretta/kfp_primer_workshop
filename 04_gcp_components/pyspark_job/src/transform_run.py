
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

# Spark Application that downloads data from a user-supplied
# BigQuery Table, applies transformations and writes the output to CSV 
# on a user specified Google Cloud Storage (GCS bucket) 
#
# The application is dependent on the BigQuery Storage API connector (Beta)
# and the GCS connector. They are passed as a single uber-jar, built with the pom.xml 
# The jar is pre-packaged in ./target/sparkicson-0.1-dependencies.jar
#
# Note that a default dataproc cluster
# uses the compute (<project>-compute@developer...) service account, which can't read from BigQuery.

""" TESTING SCRIPT ON DATAPROC set environment variables
export DATASET=<your_dataset>
export TABLE=<your_table>
export TABLEPROJECT=<your_table_project>
export CLUSTER=<your_cluster_name>
export REGION=<cluster_region> 
export OUTPUT=<path_plus_file_extension> 

gcloud dataproc jobs submit pyspark --cluster $CLUSTER  \
    --region $REGION \
    --jars ./target/sparkicson-0.1-dependencies.jar \
    transform_run.py \
    -- \
    --tableProject $TABLEPROJECT \
    --dataset $DATASET \
    --table $TABLE \
    --output $OUTPUT
"""

#! usr/bin/python
import argparse
from pyspark.sql import SparkSession

parser = argparse.ArgumentParser(description="BigQuery to GCS connector")
parser.add_argument("--output", type=str, required=True, help="specify path and file name; gs://bucket/path/file.csv")
parser.add_argument("--dataset", type=str, required=True, help="dataset name")
parser.add_argument("--tableProjectID", type=str, required=True, help="project name that contains the table")
parser.add_argument("--table", type=str, required=True, help="table name")

args = parser.parse_args()
    
def loadData(spark, tableProject, dataset, table):
    """ Download full table through BigQuery storage API
    args: 
        spark: sparksession
        tableProjectID: name of GCP project that containts the BigQuery table
        dataset: dataset name
        table: table name
    returns: dataframe
    """

    if (len(tableProject) < 1 or len(dataset) < 1 or len(table) < 1):
        return 

    qualifiedTable = tableProject + ":" + dataset + "." + table 

    df = spark.read.format('bigquery').option('table', qualifiedTable).load()

    return df

def main():
    
    ss = spark = SparkSession \
        .builder \
        .getOrCreate()
        
    # Load data 
    df = loadData(ss, args.tableProjectID, args.dataset, args.table)
    
    # Selected columns 
    # df.select("load_type")

    # Write to GCS
    df.write.mode("overwrite").save(args.output, format="csv")
    df.printSchema()
    ss.stop()

if __name__ == "__main__":
    main()