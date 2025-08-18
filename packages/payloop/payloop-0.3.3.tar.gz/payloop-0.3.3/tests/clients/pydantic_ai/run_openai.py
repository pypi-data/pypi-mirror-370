#!/usr/bin/env python3

import asyncio
import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

if os.environ.get("OPENROUTER_API_KEY", None) is None:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

openrouter_provider = OpenAIProvider(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

o4_mini = OpenAIModel("o4-mini", provider=openrouter_provider)

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).pydantic_ai.register(openrouter_provider.client)

agent = Agent(
    o4_mini,
    system_prompt="You're a comedian. Always reply with a joke.",
    model_settings=ModelSettings(max_tokens=1024),
)


def run_agent():
    result = agent.run_sync("Hello!")
    print(result.output)


async def run_agent_async():
    async with agent.run_stream("Hello!") as result:
        async for chunk in result.stream_text(delta=True):
            print(chunk, end="", flush=True)
            import time

            time.sleep(1)


if __name__ == "__main__":
    print("Running sync agent...")
    run_agent()

    print("Running async agent...")
    asyncio.run(run_agent_async())
