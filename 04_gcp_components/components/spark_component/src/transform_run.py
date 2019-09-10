
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
# When running locally, make sure the --keyfile run-time argument points
# to a service account with the right permissions to read from BigQuery
# and write to GCS. If left blank, it assumes the GOOGLE_APPLICATION_CREDENTIALS
# environment variable is set with the right permissions. Note that a default dataproc cluster
# uses the compute (<project>-compute@developer...) service account, which can't read from BigQuery.

""" set environment variables
export PROJECT=<project_name_output_bucket>
export DATASET=<your_dataset>
export TABLE=<your_table>
export TABLEPROJECT=<your_table_project>
export CLUSTER=<your_cluster_name>
export REGION=<cluster_region> 
export OUTPUT=<path_plus_file_extension> 

spark-submit  \
    --master local[3] \
    --jars ./target/sparkicson-0.1-dependencies.jar \
    transform_run.py \
    --tableProject $TABLEPROJECT \
    --dataset $DATASET \
    --table $TABLE \
    --project $PROJECT \
    --output $OUTPUT \
    --keyfile  /Users/evanderknaap/Desktop/sparkpubsub-016f689237cd.json
"""

""" dataproc run
gcloud dataproc jobs submit pyspark --cluster $CLUSTER  \
    --region $REGION \
    --jars ./target/sparkicson-0.1-dependencies.jar \
    transform_run.py \
    -- \
    --tableProject $TABLEPROJECT \
    --dataset $DATASET \
    --table $TABLE \
    --project $PROJECT \
    --output $OUTPUT
"""

import argparse
from pyspark import SparkContext
from pyspark.sql import SparkSession

parser = argparse.ArgumentParser(description="BigQuery to GCS connector")
parser.add_argument("--project", type=str, required=True, help="project name of output bucket")
parser.add_argument("--dataset", type=str, required=True, help="dataset name")
parser.add_argument("--tableProject", type=str, required=True, help="project name that contains the table")
parser.add_argument("--table", type=str, required=True, help="table name")
parser.add_argument("--output", type=str, required=True, help="specify path and file name; gs://bucket/path/file.csv")
parser.add_argument("--keyfile", 
                    type=str, 
                    required=False, 
                    default="",
                    help="location of the json service account file. If left blank, it is assumed \
                        that the GOOGLE_APPLICATION_CREDENTIALS environment variable is set") 

args = parser.parse_args()

def configureSpark(keyFile, project):
    
    spark = SparkSession \
        .builder \
        .getOrCreate()

    # Authenticate with supplied json service-account keyfile, if supplied
    # This is not needed if run on dataproc
    if (len(keyFile) > 0):

        hadoop_settings = {
            "google.cloud.auth.service.account.enable":"true",
            "google.cloud.auth.service.account.json.keyfile":keyFile,
            "fs.gs.impl":"com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            "fs.AbstractFileSystem.gs.impl":"com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            "fs.gs.project.id":project,
            "credentialsFile":keyFile # BigQuery Storage API credentials
        }

        for key in hadoop_settings.keys():
            spark.sparkContext._jsc.hadoopConfiguration()\
                .set(key, hadoop_settings[key])    
        
    return spark
    
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
    # Configure SparkSession
    ss = configureSpark(args.keyfile, args.project)

    # Load data 
    df = loadData(ss, args.tableProject, args.dataset, args.table)
    
    # Select and filter
    # df.select("load_type")
    # Write to GCS
    df.write.mode("overwrite").save(args.output, format="csv")
    df.printSchema()
    ss.stop()

if __name__ == "__main__":
    main()