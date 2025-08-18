# -*- coding: utf-8 -*-

"""
Enhanced boto3 SSM client functions.

This module provides high-level, Pythonic wrapper functions around the AWS SSM
Parameter Store boto3 client operations. The functions handle error cases gracefully,
provide better return values, and implement common patterns like existence testing
and idempotent operations.
"""

import typing as T

import botocore.exceptions
from func_args.api import remove_optional

from .constants import (
    ResourceType,
)
from .utils import (
    encode_tags,
    decode_tags,
)
from .model import (
    Parameter,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient


def get_parameter(
    ssm_client: "SSMClient",
    name: str,
    with_decryption: bool = False,
) -> Parameter | None:
    """
    Get a parameter by name with built-in existence testing.

    This function provides a convenient way to retrieve parameters while gracefully
    handling non-existent parameters. Unlike the raw boto3 client which raises 
    exceptions for missing parameters, this function returns None, making it ideal
    for existence testing and conditional parameter access.

    Example usage for existence testing::

        param = get_parameter(ssm_client, "/my/param")
        if param is not None:
            print("Parameter exists")
        else:
            print("Parameter does not exist")

    Ref:

    - `get_parameter <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter>`_

    :param ssm_client: SSM client
    :param name: parameter name (e.g., "/app/database/host")
    :param with_decryption: whether to decrypt SecureString parameter values

    :return: ``Parameter`` object if the parameter exists, None if it does not exist.
    """
    try:
        response = ssm_client.get_parameter(
            Name=name,
            **remove_optional(
                WithDecryption=with_decryption,
            ),
        )
        return Parameter(_data=response["Parameter"])
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in [
            "ParameterNotFound",
            "ParameterVersionNotFound",
        ]:
            return None
        raise  # pragma: no cover


def delete_parameter(
    ssm_client: "SSMClient",
    name: str,
) -> bool:
    """
    Delete a parameter by name with idempotent behavior.

    This function provides idempotent parameter deletion - it can be called multiple 
    times safely without raising errors. Unlike the raw boto3 client which raises
    ParameterNotFound exceptions, this function returns False for non-existent
    parameters, making it safe to use in cleanup operations and automation scripts.

    The idempotent behavior ensures that:

    - If the parameter exists, it will be deleted and return True
    - If the parameter doesn't exist, it returns False without raising an error
    - Multiple calls with the same parameter name are safe

    Example usage in cleanup scripts::

        # Safe to call even if parameter doesn't exist
        deleted = delete_parameter(client, "/app/temp/config")
        if deleted:
            print("Parameter was deleted")
        else:
            print("Parameter did not exist")

    Ref:

    - `delete_parameter <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.delete_parameter>`_

    :param ssm_client: SSM client
    :param name: parameter name (e.g., "/app/database/host")

    :return: True if the parameter was deleted, False if it did not exist.
    """
    try:
        ssm_client.delete_parameter(Name=name)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            return False
        raise  # pragma: no cover


def get_parameter_tags(
    ssm_client: "SSMClient",
    name: str,
) -> dict[str, str]:
    """
    Get all tags associated with a parameter.

    This function retrieves all tags for the specified parameter and returns them
    as a convenient key-value dictionary. If the parameter has no tags, an empty
    dictionary is returned.

    Ref:

    - `list_tags_for_resource <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.list_tags_for_resource>`_

    :param ssm_client: SSM client
    :param name: parameter name (e.g., "/app/database/host")

    :return: Dictionary of tag key-value pairs. Empty dict if parameter has no tags.
    """
    response = ssm_client.list_tags_for_resource(
        ResourceType=ResourceType.PARAMETER.value,
        ResourceId=name,
    )
    return decode_tags(response.get("TagList", []))


def remove_parameter_tags(
    ssm_client: "SSMClient",
    name: str,
    tag_keys: list[str],
):
    """
    Remove specific tags from a parameter by tag keys.

    This function removes only the specified tag keys from the parameter, leaving
    other tags unchanged. It's useful for selective tag cleanup without affecting
    the entire tag set.

    Example:
        # Remove only the "Environment" and "Team" tags
        remove_parameter_tags(client, "/app/config", ["Environment", "Team"])

    Ref:

    - `remove_tags_from_resource <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.remove_tags_from_resource>`_

    :param ssm_client: SSM client
    :param name: parameter name (e.g., "/app/database/host")
    :param tag_keys: list of tag keys to remove (e.g., ["Environment", "Team"])
    """
    return ssm_client.remove_tags_from_resource(
        ResourceType=ResourceType.PARAMETER.value,
        ResourceId=name,
        TagKeys=tag_keys,
    )


def update_parameter_tags(
    ssm_client: "SSMClient",
    name: str,
    tags: dict[str, str],
):
    """
    Add or update specific tags on a parameter (partial update).

    This function performs a partial update of parameter tags. It adds new tags
    and updates existing tags with the provided key-value pairs, while leaving
    other existing tags unchanged. This is useful for adding metadata without
    affecting the entire tag set.

    Example:
        # Add/update only specific tags, keeping others intact
        update_parameter_tags(client, "/app/config", {
            "Environment": "production",
            "LastUpdated": "2024-01-15"
        })

    Ref:

    - `add_tags_to_resource <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.add_tags_to_resource>`_

    :param ssm_client: SSM client
    :param name: parameter name (e.g., "/app/database/host")
    :param tags: dictionary of tag key-value pairs to add/update
    """
    return ssm_client.add_tags_to_resource(
        ResourceType=ResourceType.PARAMETER.value,
        ResourceId=name,
        Tags=encode_tags(tags),
    )


def put_parameter_tags(
    ssm_client: "SSMClient",
    name: str,
    tags: dict[str, str],
):
    """
    Replace all parameter tags with the provided tag set (full replacement).

    This function performs a complete replacement of all parameter tags. It removes
    all existing tags and replaces them with the provided tags. If an empty
    dictionary is provided, all tags are removed from the parameter.

    Behavior:

    - Empty dict: Remove all existing tags from the parameter
    - Non-empty dict: Replace all existing tags with the provided tags

    Example::

        # Replace all tags with new set
        put_parameter_tags(client, "/app/config", {
            "Environment": "production",
            "Owner": "platform-team"
        })
        
        # Remove all tags
        put_parameter_tags(client, "/app/config", {})

    Ref:

    - `add_tags_to_resource <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.add_tags_to_resource>`_

    :param ssm_client: SSM client
    :param name: parameter name (e.g., "/app/database/host")
    :param tags: dictionary of tag key-value pairs to set (empty dict removes all tags)
    """
    existing_tags = get_parameter_tags(ssm_client, name)

    if len(tags) == 0:
        if len(existing_tags):  # only run remove tags when there are existing tags
            remove_parameter_tags(ssm_client, name, list(existing_tags))
    else:
        # if to-update tags is super set of the existing tags
        # then no need to run remove tags
        # otherwise, need to run remove tags
        if not (len(set(existing_tags).difference(set(tags))) == 0):
            remove_parameter_tags(ssm_client, name, list(existing_tags))
        ssm_client.add_tags_to_resource(
            ResourceType="Parameter",
            ResourceId=name,
            Tags=encode_tags(tags),
        )
