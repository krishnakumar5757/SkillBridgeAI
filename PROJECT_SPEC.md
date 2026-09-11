# SkillBridge AI — Master Project Specification

## 1. Project Overview

**SkillBridge AI** is an AI-based Skill Gap and Career Readiness Assessment System designed to help students understand their current capabilities and measure their readiness for a selected career role.

The system analyzes a student's profile, academic information, interests, projects, and resume to create a structured skill profile. The student's current skills are compared against the skills required for a selected career role.

SkillBridge identifies skill gaps and generates a personalized learning roadmap. As the student progresses through the roadmap, the system tracks learning progress and updates the student's skill profile.

Finally, the system evaluates the student's overall career readiness using a rule-based reasoning system and generates a Career Readiness Score with one of three classifications:

* **Role Ready**
* **Nearly Ready**
* **Needs Improvement**

The system must demonstrate practical use of Artificial Intelligence, Natural Language Processing, recommendation techniques, heuristic search, and logical reasoning.

---

# 2. Core Project Goal

The primary goal of SkillBridge is:

> **To provide students with a measurable, personalized, and explainable pathway from their current skill level to the requirements of a desired career role.**

The system must answer three major questions:

1. **Where am I currently?**

   * Student skill profile
   * Resume-derived skills
   * Academic and project information

2. **What am I missing for my target role?**

   * Required role skills
   * Current skill levels
   * Skill gaps

3. **What should I do next, and am I becoming ready?**

   * Personalized learning roadmap
   * Learning progress
   * Career readiness evaluation

---

# 3. Project Scope

SkillBridge consists of exactly **four major functional modules**.

## Module 1 — Student Intelligence

### Purpose

Build a structured representation of the student's current skills and background.

### Features

* Student registration/profile
* Academic information
* Areas of interest
* Projects
* Existing skills
* Resume upload
* Resume text extraction
* NLP-based information extraction
* Skill extraction from resume
* Skill normalization
* Student skill profile generation

### Input

* Student information
* Resume
* Skills
* Projects
* Academic information
* Interests

### Output

A structured **Student Skill Profile**.

Example:

```text
Python       → Advanced
Java         → Intermediate
SQL          → Intermediate
React        → Beginner
Docker       → Beginner
Git          → Advanced
```

---

# 4. Module 2 — Career Intelligence

### Purpose

Determine the skill requirements for the student's desired career role and identify gaps between the student's current profile and those requirements.

### Features

* Career role selection
* Career role information
* Required skill database
* Skill proficiency requirements
* Skill matching
* Skill gap calculation
* Strong skill identification
* Weak skill identification
* Missing skill identification
* Priority gap identification

### Input

* Student Skill Profile
* Selected Career Role
* Role Skill Requirements

### Processing

The system compares:

```text
Student Current Skills
        VS
Target Role Requirements
```

### Output

A structured Skill Gap Report.

Example:

```text
Target Role: Backend Developer

Python           → Strong
SQL              → Moderate
REST APIs        → Weak
Docker           → Missing
System Design    → Missing
Git              → Strong
```

The system should prioritize gaps so that important missing prerequisite skills can be addressed before advanced skills.

---

# 5. Module 3 — Learning Intelligence

## Primary Algorithm: A* Search

### Purpose

Generate a personalized learning roadmap that moves the student from their current skill state toward the skill requirements of the selected career role.

### Core Algorithm

**A* Search**

A* Search must be implemented as an actual algorithm and must not exist only as a label or documentation claim.

### Main Components

* Skill dependency graph
* Skill nodes
* Skill relationships/dependencies
* Learning-path costs
* Heuristic function
* A* search algorithm
* Path reconstruction
* Personalized roadmap generation

### Concept

The student's current skill state is treated as the starting state.

The target career's required skill state is treated as the goal.

The skill dependency graph represents possible learning paths.

A* searches for an efficient path using:

```text
f(n) = g(n) + h(n)
```

where:

