# Dataproc pipeline

Before running the notebooks, you need for the component ``load_spark_to_GCS`` to:
1. customise `build_image.sh` setting the correct `project` and the correct `image_name`
2. run ``bash build_image.sh``
2. update the value ``image`` in ``component.yaml``