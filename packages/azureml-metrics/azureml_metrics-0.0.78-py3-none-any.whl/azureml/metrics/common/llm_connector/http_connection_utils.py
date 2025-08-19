# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Any
from azureml.metrics.common.exceptions import MissingDependencies

try:
    import aiohttp
    import requests
except ImportError:
    safe_message = "Relevant RAG Evaluation packages are not available. " \
                   "Please run pip install azureml-metrics[rag-evaluation]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )


async def async_post_with_session(
    url: str, headers: Dict[str, Any], body: Dict[str, Any], timeout_sec: float = 300.0
):

    async with aiohttp.ClientSession() as session:
        async with session.post(
                url,
                headers=headers,
                json=body,
                raise_for_status=False,
                timeout=aiohttp.ClientTimeout(total=timeout_sec),
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data
            else:
                response_data = await response.content.read()
                error_message = response_data.decode()
                raise aiohttp.ClientResponseError(
                    response.request_info,
                    response.history,
                    status=response.status,
                    message=f"Server responded with status {response.status}. Error message: {error_message}",
                    headers=response.headers,
                )


def sync_post(url: str, headers: Dict[str, Any], body: Dict[str, Any]):
    resp = requests.post(url, headers=headers, json=body)
    resp.raise_for_status()
    return resp.json()
