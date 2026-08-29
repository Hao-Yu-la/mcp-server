# Viking Knowledge Base MCP Server

This MCP server provides a tool to interact with the VolcEngine Viking Knowledge Base Service, allowing you to search and retrieve knowledge from your collections, meanwhile,
allowing you to add doc to your collections and get doc processing info by doc_id.

## Features

- Search knowledge based on queries with customizable parameters

## Setup

### Prerequisites

- Python 3.10 or higher
- API credentials (AK/SK)

### Installation

1. Install the package:

```bash
pip install -e .
```

Or with uv (recommended):

```bash
uv pip install -e .
```

### Configuration

The server requires the following environment variables:

- `VOLCENGINE_ACCESS_KEY`: Your VolcEngine access key
- `VOLCENGINE_SECRET_KEY`: Your VolcEngine secret key

Optional environment variables:
- `KNOWLEDGE_BASE_PROJECT`: Viking Knowledge Base project name (default: `default`)
- `KNOWLEDGE_BASE_REGION`: Viking Knowledge Base region (default: `cn-north-1`)
- `MCP_SERVER_HOST`: Streamable HTTP bind host (default: `127.0.0.1`)
- `MCP_SERVER_PORT`: Streamable HTTP port; falls back to `PORT` (default: `8000`)
- `STREAMABLE_HTTP_PATH`: Streamable HTTP endpoint path (default: `/mcp`)
- `KNOWLEDGE_BASE_TIMEOUT`: Upstream request timeout in seconds (default: `30`)

## Usage

### Running the Server

The server supports stdio for local integrations and stateless Streamable HTTP
for remote deployments:

```bash
python -m mcp_server_knowledgebase.server --transport stdio
```

Or:

```bash
python -m mcp_server_knowledgebase.server --transport streamable-http
```

The Streamable HTTP endpoint is `http://127.0.0.1:8000/mcp` by default.
Set `MCP_SERVER_HOST=0.0.0.0` when running behind a trusted gateway.

### MCP protocol compatibility

This server uses MCP Python SDK 2.x and speaks protocol revision `2026-07-28`.
Modern clients use the stateless per-request protocol and `server/discover`;
the same process also supports older handshake-based clients automatically.
Legacy HTTP+SSE is intentionally not exposed because it is deprecated by the
`2026-07-28` specification.

The HTTP endpoint does not turn the configured VolcEngine AK/SK into client
authentication. Protect remote deployments with an authentication gateway or
MCP-compatible OAuth, and never expose the service credentials to callers.

### Available Tools

#### add_doc

Add a document to a collection in your project.

```python
add_doc(
    collection_name="collection_name",
    add_type="url",
    doc_id="mcp_server_auto_gen_doc_id_xxxxxxx",
    doc_name="doc_xxxx",
    doc_type="pdf",
    url="http://xxxxx.pdf"
)
```

Parameters:
- `collection_name` (required): the name of the collection you want to add document .
- `add_type` (required): the type of the document to add. so far only support "url" now. 
- `doc_id` (required): you should generate a unique doc_id based on user's given url and timestamp, the doc_id can only use English letters, numbers, and underscores , and must start with an English letter. It cannot be empty. Length requirement: [1, 128], you can use a format like "mcp_server_auto_gen_doc_id_xxxxxxx".
- `doc_name` (required): the name of the document to add. You can generate a unique doc_name based on the user-provided URL and timestamp. The length of doc_name must be between 1 and 256; for example, "mcp_server_auto_gen_doc_name_xxxxxxx".
- `doc_type` (required): the type of the document to add. for structured document, we support xlsx, csv,jsonl, for unstructured document, wu support txt, doc, docx, pdf, markdown, faq.xlsx, pptx". you should judge the doc_type based on user's given url and judge if we support this doc type. if supported, assign this parameter.
- `url` (required): the url of the document to add. user should give a valid url, we will add the doc to the collection.

#### get_doc

Get information about document by collection_name and doc_id .

```python
get_doc(
    collection_name="collection_name",
    doc_id="mcp_server_auto_gen_doc_id_xxxxxxx",
)
```

Parameters:
- `collection_name` (required): the name of the collection you want to get information .
- `doc_id` (required): the doc_id of document user want to get information .

#### get_collection

Get information about a viking knowledge base collection from your project .

```python
get_collection(
    collection_name="collection_name",
)
```

Parameters:
- `collection_name` (required): the name of the collection you want to get information .


#### list_collections

List all knowledge base collections of the globally configured project .

```python
list_collections(
)
```


#### search_knowledge

Search for knowledge in the configured collection based on a query.

```python
search_knowledge(
    query="How to reset my password?",
    limit=3,
    collection_name="collection_name",
    doc_filter=None,
)
```

Parameters:
- `query` (required): The search query string
- `limit` (optional): Maximum number of results to return, from 1 to 100 (default: 3)
- `collection_name` (required): Knowledge Base collection name to search
- `doc_filter` (optional): the filter is used to filter search results(default: None), which is structured as a JSON object with the following key components:
  - `op` (string, required): specifies the query operator that defines the filtering logic. Valid values are 'must' and 'must_not', 'must' means results must satisfy the condition (inclusion filter),'must_not' means results must not satisfy the condition (exclusion filter).
  - `field` (string, required): indicates the specific document field to apply the filter on (e.g., "doc_id").
  - `conds` (array, required):  contains the concrete values used for filtering. The data type of elements in the array depends on the field.
## MCP Integration

To add this server to your MCP configuration, add the following to your MCP settings file:

```json
{
  "mcpServers": {
    "knowledgebase": {
      "command": "uvx",
        "args": [
          "--from",
          "git+https://github.com/volcengine/mcp-server#subdirectory=server/mcp_server_knowledgebase",
          "mcp-server-knowledgebase"
        ],
      "env": {
        "VOLCENGINE_ACCESS_KEY": "your-access-key",
        "VOLCENGINE_SECRET_KEY": "your-secret-key", 
        "KNOWLEDGE_BASE_PROJECT": "your-project-name",
        "KNOWLEDGE_BASE_REGION": "your-region"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your AK/SK credentials are correct
   - Check that you have the necessary permissions for the collection

2. **Connection Timeouts**
   - Check your network connection to the VolcEngine API
   - Verify the host configuration is correct

3. **Empty Results**
   - Verify the collection name is correct
   - Try broadening your search query

### Logging

The server uses Python's logging module with INFO level by default. You can see detailed logs in the console when running the server.

## Contributing

Contributions to improve the Viking Knowledge Base MCP Server are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

volcengine/mcp-server is licensed under the [MIT License](https://github.com/volcengine/mcp-server/blob/main/LICENSE).
