---
inclusion: always
---

# Feature Control and Exclusions

This document defines strict feature control policies for mypylogger v0.2.7 to maintain focus, simplicity, and maintainability.

## Feature Acceptance Criteria

**CRITICAL**: Default answer is NO. Features must meet ALL criteria:

1. **Core Mission**: Directly supports JSON logging (not achievable via config/external tools)
2. **User Impact**: Used by >50% of users, solves real pain point
3. **Simplicity**: <100 lines of code, no new dependencies, simple API
4. **Maintenance**: Easy to test, no edge cases, minimal future updates
5. **External Tools**: Cannot be solved by jq, logrotate, or stdlib logging

When in doubt, reject the feature. Users can extend or fork for specialized needs.

## AI Agent Protocol

**MANDATORY**: Before implementing ANY feature:

1. **Verify specs**: Is this explicitly requested in current specifications?
2. **Check criteria**: Does it meet ALL 5 acceptance criteria above?
3. **Challenge scope**: Can external tools solve this instead?
4. **Default NO**: Reject unless overwhelming evidence supports inclusion

### Feature Request Response
When users request new features outside specs:

```
This feature isn't in current specs and would need to meet strict criteria:
- Core JSON logging mission alignment
- Used by >50% of users  
- <100 lines, no dependencies
- Cannot be solved externally

Alternative: [suggest external tool/config approach]

Should we discuss adding this to specs, or would the alternative work?
```

## Explicitly Excluded Features

| Feature | Why Excluded | Alternative |
|---------|--------------|-------------|
| **Log Rotation** | System tools handle better | logrotate, CloudWatch, container drivers |
| **Multiple Formats** (XML, CSV) | JSON-only core value | stdlib logging + custom formatters |
| **Async Logging** | Adds complexity, stdlib is thread-safe | `logging.handlers.QueueHandler` |
| **Rate Limiting** | Aggregation layer responsibility | Configure at Splunk/Datadog/CloudWatch |
| **Context Management** | Achievable with `extra` | `logger.info("msg", extra={"key": "val"})` |
| **Custom Handlers** | Stdlib has 20+ types | Add handlers: `logger.addHandler(handler)` |
| **Performance Tools** | "Fast enough" philosophy | `cProfile`, `line_profiler` |
| **Colors/Emojis** | JSON for machines, not terminals | loguru/rich for console, jq for viewing |
| **Config Files** | Environment vars sufficient | Load configs into env vars in app code |
| **Compression/Encryption** | Infrastructure responsibility | Encrypted filesystems, TLS, platform encryption |

## Scope Boundaries

**✅ IN SCOPE** (Core Mission):
- JSON logging with consistent format
- Environment-driven configuration  
- File and stdout output
- Standard Python logging integration
- Error handling and graceful degradation

**❌ OUT OF SCOPE** (External Tools Handle Better):
- Log rotation, archival, analysis, search
- Performance monitoring, alerting, distributed tracing
- Log aggregation, shipping, pretty-printing
- Multi-format output, terminal colors

## Core Philosophy

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."

**Optimize for:**
- Easy to read and understand code
- Obvious and predictable behavior  
- Defaults that work for 90% of users
- Minimal maintenance burden

**Explicitly reject:**
- Clever abstractions hiding complexity
- Features serving <10% of users
- Configuration options for everything
- "Enterprise" bloat features

## Success Constraints

- **<500 lines**: Maintainable codebase size
- **Single dependency**: Minimal complexity/security surface  
- **JSON only**: No format debates or complexity
- **Environment config**: Universal, simple, no file parsing

## Document Maintenance

**Update when:**
- New excluded feature categories emerge
- Repeated user requests for same excluded feature
- New tools make exclusions obsolete

**Review schedule:** After major phases, repeated requests, annually minimum