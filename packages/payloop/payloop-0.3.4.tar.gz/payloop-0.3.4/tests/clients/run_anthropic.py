#!/usr/bin/env python3

import os

import anthropic

from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

if os.environ.get("ANTHROPIC_API_KEY", None) is None:
    raise RuntimeError("ANTHROPIC_API_KEY is not set")

client = anthropic.Anthropic()

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).anthropic.register(client)

# Make sure registering the same client again does not cause an issue.
payloop.anthropic.register(client)

# Test setting attribution.
payloop.attribution(
    parent_id=123,
    parent_name="Abc",
    parent_uuid="95473da0-5d7a-435d-babf-d64c5dabe971",
    subsidiary_id=456,
    subsidiary_name="Def",
    subsidiary_uuid="b789eaf4-c925-4a79-85b1-34d270342353",
)

client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
