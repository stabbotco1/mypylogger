## Setup Flow for Kiro with MCP (Documented Operations)

This section captures the sequence of steps we performed to get Kiro working with MCP, so it can be repeated or optimized later.

1. **Initial Kiro Setup**
   - Installed and launched Kiro.
   - Created a new project folder (`kp_logger`).
   - Added starter spec documents (`requirements.md`, `design.md`, etc.).
   - Verified `.gitignore` and `kiro_instructions.md` were present.

2. **MCP Initialization**
   - Observed error: *“Cannot enable MCP in an untrusted workspace.”*
   - Opened Kiro UI → **MCP Servers** panel showed “Enable MCP.”
   - Created and edited `.kiro/settings/mcp.json` to define an MCP server (`fetch`).

3. **Dependency Installation**
   - MCP server required `uvx` (runner for Python packages).
   - Error encountered: *“Failed to connect … spawn uvx ENOENT.”*
   - Installed `uv` via Homebrew (`brew install uv`).
   - Verified installation with `uvx --version`.

4. **MCP Server Configuration**
   - Updated `mcp.json`:
     ```json
     {
       "mcpServers": {
         "fetch": {
           "command": "uvx",
           "args": ["mcp-server-fetch"],
           "env": {},
           "disabled": false,
           "autoApprove": []
         }
       }
     }
     ```
   - Restarted Kiro and confirmed MCP panel listed `fetch`.

5. **Verification**
   - Opened Command Palette (`Cmd+Shift+P`) → MCP commands available.
   - MCP Servers panel showed: `fetch Connected (1 tool)`.
   - Tool description: *“Fetches a URL from the internet …”*
   - Successful baseline connectivity confirmed.

---

### Notes for Future Optimization
- Automate installation of `uv` and MCP servers in bootstrap script.
- Maintain a template `mcp.json` for new projects.
- Record test prompts (e.g., using `fetch` to retrieve a URL) as part of validation checklist.
