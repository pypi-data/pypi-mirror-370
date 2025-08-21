import asyncio
from typing import TYPE_CHECKING, Union

from loguru import logger

from sparrow import ConcurrentRequester
from sparrow.vllm.client.messages_processor import (
    batch_process_messages,
    messages_preprocess,
)
from sparrow.vllm.client.unified_processor import (
    batch_process_messages as optimized_batch_messages_preprocess,
)
from sparrow.vllm.client.image_processor import ImageCacheConfig

if TYPE_CHECKING:
    from sparrow.async_api.interface import RequestResult


class OpenAIClient:
    def __init__(
        self,
        base_url: str,
        api_key="EMPTY",
        concurrency_limit=10,
        max_qps=1000,
        timeout=100,
        retry_times=3,
        retry_delay=0.55,
        cache_image=False,
        cache_dir="image_cache",
        **kwargs,
    ):
        self._client = ConcurrentRequester(
            concurrency_limit=concurrency_limit,
            max_qps=max_qps,
            timeout=timeout,
            retry_times=retry_times,
            retry_delay=retry_delay,
        )
        self._concurrency_limit = concurrency_limit
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._cache_config = ImageCacheConfig(
            enabled=cache_image,
            cache_dir=cache_dir,
            force_refresh=False,
            retry_failed=False,
        )

    async def wrap_to_request_params(
        self,
        messages: list,
        model: str,
        max_tokens=None,
        meta=None,
        preprocess_msg=False,
        **kwargs,
    ):
        if preprocess_msg:
            messages = await messages_preprocess(
                messages, preprocess_msg=preprocess_msg, cache_config=self._cache_config
            )
        request_params = {
            "json": {
                "messages": messages,
                "model": model,
                "stream": False,
                "max_tokens": max_tokens,
                **kwargs,
            },
            "headers": self._headers,
            "meta": meta,
        }
        return request_params

    async def chat_completions(
        self,
        messages: list,
        model: str,
        return_raw=False,
        preprocess_msg=False,
        url=None,
        show_progress=False,
        **kwargs,
    ) -> Union[str, "RequestResult"]:
        result, _ = await self._client.process_requests(
            request_params=[
                await self.wrap_to_request_params(
                    messages, model, preprocess_msg=preprocess_msg, **kwargs
                )
            ],
            url=url or f"{self._base_url}/chat/completions",
            method="POST",
            show_progress=show_progress,
        )
        data = result[0]
        if return_raw:
            return data
        else:
            if data.status == "success":
                return data.data["choices"][0]["message"]["content"]
            else:
                return data

    def chat_completions_sync(
        self, messages: list, model: str, return_raw=False, url=None, **kwargs
    ):
        return asyncio.run(
            self.chat_completions(
                messages=messages, model=model, return_raw=return_raw, url=url, **kwargs
            )
        )

    async def chat_completions_batch(
        self,
        messages_list: list[list],
        model: str,
        url=None,
        return_raw=False,
        show_progress=True,
        preprocess_msg=False,
        return_summary=False,
        **kwargs,
    ):
        if preprocess_msg:
            messages_list = await optimized_batch_messages_preprocess(
                messages_list,
                max_concurrent=self._concurrency_limit,
                cache_config=self._cache_config,
            )

        results, progress = await self._client.process_requests(
            request_params=[
                await self.wrap_to_request_params(
                    messages, model, preprocess_msg=False, **kwargs
                )
                for messages in messages_list
            ],
            url=url or f"{self._base_url}/chat/completions",
            method="POST",
            show_progress=show_progress,
        )
        summary = progress.summary(print_to_console=False) if progress else None
        if return_raw:
            return (results, summary) if return_summary else results
        content_list = []
        for result in results:
            try:
                content = result.data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(
                    f"Error in chat_completions_batch: {e}\n {result=}\n set content to None"
                )
                content = None
            content_list.append(content)
        return (content_list, summary) if return_summary else content_list

    def chat_completions_batch_sync(
        self,
        messages_list: list[list],
        model: str,
        url=None,
        return_raw=False,
        show_progress=True,
        preprocess_msg=False,
        return_summary=False,
        **kwargs,
    ):
        return asyncio.run(
            self.chat_completions_batch(
                messages_list=messages_list,
                model=model,
                url=url,
                return_raw=return_raw,
                show_progress=show_progress,
                preprocess_msg=preprocess_msg,
                return_summary=return_summary,
                **kwargs,
            )
        )

    async def iter_chat_completions_batch(
        self,
        messages_list: list[list],
        model: str,
        url=None,
        batch_size=None,
        return_raw=False,
        show_progress=True,
        preprocess_msg=False,
        return_summary=False,
        **kwargs,
    ):
        if preprocess_msg:
            messages_list = await batch_process_messages(
                messages_list,
                preprocess_msg=preprocess_msg,
                max_concurrent=self._concurrency_limit,
            )

        async for batch_result in self._client.aiter_stream_requests(
            request_params=[
                await self.wrap_to_request_params(
                    messages, model, preprocess_msg=False, **kwargs
                )
                for messages in messages_list
            ],
            url=url or f"{self._base_url}/chat/completions",
            method="POST",
            show_progress=show_progress,
            batch_size=batch_size,
        ):
            for result in batch_result.completed_requests:
                if return_raw:
                    yield (
                        result.data,
                        batch_result.progress.summary(print_to_console=False)
                        if return_summary
                        else result.data,
                    )
                else:
                    try:
                        content = result.data["choices"][0]["message"]["content"]
                    except Exception as e:
                        logger.warning(
                            f"Error in chat_completions_batch: {e}\n {result=}\n set content to None"
                        )
                        content = None
                    yield (
                        content,
                        batch_result.progress.summary(print_to_console=False)
                        if return_summary
                        else content,
                    )

    def model_list(self):
        from openai import OpenAI

        client = OpenAI(base_url=self._base_url, api_key=self._api_key)
        openai_model_list = [i.id for i in client.models.list()]
        return openai_model_list
