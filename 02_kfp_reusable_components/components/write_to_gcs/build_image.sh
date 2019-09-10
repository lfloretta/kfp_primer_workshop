#!/bin/bash -e

project=kfp-primer-workshop
image_name=gcr.io/${project}/kfp_workshop/write_to_gcs
image_tag=latest
full_image_name=${image_name}:${image_tag}
base_image_tag=1.14.0-py3

docker build --build-arg BASE_IMAGE_TAG=$base_image_tag -t "$full_image_name" .

#To push to gcr you need to have run gcloud auth configure-docker
#see https://cloud.google.com/container-registry/docs/advanced-authentication
docker push "$full_image_name"

#Output the strict image name (which contains the sha256 image digest)
#This name can be used by the subsequent steps to refer to the exact image that was built even if another image with the same name was pushed.
image_name_with_digest=$(docker inspect --format="{{index .RepoDigests 0}}" "$image_name")
strict_image_name_output_file=./versions/image_digests_for_tags/$image_tag
mkdir -p "$(dirname "$strict_image_name_output_file")"
echo $image_name_with_digest | tee "$strict_image_name_output_file"