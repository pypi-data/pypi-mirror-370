# Sonyk Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Fws-github-admin%2Fsonyk-py-sdk)
[![pypi](https://img.shields.io/pypi/v/sonyk_sdk)](https://pypi.python.org/pypi/sonyk_sdk)

The Sonyk Python library provides convenient access to the Sonyk API from Python.

## Installation

```sh
pip install sonyk_sdk
```

## Reference

A full reference for this library is available [here](https://github.com/ws-github-admin/sonyk-py-sdk/blob/HEAD/./reference.md).

## Usage

Instantiate and use the client with the following:

```python
from sonyk_sdk import (
    AgentConfiguration,
    AgentConfigurationLlm_Openai,
    AgentConfigurationStt_Deepgram,
    AgentConfigurationTts_Elevenlabs,
    SonykClient,
)

client = SonykClient(
    api_key="YOUR_API_KEY",
)
client.agents.create_agent(
    agent_name="Restaurant Receptionist",
    agent_json=AgentConfiguration(
        llm=AgentConfigurationLlm_Openai(
            model="gpt-5",
            system_prompt="# Role\nYou are Georgia, a friendly and professional receptionist at the  restaurant.\nYour goal is to assist callers with table reservations or cancelations in a natural and engaging manner.\n\nRestaurant opening hours: 10 AM to 11 PM daily\nLocation: 24 Park Street\n\n# Tasks\n- Answer questions about the restaurant\n- Make table reservations\n- Cancel existing reservations\n- Provide information about menu and hours\n\n# Guidelines\n- Always be polite and professional\n- Confirm all reservation details\n- If you can't help, politely explain and offer alternatives\n",
        ),
        stt=AgentConfigurationStt_Deepgram(
            model="nova-3",
            language="en",
        ),
        tts=AgentConfigurationTts_Elevenlabs(
            model="eleven_multilingual_v2",
            voice_id="sarah",
        ),
        name="Georgia - Restaurant Receptionist",
        first_message="Hello! Welcome to  restaurant. I'm Georgia, how can I help you today?",
    ),
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
import asyncio

from sonyk_sdk import (
    AgentConfiguration,
    AgentConfigurationLlm_Openai,
    AgentConfigurationStt_Deepgram,
    AgentConfigurationTts_Elevenlabs,
    AsyncSonykClient,
)

client = AsyncSonykClient(
    api_key="YOUR_API_KEY",
)


async def main() -> None:
    await client.agents.create_agent(
        agent_name="Restaurant Receptionist",
        agent_json=AgentConfiguration(
            llm=AgentConfigurationLlm_Openai(
                model="gpt-5",
                system_prompt="# Role\nYou are Georgia, a friendly and professional receptionist at the  restaurant.\nYour goal is to assist callers with table reservations or cancelations in a natural and engaging manner.\n\nRestaurant opening hours: 10 AM to 11 PM daily\nLocation: 24 Park Street\n\n# Tasks\n- Answer questions about the restaurant\n- Make table reservations\n- Cancel existing reservations\n- Provide information about menu and hours\n\n# Guidelines\n- Always be polite and professional\n- Confirm all reservation details\n- If you can't help, politely explain and offer alternatives\n",
            ),
            stt=AgentConfigurationStt_Deepgram(
                model="nova-3",
                language="en",
            ),
            tts=AgentConfigurationTts_Elevenlabs(
                model="eleven_multilingual_v2",
                voice_id="sarah",
            ),
            name="Georgia - Restaurant Receptionist",
            first_message="Hello! Welcome to  restaurant. I'm Georgia, how can I help you today?",
        ),
    )


asyncio.run(main())
```

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from sonyk_sdk.core.api_error import ApiError

try:
    client.agents.create_agent(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Advanced

### Access Raw Response Data

The SDK provides access to raw response data, including headers, through the `.with_raw_response` property.
The `.with_raw_response` property returns a "raw" client that can be used to access the `.headers` and `.data` attributes.

```python
from sonyk_sdk import SonykClient

client = SonykClient(
    ...,
)
response = client.agents.with_raw_response.create_agent(...)
print(response.headers)  # access the response headers
print(response.data)  # access the underlying object
```

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retryable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

A request is deemed retryable when any of the following HTTP status codes is returned:

- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) (Internal Server Errors)

Use the `max_retries` request option to configure this behavior.

```python
client.agents.create_agent(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python

from sonyk_sdk import SonykClient

client = SonykClient(
    ...,
    timeout=20.0,
)


# Override timeout for a specific method
client.agents.create_agent(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
import httpx
from sonyk_sdk import SonykClient

client = SonykClient(
    ...,
    httpx_client=httpx.Client(
        proxies="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
