# LogSeq HTTP API Architecture

This document describes the LogSeq HTTP API architecture based on source code analysis and practical testing.

## Overview

The LogSeq HTTP API runs on `localhost:12315` (default) and acts as a proxy to LogSeq's internal plugin API methods. It bridges external applications to LogSeq's core functionality through JSON-RPC calls.

## API Endpoint

- **Base URL**: `http://localhost:12315`
- **API Endpoint**: `POST /api`
- **Authentication**: Bearer token required in Authorization header
- **Content-Type**: `application/json`

## Request Format

```json
{
  "method": "logseq.Namespace.methodName",
  "args": [arg1, arg2, ...]
}
```

## Response Format

Standard JSON-RPC response with result or error.

## Internal Architecture

### Request Flow
1. HTTP request hits `/api` endpoint (`server.cljs:142`)
2. Authentication validated via Bearer token (`server.cljs:74-81`)
3. Method name resolved and mapped (`server.cljs:62-72`)
4. Call forwarded to renderer process via IPC (`server.cljs:97-104`)
5. Plugin API method executed in LogSeq context
6. Result returned through the chain

### Method Name Resolution
- API methods follow pattern: `logseq.Namespace.methodName`
- Converted to snake_case internally (e.g., `createPage` → `create_page`)
- Special namespaces: `ui`, `git`, `assets` get `_` suffix

## Verified API Methods

### Editor Namespace (`logseq.Editor.*`)

#### ✅ Implemented & Tested
- **`createPage(pageName, properties, options)`**
  - Creates new page with optional properties
  - Options: `{createFirstBlock: true}` creates initial empty block
  - Example: `["My Page", {}, {"createFirstBlock": true}]`

- **`appendBlockInPage(pageName, content)`**
  - Adds content block to existing page
  - Example: `["My Page", "This is content"]`

- **`getAllPages()`**
  - Returns array of all page objects with metadata
  - Each page includes: name, properties, journal status, etc.

- **`getPage(pageName)`**
  - Returns page object with basic metadata
  - Does not include block content

- **`getPageBlocksTree(pageName)`**
  - Returns hierarchical block structure for page
  - Each block includes: content, properties, children, etc.

#### 🔍 Likely Available (Unverified)
- **`deletePage(pageName)`** - Delete page entirely
- **`updatePage(pageName, properties)`** - Update page properties
- **`insertBlock(targetBlock, content, options)`** - Insert block at position
- **`updateBlock(blockUUID, content)`** - Update specific block content
- **`removeBlock(blockUUID)`** - Delete specific block

### Graph Namespace (`logseq.App.*`)
- **`getCurrentGraph()`** - Get current graph info
- **`getGraphs()`** - List available graphs (potentially)

### Properties Namespace
- **`getPageProperties(pageName)`** - Get page properties (may not exist in all versions)
- **`setPageProperties(pageName, properties)`** - Set page properties

## Authentication

### Token Management
- Tokens stored in LogSeq config: `:server/tokens`
- Can be array of token objects: `[{:value "token123", ...}, ...]`
- Or simple strings: `["token123", "token456"]`
- Bearer token stripped of "Bearer " prefix before validation

### Token Generation
Generated in LogSeq Settings → Features → HTTP APIs server

## Error Handling

### Common Error Codes
- **401 Unauthorized**: Invalid or missing Bearer token
- **400 Bad Request**: Missing or invalid method name
- **404 Method Not Found**: API method doesn't exist (`MethodNotExist`)
- **500 Internal Error**: LogSeq internal errors

### Error Response Format
```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

## Limitations

### Search Functionality
- No direct search endpoints available
- Would require expensive page-by-page iteration:
  1. Get all pages via `getAllPages()`
  2. Get content for each via `getPageBlocksTree()`  
  3. Search content client-side
- **Recommendation**: Avoid implementing search through HTTP API

### Plugin API Boundary
- HTTP API limited to methods exposed to plugin system
- Not all internal LogSeq functions available
- Some advanced operations may require direct database access

## Configuration

### Environment Variables
- `LOGSEQ_API_TOKEN`: Bearer token for authentication
- `LOGSEQ_API_URL`: API base URL (default: `http://localhost:12315`)

### LogSeq Prerequisites
1. LogSeq application running
2. "Enable HTTP APIs server" checked in Settings → Features
3. Valid API token generated

## Implementation Notes

### Content Retrieval Strategy
For complete page content, combine multiple API calls:
1. `getPage(pageName)` - Get page metadata
2. `getPageBlocksTree(pageName)` - Get content blocks
3. `getPageProperties(pageName)` - Get properties (if available)

### Block Structure
Blocks returned by `getPageBlocksTree()` can be:
- Dictionary objects: `{"content": "text", "children": [...], ...}`
- Simple strings: `"plain text content"`
- Empty/null values for placeholder blocks

### Page Creation Pattern
To create page with content:
1. `createPage(pageName, {}, {"createFirstBlock": true})`
2. `appendBlockInPage(pageName, content)` (if content needed)

## Future Research Areas

- Block-level CRUD operations
- Graph management operations  
- Advanced property management
- Asset/file operations via `logseq.Assets.*`
- UI interaction via `logseq.UI.*`
- Git operations via `logseq.Git.*`

---

*Last Updated: 2025-01-20*
*Based on LogSeq source analysis and MCP server implementation*