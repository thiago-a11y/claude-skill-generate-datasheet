---
name: generate-api-client
version: 1.0.0
description: |
  Generates API integration pack from any codebase scan.
  Postman collection + integration guides per stack + webhook docs + auth setup.
  Every endpoint traced to code. Zero hallucination.
  
  Use when: "generate postman", "API docs", "integration guide", "webhook docs",
  "auth setup", "how to integrate", "API client", "como integrar",
  "gerar collection", "documentar API".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Generate API Client v1 — Integration Pack from Code

## What this skill produces

### 1. Postman Collection (JSON)
Importable `.json` file with every detected endpoint:
- Method, URL, headers, auth
- Request body examples extracted from code (validation rules, types, defaults)
- Environment variables for base URL, tokens, API keys
- Organized by module/domain folders
- Pre-request scripts for auth token refresh if detected

### 2. Integration Guides (Markdown)
Per-stack "connect in 5 minutes" guides:
- **React/TypeScript** — fetch/axios examples with typed responses
- **Python** — requests/httpx examples with error handling
- **PHP** — cURL examples with auth setup
- **Node.js** — native fetch/axios examples
- Each guide includes: install, auth, first request, error handling, pagination

### 3. Webhook Documentation (Markdown)
If webhooks/callbacks are detected:
- Event types with trigger conditions
- Payload schema per event (from code)
- Signature verification guide
- Retry policy (if detected)
- Example receiver code per stack

### 4. Auth Setup Guide (Markdown)
Step-by-step authentication flow:
- Auth method detected (JWT, API key, OAuth, Basic, Session)
- Token lifecycle (obtain → use → refresh → revoke)
- Code examples per stack
- Common errors and troubleshooting
- Security best practices for token storage

---

## Anti-Hallucination Protocol

Same rules as generate-datasheet — every claim traces to code evidence.

```
WRONG: "POST /api/users accepts name, email, and role"
RIGHT: "POST /api/users — accepts name (string, required), email (string, required).
       Role field: [NOT DETECTED] in validation rules.
       Evidence: api/users.php:15-30 (validation block)"

WRONG: "The API supports pagination on all endpoints"
RIGHT: "Pagination detected on 3/47 endpoints (grep 'page\|limit\|offset').
       Evidence: api/deals.php:45, api/contacts.php:32, api/activities.php:18.
       Remaining 44 endpoints: [NOT DETECTED] — may return unbounded results."
```

Uncertainty markers:
| Marker | Meaning |
|--------|---------|
| `[VERIFY]` | Found something but can't confirm behavior |
| `[NOT DETECTED]` | Looked for it, didn't find it |
| `[MANUAL]` | Requires human input (base URL, API keys, etc.) |
| `[PARTIAL]` | Found evidence but incomplete |

---

## Process

### Phase 0 — Pre-flight

Ask the user:

```
What do you need?

1. Full integration pack (Postman + guides + webhooks + auth) — recommended
2. Postman collection only
3. Integration guides only (choose stacks)
4. Webhook documentation only
5. Auth setup guide only
6. Specific endpoints (I'll tell you which)

Base URL for the API? (e.g., https://api.example.com or [MANUAL])
```

### Phase 1 — Discovery

**1.1 — Endpoint Scan**
```bash
# Route definitions
grep -rn "router\.\|app\.\(get\|post\|put\|delete\|patch\)\|Route::\|@app\.\|@Get\|@Post\|@Put\|@Delete" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.go" --include="*.rs" 2>/dev/null | head -80

# REST controller patterns
grep -rn "class.*Controller\|def\s\+\(index\|show\|create\|update\|destroy\)" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.rb" 2>/dev/null | head -40

# API directory structure
find . -path "*/api/*" -o -path "*/routes/*" -o -path "*/controllers/*" -o -path "*/endpoints/*" | grep -v "node_modules\|vendor\|\.git" | head -40
```

**1.2 — Request/Response Shapes**
```bash
# Validation rules (what fields are accepted)
grep -rn "validate\|required\|body\.\|req\.body\|request\->\|Schema\.\|z\.object\|yup\.\|joi\." --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -40

# Response shapes
grep -rn "res\.json\|return.*json\|JsonResponse\|jsonify\|response()\|\.send(" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -30

# Status codes used
grep -rn "status(\|statusCode\|HTTP_\|http\.Status" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.go" 2>/dev/null | head -20
```