* `g(n)` = accumulated cost to reach the current skill
* `h(n)` = estimated remaining cost to reach the target
* `f(n)` = estimated total cost

### Example

Student currently knows:

```text
Python
Git
```

Target:

```text
Backend Developer
```

Possible roadmap:

```text
SQL
 ↓
Database Fundamentals
 ↓
REST APIs
 ↓
Backend Framework
 ↓
Docker
 ↓
System Design
```

Another student with stronger existing skills may receive a different roadmap.

### Output

A personalized learning roadmap containing:

* Skill/topic
* Current proficiency
* Target proficiency
* Priority
* Prerequisites
* Recommended order
* Progress status

---

# 6. Module 4 — Career Readiness

## Primary Algorithm: Forward Chaining

### Purpose

Evaluate whether the student has progressed sufficiently toward the selected career role and generate an explainable Career Readiness result.

### Core Algorithm

**Forward Chaining**

Forward Chaining must be implemented as an actual inference process.

### Main Components

* Student facts
* Skill facts
* Learning-progress facts
* Skill coverage facts
* Proficiency facts
* Career readiness rules
* Rule evaluation engine
* Inference process
* Readiness classification
* Readiness explanation

### Example Facts

```text
python_proficiency = advanced
sql_proficiency = intermediate
docker_proficiency = beginner
skill_coverage = 78
learning_progress = 82
```

### Example Rules

```text
IF skill_coverage >= required_threshold
AND core_skill_proficiency >= required_level
AND learning_progress >= progress_threshold
THEN readiness = ROLE_READY
```

```text
IF skill_coverage >= minimum_threshold
AND learning_progress >= minimum_progress
THEN readiness = NEARLY_READY
```

Otherwise:

```text
readiness = NEEDS_IMPROVEMENT
```

The exact thresholds and rules must be configurable rather than hard-coded throughout the application.

### Output

The system generates:

1. Career Readiness Score
2. Readiness classification
3. Strengths
4. Remaining gaps
5. Recommended next improvements
6. Explanation of why the classification was reached

### Classification

```text
80–100 → Role Ready
60–79  → Nearly Ready
0–59   → Needs Improvement
```

The scoring model may be refined during implementation, but the final model must be documented and consistently applied.

---

# 7. Complete System Flow

The complete SkillBridge pipeline is:

```text
Student
   ↓
Student Profile
   ↓
Resume Upload
   ↓
Resume/NLP Analysis
   ↓
Student Skill Profile
   ↓
Target Career Role
   ↓
Role Skill Requirements
   ↓
Skill Gap Analysis
   ↓
A* Search
   ↓
Personalized Learning Roadmap
   ↓
Learning Progress Tracking
   ↓
Updated Skill Profile
   ↓
Forward Chaining
   ↓
Career Readiness Score
   ↓
Role Ready / Nearly Ready / Needs Improvement
```

---

# 8. Two Required Syllabus Algorithms

SkillBridge must use exactly these two primary syllabus algorithms:

## Algorithm 1 — A* Search

**Module:** Module 3 — Learning Intelligence

**Purpose:** Personalized learning roadmap generation.

## Algorithm 2 — Forward Chaining

**Module:** Module 4 — Career Readiness

**Purpose:** Rule-based career readiness reasoning and classification.

These algorithms must perform meaningful computational work within the application.

They must not be added artificially only to satisfy an academic requirement.

---

# 9. AI and NLP Usage

AI should be used where it provides genuine value.

Potential AI/NLP functionality includes:

### Resume Analysis

* Resume text extraction
* Skill identification
* Technology/entity extraction
* Project identification
* Experience extraction
* Skill normalization

### Skill Intelligence

The system may use AI/NLP techniques to map different expressions to the same standardized skill.

Example:

```text
"JS"
"Javascript"
"JavaScript programming"
```

may be normalized to:

```text
JavaScript
```

### Recommendation Support

AI may assist in:

