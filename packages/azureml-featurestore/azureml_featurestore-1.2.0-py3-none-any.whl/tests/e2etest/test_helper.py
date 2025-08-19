# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

from pyspark import SparkConf
from pyspark.sql import SparkSession

from azure.identity import AzureCliCredential
from azure.storage.blob import BlobServiceClient


class TestHelper:
    @staticmethod
    def download_blob_to_file(account_url: str, container: str, blob: str, destination: str):

        blob_service_client = BlobServiceClient(account_url=account_url, credential=AzureCliCredential())
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob)

        with open(file=os.path.join(destination), mode="wb") as blob:
            download_stream = blob_client.download_blob()
            blob.write(download_stream.readall())
