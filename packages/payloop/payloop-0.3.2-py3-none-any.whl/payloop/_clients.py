r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import asyncio

from payloop._base import BaseClient
from payloop._invoke import (
    Invoke,
    InvokeAsync,
    InvokeAsyncStreaming,
    InvokePydanticAiAsyncStreaming,
    InvokeStreaming,
)


class Anthropic(BaseClient):
    def register(self, client):
        if not hasattr(client, "messages"):
            raise RuntimeError("client provided is not instance of Anthropic")

        if not hasattr(client, "_payloop_installed"):
            client.messages.actual_create = client.messages.create
            client.messages.create = (
                Invoke(self.config, client.messages.actual_create)
                .set_client(None, "anthropic", client._version)
                .invoke
            )

            client._payloop_installed = True

        self.client = client

        return self


class Google(BaseClient):
    def register(self, client):
        if not hasattr(client, "models"):
            raise RuntimeError("client provided is not instance of genai.Client")

        if not hasattr(client, "_payloop_installed"):
            client.models.actual_generate_content = client.models.generate_content
            client.models.generate_content = (
                Invoke(self.config, client.models.actual_generate_content)
                .set_client(None, "google", client._version)
                .uses_protobuf()
                .invoke
            )

            client._payloop_installed = True

        self.client = client

        return self


class LangChain(BaseClient):
    def register(self, chatopenai=None, chatvertexai=None):
        if chatopenai is not None:
            if not hasattr(chatopenai, "client"):
                raise RuntimeError("client provided is not instance of ChatOpenAI")

            if not hasattr(chatopenai.client._client, "_payloop_installed"):
                chatopenai.client._client.actual_chat_completions_create = (
                    chatopenai.client._client.chat.completions.create
                )
                chatopenai.client._client.chat.completions.create = (
                    Invoke(
                        self.config,
                        chatopenai.client._client.actual_chat_completions_create,
                    )
                    .set_client("langchain", "chatopenai", None)
                    .invoke
                )

                chatopenai.client._client._payloop_installed = True

            self.client = chatopenai.client._client
        elif chatvertexai is not None:
            if not hasattr(chatvertexai, "prediction_client"):
                raise RuntimeError("client provided isnot instance of ChatVertexAI")

            if not hasattr(chatvertexai.prediction_client, "_payloop_installed"):
                chatvertexai.prediction_client.actual_generate_content = (
                    chatvertexai.prediction_client.generate_content
                )
                chatvertexai.prediction_client.generate_content = (
                    Invoke(
                        self.config,
                        chatvertexai.prediction_client.actual_generate_content,
                    )
                    .set_client("langchain", "chatvertexai", None)
                    .uses_protobuf()
                    .invoke
                )

                chatvertexai.prediction_client._payloop_installed = True

            self.client = chatvertexai.prediction_client
        else:
            raise RuntimeError("LangChain::register called without client")

        return self


class OpenAi(BaseClient):
    def register(self, client, _provider=None, stream=False):
        if not hasattr(client, "chat"):
            raise RuntimeError("client provided is not instance of OpenAI")

        if not hasattr(client, "_payloop_installed"):
            client.chat.completions.actual_chat_completions_create = (
                client.chat.completions.create
            )

            try:
                asyncio.get_running_loop()

                if stream is True:
                    client.chat.completions.create = (
                        InvokeAsyncStreaming(
                            self.config,
                            client.chat.completions.actual_chat_completions_create,
                        )
                        .set_client(_provider, "openai", client._version)
                        .invoke
                    )
                else:
                    client.chat.completions.create = (
                        InvokeAsync(
                            self.config,
                            client.chat.completions.actual_chat_completions_create,
                        )
                        .set_client(_provider, "openai", client._version)
                        .invoke
                    )
            except RuntimeError:
                if stream is True:
                    client.chat.completions.create = (
                        InvokeStreaming(
                            self.config,
                            client.chat.completions.actual_chat_completions_create,
                        )
                        .set_client(_provider, "openai", client._version)
                        .invoke
                    )
                else:
                    client.chat.completions.create = (
                        Invoke(
                            self.config,
                            client.chat.completions.actual_chat_completions_create,
                        )
                        .set_client(_provider, "openai", client._version)
                        .invoke
                    )

            client._payloop_installed = True

        self.client = client

        return self


class PydanticAi(BaseClient):
    def register(self, client):
        if not hasattr(client, "chat"):
            raise RuntimeError("client provided was not instantiated using PydanticAi")

        if not hasattr(client, "_payloop_installed"):
            client.chat.completions.actual_chat_completions_create = (
                client.chat.completions.create
            )

            client.chat.completions.create = (
                InvokePydanticAiAsyncStreaming(
                    self.config,
                    client.chat.completions.actual_chat_completions_create,
                )
                .set_client("pydantic_id", "openai", client._version)
                .invoke
            )

            client._payloop_installed = True

        self.client = client

        return self