* Explaining skill gaps
* Generating learning descriptions
* Providing learning-resource recommendations
* Explaining readiness results

AI-generated content must not replace the actual A* or Forward Chaining algorithms.

---

# 10. Career Role System

SkillBridge should support multiple career roles.

Examples may include:

* Full-Stack Developer
* Backend Developer
* Frontend Developer
* Data Analyst
* Machine Learning Engineer
* Data Scientist
* DevOps Engineer

The initial implementation may support a smaller set of roles.

The architecture must allow additional roles to be added without modifying the core algorithm implementations.

Each role should have structured requirements such as:

```text
Role
 ├── Required Skills
 ├── Minimum Proficiency
 ├── Skill Priority
 └── Skill Dependencies
```

---

# 11. Skill System

Skills must be represented using a standardized structure.

A skill may contain:

```text
Skill
 ├── Name
 ├── Category
 ├── Description
 ├── Proficiency Levels
 ├── Prerequisites
 └── Related Skills
```

Example:

```text
Docker
 ├── Category: DevOps
 ├── Prerequisite: Linux
 ├── Prerequisite: Networking
 └── Related: Kubernetes
```

The skill graph used by A* should be based on these relationships.

---

# 12. Learning Progress

The system should track progress against the personalized roadmap.

Possible states:

```text
Not Started
In Progress
Completed
```

The system should record progress at the skill/topic level.

Progress information may include:

* Completion percentage
* Started date
* Completion date
* Current proficiency
* Target proficiency

Progress data feeds into Module 4.

---

# 13. Career Readiness Score

The Career Readiness Score should be derived from measurable factors rather than arbitrary AI-generated numbers.

Potential factors include:

```text
Skill Coverage
Skill Proficiency
Learning Progress
Project/Experience Evidence
```

The final scoring formula must be documented in:

```text
docs/algorithms.md
```

and implemented consistently.

The score must be explainable.

The system should be able to answer:

> "Why did this student receive this readiness score?"

---

# 14. Four-Week Development Structure

Development is divided into four major weekly milestones.

## Week 1 — Module 1

**Student Intelligence**

Deliverable:

```text
Student Profile
+
Resume Upload
+
Resume/NLP Analysis
+
Skill Extraction
+
Student Skill Profile
```

The module must be demonstrable to the mentor.

---

## Week 2 — Module 2

**Career Intelligence**

Deliverable:

```text
Target Role Selection
+
Role Requirements
+
Skill Matching
+
Skill Gap Analysis
```

The module must integrate with Module 1.

---

## Week 3 — Module 3

**Learning Intelligence**

Deliverable:

```text
Skill Dependency Graph
+
A* Implementation
+
Personalized Learning Roadmap
```

The A* algorithm must be demonstrable with test cases.

---

## Week 4 — Module 4

**Career Readiness**

Deliverable:

```text
Progress Tracking
+
Readiness Scoring
+
Forward Chaining Engine
+
Readiness Classification
+
Explanation
```

The module must integrate with Modules 1–3.

---

# 15. Module Completion Rule

A module is not considered complete until:

* Implementation is complete
* Unit tests are written
* Integration tests are written where required
* Security considerations are reviewed
* Code review is completed
* Module documentation is updated
* Integration with previous modules works
* A demonstrable user workflow exists

The orchestrator must not move the project to the next module prematurely.

---

# 16. Agent Development Rules

SkillBridge is developed using a six-agent development workflow.

### krishna-dev

Primary orchestrator.

Responsibilities:

* Coordinate development
* Delegate tasks
* Maintain project consistency
* Integrate modules
* Resolve conflicts between agent recommendations
* Ensure project specification is followed

### architect

Responsibilities:

* System architecture
* Database architecture
* API architecture
* Module boundaries
* Technology decisions
* Design documentation

Architect should not unnecessarily rewrite working implementation.

### reviewer

Responsibilities:

* Code review
* Architecture review
* Maintainability
* Correctness
* Detect unnecessary complexity
* Verify algorithm implementations

