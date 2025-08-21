Got it. I’ll prepare a technical specification summary for the Model Context Protocol (MCP) repository, based on the latest version from the main branch. This will include low-level technical details, component-level breakdowns, and any integration requirements, formatted in a spec-style document suitable for engineers.

I’ll update you once the summary is ready.


# Model Context Protocol (MCP) – Technical Specification Summary

## Introduction and Overview

The **Model Context Protocol (MCP)** is an open standard for connecting AI-powered applications (LLM hosts) with external data sources and tools. It defines a client-server architecture inspired by the Language Server Protocol (LSP) to **standardize context integration** – much like a “USB-C port” for AI models. MCP allows a host application (with an embedded LLM) to interface with one or more external **MCP servers** that provide resources (data), tools (actions/functions), and prompt templates in a unified way. By using MCP, an AI application can share context with the LLM and invoke external capabilities through a consistent protocol, rather than bespoke integrations.

**Roles:** MCP defines three primary roles in its architecture:

* **Host** – the AI-powered application or environment that needs external context (e.g. a chat app, IDE, etc.).
* **Client** – the MCP client component within the host that initiates and manages connections to servers.
* **Server** – an external service providing context data or functions (capabilities) to the host.

A host may manage multiple client connections to different servers simultaneously (one per server), enabling modular, composable integrations. Communication is **stateful** over each client-server session.

## Transport and Message Format

All MCP communication uses **JSON-RPC 2.0** as the wire protocol. Every message is a JSON object with a `"jsonrpc": "2.0"` field and follows JSON-RPC conventions for requests, responses, and notifications. The general message schema is:

* **Request:** Includes an `id` (to correlate responses) and a `method` name, with optional `params` for method arguments. The client or server sending a request expects a response.
* **Response:** Includes the matching `id` and either a `result` (on success) or an `error` (on failure) object. Errors contain a numeric `code`, a message, and optional data.
* **Notification:** A one-way message with a `method` and optional `params`, but *no* `id` (no response expected). Notifications are used for events or signals (e.g. progress updates).

**Transports:** MCP is transport-agnostic – any channel that can carry JSON text can carry MCP messages. Two standard transports are defined for current implementations:

* **Stdio Transport:** Uses the process’s STDIN/STDOUT streams to send JSON-RPC messages. This is ideal for local servers launched as subprocesses (similar to LSP servers) and has very low latency (no network overhead). It is limited to local use.
* **HTTP + SSE Transport:** Uses a combination of HTTP and Server-Sent Events for networked connections. The client opens an HTTP SSE stream (e.g. GET on an `/sse` endpoint) to receive server-to-client notifications/events, and sends client-to-server requests via HTTP POST (e.g. to a `/messages` endpoint). This allows servers to push real-time updates to the client. All messages still conform to JSON-RPC 2.0 framing over this channel. For security, SSE transports should enforce origin checks and authentication (to mitigate DNS rebinding, etc.).

*MCP is designed to accommodate other transports as well (e.g. WebSocket) for scenarios requiring full-duplex communication over a single connection.* Regardless of transport, message encoding and semantics remain consistent via JSON-RPC.

## Protocol Lifecycle and Handshake

**Connection Initialization:** Every MCP session begins with a handshake sequence to establish version and capabilities compatibility:

1. **Client → Server – `initialize` Request:** The client opens a JSON-RPC connection and sends an `initialize` request. This request includes:

   * `protocolVersion`: The MCP protocol version the client supports (usually the latest it implements). MCP uses date-based version identifiers (e.g. `"2025-03-26"`) for its specification; the client supplies one of these version strings.
   * `clientInfo`: An object with the client’s name and version (for logging/diagnostics).
   * `capabilities`: An object declaring the client’s supported optional features (see **Capabilities** below). For example, a client that can provide “roots” (workspace context) or handle sampling requests will indicate those here.
   * Optionally, workspace context parameters such as `rootUri` or `workspaceFolders` (URI(s) of the workspace root(s)) if the client limits server access to certain URI scopes. (These fields mirror the LSP initialize parameters, allowing the client to suggest a root directory or multiple roots for the server to focus on.)
   * `trace`: Trace level (e.g. `"off"` or verbose) for diagnostics, if supported.

   The `initialize` request uses a unique `id` since a response is expected. ***Until the handshake completes, no other requests or notifications should be processed*** by either side (except perhaps low-level pings, see below).

