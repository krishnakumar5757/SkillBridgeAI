# AGENTS.md — SkillBridge AI

These are the project-specific instructions for all OpenCode agents working on SkillBridge AI.

The global OpenCode `AGENTS.md` remains applicable. These instructions add
SkillBridge-specific requirements and constraints.

The project's functional source of truth is:

```text
PROJECT_SPEC.md
```

All agents must read and follow `PROJECT_SPEC.md` before making significant
project decisions or implementation changes.

---

# 1. Project Identity

Project:

**SkillBridge AI — Intelligent Skill Gap and Career Readiness Assessment System**

Primary objective:

Build an AI-based platform that analyzes a student's current skills,
compares them against a selected career role, identifies skill gaps,
generates a personalized learning roadmap, tracks learning progress, and
determines career readiness.

The project consists of exactly four major functional modules.

---

# 2. Source of Truth

Agents must treat the following hierarchy as authoritative:

```text
Global AGENTS.md
        ↓
Project AGENTS.md
        ↓
PROJECT_SPEC.md
        ↓
Module-specific documentation
        ↓
Implementation
```

If an implementation decision conflicts with `PROJECT_SPEC.md`, stop and
identify the conflict before proceeding.

Do not silently change the project scope.

If a requirement appears ambiguous, identify the ambiguity and ask the
orchestrator for clarification when necessary.

---

# 3. Locked Project Scope

SkillBridge currently contains exactly four major modules:

```text
Module 1 → Student Intelligence
Module 2 → Career Intelligence
Module 3 → Learning Intelligence
Module 4 → Career Readiness
```

The two required syllabus algorithms are:

```text
A* Search
Forward Chaining
```

Their responsibilities are locked:

```text
A* Search
→ Module 3
→ Personalized Learning Roadmap

Forward Chaining
→ Module 4
→ Career Readiness Reasoning
```

Do not introduce another primary syllabus algorithm unless the project
scope is explicitly changed.

---

# 4. Explicitly Removed Feature

The following feature is OUT OF SCOPE:

**AI Role-Specific Assessment**

Agents must not implement:

* AI-generated technical examinations
* AI-generated conceptual examinations
* AI-generated scenario-based examinations
* AI-generated assessment papers
* Automated question generation
* CSP/backtracking assessment generation
* Assessment-based readiness scoring

Do not reintroduce this feature because it appears useful or common in
career platforms.

---

# 5. Four-Module Architecture

## Module 1 — Student Intelligence

Location:

```text
modules/module-1-student-intelligence/
```

Primary responsibilities:

* Student profile
* Academic information
* Interests
* Projects
* Resume upload
* Resume processing
* NLP processing
* Skill extraction
* Skill normalization
* Student skill profile

Primary output:

```text
Student Skill Profile
```

Module 1 must provide the structured student information required by
Module 2.

---

## Module 2 — Career Intelligence

Location:

```text
modules/module-2-career-intelligence/
```

Primary responsibilities:

* Career role selection
* Career role information
* Role skill requirements
* Skill matching
* Skill gap calculation
* Strong skill identification
* Weak skill identification
* Missing skill identification
* Skill prioritization

Primary output:

```text
Skill Gap Report
```

Module 2 consumes the Student Skill Profile produced by Module 1.

---

## Module 3 — Learning Intelligence

Location:

```text
modules/module-3-learning-intelligence/
```

Primary responsibilities:

* Skill dependency graph
* Skill relationships
* Learning-path generation
* A* Search
* Personalized roadmap
* Roadmap progress representation

### A* requirement

A* Search must be a genuine implementation.

The implementation must contain the necessary components such as:

* Graph representation
* Nodes
* Edges
* Cost function
* Heuristic
* Search process
* Path reconstruction

Do not create a fake A* implementation that simply returns a
predefined roadmap.

The generated roadmap must depend on the student's current skill state
and the target role's required skills.

---

## Module 4 — Career Readiness

Location:

```text
modules/module-4-career-readiness/
```

Primary responsibilities:

* Learning progress
* Skill progress
* Readiness scoring
* Facts
* Rules
* Forward Chaining
* Readiness classification
* Readiness explanation

### Forward Chaining requirement

Forward Chaining must be implemented as a genuine inference process.

The implementation should contain appropriate representations for:

* Facts
* Rules
* Rule evaluation
* Inference
* Final conclusions

The readiness classification must be explainable.

Primary classifications:

```text
Role Ready
Nearly Ready
Needs Improvement
```

---

# 6. Module Dependencies

Modules must follow this dependency flow:

```text
Module 1
Student Intelligence
      ↓
Module 2
Career Intelligence
      ↓
Module 3
Learning Intelligence
      ↓
Module 4
Career Readiness
```

The intended end-to-end data flow is:

```text
Student Data
    ↓
Resume / NLP Analysis
    ↓
Student Skill Profile
    ↓
Target Career Role
    ↓
Skill Gap Analysis
    ↓
A* Search
    ↓
Personalized Learning Roadmap
    ↓
Learning Progress
    ↓
Forward Chaining
    ↓
Career Readiness Result
```

Avoid circular dependencies between modules.

Do not allow one module to directly manipulate another module's internal
implementation when a defined interface/API/service boundary should be
used.

---

# 7. Agent Responsibilities

SkillBridge uses six development agents.

## 7.1 krishna-dev — Orchestrator

`krishna-dev` is the primary project orchestrator.

Responsibilities:

* Understand the project specification
* Coordinate the other agents
* Break work into appropriate tasks
* Assign work to specialist agents
* Maintain module boundaries
* Integrate completed work
* Resolve implementation conflicts
* Track module completion
* Ensure tests and reviews occur
* Ensure the project remains within scope

`krishna-dev` must not blindly delegate the entire project and assume the
other agents will automatically maintain consistency.

Before significant implementation:

```text
Read PROJECT_SPEC.md
↓
Inspect current project state
↓
Determine affected module
↓
Delegate where appropriate
↓
Implement/integrate
↓
Test
↓
Review
```

---

## 7.2 architect — Architecture Specialist

Responsibilities:

* System architecture
* Technology decisions
* Database architecture
* API architecture
* Module boundaries
* Data flow
* Integration design
* Architectural documentation

The architect should prioritize simplicity and project scope.

Do not introduce enterprise-level complexity without evidence that the
project requires it.

The architect should document significant decisions.

---

## 7.3 reviewer — Code and Architecture Reviewer

Responsibilities:

* Code correctness
* Maintainability
* Architecture consistency
* Project-spec compliance
* Detection of unnecessary complexity
* Detection of duplicated logic
* Algorithm implementation review
* API/interface review

For Module 3, the reviewer must verify that A* is genuinely implemented.

For Module 4, the reviewer must verify that Forward Chaining is genuinely
implemented.

The reviewer should identify problems rather than silently rewriting large
parts of the project.

---

## 7.4 security — Security Specialist

Responsibilities:

* Authentication
* Authorization
* Input validation
* Resume/file-upload security
* API security
* Sensitive student data handling
* Secrets management
* Dependency security
* Common application security risks

Security requirements must be proportional to the actual application.

Never expose secrets in source code.

Never commit real credentials, API keys, tokens, or private configuration.

---

## 7.5 debugger — Debugging Specialist

Responsibilities:

* Diagnose bugs
* Reproduce failures
* Identify root causes
* Fix implementation problems
* Verify fixes
* Avoid introducing unrelated changes

When debugging:

```text
Reproduce
↓
Investigate
↓
Identify root cause
↓
Apply focused fix
↓
Run relevant tests
↓
Verify regression safety
```

Do not hide errors merely to make tests pass.

---

## 7.6 tester — Testing Specialist

Responsibilities:

* Unit testing
* Integration testing
* End-to-end testing
* Edge-case testing
* Algorithm testing
* Regression testing

The tester must ensure that core SkillBridge functionality is verifiable.

Important algorithm tests include:

### A*

* Valid path
* No available path
* Different starting skill states
* Different target requirements
* Dependency handling
* Path correctness
* Cost/heuristic behavior

### Forward Chaining

* Rule triggering
* Multiple rule chains
* Conflicting/non-triggering conditions
* Final classification
* Edge cases around thresholds
* Explainability of conclusions

---

# 8. Weekly Development Workflow

The project is developed in four major weekly milestones.

```text
Week 1 → Module 1
Week 2 → Module 2
Week 3 → Module 3
Week 4 → Module 4
```

Each week ends with a mentor review.

---

# 9. Module Completion Gate

A module must not be considered complete merely because its code exists.

Before mentor review, the module should reach:

```text
IMPLEMENTED
    ↓
TESTED
    ↓
REVIEWED
    ↓
SECURITY CHECKED
    ↓
INTEGRATED
    ↓
DOCUMENTED
    ↓
DEMO_READY
```

The next module should not begin its main implementation until the
previous module reaches `DEMO_READY`, unless the orchestrator explicitly
determines that a dependency requires parallel preparation.

---

# 10. Weekly Deliverables

## Week 1 — Module 1

Expected demonstration:

```text
Create Student Profile
        ↓
Upload Resume
        ↓
Process Resume
        ↓
Extract Skills
        ↓
Display Student Skill Profile
```

---

## Week 2 — Module 2

Expected demonstration:

```text
Select Career Role
        ↓
Load Role Requirements
        ↓
Compare Student Skills
        ↓
Generate Skill Gap Report
```

Module 2 must consume the output of Module 1.

