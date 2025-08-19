import json

import boto3
from botocore.exceptions import ClientError

from baresquare_sdk.core import exceptions, logger
from baresquare_sdk.settings import get_settings


def get_client():
    """Return an SSM client using the Singleton Pattern.

    :return: SSM client
    """
    global ssm_client
    if "ssm_client" not in globals() or ssm_client is None:
        settings = get_settings()
        if settings.aws_profile is not None:
            session = boto3.Session(profile_name=settings.aws_profile)
            ssm_client = session.client(service_name="ssm", region_name=settings.pl_region)
        else:
            ssm_client = boto3.client(service_name="ssm", region_name=settings.pl_region)
    return ssm_client


def get_parameter(ssm_key: str, return_json: bool = False, **_) -> str | dict:
    """Retrieve parameter from AWS SSM.

    Args:
        ssm_key (str): The path to the parameter in AWS SSM
        return_json (bool): Whether to return the parameter as a json object
                            Defaults to False

    Returns:
        str | dict: The parameter value as a string or dictionary
    """
    logger.debug(f"Retrieving SSM param {ssm_key}")
    try:
        ssm_parameter = get_client().get_parameter(Name=ssm_key, WithDecryption=True)["Parameter"]["Value"]
        if return_json:
            return json.loads(ssm_parameter)
        return ssm_parameter
    except ClientError as e:
        logger.warning(f"Failed to retrieve SSM param from {ssm_key}")
        raise exceptions.ExceptionInfo(
            msg=f"Failed to retrieve SSM param from {ssm_key}",
            data={
                "ssm_parameter_name": ssm_key,
            },
        ) from e


def get_parameters(parameters_mapping: dict[str, dict[str, str | bool]]) -> dict[str, str | dict]:
    """Retrieve multiple parameters from AWS SSM in bulk (batches of 10 to avoid AWS API limit).

    Args:
        parameters_mapping: Dict mapping SSM paths to config:
            {
                "/auth0/domain": {"env_var": "AUTH0_DOMAIN", "is_json": False},
                "/auth0/api/audiences": {"env_var": "AUTH0_API_AUDIENCES", "is_json": True}
            }

    Returns:
        dict: Mapping of env_var names to their processed values
            {
                "AUTH0_DOMAIN": "example.auth0.com",
                "AUTH0_API_AUDIENCES": {"service1": "aud1", "service2": "aud2"}
            }
    """
    logger.debug(f"Retrieving {len(parameters_mapping)} SSM parameters in bulk")

    try:
        parameter_names = list(parameters_mapping.keys())
        batch_size = 10
        result = {}

        # Process in batches of 10
        for i in range(0, len(parameter_names), batch_size):
            batch = parameter_names[i : i + batch_size]

            response = get_client().get_parameters(Names=batch, WithDecryption=True)

            for param in response["Parameters"]:
                config = parameters_mapping[param["Name"]]
                value = param["Value"]

                if config["is_json"]:
                    value = json.loads(value)

                result[config["env_var"]] = value

        return result

    except ClientError as e:
        logger.warning(f"Failed to retrieve SSM parameters")
        raise exceptions.ExceptionInfo(
            msg="Failed to retrieve SSM parameters",
            data={"parameter_names": list(parameters_mapping.keys())},
        ) from e


def put_parameter(ssm_key: str, ssm_value: str, overwrite: bool, ssm_type="SecureString"):
    """Put parameter to AWS SSM.

    Args:
        ssm_key (str): The path to the parameter in AWS SSM
        ssm_value (str): The value of the SSM parameter
        overwrite (bool): Whether to overwrite an existing value for the SSM parameter
        ssm_type (str): one of 'String'|'StringList'|'SecureString'

    Returns:
        dict: Example: {'Version': 123,'Tier': 'Standard'|'Advanced'|'Intelligent-Tiering'}
    """
    logger.debug(f"Putting SSM param {ssm_key}")
    try:
        get_client().put_parameter(Name=ssm_key, Value=ssm_value, Type=ssm_type, Overwrite=overwrite)
    except ClientError as e:
        logger.error(f"Failed to put SSM param {ssm_key}")
        raise exceptions.ExceptionInfo(
            msg=f"Failed to put SSM param {ssm_key}",
            data={
                "ssm_parameter_name": ssm_key,
            },
        ) from e


def delete_parameter(ssm_key: str):
    """Delete parameter from AWS SSM.

    Args:
        ssm_key (str): The path to the parameter in AWS SSM
    """
    logger.debug(f"Deleting SSM param {ssm_key}")
    try:
        get_client().delete_parameter(Name=ssm_key)
    except ClientError as e:
        logger.warning(f"Failed to delete SSM param {ssm_key}")
        raise exceptions.ExceptionInfo(
            msg=f"Failed to delete SSM param from {ssm_key}",
            data={
                "ssm_parameter_name": ssm_key,
            },
        ) from e
