from pandas import DataFrame
from azure.storage.blob import BlobServiceClient
import os


class BlobConnection:
    def __init__(self):
        self._service_client = BlobServiceClient.from_connection_string(
            conn_str=os.getenv("ADLS_NBA_CONNECTION_STRING")
        )

    def write_dataframe_to_csv(self, data: DataFrame, container: str, blob_name: str) -> None:
        """Function to write dataframe to parquet in blob storage"""
        blob_client = self._service_client.get_blob_client(container=container, blob=blob_name)
        blob_client.upload_blob(data.to_csv(index=False), overwrite=True)


if __name__ == "__main__":
    conn = BlobConnection()
    print(conn._service_client)
