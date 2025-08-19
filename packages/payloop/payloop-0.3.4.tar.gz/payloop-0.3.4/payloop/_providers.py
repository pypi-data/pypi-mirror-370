r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

from payloop._base import BaseProvider
from payloop._clients import Anthropic as AnthropicPayloopClient
from payloop._clients import Google as GooglePayloopClient
from payloop._clients import LangChain as LangChainPayloopClient
from payloop._clients import OpenAi as OpenAiPayloopClient
from payloop._clients import PydanticAi as PydanticAiPayloopClient


class Anthropic(BaseProvider):
    def register(self, client):
        if self.client is None:
            self.client = AnthropicPayloopClient(self.config).register(client)

        return self.parent


class Google(BaseProvider):
    def register(self, client):
        if self.client is None:
            self.client = GooglePayloopClient(self.config).register(client)

        return self.parent


class LangChain(BaseProvider):
    def register(self, chatopenai=None, chatvertexai=None):
        if self.client is None:
            self.client = LangChainPayloopClient(self.config).register(
                chatopenai=chatopenai, chatvertexai=chatvertexai
            )

        return self.parent


class OpenAi(BaseProvider):
    def register(self, client, stream=False):
        if self.client is None:
            self.client = OpenAiPayloopClient(self.config).register(
                client, stream=stream
            )

        return self.parent


class PydanticAi(BaseProvider):
    def register(self, client):
        if self.client is None:
            self.client = PydanticAiPayloopClient(self.config).register(client)

        return self.parent
