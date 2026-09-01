# Viking Knowledge Base MCP Server

[简体中文](README_zh.md)

## Overview

Viking Knowledge Base MCP Server lets MCP clients such as Claude Desktop,
Cursor, Cline, and Trae interact with VolcEngine Viking Knowledge Base. It
supports managing and inspecting collections and documents, and searching for
relevant knowledge chunks.

## Features

- Add a document to a knowledge base collection by URL
- Get document information and processing status
- List documents with cursor pagination
- Get collection information and build status
- List collections in the configured project
- Search a collection with optional document filtering
- Authenticate with either a Viking API key or VolcEngine AK/SK credentials
- Run over stdio or stateless Streamable HTTP

## Prerequisites

- Python 3.10 or later
- A Viking Knowledge Base API key, or VolcEngine AK/SK credentials

## Installation

Install from PyPI:

```bash
pip install mcp-server-knowledgebase
```

Or install it as a persistent command-line tool with `uv`:

```bash
uv tool install mcp-server-knowledgebase
```

For local development, clone the repository and install this package in
editable mode:

```bash
git clone https://github.com/volcengine/mcp-server.git
cd mcp-server/server/mcp_server_knowledgebase
uv pip install -e .
```

## Configuration

### Authentication

Configure at least one authentication method:

- API key: set `VIKING_API_KEY`. Requests use
  `Authorization: Bearer <VIKING_API_KEY>`.
- AK/SK: set both `VOLCENGINE_ACCESS_KEY` and
  `VOLCENGINE_SECRET_KEY`. Requests use VolcEngine SignerV4 authentication.

When both methods are configured, `VIKING_API_KEY` takes precedence. If no API
key is set, the access key and secret key must be configured together.

### Environment variables

| Environment variable | Description | Default |
|---|---|---|
| `VIKING_API_KEY` | Viking Knowledge Base API key; takes precedence when configured | - |
| `VOLCENGINE_ACCESS_KEY` | VolcEngine access key | - |
| `VOLCENGINE_SECRET_KEY` | VolcEngine secret key | - |
| `KNOWLEDGE_BASE_PROJECT` | Viking Knowledge Base project | `default` |
| `KNOWLEDGE_BASE_REGION` | VolcEngine region used for AK/SK signing | `cn-north-1` |
| `KNOWLEDGE_BASE_TIMEOUT` | Upstream request timeout in seconds | `30` |
| `MCP_SERVER_HOST` | Streamable HTTP bind host | `127.0.0.1` |
| `MCP_SERVER_PORT` | Streamable HTTP port; falls back to `PORT` | `8000` |
| `STREAMABLE_HTTP_PATH` | Streamable HTTP endpoint path | `/mcp` |

## Running the server

Run with the default stdio transport:

```bash
mcp-server-knowledgebase
```

Run the published package without installing it persistently:

```bash
uvx --from mcp-server-knowledgebase mcp-server-knowledgebase
```

Or run the module directly from a source checkout:

```bash
python -m mcp_server_knowledgebase.server --transport stdio
```

Run with stateless Streamable HTTP:

```bash
mcp-server-knowledgebase --transport streamable-http
```

The default endpoint is `http://127.0.0.1:8000/mcp`. Set
`MCP_SERVER_HOST=0.0.0.0` only when deploying behind a trusted gateway.

### MCP protocol and deployment security

The server uses MCP Python SDK 2.x and supports protocol revision `2026-07-28`,
including stateless `server/discover` negotiation. The SDK also handles older
handshake-based clients. Legacy HTTP+SSE is not exposed because it is
deprecated by the `2026-07-28` specification.

Streamable HTTP does not turn the configured Viking API key or VolcEngine
AK/SK into client authentication. Protect remote deployments with an
authentication gateway or MCP-compatible OAuth, and never expose service
credentials to callers.

## Available tools

