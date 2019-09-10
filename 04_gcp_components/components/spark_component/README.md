# Download BigQuery table to CSV on GCS using Spark on DataProc
 
This component deploys a [pyspark job on DataProc](https://cloud.google.com/sdk/gcloud/reference/dataproc/jobs/submit/pyspark) which downloads a full table from BigQuery using the [BigQuery Storage API](https://cloud.google.com/bigquery/docs/reference/storage/) and writes the results, in csv, to a specfied location on Google Cloud Storage.

## Inputs 

| name | type | Required | Default | description |
|------|------|---------|----------|-------------|
| `clusterProject` | String | Yes ||  GCP ProjectID of the DataProc cluster|
| `cluster` | String | Yes || Name of the DataProc cluster |
| `region` | String | Yes || Region of the DataProc cluster. For example Europe-west4. |
| `staging` | String | Yes || Name of the staging bucket. NOTE, do not add gs:// to the path. On the staging bucket, the JAR dependencies and pyspark runfile is uploaded" |
| `project` | String | Yes || ProjectID that contains the target bucket, to store the data. |
| `output` | String  |Yes|| Path, including filename and extension, on GCS. For example gs://yourbucket/output/filename/csv. |
| `tableProject` | String | Yes || ProjectID of BigQuery source table. |
| `dataset`| String |Yes|| Dataset name of the BigQuery source table. |
| `table`| String |Yes|| Table name of the BigQuery source table. |
| `keyFile` | String | No | "" | Location of a service account key. This is not needed when run on GKE. The keyfile can be used to test the component locally as a python script, ot a standalone container |
| `uberjar` | String | No | target/sparkicson-0.1-dependencies.jar | Path to the pyspark uber-jar, containing all the required Java spark dependencies to run the spark job. The pyspark program uses the [gcs-connector](https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage), as well as the [bigquery storage API connector (beta)](https://github.com/GoogleCloudPlatform/spark-bigquery-connector) When the kubeflow component is run, the JAR file and the spark python file are uploaded to the staging bucket and then submitted to DataProc. In the source folder, the POM.xml file is located to build your own uber-jar, if connector versions are preferred.

## Output 

| name | type | Required | Default | description |
|------|------|---------|----------|-------------|
| `outputfile` | String | No | | Path to the component output file. |

## Container Image 

'gcr.io/sparkpubsub/sparkbqread:latest'

## Usage

To use the component, a DataProc cluster must be created so that the component
can submit the job to the DataProc cluster. The default service account of
DataProc does not allow access to the BigQuery Storage API. So after creating
the cluster, additional roles have to be assigned to the DataProc service account.

### Create a project

In the [GCP console](console.cloud.google.com), select the drop-down arrow in the top
navigation bar, and create a new project. Full instructions are [here](https://cloud.google.com/resource-manager/docs/creating-managing-projects)

Set some environment variables 
```
export PROJECT=<your_project_ID>
export REGION=<your_region>
export CLUSTER=<your_region>
```

### Enable APIs 
```bash
gcloud services enable bigquerystorage.googleapis.com 
gcloud services enable dataproc.googleapis.com
gcloud services enable iam.googleapis.com
```

### Create a DataProc cluster 
```bash
gcloud dataproc clusters create $CLUSTER \
--region=$REGION --num-workers 5
```

The default service account for a dataproc cluster is ` [project-number]-compute@developer.gserviceaccount.com` We need to assign the BigQuery User, 
and Viewer role to this service account in order it to use the BigQuery storage API.

### Set the right credetials

```bash
gcloud projects add-iam-policy-binding $PROJECT \
  --member serviceAccount:<PROJECTNUMBER>-compute@developer.gserviceaccount.com \
  --role roles/bigquery.user
```

### Create pipeline code

```python
import os
import kfp
from kfp import dsl
from kfp import gcp

@kfp.dsl.pipeline(name="BigQuery to GCS", description='Download BQ table to gcs')
def my_pipeline(
    clusterproject, 
    cluster,
    region,
    staging,
    project,
    tableproject,
    dataset=,
    table, 
    output,
    ):

    # Load the SparkJob Component
    code_path = os.path.dirname(__file__) 
    conf_path = os.path.join(code_path, 'configuration.yaml')
    spark_run_op =  kfp.components.load_component_from_file(conf_path)
    
    spark_task = spark_run_op(
            clusterproject = clusterproject,
            cluster = cluster,
            region =  region,
            staging = staging,
            project = project, # project of output bucket
            tableproject = tableproject, # table to read
            dataset = dataset,
            table = table,
            output = output, # path of output data
    ).apply(gcp.use_gcp_secret('user-gcp-sa')) 
```