from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.client_error import ClientError
from ...models.data_request_body import DataRequestBody
from ...models.http_validation_error import HTTPValidationError
from ...models.internal_error import InternalError
from ...models.paged_response_obj import PagedResponseObj
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: DataRequestBody,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/data/subject",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]:
    if response.status_code == 200:
        response_200 = PagedResponseObj.from_dict(response.json())

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
) -> Response[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRequestBody,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Response[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]:
    """Subject Fetch Rows Endpoint

     Subject data endpoint that returns json formatted row data based on input query

    Args:
        request (Request): HTTP request object
        request_body (DataRequestBody): JSON input query
        limit (int, optional): Limit for paged results. Defaults to 100.
        offset (int, optional): Offset for paged results. Defaults to 0.
        db (Session, optional): Database session object. Defaults to Depends(get_db).

    Returns:
        PagedResponseObj:
        {
            'result': [{'column': 'data'}],
            'query_sql': 'SQL statement used to generate result',
            'total_row_count': 'total rows of data for query generated (not paged)',
            'next_url': 'URL to acquire next paged result'
        }

    Args:
        limit (Union[Unset, int]):  Default: 100.
        offset (Union[Unset, int]):  Default: 0.
        body (DataRequestBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]
    """

    kwargs = _get_kwargs(
        body=body,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRequestBody,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]:
    """Subject Fetch Rows Endpoint

     Subject data endpoint that returns json formatted row data based on input query

    Args:
        request (Request): HTTP request object
        request_body (DataRequestBody): JSON input query
        limit (int, optional): Limit for paged results. Defaults to 100.
        offset (int, optional): Offset for paged results. Defaults to 0.
        db (Session, optional): Database session object. Defaults to Depends(get_db).

    Returns:
        PagedResponseObj:
        {
            'result': [{'column': 'data'}],
            'query_sql': 'SQL statement used to generate result',
            'total_row_count': 'total rows of data for query generated (not paged)',
            'next_url': 'URL to acquire next paged result'
        }

    Args:
        limit (Union[Unset, int]):  Default: 100.
        offset (Union[Unset, int]):  Default: 0.
        body (DataRequestBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]
    """

    return sync_detailed(
        client=client,
        body=body,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRequestBody,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Response[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]:
    """Subject Fetch Rows Endpoint

     Subject data endpoint that returns json formatted row data based on input query

    Args:
        request (Request): HTTP request object
        request_body (DataRequestBody): JSON input query
        limit (int, optional): Limit for paged results. Defaults to 100.
        offset (int, optional): Offset for paged results. Defaults to 0.
        db (Session, optional): Database session object. Defaults to Depends(get_db).

    Returns:
        PagedResponseObj:
        {
            'result': [{'column': 'data'}],
            'query_sql': 'SQL statement used to generate result',
            'total_row_count': 'total rows of data for query generated (not paged)',
            'next_url': 'URL to acquire next paged result'
        }

    Args:
        limit (Union[Unset, int]):  Default: 100.
        offset (Union[Unset, int]):  Default: 0.
        body (DataRequestBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]
    """

    kwargs = _get_kwargs(
        body=body,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRequestBody,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]]:
    """Subject Fetch Rows Endpoint

     Subject data endpoint that returns json formatted row data based on input query

    Args:
        request (Request): HTTP request object
        request_body (DataRequestBody): JSON input query
        limit (int, optional): Limit for paged results. Defaults to 100.
        offset (int, optional): Offset for paged results. Defaults to 0.
        db (Session, optional): Database session object. Defaults to Depends(get_db).

    Returns:
        PagedResponseObj:
        {
            'result': [{'column': 'data'}],
            'query_sql': 'SQL statement used to generate result',
            'total_row_count': 'total rows of data for query generated (not paged)',
            'next_url': 'URL to acquire next paged result'
        }

    Args:
        limit (Union[Unset, int]):  Default: 100.
        offset (Union[Unset, int]):  Default: 0.
        body (DataRequestBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClientError, HTTPValidationError, InternalError, PagedResponseObj]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            limit=limit,
            offset=offset,
        )
    ).parsed
