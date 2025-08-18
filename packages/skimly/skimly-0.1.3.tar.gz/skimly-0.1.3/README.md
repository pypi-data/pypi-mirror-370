# Skimly Python SDK

Official Python SDK for Skimly - the AI token optimization platform.

## Installation

```bash
pip install skimly
```

## Quick Start

```python
from skimly import SkimlyClient

# Initialize client
client = SkimlyClient.from_env()

# Chat with OpenAI
response = await client.chat({
    "provider": "openai",
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
})

# Upload large content once
blob = await client.create_blob("Large document content...")
print(blob["blob_id"])

# Avoid re-uploading identical content
blob = await client.create_blob_if_new("Large document content...")
```

## API Reference

### `SkimlyClient(key, base?, timeout_ms?, retries?)`

Creates a new Skimly client instance.

### `SkimlyClient.from_env()`

Creates a client from environment variables:
- `SKIMLY_KEY` - Your Skimly API key
- `SKIMLY_BASE` - Base URL (defaults to http://localhost:3000)

### `client.chat(req)`

Send a chat request. Request object should include:
- `provider` - "openai" or "anthropic"
- `model` - Model name
- `messages` - Array of message objects

### `client.create_blob(content, mime_type?)`

Upload large content once. Returns `{blob_id}`.

### `client.create_blob_if_new(content, mime_type?)`

Upload content only if it hasn't been uploaded before. Returns `{blob_id}`.
