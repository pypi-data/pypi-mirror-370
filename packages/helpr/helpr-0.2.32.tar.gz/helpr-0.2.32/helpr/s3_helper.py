import boto3
from fastapi import HTTPException, UploadFile
from botocore.exceptions import BotoCoreError, ClientError

def upload_to_s3(
    file: UploadFile,
    key: str,
    bucket_name: str,
    region: str
) -> str:
    """
    Upload a file to AWS S3.

    Args:
        file (UploadFile): File to upload (from FastAPI UploadFile).
        key (str): S3 object key (path + filename).
        bucket_name (str): S3 bucket name.
        region (str): AWS region name.

    Returns:
        str: Public URL of uploaded file.

    Raises:
        HTTPException: On AWS errors or invalid input.
    """
    s3_client = boto3.client("s3", region_name=region)

    try:
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            key,
            ExtraArgs={"ContentType": file.content_type}
        )
    except ClientError as e:
        # AWS client-side error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to S3: {e.response['Error']['Message']}"
        )
    except BotoCoreError as e:
        # AWS core error
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected AWS error during upload: {str(e)}"
        )
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during upload: {str(e)}"
        )

    file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
    return file_url
