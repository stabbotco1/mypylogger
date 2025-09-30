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

## Documentation as a Feature Deliverable

### Documentation Philosophy
Documentation is a **first-class deliverable**, not an afterthought. In the age of AI assistance, comprehensive, high-quality documentation is achievable and provides immense value:

- **User Adoption**: Great documentation drives adoption and reduces support burden
- **Professional Credibility**: Quality documentation signals professional software development
- **Knowledge Preservation**: Documentation captures decisions, rationale, and context
- **Onboarding Acceleration**: New contributors can become productive quickly
- **Maintenance Efficiency**: Future development is faster with clear documentation
- **Competitive Advantage**: Well-documented projects stand out in the ecosystem

### Documentation as Product Strategy
Treat documentation with the same rigor as code:

#### Documentation Requirements
- **User-Focused**: Written from the user's perspective, not the developer's
- **Comprehensive Coverage**: Installation, usage, troubleshooting, and advanced scenarios
- **Maintained Currency**: Updated with every feature change or architectural decision
- **Quality Assurance**: Reviewed, tested, and validated like code
- **Accessibility**: Clear language, good structure, and multiple learning paths

#### Documentation Deliverables
Every project should include these documentation deliverables:

1. **README.md**: Project overview, quick start, and key differentiators
2. **Installation Guide**: Step-by-step setup with troubleshooting
3. **Usage Documentation**: Examples from basic to advanced use cases
4. **API Documentation**: Complete reference with examples
5. **Architecture Documentation**: Design decisions and system overview
6. **Contributing Guide**: How others can contribute effectively
7. **Security Documentation**: Security model and best practices
8. **Troubleshooting Guide**: Common issues and solutions

#### Documentation Quality Standards
- **Accuracy**: All examples must work and be tested
- **Completeness**: Cover all major use cases and edge cases
- **Clarity**: Use clear language and logical organization
- **Visual Appeal**: Proper formatting, diagrams where helpful
- **Discoverability**: Easy navigation and cross-linking
- **Maintainability**: Structured for easy updates

### AI-Enhanced Documentation Process

#### Leverage AI for Documentation Excellence
With AI assistance, documentation quality can be dramatically improved:

- **Content Generation**: AI can create comprehensive first drafts
- **Example Creation**: Generate realistic, working code examples
- **Structure Optimization**: Organize information for maximum clarity
- **Cross-Referencing**: Create interconnected documentation networks
- **Quality Review**: AI can identify gaps and inconsistencies
- **Multi-Format Output**: Generate docs for different audiences and formats

#### Documentation Workflow Integration
- **Concurrent Development**: Write documentation alongside code, not after
- **Review Process**: Include documentation review in all pull requests
- **Testing**: Validate that all documented examples actually work
- **User Feedback**: Incorporate user feedback into documentation improvements
- **Metrics**: Track documentation usage and effectiveness

### Documentation Task Planning

#### Early Project Phase
- Define documentation requirements as part of initial planning
- Establish documentation standards and templates
- Set up documentation infrastructure and tooling
- Create documentation outline and structure

#### During Development
- Update documentation with each feature implementation
- Create examples and tutorials as features are built
- Document design decisions and architectural choices
- Maintain accuracy between code and documentation

#### Project Completion Phase
- **Final Documentation Review**: Comprehensive review and cleanup
- **User Journey Testing**: Validate complete user workflows
- **Gap Analysis**: Identify and fill documentation gaps
- **Polish and Refinement**: Professional presentation and formatting
- **Publication Strategy**: How and where documentation will be accessed

### Documentation Success Metrics

#### Quantitative Measures
- **Coverage**: Percentage of features documented
- **Accuracy**: Percentage of examples that work correctly
- **Completeness**: All user journeys documented
- **Freshness**: Documentation updated within X days of code changes

#### Qualitative Measures
- **User Feedback**: Positive feedback on documentation quality
- **Adoption Rate**: Faster user onboarding and feature adoption
- **Support Reduction**: Fewer support requests due to clear documentation
- **Contributor Onboarding**: New contributors can start quickly

## Quality Gates

### Before Moving to Next Task
- [ ] **Complete test suite passes** - Run `make test-complete-fast` for verification
- [ ] **Coverage maintained** - ≥90% test coverage requirement met
- [ ] **No regressions introduced** - All existing functionality intact
- [ ] **Quality gates pass** - Code formatting, linting, type checking, security
- [ ] **Documentation updated** - Any new features or changes documented
- [ ] **Performance validated** - Run `make test-complete-performance` for critical changes

**Quick Verification Command**: `make test-complete-fast`

### Before Project Completion
- [ ] **Complete test suite passes** - Run `make test-complete-performance` for full validation
- [ ] **All requirements implemented and tested** - Comprehensive verification complete
- [ ] **Documentation deliverables complete and reviewed**
- [ ] **All examples tested and working**
- [ ] **User journey documentation validated**
- [ ] **Performance benchmarks meet requirements** - <1ms latency, >10K logs/sec
- [ ] **Security scans clean** - No vulnerabilities detected
- [ ] **Package builds successfully** - Ready for distribution
- [ ] Steering documents updated with lessons learned
- [ ] Reusable patterns documented for future projects
- [ ] **Final documentation review and polish completed**

**Final Verification Command**: `make test-complete-performance`