# Feature Control and Exclusions

## Purpose

This document defines strict feature control policies for mypylogger v0.2.5 to maintain focus, simplicity, and maintainability.

## Feature Acceptance Criteria

**Before adding ANY feature, it must meet ALL these criteria:**

1. ✅ **Core Mission Alignment**
   - Directly supports JSON logging functionality
   - Not achievable via configuration or external tools

2. ✅ **User Impact**
   - Used by >50% of expected users
   - Solves a real pain point, not a "nice to have"

3. ✅ **Simplicity Test**
   - Adds <100 lines of code
   - Does not require new dependencies
   - Does not complicate the API

4. ✅ **Maintenance Burden**
   - Easy to test and verify
   - Does not create edge cases
   - Will not require frequent updates

5. ✅ **External Tool Check**
   - Cannot be solved with jq, logrotate, or log aggregation tools
   - Not already provided by Python stdlib logging

**DEFAULT ANSWER: NO**

When in doubt, features should be rejected. Users can always extend or fork if they need specialized functionality.

## Critical Agent Instructions

**MANDATORY for all AI agents working on this project:**

### Before Implementing ANY Feature
1. **Check exclusion criteria** - Does it meet ALL acceptance criteria above?
2. **Challenge the request** - Ask: "Can external tools solve this?"
3. **Verify scope** - Is this explicitly requested in current specs?
4. **Default to NO** - Unless overwhelming evidence supports the feature

### When User Requests New Features
**Agent should ask:**
1. "Is this feature in the current specs?"
2. "Does this align with the core mission (JSON logging)?"
3. "Can this be achieved with configuration or external tools?"
4. "Should we add this to specs first, or is it out of scope?"

### Feature Request Response Template
```
Thank you for the suggestion! However, [FEATURE] would need to meet our strict feature acceptance criteria:

- Core mission alignment (JSON logging only)
- Used by >50% of users
- <100 lines of code
- No new dependencies
- Cannot be solved by external tools

Instead, I recommend: [ALTERNATIVE SOLUTIONS]

This keeps mypylogger focused on its core mission. Would you like help implementing one of these alternatives?
```

## Explicitly Excluded Features

### ❌ Log Rotation
**Why excluded:** System tools (logrotate, CloudWatch) handle this better
**Alternative:** Configure logrotate, use CloudWatch Logs, or container log drivers

### ❌ Multiple Output Formats (XML, CSV, YAML)
**Why excluded:** JSON-only is our core value proposition
**Alternative:** Use Python's stdlib logging with custom formatters for other formats

### ❌ Async/Awaitable Logging
**Why excluded:** Python's stdlib logging is thread-safe, adds complexity
**Alternative:** Use `logging.handlers.QueueHandler` for async-like behavior

### ❌ Log Sampling/Rate Limiting
**Why excluded:** Should be done at log aggregation layer
**Alternative:** Configure sampling at Splunk/Datadog/CloudWatch level

### ❌ Structured Context Management (bind/contextualize)
**Why excluded:** Adds complexity, achievable with `extra` parameter
**Alternative:** Use `logger.info("msg", extra={"key": "val"})`

### ❌ Custom Sinks/Handlers Beyond File+Stdout
**Why excluded:** Stdlib logging has 20+ handler types already
**Alternative:** Add stdlib handlers directly: `logger.addHandler(handler)`

### ❌ Performance Benchmarking Tools
**Why excluded:** "Fast enough" is sufficient, not "fastest possible"
**Alternative:** Use `cProfile` or `line_profiler` for performance analysis

### ❌ Color/Emoji Support in JSON Output
**Why excluded:** JSON logs are for machines, not terminal pretty-printing
**Alternative:** Use loguru or rich for console output, jq/Splunk for JSON viewing

### ❌ Configuration File Support (YAML/TOML/JSON)
**Why excluded:** Environment variables are sufficient and universal
**Alternative:** Load config files into environment variables in application code

### ❌ Log Compression/Encryption
**Why excluded:** Should be handled at infrastructure level
**Alternative:** Use encrypted file systems, TLS for shipping, platform encryption

## Scope Boundaries

### ✅ IN SCOPE (Core Mission)
- JSON logging with consistent format
- Environment-driven configuration
- File and stdout output
- Standard Python logging integration
- Error handling and graceful degradation

### ❌ OUT OF SCOPE (External Tools Handle Better)
- Log rotation and archival
- Log analysis and search
- Performance monitoring and alerting
- Distributed tracing integration
- Log aggregation and shipping
- Pretty-printing for terminals
- Multi-format output

## Maintaining Focus

### Project Philosophy
> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."

**We optimize for:**
- Code that is easy to read and understand
- Behavior that is obvious and predictable
- Defaults that work for 90% of users
- Minimal maintenance burden

**We explicitly reject:**
- Clever abstractions that hide complexity
- Features that serve <10% of users
- Configuration options for everything
- "Enterprise" features that add bloat

### Success Through Constraints
- **Small codebase:** <500 lines keeps it maintainable
- **Single dependency:** Reduces complexity and security surface
- **JSON only:** Eliminates format debates and complexity
- **Environment config:** Universal, simple, no file parsing needed

## Review and Updates

### When to Update This Document
- New feature categories emerge that should be excluded
- Users frequently request the same excluded feature
- New tools make previously excluded features obsolete

### Review Schedule
- After each major phase completion
- When receiving repeated feature requests
- Annually (minimum)

This document is critical for maintaining mypylogger's focus and preventing scope creep.