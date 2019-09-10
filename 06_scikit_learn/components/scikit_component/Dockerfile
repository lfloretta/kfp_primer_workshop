
ARG BASE_IMAGE_TAG=1.12.0-py3
FROM tensorflow/tensorflow:$BASE_IMAGE_TAG
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY ./src /pipelines/component/src