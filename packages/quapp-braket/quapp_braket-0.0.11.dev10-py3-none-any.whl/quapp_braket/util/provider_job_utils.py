#  Quapp Platform Project
#  provider_job_utils.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
import re
from typing import Union, Optional, Any
from quapp_common.config.logging_config import logger

logger = logger.bind(context='ProviderJobUtils')


def is_valid_job_arn(arn: Union[str, None]) -> bool:
    """
    Validates if the provided ARN follows the AWS Job ARN format.

    Args:
        arn (str or None): The ARN string to validate

    Returns:
        bool: True if the ARN is valid, False otherwise
    """
    if not arn:
        return False

    # AWS Job ARN pattern
    # Format: arn:aws:braket:<region>:<account-id>:job/<job-name>
    job_arn_pattern = r'^arn:aws:braket:[a-z0-9-]+:\d{12}:job/[\w-]+$'

    return bool(re.match(job_arn_pattern, arn))


def is_valid_quantum_task_arn(arn: Union[str, None]) -> bool:
    """
    Validates if the provided ARN follows the AWS Quantum Task ARN format.

    Args:
        arn (str or None): The ARN string to validate

    Returns:
        bool: True if the ARN is valid, False otherwise
    """
    if not arn:
        return False

    # AWS Quantum Task ARN pattern
    # Format: arn:aws:braket:<region>:<account-id>:quantum-task/<task-id>
    quantum_task_arn_pattern = r'^arn:aws:braket:[a-z0-9-]+:\d{12}:quantum-task/[\w-]+$'

    return bool(re.match(quantum_task_arn_pattern, arn))


def get_region(job_id: str) -> str | None:
    """
    Extracts the AWS region from a job ID or ARN.

    Args:
        job_id (str): AWS job ID or ARN

    Returns:
        Optional[str]: AWS region if found, None otherwise

    Examples:
        >>> get_region("arn:aws:braket:us-west-2:123456789012:job/test-job")
        'us-west-2'
        >>> get_region("us-west-2_job_123")
        'us-west-2'
    """
    try:
        if not job_id:
            logger.warning("Empty job ID provided")
            return None

        # Pattern for full ARN format
        arn_pattern = r'arn:aws:braket:([a-z0-9-]+):'
        arn_match = re.search(arn_pattern, job_id)
        if arn_match:
            logger.debug(f"Found region in ARN: {arn_match.group(1)}")
            return arn_match.group(1)

        # Pattern for region prefix format (e.g., "us-west-2_job_123")
        region_pattern = r'^([a-z]{2}-[a-z]+-\d{1,2})_'
        region_match = re.search(region_pattern, job_id)
        if region_match:
            logger.debug(f"Found region in job ID: {region_match.group(1)}")
            return region_match.group(1)

        logger.warning(f"Could not extract region from job ID: {job_id}")
        return None

    except Exception as e:
        logger.error(f"Error extracting region from job ID: {str(e)}")
        return None
