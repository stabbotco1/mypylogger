# Kiro FAQ

This document contains frequently asked questions about using Kiro IDE and common issues encountered during development.

## Kiro IDE Components Overview

### Chat Interface
The **Kiro Chat** is the conversational AI interface where you interact with your AI pair programming partner. It provides real-time assistance, code analysis, implementation guidance, and can execute commands and modify files. The chat maintains context about your project and can see your open files, understand your codebase structure, and help with complex development tasks.

### Editor
The **Kiro Editor** is where you write and edit your code files. It integrates seamlessly with the AI chat, allowing the AI to make direct modifications to your files when requested. The editor supports syntax highlighting, code completion, and real-time collaboration with the AI assistant. Files modified by the AI are automatically formatted and can be reviewed before acceptance.

### File Explorer
The **Kiro File Explorer** provides navigation through your project structure. It allows you to browse directories, open files, and manage your project organization. The AI can see which files you have open and can reference specific files or folders when providing assistance. It integrates with version control systems and shows file status indicators.

### Agent Hooks
**Agent Hooks** are automated workflows that trigger AI actions based on specific events or user interactions. Examples include:
- Automatically running tests when code files are saved
- Updating translation files when strings change
- Performing code reviews on file modifications
- Running linting or formatting on demand
Hooks can be configured through the Agent Hooks section in the explorer view or via the command palette.

### Spec System
The **Spec System** provides structured feature development through formalized requirements, design, and implementation processes. It includes:
- **Requirements documents** with EARS-formatted acceptance criteria
- **Design documents** outlining architecture and implementation approach
- **Task breakdowns** with discrete, testable implementation steps
- **Incremental development** with control and feedback at each stage
Specs allow complex features to be built systematically with proper documentation and verification.

## Getting Started with Kiro

*Information accurate as of September 24, 2025*

### Primary Resources

Based on current research, the following are the accessible resources for getting started with Kiro IDE:

**Official Website:**
- **kiro.dev** - The main accessible Kiro website with documentation and resources

**Development Resources:**
- **GitHub Organization**: https://github.com/kirolabs - Contains Kiro-related repositories and development resources

### Installation and Setup

**Note**: As of September 2025, some Kiro infrastructure appears to be in transition. The following domains experienced connectivity issues during research:
- kiro.ai (connection timeouts)
- docs.kiro.ai (DNS resolution issues)
- kirolabs.com (SSL certificate problems)

**Recommended Approach:**
1. **Visit kiro.dev** for the most current installation instructions
2. **Check github.com/kirolabs** for:
   - Latest releases and downloads
   - Installation guides in repository README files
   - Community discussions and issues
   - Development documentation

### Package Managers

**NPM**: A package named "kiro" exists on npm (version 1.0.0), but appears to be unrelated to Kiro IDE based on its minimal description ("a simple project"). Verify this is the correct package before installing.

**PyPI**: No Kiro IDE package found on Python Package Index as of September 2025.

### Getting Help

**Primary Channels:**
- GitHub Issues at repositories under github.com/kirolabs
- Documentation at kiro.dev
- Community discussions in Kiro GitHub repositories

### Important Notes

- **Infrastructure Status**: Some official Kiro domains were inaccessible during September 2025 research, suggesting possible infrastructure updates or regional restrictions
- **Verification Recommended**: Always verify you're downloading from official sources due to the mixed accessibility of Kiro domains
- **Community Resources**: The GitHub organization (kirolabs) appears to be the most reliable source for current information

*This information was compiled through automated research on September 24, 2025. Due to the dynamic nature of web resources, some links or availability may have changed since this research was conducted.*

## General Kiro Usage

### Q: What is this Kiro window referred to as?
**A:** This interface is called the **Kiro Chat** - the conversational interface for AI pair programming assistance, part of the broader Kiro IDE ecosystem that includes the chat, editor, file explorer, agent hooks, and spec system.

### Q: What methods can be used within the Kiro UI to open this window?
**A:** Multiple methods: keyboard shortcuts (often Cmd+K), menu bar options, sidebar chat icon, command palette ("Open Chat"), right-click context menus, or status bar indicators. The exact methods depend on your Kiro IDE configuration.

## Known Issues

### Q: Why does Kiro get stuck in "Working..." state after CLI commands, and how do I fix it?
**A:** This is a known callback/response integration issue where:
- CLI tool execution succeeds and produces correct output
- The callback mechanism fails to return results to the chat interface
- Kiro remains stuck in "Working..." state indefinitely
- **Workaround**: Copy the command output from your terminal/console and paste it into the chat window. This will "unstick" Kiro and allow it to continue as if it received the results normally.
- **Frequency**: This occurs always or more than 95% of the time with CLI operations
- **Impact**: Affects basic AI-tool integration workflow but doesn't prevent successful completion of tasks when workaround is applied

---

## 🚨 IMPORTANT REMINDER 🚨

**FOLLOW UP REQUIRED**: Create a support ticket for the CLI callback integration issue described above. This is a systematic bug that significantly impacts user experience and should be reported to the Kiro development team.

**Issue Details for Support Ticket:**
- **Problem**: CLI tool execution callback mechanism fails consistently
- **Symptoms**: Kiro stuck in "Working..." state after successful CLI commands
- **Frequency**: 95%+ of CLI operations affected
- **Workaround**: Manual copy-paste of console output into chat
- **Impact**: Core functionality issue affecting AI-tool integration workflow
- **Evidence**: MCP tool failures visible in UI, systematic callback timeouts

**Next Steps:**
1. Find Kiro's official support/issue reporting channel
2. Create detailed bug report with above information
3. Include screenshots of the "Working..." state and MCP tool failures
4. Reference this FAQ for additional context
