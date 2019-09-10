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

# [ ] Write a Readme
# [ ] Readme
  
import os
import kfp
from kfp import dsl
from kfp import gcp


# Load the SparkJob Component
# code_path = os.path.dirname(__file__)
# conf_path = os.path.join(code_path, 'configuration.yaml')
# spark_run_op =  kfp.components.load_component_from_file(conf_path)

component_store = kfp.components.ComponentStore(
    local_search_paths=['components'])
spark_run_op = component_store.load_component('spark_component')


@kfp.dsl.pipeline(name="test", description='Hans, get the kubeflower')
def my_pipeline(
    clusterproject='sparkpubsub', 
    cluster='spark',
    region='europe-west4',
    staging='output-sparkpubsub-tweets',
    project='sparkpubsub',
    tableproject='sparkpubsub',
    dataset='wordcount',
    table='wordcount_output', 
    output='gs://output-sparkpubsub-tweets/output/data.csv',
    ):

    spark_task = spark_run_op(
            clusterproject=clusterproject,
            cluster=cluster,
            region=region,
            staging=staging,
            project=project, # project of output bucket
            tableproject=tableproject, # table to read
            dataset=dataset,
            table=table,
            output=output, # path of output data
    ).apply(gcp.use_gcp_secret('user-gcp-sa')) 

# compile the bad boy 
# dsl-compile --py pipeline.py  --output ./pipeline.tar.gz