2. **Server → Client – `initialize` Response:** The server responds to the initialize request with either a success result or an error. On success, the response’s `result` **must** include:

   * `protocolVersion`: The version that will be used for this session. If the server supports the client’s requested version, it echoes it; if not, the server may respond with a different version it supports (typically its latest). The client should disconnect if it cannot handle the version returned by the server (ensuring both sides agree on a common spec version).
   * `capabilities`: An object declaring the server’s available features/capabilities for this session. This tells the client which categories of functionality the server provides (and any special capability options – see below).
   * `serverInfo`: An object with server’s name and version (for display or logging).
   * `instructions`: *Optional.* A free-form string with any special instructions or guidance for the client/user. Servers may use this to convey setup info or usage tips to be shown in the UI.

   For example, a server response might look like:

   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "protocolVersion": "2024-11-05",
       "capabilities": {
         "logging": {}, 
         "prompts": { "listChanged": true },
         "resources": { "subscribe": true, "listChanged": true },
         "tools": { "listChanged": true }
       },
       "serverInfo": { "name": "ExampleServer", "version": "1.0.0" },
       "instructions": "Additional usage info..."
     }
   }
   ```



   In this example, the server chose version `"2024-11-05"` and advertises that it supports logging, prompts, resources, and tools (with some extra flags described below).

3. **Client → Server – `initialized` Notification:** After receiving a successful response, the client sends an `initialized` notification to confirm the handshake is complete. This message has a method like `"notifications/initialized"` (no `id`) and no special params. It signals that the client is ready to proceed. The server should not send any requests (other than trivial pings or logs) before this notification is received.

At this point, the session is established. Both parties *must* respect the negotiated `protocolVersion` and only use features that were agreed upon in the capabilities exchange.

### Capability Negotiation

During initialization, **capability objects** from client and server determine which optional protocol features will be active. Capabilities are grouped by category:

* **Client Capabilities:** Indicate what the *client* can do or is willing to handle. Key flags include:

  * `roots`: The client can provide **workspace roots** (context URIs) to the server. If supported, the client includes a list of root URIs in the initialize params (via `rootUri` or `workspaceFolders`). The server should then limit scope to those roots and may assume those are the relevant contexts.
  * `sampling`: The client supports **LLM sampling requests** from the server. (This means the client is willing to let the server request that the host’s LLM generate text – see *Sampling* below. Usually this also implies the client will implement a user approval flow for such requests.)
  * `experimental`: A general flag indicating the client supports vendor-specific or non-standard extensions. Any experimental features would be negotiated separately (not detailed in the core spec).

* **Server Capabilities:** Indicate what features the *server* offers. The primary categories are:

  * `resources`: The server can provide **Resources** (readable data items).
  * `tools`: The server offers executable **Tools** (functions/actions).
  * `prompts`: The server provides predefined **Prompt templates** or workflows.
  * `logging`: The server can emit **log messages** for debugging or audit.
  * `experimental`: The server has some experimental extensions (outside standard spec).

  Each capability may be an object that includes boolean flags for sub-features. For example, as shown in the handshake above, the server set `"tools": { "listChanged": true }` – this means the server supports sending notifications if the list of tools changes at runtime. Common sub-capabilities include:

  * `listChanged`: server can notify the client of additions/removals in its list of prompts/resources/tools.
  * `subscribe`: server supports subscription to updates on individual items (applicable to resources).

  If a capability object is present (even empty `{}`), it generally implies support for that category. For instance, `"logging": {}` in the server response means the server will send log messages, and `"resources": { "subscribe": true, "listChanged": true }` means the server provides resources, supports subscriptions to resource updates, and will notify on resource list changes. Absent or false capabilities indicate that feature is not available. The client and server should only use the features that both sides have negotiated as supported.

*Versioning:* The MCP specification is versioned, and both client and server **MUST** agree on a version during initialization. Each release of the spec is identified by a date (e.g. *2024-11-05*, *2025-03-26*). The client sends its supported version, the server may respond with a different version if needed, and the client should disconnect if no common version exists. This mechanism ensures interoperability as the protocol evolves. New capability categories or message types can be introduced in future versions without breaking older clients, since unsupported features will simply not be negotiated.

## Core Protocol Operations (Features and Messages)

After initialization, the client and server engage in the **operation phase**, exchanging JSON-RPC requests and notifications according to the features enabled. MCP defines standard methods (with namespaced method strings) for each major capability. All method names are lowercase and typically use a category prefix (e.g. `resources/…`, `tools/…`, `prompts/…`). Below is a detailed breakdown of each major component:

### Resources (Context Data)

**Resources** represent data or content that a server can expose for the client/LLM to use as context (files, documents, database records, API results, etc.). Each resource is identified by a **URI** and can be text or binary data. The protocol defines methods to discover and read these resources:

* **List Resources –** `resources/list` (Request): The client requests a list of available resources from the server. The response contains an array of **resource descriptors**, each describing one resource. Each resource descriptor includes:

  ```typescript
  {
    uri: string;          // Unique identifier (URI) for the resource
    name: string;         // Human-readable name
    description?: string; // Optional description
    mimeType?: string;    // Optional MIME type of the resource content
  }
  ```

  The `uri` is often a scheme-specific URI (e.g. a `file://` path, a custom scheme like `db://` or `http://` for web resources). The `name` and `description` help the user/AI understand what the resource is (for example, a file name or title). The `mimeType` can hint at the content type (e.g. `"text/plain"`, `"application/pdf"`).

  *Dynamic Resources:* Servers can also advertise **resource templates** – URI patterns for resources that can be constructed on the fly (e.g. a template for querying a database). These templates are given in the resource list as objects with a `uriTemplate` (RFC 6570 format) and descriptive fields, allowing clients to know how to form valid resource URIs.

