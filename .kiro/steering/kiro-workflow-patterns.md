---
inclusion: always
---

# Kiro Workflow Patterns and Best Practices

## Purpose
This document captures reusable patterns for efficiently using Kiro across projects, ensuring consistent, incremental, and verifiable development workflows.

## Core Kiro Workflow Pattern

### 1. Spec-Driven Development Cycle
- **Requirements First**: Always start with clear, EARS-formatted requirements
- **Design Before Code**: Create comprehensive design documents before implementation
- **Task Breakdown**: Convert design into discrete, testable implementation tasks
- **One Task at a Time**: Execute tasks sequentially, verifying each step

### 2. Incremental Implementation Strategy
- **TDD Foundation**: Start with failing tests, implement minimal passing code
- **Stub-First Approach**: Create working stubs for all components before full implementation
- **Continuous Verification**: Ensure code compiles and basic functionality works after each task
- **No Breaking Changes**: Maintain working state throughout development

### 3. Steering Document Hierarchy
- **Generic Patterns**: Workflow patterns applicable across projects (this document)
- **Technology Standards**: Language/framework-specific conventions (e.g., Python standards)
- **Project-Specific Rules**: Unique requirements for current project
- **Discovery Updates**: Capture lessons learned during implementation

## Task Execution Best Practices

### Before Starting Any Task
1. Read requirements, design, and task details
2. Understand dependencies and prerequisites
3. Write failing tests first (TDD approach)
4. Implement minimal solution to pass tests

### During Task Execution
- Focus on single task objective only
- Reference specific requirements mentioned in task
- Maintain code quality standards from steering documents
- Document any deviations or discoveries

### After Task Completion
- Verify all tests pass
- Check that code can be imported/executed
- Update documentation if needed
- Stop and wait for user review before proceeding

## Steering Document Management

### When to Update Steering Documents
- **During Discovery**: When implementation reveals better approaches
- **Pattern Recognition**: When repeating similar solutions across tasks
- **Error Prevention**: When encountering common mistakes or pitfalls
- **Workflow Optimization**: When finding more efficient development patterns

### Types of Updates
- **Generic Patterns**: Add to workflow pattern documents (like this one)
- **Technology Standards**: Update language/framework-specific documents
- **Project Rules**: Add to project-specific steering documents
- **Anti-Patterns**: Document what doesn't work well

## Reusable Project Patterns

### Python Project Structure
```
project/
├── .kiro/
│   ├── specs/           # Requirements, design, tasks
│   └── steering/        # Workflow patterns, standards, project rules
├── src/package_name/    # Main package code
├── tests/              # Test suite
├── pyproject.toml      # Dependencies and build config
└── README.md           # Project overview
```

### Common Task Patterns
1. **Foundation Setup**: Project structure, dependencies, basic imports
2. **Core Interfaces**: Define main APIs with stubs and tests
3. **Configuration**: Environment-driven settings with validation
4. **Implementation**: Incremental feature development with TDD
5. **Integration**: End-to-end testing and examples
6. **Documentation**: Usage examples and API documentation

## Discovery and Learning Integration

### Capture Lessons Learned
- Update steering documents with discovered patterns
- Document what worked well vs. what didn't
- Add specific examples of successful approaches
- Note common pitfalls and how to avoid them

### Iterative Improvement
- Review steering documents after each project phase
- Refine patterns based on implementation experience
- Share successful patterns across projects
- Build library of reusable approaches

## Quality Gates

### Before Moving to Next Task
- [ ] All tests pass
- [ ] Code compiles and can be imported
- [ ] Basic functionality works as expected
- [ ] Steering document compliance verified
- [ ] No breaking changes introduced

### Before Project Completion
- [ ] All requirements implemented and tested
- [ ] Documentation complete and accurate
- [ ] Steering documents updated with lessons learned
- [ ] Reusable patterns documented for future projects