from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.client_error import ClientError
from ...models.column_values_response_obj import ColumnValuesResponseObj
from ...models.http_validation_error import HTTPValidationError
from ...models.internal_error import InternalError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    column: str,
    *,
    data_source: Union[Unset, str] = "",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["data_source"] = data_source

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/column_values/{column}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]:
    if response.status_code == 200:
        response_200 = ColumnValuesResponseObj.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = ClientError.from_dict(response.json())

        return response_400
    if response.status_code == 500:
        response_500 = InternalError.from_dict(response.json())

        return response_500
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    column: str,
    *,
    client: Union[AuthenticatedClient, Client],
    data_source: Union[Unset, str] = "",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
) -> Response[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]:
    """Column Values Endpoint

     _summary_

    Args:
        request (Request): _description_
        column (str): _description_
        data_source (str): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        ColumnValuesResponseObj: _description_

    Args:
        column (str):
        data_source (Union[Unset, str]):  Default: ''.
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]
    """

    kwargs = _get_kwargs(
        column=column,
        data_source=data_source,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    column: str,
    *,
    client: Union[AuthenticatedClient, Client],
    data_source: Union[Unset, str] = "",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
) -> Optional[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]:
    """Column Values Endpoint

     _summary_

    Args:
        request (Request): _description_
        column (str): _description_
        data_source (str): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        ColumnValuesResponseObj: _description_

    Args:
        column (str):
        data_source (Union[Unset, str]):  Default: ''.
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]
    """

    return sync_detailed(
        column=column,
        client=client,
        data_source=data_source,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    column: str,
    *,
    client: Union[AuthenticatedClient, Client],
    data_source: Union[Unset, str] = "",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
) -> Response[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]:
    """Column Values Endpoint

     _summary_

    Args:
        request (Request): _description_
        column (str): _description_
        data_source (str): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        ColumnValuesResponseObj: _description_

    Args:
        column (str):
        data_source (Union[Unset, str]):  Default: ''.
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]
    """

    kwargs = _get_kwargs(
        column=column,
        data_source=data_source,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    column: str,
    *,
    client: Union[AuthenticatedClient, Client],
    data_source: Union[Unset, str] = "",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
) -> Optional[Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]]:
    """Column Values Endpoint

     _summary_

    Args:
        request (Request): _description_
        column (str): _description_
        data_source (str): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        ColumnValuesResponseObj: _description_

    Args:
        column (str):
        data_source (Union[Unset, str]):  Default: ''.
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClientError, ColumnValuesResponseObj, HTTPValidationError, InternalError]
    """

    return (
        await asyncio_detailed(
            column=column,
            client=client,
            data_source=data_source,
            limit=limit,
            offset=offset,
        )
    ).parsed