**1.3 — Authentication**
```bash
# Auth middleware / decorators
grep -rn "auth\|middleware\|bearer\|token\|api.key\|apiKey\|x-api-key\|Authorization" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -30

# JWT patterns
grep -rn "jwt\.\|jsonwebtoken\|JWT\|decode.*token\|verify.*token\|sign.*token" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15

# OAuth patterns
grep -rn "oauth\|OAuth\|client_id\|client_secret\|authorization_code\|access_token\|refresh_token" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15

# Auth endpoints (login, register, token)
grep -rn "login\|register\|signup\|token\|auth\|session" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | grep -i "route\|router\|app\.\|post\|get" | head -15
```

**1.4 — Webhooks / Callbacks**
```bash
# Webhook patterns
grep -rn "webhook\|callback\|event.*emit\|event.*dispatch\|notify\|hook\|trigger" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -20

# Event types / payload construction
grep -rn "event.*type\|eventType\|event_name\|payload\|webhook.*send\|dispatch.*event" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15

# Signature verification
grep -rn "hmac\|signature\|webhook.*secret\|verify.*signature\|webhook.*verify" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10
```

**1.5 — Pagination, Rate Limiting, Versioning**
```bash
# Pagination
grep -rn "page\|limit\|offset\|cursor\|per_page\|pageSize\|next_cursor" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | grep -v "node_modules\|vendor" | head -15

# Rate limiting
grep -rn "rate.limit\|throttle\|X-RateLimit\|rateLimit\|too.many.requests\|429" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10

# API versioning
grep -rn "v1\|v2\|api.*version\|Accept.*version" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | grep -i "route\|path\|url\|prefix" | head -10
```

**1.6 — Error Handling**
```bash
# Error response patterns
grep -rn "error\|Error\|exception\|Exception\|abort\|HttpException\|ApiError" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | grep -i "response\|json\|status\|return" | head -20

# Error codes / messages
grep -rn "error.*code\|error.*message\|errorCode\|error_code" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15
```

### Phase 2 — Inventory Presentation

```
## API Discovery Results

### Endpoints
- Total: [count] endpoints detected
- Methods: GET [count] / POST [count] / PUT [count] / DELETE [count] / PATCH [count]
- Auth-protected: [count] / [total]

### Authentication
- Method: [JWT / API Key / OAuth / Basic / NOT DETECTED]
- Token endpoint: [path / NOT DETECTED]
- Refresh mechanism: [detected / NOT DETECTED]

### Webhooks
- Events detected: [count / NOT DETECTED]
- Signature verification: [detected / NOT DETECTED]

### Features
- Pagination: [detected on N endpoints / NOT DETECTED]
- Rate limiting: [detected / NOT DETECTED]
- Versioning: [detected / NOT DETECTED]

### Stacks for integration guides
Which stacks? (React/TS, Python, PHP, Node.js, all)

Is this accurate? Anything to add or correct?
```

### Phase 3 — Generate Postman Collection

Generate a valid Postman Collection v2.1 JSON file.

**Structure:**
```json
{
  "info": {
    "name": "{Project Name} API",
    "description": "Generated from codebase scan. [MANUAL] items need human input.",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {"key": "baseUrl", "value": "[MANUAL — set your API base URL]"},
    {"key": "authToken", "value": "[MANUAL — set after login]"}
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/login",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\"email\": \"user@example.com\", \"password\": \"[MANUAL]\"}"
            }
          }
        }
      ]
    }
  ]
}
```

Rules for collection generation:
- Group endpoints by module/domain (from directory structure)
- Include request body with field types from validation rules
- Add `[MANUAL]` for values that can't be extracted from code
- Include auth header on protected endpoints
- Add description with source file:line reference per endpoint
- Environment variables for base URL, auth tokens, common IDs

### Phase 4 — Generate Integration Guides

One markdown file per stack. Template:

```markdown
# {Project Name} API — {Stack} Integration Guide
<!-- Generated by generate-api-client v1. Sources cited per section. -->

## Quick Start (5 minutes)

### 1. Install
<!-- source: package.json or detected SDK -->

### 2. Authenticate
<!-- source: auth middleware at {file}:{line} -->

### 3. First Request
<!-- source: simplest GET endpoint at {file}:{line} -->

## Authentication
<!-- source: {auth files} -->

### Get Token
### Use Token
### Refresh Token (if detected)
### Handle Expired Token

## Endpoints by Module

### {Module Name}
<!-- source: {route file}:{lines} -->

#### {Method} {Path}
- **Auth**: required / optional / none
- **Request body**: {fields with types}
- **Response**: {shape from code}
- **Example**:

## Error Handling
<!-- source: error handler at {file}:{line} -->

| Status | Meaning | Example Response |
|--------|---------|-----------------|

## Pagination
<!-- source: {file}:{line} or [NOT DETECTED] -->

## Rate Limits
<!-- source: {file}:{line} or [NOT DETECTED] -->
```

### Phase 5 — Generate Webhook Documentation

Only generate if webhooks detected in Phase 1.4. If not detected, skip with note.

```markdown
# {Project Name} — Webhook Documentation
<!-- Generated by generate-api-client v1. -->

## Overview
- Events detected: [count]
- Delivery method: [HTTP POST / NOT DETECTED]
- Signature verification: [method / NOT DETECTED]
- Retry policy: [details / NOT DETECTED]

## Events

### {event.type}
<!-- source: {file}:{line} -->
- **Trigger**: {when this event fires}
- **Payload**:
```json
{
  "event": "{event.type}",
  "data": { ... }
}
```
- **Fields**: {description of each field with source}

## Verifying Signatures
<!-- source: {file}:{line} or [NOT DETECTED] -->

## Receiver Examples

### Node.js
### Python
### PHP
```

### Phase 6 — Generate Auth Setup Guide

```markdown
# {Project Name} — Authentication Guide
<!-- Generated by generate-api-client v1. -->

## Auth Method: {JWT / API Key / OAuth / Basic}
<!-- source: {auth middleware file}:{line} -->

## Flow

### Step 1: Obtain credentials
[MANUAL — describe how users get API access]

### Step 2: Authenticate
<!-- source: {login endpoint file}:{line} -->

### Step 3: Use token in requests
<!-- source: {auth middleware file}:{line} -->

### Step 4: Refresh token (if applicable)
<!-- source: {refresh endpoint file}:{line} or [NOT DETECTED] -->

### Step 5: Handle errors
<!-- source: {auth error handler file}:{line} -->

| Error | Cause | Solution |
|-------|-------|----------|

## Security Best Practices
- Token storage: [recommendations based on detected patterns]
- Token expiry: [detected TTL or MANUAL]
- HTTPS: [enforced / NOT DETECTED]
- CORS: [configuration or NOT DETECTED]

## Code Examples
### cURL
### JavaScript (fetch)
### Python (requests)
### PHP (cURL)
```

### Phase 7 — Validation & Report

```
## Integration Pack Generated

### Postman Collection
- {project}-api.postman_collection.json
- Endpoints: [count]
- With auth: [count]
- [MANUAL] fields: [count]

### Integration Guides
- docs/integration-react.md (if selected)
- docs/integration-python.md (if selected)
- docs/integration-php.md (if selected)
- docs/integration-node.md (if selected)

### Webhook Documentation
- docs/webhooks.md ([count] events / or "not generated — no webhooks detected")

### Auth Setup Guide
- docs/auth-setup.md

### Human Input Needed
- [count] items marked [MANUAL]
- Base URL configuration
- API credentials for testing
- Webhook endpoint URL for receiving events
```

---

## Key Principles

1. **Evidence over inference** — every endpoint traced to file:line
2. **Importable output** — Postman collection is valid JSON, ready to import
3. **Stack-specific** — code examples use each stack's idioms and best practices
4. **Uncertainty is honest** — `[NOT DETECTED]` for missing pagination, rate limits, etc.
5. **Humans provide context** — base URLs, credentials, business rules are `[MANUAL]`
6. **Zero dependencies** — generates files, doesn't install anything

## What This Skill Is NOT

- Not an API gateway — generates docs, doesn't proxy requests
- Not OpenAPI/Swagger — generates Postman + guides, not spec files
- Not a mock server — documents real endpoints from code
- Not a testing tool — generates examples, humans test them