---

## Week 3 — Module 3

Expected demonstration:

```text
Skill Gap
    ↓
Skill Dependency Graph
    ↓
A* Search
    ↓
Personalized Learning Roadmap
```

The actual A* implementation must be demonstrable and testable.

---

## Week 4 — Module 4

Expected demonstration:

```text
Learning Progress
       +
Skill Profile
       ↓
Facts
       ↓
Forward Chaining
       ↓
Readiness Rules
       ↓
Career Readiness Result
```

The final result must include an understandable explanation.

---

# 11. Demo-Ready Standard

A module is `DEMO_READY` when a real user can execute its intended
workflow successfully.

A module is NOT `DEMO_READY` if:

* Major features are placeholders
* Core logic is hard-coded
* Tests are missing for important functionality
* The module breaks previously completed modules
* The primary algorithm is only simulated
* The UI claims functionality that the backend does not implement
* Important errors are ignored

---

# 12. Algorithm Integrity

The two required algorithms are academic requirements as well as real
system components.

Agents must not:

* Fake algorithm execution
* Hard-code algorithm outputs
* Rename ordinary logic as A*
* Rename ordinary rule checks as Forward Chaining
* Use an external library as a substitute for implementing the required
  algorithm without explicit approval

The implementation should be understandable enough for academic
demonstration and viva explanation.

Algorithm documentation must include:

* Problem being solved
* Input
* Output
* Algorithm steps
* Data structures
* Complexity
* Implementation
* Example
* Test cases
* How the algorithm contributes to SkillBridge

---

# 13. AI/NLP Integrity

AI and NLP components should solve meaningful problems.

Possible uses include:

* Resume parsing
* Skill extraction
* Skill normalization
* Skill descriptions
* Learning-resource recommendations
* Explanations

AI must not replace deterministic core logic where deterministic logic
is required.

Specifically:

```text
A* → actual A* implementation
Forward Chaining → actual inference implementation
```

An LLM may assist with surrounding functionality, but it must not merely
pretend to execute these algorithms.

---

# 14. Scope Control

Do not add features simply because they are technically interesting.

Before implementing a new feature, determine:

1. Is it in `PROJECT_SPEC.md`?
2. Does it support SkillBridge's primary objective?
3. Does it fit one of the four modules?
4. Does it introduce unnecessary complexity?
5. Can it be completed within the project timeline?

If the answer is unclear, escalate to `krishna-dev`.

---

# 15. No Silent Scope Changes

Agents must not silently:

* Add new modules
* Remove modules
* Change algorithm assignments
* Reintroduce removed features
* Change readiness classifications
* Change the core project workflow
* Replace an algorithm with another approach

Any significant scope change must be explicitly discussed and reflected in
`PROJECT_SPEC.md`.

---

# 16. Documentation Rules

Important project documentation belongs in:

```text
docs/
```

Expected documents include:

```text
docs/project-overview.md
docs/architecture.md
docs/database-design.md
docs/api-design.md
docs/algorithms.md
docs/module-1.md
docs/module-2.md
docs/module-3.md
docs/module-4.md
```

Weekly development records belong in:

```text
docs/development-log/
```

Agents should update documentation when implementation significantly changes
the documented architecture or behavior.

---

# 17. Testing Rules

Tests must be added alongside meaningful implementation.

Do not postpone all testing until the end of the project.

Testing should exist at appropriate levels:

```text
tests/
├── unit/
├── integration/
└── end-to-end/
```

Module-specific tests may also live within each module.

A change that breaks an already completed module must be fixed before the
new work is considered complete.

---

# 18. Security Rules

Never commit:

* API keys
* Passwords
* Authentication tokens
* Database credentials
* Private certificates
* Production secrets

Use environment variables and `.env.example` for configuration examples.

Resume files and student information should be treated as potentially
sensitive application data.

Validate uploaded files and user-provided input.

---

# 19. Code Quality

Prefer:

* Small focused functions
* Clear naming
* Explicit interfaces
* Reusable logic
* Meaningful error handling
* Tests
* Minimal dependencies

Avoid:

* Giant files
* Giant functions
* Copy-pasted logic
* Unnecessary abstractions
* Dead code
* Unused dependencies
* Magic values
* Hard-coded production configuration

Do not refactor working code merely for stylistic preference unless the
change provides a meaningful benefit.

---

# 20. Integration Rules

When integrating modules:

```text
Module 1 → Module 2
Module 2 → Module 3
Module 3 → Module 4
```

Existing module behavior must be preserved unless the change is explicitly
required.

Before merging significant changes:

1. Run relevant tests.
2. Check affected module behavior.
3. Check integration behavior.
4. Review for regressions.
5. Verify project specification compliance.

---

# 21. Agent Communication

When handing work between agents, provide:

