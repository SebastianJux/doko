import streamlit as st
from azure.storage.blob import BlobServiceClient
from io import BytesIO
import pandas as pd

def read_csv_from_blob(container_name: str, blob_name: str) -> pd.DataFrame:
    blob_service_client = BlobServiceClient.from_connection_string(st.secrets["blob_connection_string"])
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    return pd.read_csv(BytesIO(blob_data))


def write_csv_to_blob(df: pd.DataFrame, container_name: str, blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(st.secrets["blob_connection_string"])
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)