* **Read Resource –** `resources/read` (Request): The client requests the content of a specific resource by providing its `uri` in the params. The server responds with the resource data. The response format is:

  ```json
  {
    "contents": [
      {
        "uri": "<same URI requested>",
        "mimeType": "type/subtype",
        // One of the following:
        "text": "...",   // for textual content
        "blob": "BASE64_ENCODED_DATA"  // for binary content
      },
      { ... further items ... }
    ]
  }
  ```

  Each item in the `contents` array is a **Content Item** representing the resource (or part of it). Typically, a single-item array is returned containing the whole content. The content can be given as plain text (for text resources) or as a base64 `blob` (for binaries). The server echoes the `uri` and may include a `mimeType` if not obvious. Notably, MCP allows returning **multiple content items** for one `resources/read` request – for example, if the `uri` was a folder, the server might return a list of files in that folder as multiple items, or if a resource is large it might be chunked (though chunking is typically handled via streaming/progress rather than multiple items). In general, however, a single resource corresponds to one content payload.

* **Resource Updates:** If negotiated, the server can support real-time updates to resources:

  * **List Changes:** The server sends a notification `notifications/resources/list_changed` when the overall set of resources has changed (e.g. a new file became available). The client might then call `resources/list` again to get the updated list. This feature corresponds to the `listChanged` capability flag for resources.
  * **Content Changes:** The client can subscribe to a particular resource’s updates if the server supports it. This is done via a `resources/subscribe` request (with the target `uri`), and later `resources/unsubscribe` to cancel. While subscribed, the server will send `notifications/resources/updated` whenever that resource’s content changes. The client can then call `resources/read` again to fetch the new content. This corresponds to the `subscribe` capability.

In summary, the Resources feature provides a **read-only data sharing interface**. The client remains in control of which resources to retrieve (the server does not push full contents without a request, aside from update signals). For security, hosts MUST obtain user consent before transmitting any sensitive user data via `resources/read` or subscribing to updates.

### Tools (Executable Actions)

**Tools** are functions or operations that the server can perform on behalf of the client, potentially affecting external systems or returning computed results. Tools allow an LLM (via the client) to act – for example, run a calculation, query an API, or modify something – under controlled conditions. Each tool is essentially a **remote procedure** exposed by the server. MCP defines methods for discovering available tools and invoking them:

* **List Tools –** `tools/list` (Request): The client queries what tools the server offers. The response is a list of tool definitions, each containing:

  ```typescript
  {
    name: string;           // Unique tool identifier
    description?: string;   // Human-readable description of what the tool does
    inputSchema: {          // JSON Schema for the tool's expected input parameters
       type: "object";
       properties: { ... };
       required?: [ ... ];
    };
    annotations?: {         // Optional behavioral hints
       title?: string;              
       readOnlyHint?: boolean;     // true if tool does not modify state
       destructiveHint?: boolean;  // true if tool may have side-effects
       idempotentHint?: boolean;   // true if calling with same args twice is safe
       openWorldHint?: boolean;    // true if tool interacts with external world
    }
  }
  ```

  Every tool has a unique `name` by which it is invoked. The `inputSchema` is a JSON Schema (object type) defining the parameters that must be provided when calling the tool. This schema includes the property names, types, and which are required, allowing the client (and the LLM) to understand how to format a valid tool call. For example, a “translate” tool might have an input schema requiring a `text` string and a `targetLanguage` code.

  The optional `annotations` give additional metadata about the tool’s behavior. These hints are not strictly enforced by the protocol but serve as guidance to the client or end-user. For instance, a tool marked `readOnlyHint: true` should not alter any data (safe to run without side-effects), whereas `destructiveHint: true` indicates it *may* perform destructive operations (like deleting data). Clients can use these flags to, say, warn users or require extra confirmation before allowing the LLM to call such a tool. `openWorldHint` signifies the tool reaches out to external systems (e.g. makes network calls). These annotations enhance safety and transparency.

  **Discovery:** The `tools/list` response thus provides the full catalog of the server’s capabilities in terms of actions, along with the exact inputs each expects. The client will typically present these to the LLM (or user) so that they know what functions are at their disposal.

* **Call Tool –** `tools/call` (Request): The client invokes a specific tool by name. The request parameters include the tool `name` (or an equivalent identifier) and an object of arguments conforming to that tool’s inputSchema. For example:

  ```json
  {
    "id": 42,
    "method": "tools/call",
    "params": { 
       "tool": "calculate_sum",
       "args": { "numbers": [1,2,3] }
    }
  }
  ```

  (The exact param structure – e.g. using `"tool"` and `"args"` fields – is defined by the JSON schema; it must align with how the SDK expects it. In this example, we assume a tool named *calculate\_sum* that sums a list of numbers.)

  The server will execute the requested function and return either a result or an error. The **result** (`tools/call` Response) can be any JSON value or structured object that the tool produces. For instance, a calculation might return `{ "result": 6 }`, or a tool that fetches an API could return a JSON payload. The format of the result is *tool-specific* – it should be documented by the tool’s description/contract. If the tool fails or cannot be executed, the server returns a JSON-RPC error with details. Common error codes might include standard JSON-RPC errors or custom codes for tool-specific failures (the spec does not fix specific tool error codes, but servers should provide a descriptive `message` and optional `data`).

  **Tool Execution Semantics:** Tools are potentially powerful (they might execute code or alter external state). Therefore, MCP implementations **must require explicit user approval** before an AI invokes a tool. Typically, the client will intercept an LLM’s decision to use a tool and prompt the user to allow or deny it. The protocol itself just transmits the request; the policy of requiring user consent is an important *implementation* consideration (not an automated part of MCP). The `annotations` mentioned above assist the client in deciding how to present the tool (e.g. flag dangerous ones).

  Tools are meant to be **dynamic actions**. Unlike resources, which are passive data, a tool can have side effects and produce different outputs for each call. The client should treat tool calls as potentially altering the environment (unless marked `readOnlyHint`). The server should handle duplicate requests carefully (idempotent tools vs. non-idempotent). The protocol itself includes a standard cancellation mechanism (discussed under **Utilities** below) – if a tool call is long-running, the client can attempt to cancel it via `$/cancelRequest`.

### Prompts (Templates & Workflows)

**Prompts** in MCP are reusable prompt templates or multi-step conversational workflows provided by the server. They allow servers to supply predefined instructions or dialogues that the client (and ultimately the LLM) can use, which is useful for standardizing interactions (for example, a “bug report summary” prompt template). Prompts are primarily **user-controlled**: the intention is that a user or client explicitly selects a prompt template to use, rather than the LLM choosing arbitrarily.