- [`add_doc`](https://www.volcengine.com/docs/84313/1254624): Add a document by URL
- [`get_doc`](https://www.volcengine.com/docs/84313/1254615): Get document information and processing status
- [`list_docs`](https://docs.volcengine.com/docs/84313/2477871?lang=zh): List documents with cursor pagination
- [`get_collection`](https://www.volcengine.com/docs/84313/1254602): Get collection information
- [`list_collections`](https://www.volcengine.com/docs/84313/1254596): List collections in the configured project
- [`search_knowledge`](https://www.volcengine.com/docs/84313/1350012): Search knowledge in a collection

### `add_doc`

Add a supported document to a collection by URL.

```python
add_doc(
    collection_name="product_docs",
    add_type="url",
    doc_id="product_guide_2026",
    doc_name="Product Guide",
    doc_type="pdf",
    url="https://example.com/product-guide.pdf",
)
```

Parameters:

- `collection_name` (required): Target collection name.
- `add_type` (required): Currently only `"url"` is supported.
- `doc_id` (required): Unique ID containing only letters, numbers, and
  underscores. It must start with a letter and contain 1–128 characters.
- `doc_name` (required): Document name containing 1–256 characters.
- `doc_type` (required): One of `xlsx`, `csv`, `jsonl`, `txt`, `doc`, `docx`,
  `pdf`, `markdown`, `faq.xlsx`, or `pptx`.
- `url` (required): Accessible URL of the document.

Example result:

```json
{
  "collection_name": "product_docs",
  "doc_id": "product_guide_2026"
}
```

### `get_doc`

Get a document's metadata and processing status.

```python
get_doc(
    collection_name="product_docs",
    doc_id="product_guide_2026",
)
```

Parameters:

- `collection_name` (required): Collection containing the document.
- `doc_id` (required): Document ID.

Example result:

```json
{
  "collection_name": "product_docs",
  "doc_id": "product_guide_2026",
  "doc_name": "Product Guide",
  "doc_type": "pdf",
  "url": "https://example.com/product-guide.pdf",
  "add_type": "url",
  "create_time": 1788220800,
  "update_time": 1788220860,
  "point_num": 53,
  "status": {
    "process_status": 0,
    "failed_code": null
  }
}
```

`process_status` values: `0` completed, `1` failed, `2` or `3` queued, `5`
deleting, and `6` processing. Fields not returned by Viking are `null`;
additional upstream document fields are preserved.

### `list_docs`

List documents in a collection using cursor pagination.

```python
list_docs(
    collection_name="product_docs",
    limit=2,
    next_token=None,
)
```

Parameters:

- `collection_name` (required): Collection whose documents will be listed.
- `limit` (optional): Number of documents to return, from 1 to 100. Defaults
  to `100`.
- `next_token` (optional): Opaque cursor returned by the previous call. Omit
  it for the first page. An empty cursor in the result means all documents
  have been returned.

Example result:

```json
{
  "collection_name": "product_docs",
  "total_num": 3,
  "count": 2,
  "doc_list": [
    {
      "collection_name": "product_docs",
      "doc_id": "product_guide_2026",
      "doc_name": "Product Guide",
      "doc_type": "pdf",
      "url": "https://example.com/product-guide.pdf",
      "add_type": "url",
      "create_time": 1788220800,
      "update_time": 1788220860,
      "point_num": 53,
      "status": {
        "process_status": 0
      },
      "brief_summary": "An introduction to the product.",
      "total_tokens": 345
    }
  ],
  "has_more": true,
  "next_token": "opaque-cursor-for-next-page"
}
```

`total_num` is `null` when Viking does not provide it. Document entries
preserve additional upstream fields such as summaries and token counts.

### `get_collection`

Get information and build status for a collection.

```python
get_collection(collection_name="product_docs")
```

Parameters:

- `collection_name` (required): Collection name.

Example result:

```json
{
  "collection_name": "product_docs",
  "description": "Product manuals and release notes",
  "status": 1
}
```

Collection status values: `-1` pending build, `0` building, `1` completed,
`2` failed, and `3` changing.

### `list_collections`

List all collections in the globally configured project.

```python
list_collections()
```

This tool has no parameters.

Example result:

```json
{
  "collection_list": [
    {
      "collection_name": "product_docs",
      "description": "Product manuals and release notes"
    },
    {
      "collection_name": "support_faq",
      "description": "Frequently asked support questions"
    }
  ]
}
```

### `search_knowledge`

Search for relevant chunks in a collection. An optional document filter can
include or exclude matching document field values.

```python
search_knowledge(
    query="How do I reset my password?",
    collection_name="support_faq",
    limit=3,
    doc_filter={
        "op": "must",
        "field": "doc_id",
        "conds": ["account_guide"],
    },
)
```

Parameters:

- `query` (required): Search query.
- `collection_name` (required): Collection to search.
- `limit` (optional): Maximum number of chunks to return, from 1 to 100.
  Defaults to `3`.
- `doc_filter` (optional): Object with the following fields:
  - `op`: `"must"` to include matches or `"must_not"` to exclude them.
  - `field`: Document field to filter, such as `"doc_id"`.
  - `conds`: Non-empty list of values to match.

Example result:

```json
{
  "result_list": [
    {
      "id": "chunk_001",
      "content": "Open Account Settings and select Reset Password.",
      "doc_id": "account_guide",
      "doc_name": "Account Guide"
    }
  ]
}
```

`doc_id` and `doc_name` are `null` when Viking does not provide document
metadata. A non-null `doc_id` can be passed directly to `get_doc`.

## MCP client configuration

Example stdio configuration using `uvx` and a Viking API key:

```json
{
  "mcpServers": {
    "knowledgebase": {
      "command": "uvx",
      "args": [
        "--from",
        "mcp-server-knowledgebase>=0.2.0",
        "mcp-server-knowledgebase"
      ],
      "env": {
        "VIKING_API_KEY": "your-viking-api-key",
        "KNOWLEDGE_BASE_PROJECT": "your-project-name",
        "KNOWLEDGE_BASE_REGION": "cn-north-1"
      }
    }
  }
}
```

You can instead configure both `VOLCENGINE_ACCESS_KEY` and
`VOLCENGINE_SECRET_KEY`. If all three credentials are present,
`VIKING_API_KEY` takes precedence.

## Troubleshooting

1. Authentication errors
   - Verify the API key or AK/SK credentials.
   - When using AK/SK, configure both values together.
   - Check that the credentials can access the configured project and collection.
2. Connection timeouts
   - Check network connectivity to the VolcEngine API.
   - Adjust `KNOWLEDGE_BASE_TIMEOUT` when necessary.
3. Empty results
   - Verify the project and collection names.
   - For search, try a broader query or remove the document filter.
   - For document listing, continue only with the exact `next_token` returned
     by the previous call.

## License

This project is licensed under the [MIT License](https://github.com/volcengine/mcp-server/blob/main/LICENSE).
