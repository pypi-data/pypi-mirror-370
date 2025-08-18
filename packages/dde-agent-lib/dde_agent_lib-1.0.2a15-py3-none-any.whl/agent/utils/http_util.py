from typing import Optional

import httpx
from fastapi import HTTPException


async def async_http_get(url: str, params=None, timeout=10.0):
    timeout_config = httpx.Timeout(timeout, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        response = await client.get(url=url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="API call failed")
        return response.json()


async def async_http_post(url: str, data, headers: [Optional] = None, timeout=10.0):
    timeout_config = httpx.Timeout(timeout, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        response = await client.post(url=url, json=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="API call failed")
        return response.json()


def http_get(url: str, params=None, timeout=10.0):
    timeout_config = httpx.Timeout(timeout, connect=5.0)
    with httpx.Client(timeout=timeout_config) as client:
        response = client.get(url=url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="API call failed")
        return response.json()


def http_post(url: str, data, headers: [Optional] = None, timeout=10.0):
    timeout_config = httpx.Timeout(timeout, connect=5.0)
    with httpx.Client(timeout=timeout_config) as client:
        response = client.post(url=url, json=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="API call failed")
        return response.json()


