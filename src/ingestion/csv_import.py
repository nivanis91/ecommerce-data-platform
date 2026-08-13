import os
from io import BytesIO
import pandas as pd 

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def list_files(s3_client):
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME
    )

    return [
        obj["Key"]
        for obj in response.get("Contents", [])
    ]


def load_csv(s3_client, key):
    response = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=key
    )

    return pd.read_csv(
        BytesIO(response["Body"].read())
    )