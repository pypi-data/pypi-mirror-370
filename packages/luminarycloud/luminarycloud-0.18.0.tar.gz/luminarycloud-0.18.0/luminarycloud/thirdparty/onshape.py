# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
"""
Onshape integration functionality for the Luminary SDK.

This module provides functions for interacting with Onshape CAD platform,
allowing users to check authentication status and fetch variables using
native Python types. This is in addition to our more integrated uses of
Onshape within the SDK, such as allowing Onshape URLs in create_geometry.
"""

from typing import NamedTuple
from dataclasses import dataclass
import re

from .._client import get_default_client
from .._proto.api.v0.luminarycloud.thirdpartyintegration.onshape import onshape_pb2 as onshapepb


@dataclass
class OnshapeVariable:
    """
    Represents a variable from Onshape according to its variable studio definition.

    Attributes
    ----------
    type : str
        The type of the variable (e.g., "LENGTH", "ANGLE", "NUMBER", "ANY")
    name : str
        The name of the variable
    description : str
        A description of the variable
    value : str
        The current value of the variable as a string
    expression : str
        The expression defining the variable
    """

    type: str
    name: str
    description: str
    value: str
    expression: str


class AuthenticationStatus(NamedTuple):
    """
    Authentication status for Onshape.

    Attributes
    ----------
    is_authenticated : bool
        Whether the use has active authentication with Onshape.
    """

    is_authenticated: bool


def _parse_onshape_url(url: str) -> onshapepb.OnshapePath:
    """
    Parse an Onshape URL to extract the necessary components and return an OnshapePath.

    Parameters
    ----------
    url : str
        The Onshape URL to parse

    Returns
    -------
    OnshapePath
        A protobuf OnshapePath object with all fields populated

    Raises
    ------
    ValueError
        If the URL format is invalid or cannot be parsed
    """

    # Expected format: https://{company_prefix}.onshape.com/documents/{document_id}/{w_or_v}/{wv_id}/e/{element_id}
    url_pattern = (
        r"https://([^.\s]+)\.onshape\.com/documents/([^/\s]+)/([wv])/([^/\s]+)/e/([^/\s?#]+)$"
    )
    match = re.match(url_pattern, url)

    if not match:
        raise ValueError(f"Invalid Onshape URL format: {url}")

    company_prefix, document_id, w_or_v, wv_id, element_id = match.groups()

    return onshapepb.OnshapePath(
        company_prefix=company_prefix,
        document_id=document_id,
        w_or_v=w_or_v,
        wv_id=wv_id,
        element_id=element_id,
    )


def get_authentication_status() -> AuthenticationStatus:
    """
    Check whether the current user has valid authentication with Onshape.

    Returns
    -------
    AuthenticationStatus
        The authentication status containing whether the user is authenticated

    Examples
    --------
    >>> import luminarycloud.thirdparty.onshape as onshape
    >>> status = onshape.get_authentication_status()
    >>> if status.is_authenticated:
    ...     print("User is authenticated with Onshape")
    ... else:
    ...     print("User needs to authenticate with Onshape")
    """
    req = onshapepb.GetAuthenticationStatusRequest()
    res = get_default_client().GetAuthenticationStatus(req)
    return AuthenticationStatus(is_authenticated=res.auth_active)


def fetch_variables(onshape_url: str) -> list[OnshapeVariable]:
    """
    Fetch variables from an Onshape document using an Onshape URL.

    Parameters
    ----------
    onshape_url : str
        The Onshape URL pointing to the document element.
        Expected format: https://{company}.onshape.com/documents/{doc_id}/{w_or_v}/{workspace_or_version_id}/e/{element_id}

    Returns
    -------
    list[OnshapeVariable]
        A list of variables available in the specified Onshape element

    Raises
    ------
    ValueError
        If the URL format is invalid or cannot be parsed

    Examples
    --------
    >>> import luminarycloud.thirdparty.onshape as onshape
    >>> # Fetch variables from a workspace URL
    >>> fake_url = "https://cad.onshape.com/documents/abc123/w/def456/e/ghi789"
    >>> variables = onshape.fetch_variables(fake_url)
    >>> for var in variables:
    ...     print(f"{var.name}: {var.value} ({var.type})")

    >>> # Fetch variables from a version URL
    >>> fake_url = "https://cad.onshape.com/documents/abc123/v/xyz999/e/ghi789"
    >>> variables = onshape.fetch_variables(fake_url)
    """

    path = _parse_onshape_url(onshape_url)
    req = onshapepb.FetchVariablesRequest(path=path)
    res = get_default_client().FetchVariables(req)
    variables = []
    for proto_var in res.variables:
        variables.append(
            OnshapeVariable(
                type=proto_var.type,
                name=proto_var.name,
                value=proto_var.value,
                expression=proto_var.expression,
                description=proto_var.description,
            )
        )

    return variables
