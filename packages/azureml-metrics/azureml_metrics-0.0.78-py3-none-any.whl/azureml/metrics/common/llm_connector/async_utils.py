# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import logging
import os
import random

from azureml.metrics.common.exceptions import MissingDependencies

try:
    import openai

    if openai.__version__ < "1.0.0":
        # setting the logging level for openai library
        openai.util.logger.setLevel(logging.ERROR)
    else:
        os.environ["OPENAI_LOG"] = "error"

    from tqdm.asyncio import tqdm_asyncio
except ImportError:
    safe_message = "Relevant GPT Star metrics packages are not available. " \
                   "Please run pip install azureml-metrics[prompt-flow]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )


async def get_async_chat_completion(index, client, openai_v1_kwargs, **kwargs):
    """Making an async call to openai chatcompletion API"""
    # add random delay between 10 ms to 100 ms
    delay = random.uniform(0.01, 0.1)
    await asyncio.sleep(delay)

    if openai.__version__ < "1.0.0":
        from openai.error import InvalidRequestError
        try:
            chat_completion_resp = await openai.ChatCompletion.acreate(**kwargs)
        except InvalidRequestError:
            chat_completion_resp = "BadRequestError"

    else:
        from openai import BadRequestError
        try:
            chat_completion_resp = client.chat.completions.create(
                messages=kwargs.get("messages"),
                **openai_v1_kwargs,
            )
        except BadRequestError:
            chat_completion_resp = "BadRequestError"

    return {index: chat_completion_resp}


async def get_async_completion(index, client, openai_v1_kwargs, **kwargs):
    """Making an async call to openai completion API"""
    # add random delay between 10 ms to 100 ms
    delay = random.uniform(0.01, 0.1)
    await asyncio.sleep(delay)

    if openai.__version__ < "1.0.0":
        completion_resp = await openai.Completion.acreate(**kwargs)
    else:
        completion_resp = client.completions.create(
            prompt=kwargs.get("prompt"),
            **openai_v1_kwargs,
        )

    return {index: completion_resp}


async def gather_with_concurrency(max_concurrent_calls, *coros):
    """
    Run coroutines with a limit on the number of concurrent tasks.
    # source: https://stackoverflow.com/questions/48483348/how-to-limit-concurrency-with-python-asyncio
    """
    max_concurrent_calls = min(max_concurrent_calls, len(coros))
    semaphore = asyncio.Semaphore(max_concurrent_calls)

    async def sem_coro(coro):
        # TODO: control the level of logging
        async with semaphore:
            return await coro
    return await tqdm_asyncio.gather(*(sem_coro(c) for c in coros))