### security

Responsibilities:

* Authentication/authorization review
* Resume/file-upload security
* Input validation
* API security
* Sensitive data handling
* Dependency/security concerns

### debugger

Responsibilities:

* Investigate bugs
* Diagnose failures
* Fix implementation issues
* Identify root causes
* Avoid masking underlying problems

### tester

Responsibilities:

* Unit tests
* Integration tests
* End-to-end tests
* Algorithm test cases
* Regression testing
* Edge-case testing

---

# 17. Agent Collaboration Rules

All agents must treat this document as the project source of truth.

Agents must:

* Read the relevant module documentation before modifying it.
* Avoid changing another module's core logic without coordination.
* Avoid unnecessary dependencies.
* Prefer simple, maintainable solutions.
* Write tests for important functionality.
* Preserve working functionality when making changes.
* Document important architectural decisions.
* Never fabricate completed functionality.
* Never claim an algorithm is implemented when only a placeholder exists.

The orchestrator has final responsibility for integration.

---

# 18. Out of Scope

The following functionality is explicitly **NOT part of SkillBridge's core scope** unless the project specification is intentionally revised later:

### Removed Feature

**AI Role-Specific Assessment**

SkillBridge will NOT include:

* AI-generated technical examinations
* AI-generated conceptual examinations
* AI-generated scenario-based assessments
* Automated question-paper generation
* Assessment question selection using CSP/backtracking
* Exam scoring based on generated questions

The Career Readiness result is instead based on the student's:

* Skill profile
* Skill coverage
* Skill proficiency
* Learning progress
* Project/experience evidence
* Forward Chaining rules

---

# 19. Scope Control

The project should prioritize completion and correctness over feature quantity.

New features should only be added if they:

1. Support the main SkillBridge objective.
2. Do not compromise the four-module structure.
3. Do not interfere with the two required algorithms.
4. Can reasonably be completed within the project timeline.
5. Are approved by the project team before implementation.

Avoid unnecessary features such as:

* Social networking
* Chat systems
* Generic AI assistants
* Gamification
* Complex recommendation marketplaces
* Unrelated dashboards
* Features added only because they are technically interesting

---

# 20. Quality Requirements

SkillBridge should be:

### Explainable

The system should explain:

* Why a skill is considered missing
* Why a roadmap step was selected
* Why a readiness score was generated
* Why a student received a particular readiness classification

### Modular

Each of the four modules should have clear responsibilities and interfaces.

### Testable

Core algorithms and business logic must have deterministic test cases.

### Maintainable

Avoid unnecessary complexity and duplicated logic.

### Extensible

New career roles and skills should be addable without rewriting core algorithms.

### Secure

Student data and uploaded resumes must be handled securely.

---

# 21. Definition of Success

SkillBridge is considered successful when a student can complete the following end-to-end workflow:

```text
1. Create Student Profile
          ↓
2. Upload Resume
          ↓
3. Generate Skill Profile
          ↓
4. Select Career Role
          ↓
5. View Skill Gaps
          ↓
6. Generate Personalized Roadmap
          ↓
7. Follow/Update Roadmap Progress
          ↓
8. Generate Career Readiness Result
          ↓
9. Understand Strengths and Remaining Gaps
```

The system must demonstrate that:

* NLP/AI can extract useful student skill information.
* Skill gaps can be identified against a target role.
* A* can generate a personalized learning path.
* Learning progress can be tracked.
* Forward Chaining can reason over student facts and readiness rules.
* The final readiness result is measurable and explainable.

---

# 22. Source of Truth

This document defines the functional scope of SkillBridge AI.

If another document, agent instruction, or implementation decision conflicts with this specification, the conflict must be identified and resolved before implementation continues.

Changes to the project scope should be documented rather than silently introduced.

**Current locked scope:**

```text
4 Modules
+
A* Search
+
Forward Chaining
+
No AI Role-Specific Assessment
```
