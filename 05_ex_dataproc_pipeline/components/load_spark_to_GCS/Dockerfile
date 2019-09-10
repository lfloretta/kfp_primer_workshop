FROM python:3.7.4-alpine3.10
COPY ./src /pipelines/component/src
RUN pip install google-cloud-storage==1.19.0
ENTRYPOINT ["python3","/pipelines/component/src/load_files_to_GCS.py"]