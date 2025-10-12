import ibm_boto3
from ibm_botocore.client import Config, ClientError
from .config import COS_CREDS, COS_BUCKET_NAME

def upload_file_to_cos(local_file_path, item_name):
    """
    Uploads a file from a local path to the COS bucket.

    Args:
        local_file_path (str): The path to the file saved on the server.
        item_name (str): The name to give the file in the COS bucket.

    Returns:
        str: The public URL of the uploaded file if successful, otherwise None.
    """
    try:
        cos_resource = ibm_boto3.resource("s3",
            ibm_api_key_id=COS_CREDS["api_key_id"],
            ibm_service_instance_id=COS_CREDS["service_instance_id"],
            config=Config(signature_version="oauth"),
            endpoint_url=COS_CREDS["endpoint_url"]
        )
        print("Successfully created IBM COS resource client.")

        # MODIFIED: Use upload_file for files saved to disk
        cos_resource.Bucket(COS_BUCKET_NAME).upload_file(
            Filename=local_file_path,
            Key=item_name
        )
        print(f"File '{item_name}' uploaded successfully to bucket '{COS_BUCKET_NAME}'.")

        public_url = f"{COS_CREDS['endpoint_url']}/{COS_BUCKET_NAME}/{item_name}"
        return public_url

    except ClientError as be:
        print("\nCLIENT ERROR: A client-side error occurred.")
        print(f"Error Code: {be.response['Error']['Code']}")
        print(f"Error Message: {be.response['Error']['Message']}")
        return None
        
    except Exception as e:
        print("\nUNABLE TO CONNECT TO COS: An unexpected error occurred.")
        print(f"Error details: {e}")
        return None

