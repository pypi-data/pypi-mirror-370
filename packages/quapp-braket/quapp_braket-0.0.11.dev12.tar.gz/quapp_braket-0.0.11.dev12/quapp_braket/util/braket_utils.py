#  Quapp Platform Project
#  braket_utils.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
import json

import boto3
from botocore.exceptions import ClientError
from braket.aws import AwsSession
from quapp_common.config.logging_config import logger

from quapp_braket.constant.authentication_const import ACCESS_KEY, SECRET_KEY, \
    REGION_NAME

logger = logger.bind(context='BraketUtils')


def verify_credentials(authentication: dict) -> None:
    """
    Verify that the required AWS credentials are present in the authentication dictionary.

    Args:
        authentication (dict): Dictionary containing authentication credentials

    Raises:
        ValueError: If required credentials are missing
    """
    required_fields = [ACCESS_KEY, SECRET_KEY, REGION_NAME]
    missing_fields = [field for field in required_fields if
                      field not in authentication]

    if missing_fields:
        logger.error(
                f'Missing required authentication fields: {missing_fields}')
        raise ValueError(
                f'Missing required authentication credentials: {missing_fields}')


def create_boto3_session(access_key: str, secret_key: str,
        region_name: str = None) -> boto3.Session:
    """
    Creates a boto3 session using the provided credentials.

    Args:
        access_key (str): AWS access key ID
        secret_key (str): AWS secret access key
        region_name (str, optional): AWS region name

    Returns:
        boto3.Session: Configured boto3 session

    Raises:
        boto3.exceptions.BotoError: If session creation fails
    """
    try:
        logger.debug(f"Creating boto3 session for region: {region_name}")

        return boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region_name
        )

    except Exception as e:
        logger.error(f"Failed to create boto3 session: {str(e)}")
        raise e


def get_braket_client(session: AwsSession):
    return session.braket_client


def read_s3_content(authentication: dict, bucket_name: str,
        object_key: str) -> dict:
    """
    Reads and parses JSON content from an S3 bucket using provided authentication.

    Args:
        authentication (dict): Dictionary containing AWS credentials (access_key, secret_key, region_name)
        bucket_name (str): Name of the S3 bucket
        object_key (str): Object key (path) in the S3 bucket

    Returns:
        dict: Parsed JSON content from the S3 object

    Raises:
        ClientError: If S3 operations fail
        JSONDecodeError: If content cannot be parsed as JSON
        ValueError: If authentication credentials are invalid
    """
    try:
        # Extract authentication credentials
        access_key = authentication.get(ACCESS_KEY)
        secret_key = authentication.get(SECRET_KEY)
        region_name = authentication.get(REGION_NAME)

        if not all([access_key, secret_key]):
            raise ValueError("Missing required AWS credentials")

        # Create S3 client
        s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region_name
        )

        logger.debug(
                f"Attempting to read from S3 bucket: {bucket_name}, key: {object_key}")

        # Get object from S3
        response = s3_client.get_object(
                Bucket=bucket_name,
                Key=object_key
        )

        # Read and parse content
        content = response['Body'].read().decode('utf-8')
        parsed_content = json.loads(content)

        logger.debug("Successfully read and parsed S3 content")
        return parsed_content

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"S3 operation failed: {error_code} - {error_message}")
        raise

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON content: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error reading S3 content: {str(e)}")
        raise
