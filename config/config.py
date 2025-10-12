# ===================================================================
# IBM Db2 Credentials
# This dictionary holds all the connection details for your Db2 instance.
# ===================================================================
DB2_credentials = {
    "database": "bludb",
    "hostname": "b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud",
    "port": "32304",
    "user": "qbw01092",
    "password": "aj1diEOaEfgRRzHt"
}

# ===================================================================
# IBM Cloud Object Storage (COS) Credentials
# This dictionary holds the details for connecting to your storage bucket.
# ===================================================================
COS_CREDS = {
    # This endpoint is correct based on your bucket's location.
    "endpoint_url": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
    
    # This is your API Key.
    "api_key_id": "04uLXtF-u70RyHwSSXyPFiKxb68lHUfr4fhw5L0CpcBR",
    
    # CORRECTED: This is the main Service Instance ID, not the bucket-specific one.
    "service_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/0d786ff508e34bd6bbb0e5832dbda8a9:4dc10937-5ca9-4c6d-a429-03d9d00f6550::"
}

# The name of the bucket you created to store the MRI images.
COS_BUCKET_NAME = "heart-mri-bucket"

