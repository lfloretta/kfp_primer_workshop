#!/bin/bash -e
project=sparkpubsub
image_name=sparkbqread
image_tag=latest
full_image_name=gcr.io/${project}/${image_name}:${image_tag}

cd "$(dirname "$0")" 
docker build -t "${full_image_name}" .
docker push "$full_image_name"