* What was changed
* Why it was changed
* Files affected
* Tests performed
* Known limitations
* Remaining issues
* Any decisions that require review

Do not claim a task is complete when it is only partially implemented.

Use explicit statuses such as:

```text
PLANNED
IN_PROGRESS
BLOCKED
IMPLEMENTED
TESTED
REVIEWED
DEMO_READY
COMPLETE
```

---

# 22. Final Principle

The goal is not to produce the largest possible codebase.

The goal is to produce a:

```text
Correct
+
Explainable
+
Testable
+
Secure
+
Maintainable
+
Academically Defensible
+
Actually Working
```

SkillBridge AI system.

Every agent should optimize for the quality and correctness of the final
project rather than the quantity of generated code.

**PROJECT_SPEC.md defines WHAT SkillBridge is.**

**This AGENTS.md defines HOW the agents build it.**

EFFICIENCY RULES

- Do not reread documents already established in the current task unless
  a specific unresolved question requires them.
- Do not reread the entire repository.
- Inspect only files relevant to the current task.
- Prefer git diff and targeted file inspection.
- Do not delegate an agent for a task that can be verified locally.
- Do not delegate Architect/Reviewer for routine implementation fixes.
- Use Tester/Debugger for testing/debugging work.
- Run tests only after a meaningful implementation checkpoint.
- Do not repeat a failed command more than twice.
- If a tool call fails twice, stop and report the problem.
- Never enter a repetitive planning/tool-call loop.
- Keep implementation tasks incremental and bounded.

COMMAND EXECUTION & AUTONOMY POLICY

The SkillBridge project is developed on Windows.

Agents should operate autonomously for normal development commands without
asking the user for confirmation each time.

ALLOWED WITHOUT CONFIRMATION

Agents may automatically execute commands required for the current task,
including:

- Reading files and directories
- Searching the repository
- git status
- git diff
- git log
- Creating/editing project files
- Python commands
- pytest
- ruff
- npm / npm.cmd commands
- npm install
- npm run
- Alembic commands
- SQLite inspection
- Database migrations
- Starting/stopping LOCAL development servers
- curl / Invoke-WebRequest for LOCAL endpoints
- Build commands
- Package/dependency commands required by the project
- Bash/PowerShell commands that are non-destructive and scoped to the
  SkillBridge repository

Do not ask for confirmation for routine development operations.

WINDOWS ENVIRONMENT

Prefer PowerShell-compatible commands on this Windows machine.

Use:
- Get-ChildItem
- Get-Content
- Select-String
- Test-Path
- Set-Location
- Remove-Item when deletion is explicitly part of the current task
- npm.cmd
- Python
- pytest
- ruff

Do not use Linux-specific syntax when PowerShell is available:
- /dev/null
- 2>/dev/null
- cd /d
- Unix-only ls flags

If Bash is explicitly available and appropriate, it may be used for
non-destructive repository operations.

COMMAND FAILURE POLICY

If a command fails:

1. Read the actual error.
2. Diagnose the cause.
3. Try an appropriate corrected command.

Never repeat the exact same failed command more than twice.

If the same operation fails twice, STOP and report the failure instead of
entering a repetitive tool-call loop.

Never repeatedly generate planning text without executing the required
operation.

SENSITIVE / DESTRUCTIVE COMMANDS

Require explicit user confirmation before executing commands that are
destructive, irreversible, security-sensitive, or outside the project.

Examples include:

- git reset --hard
- git clean -fd / git clean -fdx
- force push
- deleting the repository
- recursive deletion of large directories
- deleting databases when data may be lost
- dropping production databases/tables
- modifying files outside the SkillBridge project
- modifying Windows/system configuration
- changing firewall/security settings
- installing system-wide software
- changing credentials or authentication infrastructure
- exposing, printing, committing, or transmitting API keys/secrets
- reading credential stores or unrelated private files
- sending data to external services not required by the task
- executing unknown/untrusted scripts
- commands that could cause irreversible data loss

For sensitive commands, STOP and ask the user for confirmation.

SECRET HANDLING

Never print API keys, passwords, tokens, JWT secrets, database credentials,
or other secrets to the terminal output.

Never commit secrets.

When inspecting configuration containing secrets, redact them in output.

SCOPE CONTROL

Commands must remain relevant to the current SkillBridge task.

Do not:
- explore unrelated directories
- modify unrelated projects
- install unnecessary dependencies
- perform unrelated cleanup
- change approved architecture without authorization

EFFICIENCY

- Inspect only files relevant to the current task.
- Do not reread large project documents unnecessarily.
- Prefer git diff and targeted inspection.
- Do not delegate agents for trivial verification.
- Keep tasks incremental.
- Run relevant tests after meaningful checkpoints.
- Do not start unrelated modules.