Key interactions for prompts:

* **List Prompts –** `prompts/list` (Request): The client asks the server for all available prompt templates. The response contains a list of prompt definitions, each including:

  ```typescript
  {
    name: string;              // Unique identifier for the prompt
    description?: string;      // Description of what the prompt does
    arguments?: [             // Optional list of expected user arguments
      {
        name: string; 
        description?: string;
        required?: boolean;
      },
      ...
    ]
  }
  ```

  The `name` is an identifier used to refer to the prompt (e.g. `"analyze-code"`). The optional `arguments` array specifies any placeholders or inputs that should be provided when using the prompt. For example, a prompt named "translate-text" might accept an argument for the target language. Each argument can have a description and a flag if it’s required. The prompt’s actual content (e.g. the template text) is not fully given in the list; the list is more of an index of available prompts.

* **Get Prompt –** `prompts/get` (Request): The client retrieves the full content of a prompt template by name, typically when the user or AI has chosen to use that prompt. The request params include the `name` of the prompt and an optional map of `arguments` values to fill into the template. The server responds with the prompt **payload**, which usually includes:

  * `description`: (Optional) A text description of the prompt (could repeat the one from list).
  * `messages`: An array of message objects that form the prompt conversation. Each message object has a `role` (such as `"system"`, `"user"`, or `"assistant"`) and a `content`. The content can be a **text segment** or a **resource reference**. For example, a simple prompt might return:

    ```json
    {
      "description": "Analyze Python code for potential improvements",
      "messages": [
        {
          "role": "user",
          "content": {
            "type": "text",
            "text": "Please analyze the following Python code for potential improvements:\n\n<code snippet here>"
          }
        }
      ]
    }
    ```

    In this case, the prompt defined a user message containing a template text (with perhaps an inserted code snippet). If the prompt included placeholders and the client provided `arguments`, the server will have filled those in (e.g. inserted the actual `language: "python"` into the template as shown in the snippet above).

    More complex prompts can include multiple messages and even embed resource contents. For instance, a prompt workflow might include a system message with instructions, then a user message that includes content of a resource (like logs or a file) for the model to consider. The `content` object in a message can have `type: "resource"`, which means it inlines a resource’s content. The server will provide the resource’s `uri`, possibly a snippet of its `text` data, and a `mimeType` in such cases. This allows a prompt to say “Analyze *this* data” and actually include the data from a resource.

Using prompts is typically a matter of the client receiving the `messages` array and then feeding those messages into the LLM’s context (prepended to the conversation) when the user or agent triggers that prompt. Prompts can implement multi-step workflows by returning a sequence of messages the client should process or display in order.

### Sampling (Server-Initiated LLM Queries)

**Sampling** is an **optional** feature that allows the server to ask the client’s LLM to generate text, effectively letting the server initiate an AI completion with some control. This feature enables more complex agent behaviors: for example, the server might reach a point in a tool’s operation where it needs the AI to make a decision or summarize something, and it can offload that query back to the client’s model. Because this has significant security implications (the server could potentially prompt the AI arbitrarily), it is only enabled if the client advertises the `sampling` capability and the server agrees. Even then, the design is **human-in-the-loop** – the client/user should review and approve any server-initiated prompts to the LLM.

The primary method is:

* **Create Message (Sample) –** `sampling/createMessage` (Request): Sent *from the server to the client*. The server provides a prompt (or conversation context) for which it wants the client to obtain an LLM completion. The request parameters include:

  * `messages`: an array of messages (role/content objects) that serve as the conversation context. This is the prompt the server wants the model to process. It may include user or assistant turns. The format of each message is similar to that used in prompts: a `role` and a `content` where content can be text or image (for example, the server could ask the client’s model to describe an image by including an image content with base64 data and mimeType). Typically, the server will include a final user message or a system instruction and expect the model (assistant) to produce the next message.
  * `modelPreferences`: an optional object where the server can suggest which model or what sampling parameters to use. This can include hints like a preferred model name/family, or priorities such as `costPriority` and `speedPriority` (values 0.0–1.0) to indicate whether minimizing cost or latency is more important. These are just hints; the client may choose how to interpret them (e.g. selecting a smaller model if costPriority is high, etc.).

  When the client receives this request, it should typically: (1) notify the user (since the server is effectively asking the model a question on the user’s behalf), (2) optionally allow the user to edit or approve the prompt, then (3) have the LLM generate a completion using its own inference endpoint or API. The resulting completion (which would be an assistant message) is then returned to the server as the response of `sampling/createMessage`. The response data would include the assistant’s message content (text or other format) generated by the model.

  This flow ensures the server can leverage the client’s AI for subtasks, but **the client remains in control**: the server never directly interacts with the model without the client’s mediation. All server-initiated sampling requests must be explicitly approved by the user according to MCP’s security guidelines. For example, a server might use this to ask *“Hey model, given this data you retrieved via a tool, what should we do next?”* – but the user would see that prompt and confirm it before the model responds.

