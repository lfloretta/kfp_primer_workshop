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
# Submit a pyspark job to a DataProc cluster 

import argparse
import os
from google.cloud import dataproc_v1
from google.cloud.dataproc_v1.gapic.transports import (job_controller_grpc_transport)
from google.cloud import storage
import tensorflow as tf 
from pathlib import Path

""" Local test: export environment variables
export PROJECT=<project_name_output_bucket>
export DATASET=<your_dataset>
export TABLE=<your_table>
export TABLEPROJECT=<your_table_project>
export CLUSTER=<your_cluster_name>
export REGION=<cluster_region> 
export OUTPUT=<path_plus_file_extension> 
export STAGING=<bucket_name_without_gs://> 
export REGION=<your_region>

python3 src/transform.py  \
    --clusterProject $PROJECT \
    --cluster $CLUSTER \
    --region $REGION \
    --output $OUTPUT \
    --project $PROJECT \
    --staging $STAGING \
    --tableProject $TABLEPROJECT \
    --dataset $DATASET \
    --table $TABLE 
"""

# Make sure that the service account of the DataProc cluster 
# has the BigQuery User and Viewer role, to access BigQuery Storage API.

"""
gcloud dataproc clusters create $CLUSTER \
    --service-account=dataproc-510@sparkpubsub.iam.gserviceaccount.com \
    --region $REGION \
    --zone $ZONE
"""

def getRuntimeArguments():

    parser = argparse.ArgumentParser(description="Submit pyspark to DataProc cluster")
    parser.add_argument("--clusterProject", type=str, required=True, help="project name of output bucket")
    parser.add_argument("--cluster", type=str, required=True, help= "DataProc cluster name")
    parser.add_argument("--region", type=str, required=True, help= "Region of DataProc Cluster")
    parser.add_argument("--staging", type=str, required=True, help="staging bucket name")
    parser.add_argument("--project", type=str, required=True, help="project name of output bucket")
    parser.add_argument("--dataset", type=str, required=True, help="dataset name")
    parser.add_argument("--tableProject", type=str, required=True, help="project name that contains the table")
    parser.add_argument("--table", type=str, required=True, help="table name")
    parser.add_argument("--runfile", type=str, required=False, default="transform_run.py")
    parser.add_argument("--uberjar", type=str, required=False, default="./target/sparkicson-0.1-dependencies.jar")
    parser.add_argument("--keyfile", 
                        type=str, 
                        required=False, 
                        default="",
                        help="location of the json service account file. If left blank, it is assumed \
                            that the GOOGLE_APPLICATION_CREDENTIALS environment variable is set") 
    parser.add_argument("--output", type=str, required=True, help="URI path for the output gs://bucket/path/file.csv")
    parser.add_argument("--output-file", 
                        type=str, 
                        required=False, 
                        help="URI to the output file, containing output URI",
                        default="./out.txt")
    args =  parser.parse_args()

    return args

# Upload files to gcs 
def upload_to_gcs(project, bucket_name, file_path):
    """Upload dependencies and run file to GCS"""
    filename = os.path.basename(file_path) # get just the filename

    print('Uploading {} to GCS'.format(filename))
    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename) # path on the bucket
    blob.upload_from_filename(file_path)
    return "gs://" + bucket_name + "/" + filename
    
def submit_pyspark_job(dataproc, project, region, cluster, spark_properties, main_file, jar):
    
    job_details =  {
            "placement": {
                "cluster_name": cluster,
            },
            "pyspark_job": {
                "main_python_file_uri": main_file,
                "jar_file_uris": [jar],
                "args" : spark_properties
                }
            }

    result = dataproc.submit_job(
        project_id=project,
        region=region,
        job=job_details
    )

    job_id = result.reference.job_id
    print('submitted job {}'.format(job_id))
    return job_id 

def setSparkJobProperties(tableProject, dataset, table, gcsproject, output, keyfile):
    print("Setting spark config") 
    spark_job_properties = [
                    "--tableProject", tableProject,
                    "--dataset" , dataset,
                    "--table" , table,
                    "--project", gcsproject,
                    "--output" ,  output
                ]
    if (len(keyfile) > 0):
        spark_job_properties.append("--keyfile")
        spark_job_properties.append(keyfile)

    return spark_job_properties

def getDataProcClient(region):
    print ("Connecting to DataProc")
    job_transport = (
        job_controller_grpc_transport.JobControllerGrpcTransport(
            address='{}-dataproc.googleapis.com:443'.format(region)))
    dataproc_job_client = dataproc_v1.JobControllerClient(job_transport)
    return dataproc_job_client
    
def main():
    # Parse runtime arguments
    args = getRuntimeArguments()

    # Set Sparkjob properties. 
    spark_properties = setSparkJobProperties(
        tableProject = args.tableProject,
        dataset = args.dataset,
        table = args.table,
        gcsproject = args.project,
        output = args.output,
        keyfile = args.keyfile)

    # Upload the run_file, and dependencies jar to a staging bucket
    code_path = os.path.abspath(os.path.dirname(__file__)) # Base path of this file
    run_file_local =  os.path.join(code_path, args.runfile)
    jar_file_local = os.path.join(code_path, args.uberjar)
    
    run_file_gcs = upload_to_gcs(project=args.project, bucket_name=args.staging, file_path = run_file_local)
    jar_file_gcs = upload_to_gcs(project=args.project, bucket_name=args.staging, file_path = jar_file_local)

    # Create dataproc client with regional end-point    
    dataproc_client = getDataProcClient(args.region)

    job_id = submit_pyspark_job(
        dataproc = dataproc_client,
        project = args.clusterProject,
        region = args.region,
        cluster = args.cluster,
        spark_properties =  spark_properties,
        main_file = run_file_gcs,
        jar = jar_file_gcs
    )

    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_file).write_text(args.output)

    return 
 
if __name__ == "__main__":
    main()
