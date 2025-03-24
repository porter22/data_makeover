import streamlit as st
import smtplib
from email.message import EmailMessage
from azure.storage.blob import BlobServiceClient

# Set Page Layout to Fullscreen
st.set_page_config(page_title="Data Transformer", page_icon="⚡", layout="wide")

# Load External CSS
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply CSS
load_css("styles.css")

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = st.secrets["azure"]["AZURE_BLOB_CONNECTION_STRING"]
CONTAINER_NAME = st.secrets["azure"]["AZURE_BLOB_CONTAINER_NAME"]

# Email Notification Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = st.secrets["email"]["SENDER_EMAIL"]
SENDER_PASSWORD = st.secrets["email"]["SENDER_PASSWORD"]
ADMIN_EMAIL = st.secrets["email"]["RECEIVER_EMAIL"]

# Initialize Azure Blob Service
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# App Header
st.markdown("<h1>📂 Data Transformer</h1>", unsafe_allow_html=True)
st.markdown("<p> Upload your data file below and describe the transformation that you want to achieve. Our data experts will take care of the rest.<p>", unsafe_allow_html=True)

# User Inputs
with st.container(border = True):
    # File Upload Section (Dark Mode)
    uploaded_file = st.file_uploader("", type=["csv", "xls", "xlsx"])

    col1, col2, col3 = st.columns([0.6, 0.1, 1])
    with col1:
        st.markdown("<br><br>", unsafe_allow_html=True)  # Push col2 lower
        email = st.text_input("📧 Enter your email", placeholder="example@example.com")
        transformation_prompt = st.text_area("✏️ Describe your data transformation", placeholder="Example: Remove duplicates, filter 'Age' > 30, etc.")
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)  # Push col2 lower
    with col3:
        st.markdown("<br><br>", unsafe_allow_html=True)  # Push col2 lower
        st.markdown("<p>✔️ Fast & Secure Processing </p>", unsafe_allow_html=True)
        st.markdown("<p>✔️ Supports CSV, XLS, XLSX Formats </p>", unsafe_allow_html=True)
        st.markdown("<p>✔️ Custom Transformations (We remove duplicates, outliers, etc. - you name it!) </p>", unsafe_allow_html=True)
        st.markdown("<p>✔️ Receive Processed File via Email </p>", unsafe_allow_html=True)


# Handle Upload and Email Notification
if uploaded_file and st.button("🚀 Upload & Transform"):
    if not email.strip():
        st.error("❌ Please enter a valid email address.")
    elif not transformation_prompt.strip():
        st.error("❌ Please describe your transformation.")
    else:
        # Upload File to Azure Blob Storage
        blob_client = container_client.get_blob_client(uploaded_file.name)
        blob_client.upload_blob(uploaded_file, overwrite=True)

        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        st.write(f"📩 You will receive a download link at: {email}")

        # Send Email Notification
        def send_email_notification(user_email, file_name, transformation_details):
            msg = EmailMessage()
            msg["Subject"] = "New File Upload Notification"
            msg["From"] = SENDER_EMAIL
            msg["To"] = ADMIN_EMAIL
            msg.set_content(f"""
            A new file has been uploaded.

            📧 User Email: {user_email}
            📂 File Name: {file_name}
            ✏️ Transformation Request: {transformation_details}

            Check the Azure Blob Storage for the file.
            """)

            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                st.error(f"❌ Email notification failed: {e}")

        send_email_notification(email, uploaded_file.name, transformation_prompt)