At the time of writing, not all clients support sampling (e.g. Claude Desktop did not yet support it as of early 2025), but the protocol is designed to accommodate this powerful pattern in a safe manner.

### Additional Utilities and Controls

MCP includes a few built-in utility mechanisms to manage the session and long-running tasks:

* **Heartbeats/Pings:** MCP may define a lightweight ping message (the spec references a `ping` method) to allow one side to check connectivity or latency. These would typically be notifications or requests that echo back, used to keep the connection alive. (Exact method name is not given in the summary above, but likely something like `$/.ping` or similar, as hinted by references.)

* **Progress Notifications:** For lengthy operations (such as a tool call that takes significant time), the server can send incremental progress updates to the client. The protocol reserves a method (conventionally `$/progress`) as a notification for this purpose. The progress notification may carry data about percentage completed or status text. This enables the client UI to inform the user that a task is in progress. Progress messages are purely advisory (no response from client). The server should send them at a reasonable rate if at all. The example method name uses the `$` prefix, which denotes an internal/extension method (following JSON-RPC/LSP convention).

* **Cancellation:** MCP allows requests to be cancelled. If a client needs to abort an in-flight request (e.g. the user clicked “Cancel” on a long tool invocation), it can send a `$/cancelRequest` notification targeting the request’s `id`. Upon receiving cancellation, the server *should* attempt to halt the operation and respond with an error (e.g. code `-32800` for cancelled, or a custom code) if the operation can indeed be stopped. The exact cancellation protocol mirrors JSON-RPC cancellation used in LSP.

* **Error Handling:** Besides standard JSON-RPC errors for request failures, MCP doesn’t introduce new error codes except where logically needed. It does suggest using existing JSON-RPC codes (`-32600` invalid request, `-32602` invalid params, etc.) or custom codes for domain-specific issues. Servers should provide helpful `message` strings and can use the `data` field in error objects to convey extra debug info. Both client and server can emit errors – e.g., if the server calls the client (sampling) and it fails, the client returns an error.

* **Logging:** If the server’s `logging` capability is enabled, the server can send log entries to the client for debugging or audit. The spec defines **structured logging** messages (the reference suggests a `logging` notification category). These might include a log level, message, and maybe timestamp or other data. For example, a server might notify `logging/message` with params like `{ level: "info", message: "Indexed 5 files" }`. The client could display or record these logs. Logging is one-way (server→client) and optional; it’s mainly for developers or power users to inspect what the server is doing.

All the above utilities are designed to improve the robustness of the integration (with feedback, control, and transparency). They are generally prefixed with `$` or placed under a distinct namespace (`notifications/` or `logging/`) to avoid conflict with core feature methods.

## Data Models and Schema Availability

The MCP specification is formally defined by a TypeScript schema file in the official repository. The **protocol schema** includes all request/response structures, notifications, and data types (tools, resources, etc.) as TypeScript interfaces. This source of truth is used to generate a **JSON Schema** definition for broader language compatibility. Integrators can use the JSON Schema to validate messages or even autogenerate code for unsupported languages.

For convenience, the MCP working group provides **SDKs** in multiple languages, which implement these interfaces and handle transport details:

