from azure.storage.blob import BlobServiceClient
import streamlit as st
import smtplib
from email.message import EmailMessage

# Fetch Azure credentials from Streamlit secrets
AZURE_STORAGE_CONNECTION_STRING = st.secrets["azure"]["AZURE_BLOB_CONNECTION_STRING"]
CONTAINER_NAME = st.secrets["azure"]["AZURE_BLOB_CONTAINER_NAME"]

# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = st.secrets["email"]["SENDER_EMAIL"]  # Your Gmail address
SENDER_PASSWORD = st.secrets["email"]["SENDER_PASSWORD"]  # Your App Password from Google
ADMIN_EMAIL = st.secrets["email"]["RECEIVER_EMAIL"]  # Replace with your own email

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Streamlit app title
st.title("DataMakeover: Transform Your CSV Files with Ease")

# Introductory Section
st.subheader("Welcome to DataMakeover!")
st.markdown("""
We make it simple to clean, process, and transform your data:
- Upload your CSV or Excel file.
- Describe the transformation you need (e.g., filtering, grouping, aggregations).
- Provide your email address, and we'll send a link to the transformed file once it's ready.

**Get started by uploading your file below!**
""")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xls", "xlsx"])

# Email input field
email = st.text_input("Enter your email", placeholder="example@example.com")

# User prompt for data transformation
if uploaded_file is not None:
    st.write("File uploaded successfully. Now, describe the transformation you'd like:")
    
    transformation_prompt = st.text_area(
        "Describe your transformation",
        placeholder="Example: Filter rows where 'Age' > 30, group by 'City', and calculate the average 'Salary'."
    )
    
    if st.button("Submit"):
        if not email.strip():
            st.error("Please provide a valid email address.")
        elif not transformation_prompt.strip():
            st.error("Please describe your transformation before submitting.")
        else:
            # Save uploaded file to Blob Storage
            blob_name = uploaded_file.name
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(uploaded_file, overwrite=True)

            st.success(f"File '{blob_name}' uploaded successfully.")
            st.write(f"Your transformation request: {transformation_prompt}")
            st.write(f"A link to the processed file will be sent to: {email}")
            
            # Send notification email
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
                    st.success("Admin has been notified of the upload.")
                except Exception as e:
                    st.error(f"Error sending email: {e}")

            # Call the email notification function
            send_email_notification(email, blob_name, transformation_prompt)
