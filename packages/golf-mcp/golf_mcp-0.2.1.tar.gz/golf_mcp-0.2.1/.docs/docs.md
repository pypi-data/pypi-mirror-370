# Golf Framework — Technical Specification

## 1  Purpose

Golf is a **filesystem‑first build engine** that compiles a directory tree of *tools*, *prompts*, and *resources* into a runnable [FastMCP](https://github.com/fastmcp/fastmcp) server application. This document is the authoritative technical spec for implementers and integrators.

---

## 2  Terminology

| Term               | Definition                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| **Component**      | A *tool*, *prompt*, or *resource* file discovered under the project’s category directories.          |
| **ID**             | Stable identifier derived from a component’s path. Used as registration name inside FastMCP.         |
| **Project Root**   | Directory containing `golf.json` (or `golf.yaml`).                                                   |
| **Build Artifact** | The generated Python package (default `build/app.py`) that instantiates and runs the FastMCP server. |

---

## 3  On‑Disk Layout

```
<project‐root>/
│
├─ golf.json          # Mandatory configuration
│
├─ tools/             # Category directory: tools
│   └─ …/*.py         # Nested arbitrarily deep
│
├─ prompts/           # Category directory: prompts
│   └─ …/*.py
│
└─ resources/         # Category directory: resources
    └─ …/*.py
```

*Each Python file defines exactly **one** component.* Non‑Python files and `__init__.py` are ignored. common.py files hold common implementation for group of tools, things like auth or SDK clients, common variables or data types.

---

## 4  ID Derivation Algorithm

Given a component file `C` with absolute path

```
<project‑root>/<category>/<p₁>/…/<pₙ>/<filename>.py
```

let `PathRev = [pₙ, …, p₁]` (reverse order of parent dirs under the category). The **ID** is

```
<filename> + ("_" + "_".join(PathRev) if PathRev else "")
```

### Formal Definition (BNF)

```
<id> ::= <token> [ "-" <token> { "-" <token> } ]
<token> ::= /[a-z0-9_]+/
```

Case is preserved; implementers MUST leave tokens unchanged. Collisions are a build‑time error.

---

## 5  Component Specification

### 5.1  Metadata Source

1. **Module docstring** — mandatory, first triple‑quoted literal.
2. **Function docstring** — optional; ignored unless module docstring missing.

### 5.2  Function Signature Requirements

| Component | Required Object                 | Rules                                                                                                |
| --------- | ------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Tool      | One top‑level `def` (any name). | ‑ Positional & keyword params MUST have type hints.<br>‑ Return annotation REQUIRED.<br>             |
| Prompt    | One top‑level `def`.            | Returns `str` or `fastmcp.PromptMessage`.                                                            |
| Resource  | Either `def` or constant.       | If constant, MUST be JSON‑serialisable. If `def`, obey same type rules as Tool but **no arguments**. |

### 5.3  Automatic Validation

The parser SHALL fail the build if:

* No module docstring.
* Multiple top‑level functions.
* Unsupported parameter/return types (not JSON or pydantic‑serialisable).

---

## 6  Build Process (Pipeline)

| Phase                     | Responsibility                                                                                              |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **0 Config Load**         | Parse `golf.json` → `Config` object with defaults.                                                          |
| **1 Discovery**           | Recursively walk `tools/`, `prompts/`, `resources/`; collect `.py` files.                                   |
| **2 Parsing**             | `ast.parse()` each file → build `Component` objects (id, type, path, description, function ref, signature). |
| **3 Semantic Validation** | Detect ID collisions, type‑hint violations, missing metadata, reserved keyword conflicts.                   |
| **4 Code Generation**     | Emit `build/app.py`:                                                                                        |

1. Imports for every component module.
2. Instantiates `FastMCP(name=config.name)`.
3. For each component generates `mcp.tool|prompt|resource(...)(func)`.
4. Configures runtime host/port via `mcp.run(host=config.host, port=config.port, transport=config.transport)`.
5. Footer `if __name__ == "__main__": mcp.run()`. |
   \| **5 Code Generation** | Emit `build/app.py`:
6. Imports for every component module.
7. Instantiates `FastMCP(name=config.name)`.
8. For each component generates `mcp.tool|prompt|resource(...)(func)`.
9. Adds runtime injection wrappers where needed.
10. Configures runtime host/port via `mcp.run(host=config.host, port=config.port, transport=config.transport)` and applies auth middleware if defined.
11. Footer `if __name__ == "__main__": mcp.run()`.
    \| **6 Packaging** | Copy auxiliary files (e.g. TLS certs) if declared. |
    \| **7 Completion** | Write artifact map & build log. |

---

## 7  CLI Contract

```bash
$ golf init [--template <repo‑url>]     # scaffold
$ golf build [--outdir DIR]             # compile once
$ golf run   [--host HOST] [--port P]   # build if stale then exec app.py
```

Exit codes: `0` success · `1` validation error · `2` runtime failure.

---

## 8  Configuration File (`golf.json` v 0.2)

```jsonc
{
  "name": "AssistantServer",          // FastMCP instance name
  "output_dir": "build",              // build artifact folder
  "host": "0.0.0.0",                  // listening interface
  "port": 8080,                        // listening port
  "transport": "http"                 // "http" (streamable HTTP, default) or "sse"
}
```

### JSON‑Schema (abridged)

````jsonc
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "output_dir": { "type": "string" },
    "host": { "type": "string" },
    "port": { "type": "integer" },
    "transport": { "enum": ["http", "sse"] }
  },
  "required": ["name"]
}
```jsonc
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "output_dir": { "type": "string" },
    "host": { "type": "string" },
    "port": { "type": "integer" }
  },
  "required": ["name"]
}
````

---

## 9  File→Code Translation Example (Tool)

**Input file** `tools/payments/refund/submit.py`

```python
"""Submit a refund request to Stripe."""
import stripe
from resources.clients import stripe_client

def run(charge_id: str, amount: int) -> dict:
    refund = stripe_client.Refund.create(charge=charge_id, amount=amount)
    return refund
```

**Generated snippet in `build/app.py`**

```python
from tools.payments.refund import submit as _submit

mcp.tool(
    name="submit_refund_payments",
    description="Submit a refund request to Stripe."
)(_submit.run)
```

---

## 10  Extensibility Hooks

* **Pre‑Build Plugins** — `pre_build.py` in project root can register callbacks to mutate `Component` objects.
* **Transport Providers** — third‑party packages can expose `golf_transport` entry‑point returning `TransportFactory` classes recognised by codegen.
