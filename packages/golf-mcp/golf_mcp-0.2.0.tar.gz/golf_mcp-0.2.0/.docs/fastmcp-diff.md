**FastMCP Changes Since v2.5.1**

**Breaking Changes**

* **Decorator & API Refactor**: Decorators now return their created Tool/Resource object; old auto-conversion methods are deprecated.
* **OpenAPI Routes as Tools**: All OpenAPI endpoints are treated as Tools by default, changing prior behavior.
* **MCP Spec 1.10 (v2.10.0)**: `client.call_tool()` now returns a `CallToolResult` (with `result` property) instead of raw JSON. Requires MCP Python SDK ≥1.10.
* **CLI Flag Rename**: `fastmcp run --server` is replaced by `--name`.
* **Removed Custom Separators**: Support for custom nested-resource separators was dropped.

**Non-Breaking Improvements & New Features**

* **Built-In Authentication**

  * Bearer-token support (v2.6.0)
  * OAuth2 & WorkOS AuthProvider integration (v2.11.0)
  * Enhanced JWT handling, scopes, and debug logging
* **Session & State Management**

  * `ctx.session_id` property for each request (v2.9.0)
  * Persistent session-state dict via `ctx.state` (v2.11.0)
* **Middleware System** (v2.9.0): Plug in logging, auth checks, rate limiting, etc.
* **Tool Transforms & Tagging** (v2.8.0): Wrap, rename, enable/disable tools at runtime; filter by tags.
* **Structured Outputs & Elicitation** (v2.10.0): JSON schemas for tool outputs; interactive parameter prompting.
* **Hot-Reload Notifications** (v2.9.1): Clients are notified when tools/resources change at runtime.
* **Audio Content Support** (v2.8.1): Tools can handle audio inputs/outputs.
* **Performance & Stability**: Optimized OpenAPI parsing, concurrency fixes, standardized logging.
