# TUI Mockups - Horizontal Split Layout

These mockups show the preferred layout option (Horizontal Split) in various states, demonstrating how the interface responds to different user selections.

## Layout Overview

- **Top Section**: Global Security and Auditing (static, always visible)
- **Bottom Section**: Three-pane layout for server management
  - Left: MCP Servers list
  - Middle: Server plugins list  
  - Right: Configuration details

## 1. MCP Server Selected (No Plugin Selected)

```
╭─ Watchgate Security Configuration ────────────────────────────────────────────────────────────╮
│ GLOBAL SECURITY ══════════════════════════════════════════════════════════════════════════════││
│ PII Filter      [✅ Active]  Redacting: Email, Phone, SSN                          [Configure]││
│ Secrets Filter  [✅ Active]  Blocking: API Keys, Tokens, Passwords                 [Configure]││
│ Prompt Defense  [❌ Disabled]  Click to enable injection protection                [Enable]   ││
│                                                                                               ││
│ GLOBAL AUDITING ══════════════════════════════════════════════════════════════════════════════││
│ JSON Logger     [✅ Active]  logs/audit.json (2.3 MB today, 45 MB total)          [View Logs]││
│ CSV Export      [❌ Disabled]  Export audit logs to CSV format                     [Setup]    ││
│ Syslog Forward  [○ Available]  Send logs to remote syslog server                  [Setup]    ││
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─ MCP Servers ──────┐ ┌─ Server Plugins ───────────┐ ┌─ Server Overview ────────────────────┐│
│ │                    │ │ filesystem plugins:        │ │ filesystem Server                     ││
│ │ ● filesystem   ←  │ │                            │ │ ─────────────────────────────────     ││
│ │   /app/sandbox    │ │ • Tool Allowlist      ✅   │ │                                       ││
│ │   12 tools        │ │   Allow 4/12 tools        │ │ Status: ● Connected                  ││
│ │                    │ │                            │ │ Command: npx @modelcontextprotocol/  ││
│ │ ○ github          │ │ • Path Security       ✅   │ │          server-filesystem            ││
│ │   Not connected   │ │   Sandbox restricted      │ │ Args: /app/sandbox                    ││
│ │   28 tools        │ │                            │ │ PID: 12345                            ││
│ │                    │ │ • Rate Limiting       ○   │ │ Started: 2h 15m ago                  ││
│ │ ○ sqlite          │ │   Available to enable     │ │                                       ││
│ │   Not configured  │ │                            │ │ Available Tools (12):                 ││
│ │   8 tools         │ │ • Custom Headers      ○   │ │ • read_file      • delete_file       ││
│ │                    │ │   Available to enable     │ │ • write_file     • execute_command   ││
│ │ ──────────────    │ │                            │ │ • list_directory • move_file         ││
│ │ + Add Server       │ │ [+ Add Plugin]             │ │ • create_dir     • copy_file         ││
│ └────────────────────┘ └────────────────────────────┘ │ • get_permissions• set_permissions   ││
│                                                        │ • watch_directory• search_files      ││
│                                                        │                                       ││
│                                                        │ [Test Connection] [Restart] [Remove] ││
│                                                        └───────────────────────────────────────┘│
│ Connected: 1/3 | Plugins: 7 active | [Save] [Load Profile] | ↑↓ Navigate | Enter: Configure   │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 2. Global PII Filter Selected

```
╭─ Watchgate Security Configuration ────────────────────────────────────────────────────────────╮
│ GLOBAL SECURITY ══════════════════════════════════════════════════════════════════════════════││
│ PII Filter      [✅ Active]  Redacting: Email, Phone, SSN                     ← [Configure]  ││
│ Secrets Filter  [✅ Active]  Blocking: API Keys, Tokens, Passwords                 [Configure]││
│ Prompt Defense  [❌ Disabled]  Click to enable injection protection                [Enable]   ││
│                                                                                               ││
│ GLOBAL AUDITING ══════════════════════════════════════════════════════════════════════════════││
│ JSON Logger     [✅ Active]  logs/audit.json (2.3 MB today, 45 MB total)          [View Logs]││
│ CSV Export      [❌ Disabled]  Export audit logs to CSV format                     [Setup]    ││
│ Syslog Forward  [○ Available]  Send logs to remote syslog server                  [Setup]    ││
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────┐│
│ │ PII Filter Configuration (Global - Applies to All Servers)                                  ││
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ││
│ │                                                                                             ││
│ │ Detection Action:                                                                           ││
│ │ ● Redact - Replace detected PII with [REDACTED]                                           ││
│ │ ○ Block - Reject requests containing PII                                                  ││
│ │ ○ Audit Only - Log detections but don't modify                                            ││
│ │                                                                                             ││
│ │ PII Types to Detect:                                                                       ││
│ │ ┌─ Personal Information ─────┐ ┌─ Financial ──────────────┐ ┌─ Network & Technical ──────┐││
│ │ │ ☑ Email Addresses         │ │ ☐ Credit Card Numbers    │ │ ☑ IP Addresses (IPv4/IPv6) │││
│ │ │ ☑ Phone Numbers           │ │ ☐ Bank Account Numbers   │ │ ☐ MAC Addresses            │││
│ │ │ ☑ Social Security Numbers │ │ ☐ Routing Numbers        │ │ ☐ URLs                     │││
│ │ │ ☐ Passport Numbers        │ │ ☐ IBAN                   │ │ ☐ Bitcoin Addresses        │││
│ │ │ ☐ Driver's License        │ │ ☐ CVV Codes              │ │                            │││
│ │ └─────────────────────────────┘ └──────────────────────────┘ └────────────────────────────┘││
│ │                                                                                             ││
│ │ Regional Formats:                      Advanced Options:                                   ││
│ │ ☑ US Formats (SSN, Phone)             ☐ Scan Base64 Encoded Content                       ││
│ │ ☑ EU Formats (VAT, Phone)             ☐ Case Sensitive Matching                          ││
│ │ ☐ UK Formats (NI, Postcode)           Priority: [20] (Lower = Higher Priority)           ││
│ │                                                                                             ││
│ │ Statistics: Redacted today: 156 items | Last triggered: 2 minutes ago                     ││
│ │ [Test Pattern] [Reset to Defaults] [Apply Changes] [Cancel]                               ││
│ └─────────────────────────────────────────────────────────────────────────────────────────────┘│
│ Esc: Back to Server View | Tab: Next Field | Space: Toggle Checkbox | Enter: Apply           │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 3. Global Secrets Filter Selected

