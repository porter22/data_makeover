from azure.storage.blob import BlobServiceClient
import streamlit as st

print(st)
# Fetch Azure credentials from Streamlit secrets
AZURE_STORAGE_CONNECTION_STRING = st.secrets["azure"]["AZURE_BLOB_CONNECTION_STRING"]
CONTAINER_NAME = st.secrets["azure"]["AZURE_BLOB_CONTAINER_NAME"]

print(CONTAINER_NAME)

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Streamlit file uploader
st.title("Upload CSV to Azure Blob Storage")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Save uploaded file to Blob Storage
    blob_name = uploaded_file.name
    blob_client = container_client.get_blob_client(blob_name)

    # Upload file
    blob_client.upload_blob(uploaded_file, overwrite=True)
    st.success(f"File '{blob_name}' uploaded to Azure Blob Storage.")
