ARG BASE_IMAGE_TAG=1.14.0-py3
FROM tensorflow/tensorflow:$BASE_IMAGE_TAG
COPY ./src /pipelines/component/src
ENTRYPOINT ["python3","/pipelines/component/src/read_from_gcs.py"]