```
╭─ Watchgate Security Configuration ────────────────────────────────────────────────────────────╮
│ GLOBAL SECURITY ══════════════════════════════════════════════════════════════════════════════││
│ PII Filter      [✅ Active]  Redacting: Email, Phone, SSN                          [Configure]││
│ Secrets Filter  [✅ Active]  Blocking: API Keys, Tokens, Passwords            ← [Configure]  ││
│ Prompt Defense  [❌ Disabled]  Click to enable injection protection                [Enable]   ││
│                                                                                               ││
│ GLOBAL AUDITING ══════════════════════════════════════════════════════════════════════════════││
│ JSON Logger     [✅ Active]  logs/audit.json (2.3 MB today, 45 MB total)          [View Logs]││
│ CSV Export      [❌ Disabled]  Export audit logs to CSV format                     [Setup]    ││
│ Syslog Forward  [○ Available]  Send logs to remote syslog server                  [Setup]    ││
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────┐│
│ │ Secrets Filter Configuration (Global - Applies to All Servers)                              ││
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ││
│ │                                                                                             ││
│ │ Detection Action:                                                                           ││
│ │ ○ Redact - Replace detected secrets with [REDACTED]                                       ││
│ │ ● Block - Reject requests containing secrets                                              ││
│ │ ○ Audit Only - Log detections but don't modify                                            ││
│ │                                                                                             ││
│ │ Secret Types to Detect:                                                                    ││
│ │ ┌─ API Keys & Tokens ────────┐ ┌─ Cloud Providers ──────────┐ ┌─ Authentication ─────────┐││
│ │ │ ☑ AWS Access Keys (AKIA...)│ │ ☑ GCP Service Account Keys│ │ ☑ JWT Tokens            │││
│ │ │ ☑ AWS Secret Keys         │ │ ☑ Azure Subscription Keys │ │ ☑ OAuth Tokens          │││
│ │ │ ☑ GitHub Tokens (ghp_...) │ │ ☑ DigitalOcean Tokens     │ │ ☑ Basic Auth Headers    │││
│ │ │ ☑ GitLab Tokens           │ │ ☑ Heroku API Keys         │ │ ☑ Bearer Tokens         │││
│ │ │ ☑ Slack Tokens            │ │ ☐ Alibaba Cloud Keys      │ │ ☐ Session Cookies       │││
│ │ └─────────────────────────────┘ └────────────────────────────┘ └──────────────────────────┘││
│ │                                                                                             ││
│ │ ┌─ Database & Services ──────┐ ┌─ Encryption Keys ──────────┐                             ││
│ │ │ ☑ Database Passwords      │ │ ☑ Private Keys (PEM/RSA)  │                             ││
│ │ │ ☑ Connection Strings      │ │ ☑ SSH Private Keys        │                             ││
│ │ │ ☑ Redis Passwords         │ │ ☐ GPG Private Keys        │                             ││
│ │ │ ☑ MongoDB URIs            │ │ ☐ Certificate Private Keys│                             ││
│ │ └─────────────────────────────┘ └────────────────────────────┘                             ││
│ │                                                                                             ││
│ │ Entropy Detection:                                                                         ││
│ │ ☑ Enable High-Entropy String Detection   Min Entropy: [4.5] Min Length: [10] chars        ││
│ │                                                                                             ││
│ │ Statistics: Blocked today: 23 secrets | Last detected: 5 minutes ago                      ││
│ │ [Test Pattern] [Import Rules] [Apply Changes] [Cancel]                                    ││
│ └─────────────────────────────────────────────────────────────────────────────────────────────┘│
│ Esc: Back to Server View | Tab: Next Field | Space: Toggle Checkbox | Enter: Apply           │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 4. Tool Allowlist Selected (Server-Specific)

```
╭─ Watchgate Security Configuration ────────────────────────────────────────────────────────────╮
│ GLOBAL SECURITY ══════════════════════════════════════════════════════════════════════════════││
│ PII Filter      [✅ Active]  Redacting: Email, Phone, SSN                          [Configure]││
│ Secrets Filter  [✅ Active]  Blocking: API Keys, Tokens, Passwords                 [Configure]││
│ Prompt Defense  [❌ Disabled]  Click to enable injection protection                [Enable]   ││
│                                                                                               ││
│ GLOBAL AUDITING ══════════════════════════════════════════════════════════════════════════════││
│ JSON Logger     [✅ Active]  logs/audit.json (2.3 MB today, 45 MB total)          [View Logs]││
│ CSV Export      [❌ Disabled]  Export audit logs to CSV format                     [Setup]    ││
│ Syslog Forward  [○ Available]  Send logs to remote syslog server                  [Setup]    ││
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─ MCP Servers ──────┐ ┌─ Server Plugins ───────────┐ ┌─ Tool Allowlist Configuration ────────┐│
│ │                    │ │ filesystem plugins:        │ │ Server: filesystem                    ││
│ │ ● filesystem   ←  │ │                            │ │ ─────────────────────────────────     ││
│ │   /app/sandbox    │ │ • Tool Allowlist      ✅ ← │ │                                       ││
│ │   12 tools        │ │   Allow 4/12 tools        │ │ Access Control Mode:                 ││
│ │                    │ │                            │ │ ○ Allow All - No restrictions        ││
│ │ ○ github          │ │ • Path Security       ✅   │ │ ● Allowlist - Only allow selected    ││
│ │   Not connected   │ │   Sandbox restricted      │ │ ○ Blocklist - Block selected tools   ││
│ │   28 tools        │ │                            │ │                                       ││
│ │                    │ │ • Rate Limiting       ○   │ │ Available Tools (12):                 ││
│ │ ○ sqlite          │ │   Available to enable     │ │ ┌─ File Operations ───────────────┐  ││
│ │   Not configured  │ │                            │ │ │ ☑ read_file                    │  ││
│ │   8 tools         │ │ • Custom Headers      ○   │ │ │ ☑ write_file                   │  ││
│ │                    │ │   Available to enable     │ │ │ ☐ delete_file ⚠️ Dangerous     │  ││
│ │ ──────────────    │ │                            │ │ │ ☐ move_file                    │  ││
│ │ + Add Server       │ │ [+ Add Plugin]             │ │ │ ☐ copy_file                    │  ││
│ └────────────────────┘ └────────────────────────────┘ │ └───────────────────────────────┘  ││
│                                                        │ ┌─ Directory Operations ────────┐  ││
│                                                        │ │ ☑ list_directory              │  ││
│                                                        │ │ ☑ create_directory            │  ││
│                                                        │ │ ☐ remove_directory ⚠️         │  ││
│                                                        │ │ ☐ watch_directory             │  ││
│                                                        │ └───────────────────────────────┘  ││
│                                                        │ ┌─ System Operations ───────────┐  ││
│                                                        │ │ ☐ execute_command ⚠️ Dangerous│  ││
│                                                        │ │ ☐ get_permissions             │  ││
│                                                        │ │ ☐ set_permissions ⚠️          │  ││
│                                                        │ └───────────────────────────────┘  ││
│                                                        │                                       ││
│                                                        │ Custom Block Message:                 ││
│                                                        │ [Tool access denied by policy______] ││
│                                                        │                                       ││
│                                                        │ Summary: 4 of 12 tools allowed       ││
│                                                        │ [Safe Defaults] [Clear] [Apply]      ││
│                                                        └───────────────────────────────────────┘│
│ Connected: 1/3 | Plugins: 7 active | [Save] [Load Profile] | ↑↓ Navigate | Enter: Configure   │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 5. Path Security Selected (Filesystem Server)