* **TypeScript/Node.js SDK:** Provides classes for Server and Client, JSON-RPC transport implementations (stdio, HTTP/SSE), and helpers to define tools/resources easily. Built with Node – the repo includes build configs like *package.json*, *.npmrc*, and a TypeScript config. Developers can import the official NPM package (e.g. `@modelcontextprotocol/typescript-sdk`) to get started.
* **Python SDK:** Similarly, offers `Server` and `Client` classes, and integrations with asyncio for transports. Likely published on PyPI (e.g. `modelcontext` package).
* **Java, Kotlin, C#, Swift SDKs:** Implementations for these languages exist, aligning to the same protocol schema. For example, the Java/Kotlin SDK may use WebSocket or HTTP clients for connecting, and C# for .NET integration.

Using an official SDK is recommended to ensure correct protocol handling (message formatting, threading, etc.). However, because MCP is fully specified, developers can also implement it from scratch in any language by following the JSON-RPC message schema and required method set.

**Dependencies and Build:** The core specification repository is primarily a TypeScript project (requires Node.js). Building it will generate the JSON Schema and possibly documentation. Runtime dependencies are minimal since JSON-RPC is simple; e.g. the Node SDK might use a lightweight HTTP library for SSE, and the Python SDK might use `aiohttp` or `starlette` for SSE support. No proprietary formats are used – all data is JSON-based, with binary data base64-encoded if needed. This choice maximizes interoperability across platforms.

Versioning is handled via the handshake as described, so an MCP client/server pair will automatically degrade to the highest mutually supported spec version. The MCP working group releases new versions periodically (the latest as of writing is **2025-03-26**) and maintains backward compatibility guidelines through the negotiation mechanism. Integrators should track the spec repository for updates (it has a version history and “Key Changes” documented for each release).

## Security and Interoperability Considerations

MCP’s power – exposing arbitrary data and tools to an AI – comes with significant security responsibilities. The protocol itself provides hooks for safety (like capability negotiation, user approval steps, and rich metadata), but implementers **MUST** enforce policies such as:

* **User Consent:** The user should always be in control of what an AI can access or do. For example, the client should require user approval before an LLM reads a private resource or invokes a tool that could cause side effects. All actions initiated via MCP should be transparent to the user.
* **Data Privacy:** Clients must not send user data to servers without permission. The server only sees what the client chooses to share (e.g. the client might filter or redact parts of a file before sending via `resources/read` if needed). Hosts should sandbox local servers and use authentication for remote servers when appropriate.
* **Tool Safety:** Tools are essentially remote code execution from the perspective of the host. Clients should treat tool definitions and results as untrusted by default (unless the server is fully trusted). Descriptions and annotations come from the server and could misrepresent the tool – clients might choose to override or vet these descriptions if security is critical.
* **LLM Prompt Controls:** For sampling requests, the protocol deliberately limits what the server can see of the LLM’s state – typically the server only provides the prompt for that specific request, and does not get to see the entire conversation history (unless the client explicitly includes it). This prevents a server from covertly extracting information from the conversation. Clients should also ensure that any server-provided prompt (in `sampling/createMessage`) is shown to the user before allowing the model to act on it.

Because MCP is an open protocol, interoperability is a priority: any client should work with any server as long as they speak the same version and negotiate capabilities. The JSON Schema and well-defined method semantics facilitate this. Different implementations (language SDKs or custom) can interoperate on the wire. For example, one could run an official Python MCP server and connect to it from a third-party MCP client in Go, and it should function, provided both conform to the spec. Testing across implementations is encouraged to ensure consistency.

Finally, MCP’s design is *extensible*. The `"experimental"` capability flags allow trying new extensions in a controlled way. The working group process (on the GitHub repository) governs the evolution of the protocol – proposals for new features go through discussions and versioned releases. Integrators should aim to implement the spec as written, and use the capability negotiation to handle any custom extensions, to maintain compatibility with the wider ecosystem.

**Conclusion:** This specification summary covers MCP’s main components – from the JSON-RPC message format and transport bindings, to the data models for resources, tools, and prompts, as well as the initialization handshake and safety mechanisms. It serves as a blueprint for engineers to implement or integrate MCP. By following the standard method names, schemas, and flows described above, developers can enable their AI applications to seamlessly connect with a rich variety of external data sources and operations in a secure, interoperable manner. The MCP repository provides further details (including the full schema and SDK code) for reference, ensuring that this open protocol can be adopted consistently across languages and platforms.
