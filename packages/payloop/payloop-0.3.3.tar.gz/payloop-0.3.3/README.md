Welcome to Payloop!
-------------------

Payloop is a new infrastructure platform that helps AI companies monetize agents based on business outcomes, like leads generated or tickets resolved, rather than usage or seat-based pricing. As agents begin automating workflows across sales, support, and operations, teams need clearer pricing strategies and better visibility into what it actually costs to deliver results.

Payloop gives AI-native companies the tools to define outcomes, track margins per action, and automate billing when those outcomes are met - ultimately helping teams price more confidently and scale more efficiently.

[https://trypayloop.com/](https://trypayloop.com)

## Installation

    pip install payloop

## Usage

### Anthropic

    import anthropic
    from payloop import Payloop

    client = anthropic.Anthropic(...)
    payloop = Payloop(api_key="[your Payloop API key]").anthropic.register(client)

### Google

    from google import genai
    from payloop import Payloop

    client = genai.Client(...)
    payloop = Payloop(api_key="[your Payloop API key]").google.register(client)

### LangChain

    from lanchain_google_vertexai import ChatVertexAI
    from payloop import Payloop

    client = ChatVertexAI(...)
    payloop = Payloop(api_key="[your Payloop API key]".langchain.register(
        chatvertexai=client
    )

    -----------------------------------------------------------------------

    from langchain_openai import ChatOpenAI
    from payloop import Payloop

    client = ChatOpenAI(...)
    payloop = Payloop(api_key="[your Payloop API key]".langchain.register(
        chatopenai=client
    )

### OpenAI

    from openai import OpenAI
    from payloop import Payloop

    client = OpenAI(...)
    payloop = Payloop(api_key="[your Payloop API key]").openai.register(client)

### PydanticAI

    from payloop import Payloop
    from pydantic_ai.models.openai import OpenAIModel

    client = OpenAIModel(...)
    payloop = Payloop(api_key="[your Payloop API key]").pydantic_ai.register(client)

After you have instantiated your LLM client and registered it with Payloop all you
need to do is use the instantiated LLM object as you normally would.

## Transactions

Each call you make to any LLM client that is registered with Payloop will tag your conversation with a transaction ID. As long as the Payloop object you instantiated remains in scope, all LLM calls will be tagged with the same transaction ID.

You might use this in the case you have a single agent that first calls OpenAI, then Anthropic, then Gemini and you want to let Payloop know that all of these operations are associated with a single agent.

If you want to start a new transaction at any time you can either reinstantiate the Payloop object or execute the following call on an instantiated Payloop instance:

    payloop.new_transaction()

# Attribution

Payloop can provide usage and cost breakdowns based on the customers that are using your product. To create attribution, do the following:

    from openai import OpenAI
    from payloop import Payloop

    client = OpenAI(api_key="...")
    payloop = (
        Payloop(api_key="[your Payloop API key]")
        .attribution(
            parent_id=123,
            parent_name="Customer A",
            parent_uuid=...,
            subsidiary_id=456,
            subsidiary_name="Customer Subsidiary B",
            subsidiary_uuid=...
        )
        .openai.register(client)
    )

You can provide a parent, subsidiary or parent and subsidiary. ID, name and UUID are not all required, only one is. However, we strongly encourage that you provide either an ID or a UUID as a unique identifier for the associated parent or subsidiary.

### Supported Functionality

Payloop supports all synchronous, asynchronous and streaming implementations.