```
╭─ Watchgate Security Configuration ────────────────────────────────────────────────────────────╮
│ GLOBAL SECURITY ══════════════════════════════════════════════════════════════════════════════││
│ PII Filter      [✅ Active]  Redacting: Email, Phone, SSN                          [Configure]││
│ Secrets Filter  [✅ Active]  Blocking: API Keys, Tokens, Passwords                 [Configure]││
│ Prompt Defense  [❌ Disabled]  Click to enable injection protection                [Enable]   ││
│                                                                                               ││
│ GLOBAL AUDITING ══════════════════════════════════════════════════════════════════════════════││
│ JSON Logger     [✅ Active]  logs/audit.json (2.3 MB today, 45 MB total)          [View Logs]││
│ CSV Export      [❌ Disabled]  Export audit logs to CSV format                     [Setup]    ││
│ Syslog Forward  [○ Available]  Send logs to remote syslog server                  [Setup]    ││
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─ MCP Servers ──────┐ ┌─ Server Plugins ───────────┐ ┌─ Path Security Configuration ─────────┐│
│ │                    │ │ filesystem plugins:        │ │ Server: filesystem                    ││
│ │ ● filesystem   ←  │ │                            │ │ ─────────────────────────────────     ││
│ │   /app/sandbox    │ │ • Tool Allowlist      ✅   │ │                                       ││
│ │   12 tools        │ │   Allow 4/12 tools        │ │ Path Access Control:                 ││
│ │                    │ │                            │ │ Restrict file operations to specific ││
│ │ ○ github          │ │ • Path Security       ✅ ← │ │ directories and block sensitive files││
│ │   Not connected   │ │   Sandbox restricted      │ │                                       ││
│ │   28 tools        │ │                            │ │ Allowed Paths:                        ││
│ │                    │ │ • Rate Limiting       ○   │ │ ┌─────────────────────────────────┐  ││
│ │ ○ sqlite          │ │   Available to enable     │ │ │ /app/sandbox/**                 │  ││
│ │   Not configured  │ │                            │ │ │ /shared/data/                   │  ││
│ │   8 tools         │ │ • Custom Headers      ○   │ │ │ ~/Documents/projects/           │  ││
│ │                    │ │   Available to enable     │ │ │ [+ Add Path]                    │  ││
│ │ ──────────────    │ │                            │ │ └─────────────────────────────────┘  ││
│ │ + Add Server       │ │ [+ Add Plugin]             │ │                                       ││
│ └────────────────────┘ └────────────────────────────┘ │ Blocked Patterns:                    ││
│                                                        │ ┌─────────────────────────────────┐  ││
│                                                        │ │ *.secret                        │  ││
│                                                        │ │ *.key                           │  ││
│                                                        │ │ *.pem                           │  ││
│                                                        │ │ .env*                           │  ││
│                                                        │ │ **/node_modules/**              │  ││
│                                                        │ │ **/.git/**                      │  ││
│                                                        │ │ [+ Add Pattern]                 │  ││
│                                                        │ └─────────────────────────────────┘  ││
│                                                        │                                       ││
│                                                        │ Additional Security:                  ││
│                                                        │ ☑ Block path traversal attempts      ││
│                                                        │ ☑ Prevent symlink escapes            ││
│                                                        │ ☑ Hide directory listings            ││
│                                                        │ ☐ Read-only mode                     ││
│                                                        │                                       ││
│                                                        │ [Test Path] [Apply] [Cancel]         ││
│                                                        └───────────────────────────────────────┘│
│ Connected: 1/3 | Plugins: 7 active | [Save] [Load Profile] | ↑↓ Navigate | Enter: Configure   │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 6. Prompt Injection Defense (When Enabling)

```
╭─ Watchgate Security Configuration ────────────────────────────────────────────────────────────╮
│ GLOBAL SECURITY ══════════════════════════════════════════════════════════════════════════════││
│ PII Filter      [✅ Active]  Redacting: Email, Phone, SSN                          [Configure]││
│ Secrets Filter  [✅ Active]  Blocking: API Keys, Tokens, Passwords                 [Configure]││
│ Prompt Defense  [❌ Disabled]  Click to enable injection protection            ← [Enable]     ││
│                                                                                               ││
│ GLOBAL AUDITING ══════════════════════════════════════════════════════════════════════════════││
│ JSON Logger     [✅ Active]  logs/audit.json (2.3 MB today, 45 MB total)          [View Logs]││
│ CSV Export      [❌ Disabled]  Export audit logs to CSV format                     [Setup]    ││
│ Syslog Forward  [○ Available]  Send logs to remote syslog server                  [Setup]    ││
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────┐│
│ │ Prompt Injection Defense Configuration (Global - Applies to All Servers)                    ││
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ││
│ │                                                                                             ││
│ │ ⚠️ This plugin protects against attempts to manipulate AI behavior through prompt injection ││
│ │                                                                                             ││
│ │ Detection Action:                                                                           ││
│ │ ● Block - Reject suspicious requests immediately                                           ││
│ │ ○ Audit Only - Log detections but allow through (testing mode)                            ││
│ │                                                                                             ││
│ │ Detection Sensitivity:                                                                      ││
│ │ ○ Standard - Balance between security and false positives                                 ││
│ │ ● Strict - Maximum protection, may have more false positives                              ││
│ │                                                                                             ││
│ │ Detection Methods:                                                                          ││
│ │ ┌─ Attack Patterns ──────────┐ ┌─ Behavioral Detection ─────┐ ┌─ Content Analysis ──────┐││
│ │ │ ☑ Delimiter Injection      │ │ ☑ Role Manipulation         │ │ ☑ Command Patterns      │││
│ │ │   (````, |||, <<<)         │ │   ("ignore previous")       │ │   (execute, run, eval)  │││
│ │ │ ☑ Context Breaking         │ │ ☑ System Prompt Override    │ │ ☑ Code Injection        │││
│ │ │   (END, STOP, IGNORE)      │ │   ("you are now")           │ │   (import, require)     │││
│ │ │ ☑ Encoding Bypass          │ │ ☑ Instruction Hijacking     │ │ ☑ Data Exfiltration     │││
│ │ │   (base64, unicode)        │ │   ("new instructions")      │ │   (send, post, leak)    │││
│ │ └─────────────────────────────┘ └──────────────────────────────┘ └────────────────────────┘││
│ │                                                                                             ││
│ │ Custom Patterns:                                                                            ││
│ │ ┌───────────────────────────────────────────────────────────────────────────────────┐     ││
│ │ │ Pattern Name          | Regex Pattern                     | Action                 │     ││
│ │ │ ─────────────────────────────────────────────────────────────────────────────────│     ││
│ │ │ Custom Delimiter      | \[\[SYSTEM\]\].*\[\[/SYSTEM\]\]  | Block                  │     ││
│ │ │ [+ Add Custom Pattern]                                                            │     ││
│ │ └───────────────────────────────────────────────────────────────────────────────────┘     ││
│ │                                                                                             ││
│ │ Exemptions:                                                                                 ││
│ │ Tools to exclude from checking: [None selected] [Select Tools...]                          ││
│ │                                                                                             ││
│ │ [Enable Protection] [Configure Later] [Cancel]                                             ││
│ └─────────────────────────────────────────────────────────────────────────────────────────────┘│
│ Esc: Cancel | Tab: Next Field | Space: Toggle | Enter: Enable                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Design Notes

### Navigation Flow
1. **Global plugins**: Click any global security/auditing item → full-screen configuration
2. **Server plugins**: Select server → see plugins → select plugin → detailed configuration in right pane
3. **Escape key**: Always returns to main server view
4. **Tab navigation**: Cycles through form fields in configuration views

### Visual Indicators
- **●** Connected/Active
- **○** Available/Disconnected  
- **❌** Disabled
- **✅** Enabled/Active
- **←** Currently selected
- **⚠️** Dangerous/Warning

### Key Features
- Global plugins always visible at top
- Server context preserved during plugin configuration
- Clear scope indication (Global vs Server-specific)
- Consistent configuration patterns across all plugins
- Status information and statistics where relevant