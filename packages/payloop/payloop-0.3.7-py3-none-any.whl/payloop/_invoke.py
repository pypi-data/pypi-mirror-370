r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import time
from collections.abc import AsyncIterator

from payloop._base import BaseInvoke
from payloop._network import Collector
from payloop._stream import AsyncStream
from payloop._utils import merge_chunk


class Invoke(BaseInvoke):
    def invoke(self, **kwargs):
        start = time.time()

        raw_response = self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )

        return raw_response


class InvokeAsync(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        raw_response = await self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )

        return raw_response


class InvokeAsyncStreaming(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        stream = await self._method(**kwargs)

        raw_response = {}
        async for chunk in stream:
            raw_response = merge_chunk(raw_response, chunk.__dict__)
            yield chunk

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )


class InvokePydanticAiAsyncStreaming(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        raw_response = await self._method(**kwargs)
        if isinstance(raw_response, AsyncIterator):
            return (
                AsyncStream(self.config, raw_response)
                .configure_invoke(self)
                .configure_request(kwargs, start)
            )
        else:
            Collector(self.config).fire_and_forget(
                self._format_payload(
                    self._client_provider,
                    self._client_title,
                    self._client_version,
                    start,
                    time.time(),
                    self._format_kwargs(kwargs),
                    self._format_response(raw_response),
                )
            )

            return raw_response


class InvokeStreaming(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        raw_response = await self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )

        return raw_response
