# SkillBridge AI - Architecture Verification Review (v2.1)

> **Reviewer:** Reviewer Agent
> **Date:** 2026-08-20
> **Subject:** Follow-up verification of `docs/architecture.md` v2.1 (4,509 lines)
> **Prior Verdict:** APPROVE WITH CHANGES (v2.0, see `docs/architecture-review.md`)
> **Architect's Claim:** All HIGH and MEDIUM findings RESOLVED
> **Verification Status:** See Section 6 - Architecture Status Verdict

---

## 1. Executive Summary

This report verifies whether the Architect's revision of `docs/architecture.md`
from v2.0 (3,481 lines) to v2.1 (4,509 lines) actually resolved every HIGH and
MEDIUM finding from the prior formal review (`docs/architecture-review.md`).

### Verification Method

For each previous HIGH and MEDIUM finding, the reviewer:

1. Located the relevant section in v2.1 using the `Revision Note` callouts
   (66 callouts total, each tagged with the finding ID it addresses).
2. Read the actual revised content - not merely the architect's revision summary
   in Section 19.
3. Checked internal consistency across sections (A* pipeline, FC pipeline,
   database schema, API contracts, data flow, module boundaries).
4. Searched for residual references to removed constructs
   (e.g., `contributes_to_score`, `edge_cost`, the score-threshold if/else).

### Overall Assessment

The Architect did **substantial, high-quality revision work**. The A* heuristic
admissibility proof is now mathematically correct and well-articulated. The
Forward Chaining pipeline is genuinely multi-step. The dual scoring model is
eliminated. The database schema gaps (Project entity, progress duplication) are
closed. The module boundary coupling is reduced.

**However, the verification identified one new HIGH-severity defect** in the
Forward Chaining engine design that was not present (or not exposed) in v2.0:
the engine will **overwrite** the `role_ready` classification with
`nearly_ready` and then `needs_improvement` because the lower-priority
classification rules' conditions remain satisfied after the higher-priority rule
fires, and the engine has no guard against overwriting an already-asserted
classification. The process diagram (Section 7.6, iteration 4) claims the
engine stops, but the actual engine code (Section 7.5) does not implement that
stopping behavior.

This defect must be fixed before implementation, but it is a localized fix
(add a guard condition or change the rule conditions). It does not require
rearchitecting.

### Finding Disposition Summary

| Category | Count |
|----------|-------|
| HIGH findings fully FIXED | 2 of 3 |
| HIGH findings with a NEW defect | 1 (F-FC-1 - the fix introduced a new bug) |
| MEDIUM findings fully FIXED | 8 of 8 |
| New HIGH-severity issues introduced | 1 (F-NEW-1) |
| Documentation bloat | Moderate (see Section 4) |

### Verdict

**APPROVE WITH ONE REQUIRED FIX** - The architecture is ready for
implementation **after** the Forward Chaining engine's classification-overwrite
bug (F-NEW-1) is corrected. All other HIGH and MEDIUM findings are genuinely
resolved.

---

## 2. Finding-by-Finding Verification (HIGH and MEDIUM)

### 2.1 F-ASTAR-1 - A* Heuristic Admissibility Proof (HIGH)

**Prior Problem:** The admissibility proof was incomplete/incorrectly reasoned
and could mislead implementers into adding prerequisite costs to `h`, breaking
admissibility.

**Disposition: FIXED**

**Evidence (Section 6.8, lines 1235-1324):**

The proof has been completely rewritten and is now mathematically correct:

1. **Definition of h is precise** (lines 1246-1268): `h(state)` sums the base
   `learning_cost(skill)` for each skill in `remaining = goal_required_skill_ids
   - state`. The code matches the prose exactly.

2. **The h(n) <= h*(n) argument is correct** (lines 1271-1301):
   - Step 2 correctly argues that each missing required skill must be learned
     at least once (goal test requires subset inclusion), and the successor
     function enforces "learned at most once," so each contributes exactly its
     base cost.
   - Step 3 correctly argues the actual cost may be *higher* due to
     non-required prerequisites whose costs are NOT in `h`.
   - The inequality `h*(state) = Sigma required + Sigma non-required-prereqs
     >= Sigma required = h(state)` is correctly stated (lines 1292-1297).

3. **The warning is present and explicit** (lines 1260-1263):
   "WARNING: Do NOT add prerequisite costs to h. Doing so would risk
   double-counting (a prerequisite that is itself a required skill would be
   counted both as a required skill and as a prerequisite) and could make h
   INADMISSIBLE, voiding A*'s optimality guarantee."

4. **Consistency proof added** (lines 1303-1316): The document now also proves
   the heuristic is *consistent* (monotone), which is a stronger property and
   correctly justifies the closed-set optimization in the A* implementation.

5. **Trade-off acknowledged** (lines 1318-1324): The document explicitly states
   `h` is a relaxed lower bound that ignores prerequisite chains, so pruning may
   be limited (A* behaves closer to Dijkstra). This is an honest, defensible
   statement.

6. **Heuristic definition is consistent with the proof**: The code
   `sum(learning_cost(skill) for skill in remaining)` (line 1268) matches the
   proof's definition (line 1276-1278). No discrepancy.

**Verification of the worked example (Section 6.13, lines 1448-1500):**
The worked example now correctly shows `g`, `h`, and `f` separately at each
step. Step 3 (learning Linux, a non-required prerequisite) correctly shows `h`
unchanged (40) while `g` increases (45), with an explicit note (lines 1509-1513)
explaining why `h` does not decrease. This also resolves F-ASTAR-5 (LOW).

**Conclusion:** The proof is mathematically sound, the warning is explicit, and
the heuristic definition is consistent with the proof. F-ASTAR-1 is fully
resolved.

---

### 2.2 F-FC-1 - Forward Chaining Sole Classification (HIGH)

**Prior Problem:** Two independent classification mechanisms existed (FC rules
and a score-threshold if/else), with a precedence rule that undermined FC's
role as the required algorithm.

**Disposition: PARTIALLY FIXED - the fix introduced a new HIGH-severity defect
(see F-NEW-1 in Section 5)**

**What was fixed:**

1. **The score-threshold if/else is removed.** The former "Classification
   Thresholds" section (v2.0 Section 7.10) is replaced by Section 7.10
   "Classification (Forward Chaining is Sole Authority)" (lines 2257-2301).
   There is no `if score >= 80 ... elif score >= 60 ...` code anywhere in v2.1.
   A grep for the prior score-threshold pattern confirms its absence.

2. **FC is explicitly the sole authority.** Section 7.1 (lines 1625-1632),
   Section 7.8 (lines 2145-2171), Section 7.10 (lines 2266-2301), and Appendix
   B Q7 (lines 4398-4405) all state consistently that FC is the sole
   classification mechanism and the score is "supporting evidence only."

3. **Rule thresholds are aligned with spec score ranges** (lines 2284-2287):
   `rule_role_ready` requires `skill_coverage_percent >= 80` (aligned with
   80-100), `rule_nearly_ready` requires `>= 60` (aligned with 60-79), and the
   default catches 0-59. This alignment is documented.

4. **The score is computed BEFORE FC runs** (lines 2095-2100, 2188-2190) and
   exposed as a `readiness_score` fact, so rules *could* reference it but the
   default rule base does not. This is a clean separation.

**What is NOT fixed (the new defect - F-NEW-1):**

The engine design has a classification-overwrite bug. See Section 5, F-NEW-1 for
the full analysis. In short: after `rule_role_ready` fires and asserts
`readiness_classification = "role_ready"`, the lower-priority
`rule_nearly_ready` (whose conditions `skill_coverage >= 60` and
`learning_progress >= 50` are *still satisfied*) will fire in the next iteration
and **overwrite** the classification to `"nearly_ready"`. Then the default rule
(empty conditions, always applicable) will fire and overwrite it again to
`"needs_improvement"`. The process diagram (Section 7.6, iteration 4, lines
2024-2037) claims the engine stops because "classification set," but the actual
engine code (Section 7.5, lines 1896-1922) has no such guard.

**Conclusion:** The *intent* of F-FC-1 is met - FC is the sole classifier and
the score-threshold if/else is gone. But the *implementation design* of the FC
engine does not actually produce the classification the document claims it
produces. This is a correctness flaw that must be fixed before implementation.

---

### 2.3 F-FC-2 - `contributes_to_score` Removed / Single Scoring Model (HIGH)

**Prior Problem:** The rule schema had a `contributes_to_score` field implying
rules drive the score, but the scoring formula ignored it - creating two
inconsistent scoring models.

**Disposition: FIXED**

**Evidence:**

1. **`contributes_to_score` is removed from the `Conclusion` schema**
   (Section 7.3, lines 1723-1728). The schema now contains only `fact_key` and
   `fact_value`, with an explicit comment: "NOTE: contributes_to_score has been
   REMOVED (F-FC-2)."

2. **All example rules no longer have the field** (Section 7.4, lines
   1753-1825). A grep of v2.1 confirms `contributes_to_score` appears only in
   revision notes and test descriptions (verifying its absence), never in an
   actual rule definition or schema.

3. **The process diagram no longer sums rule contributions** (Section 7.6,
   lines 1960-2038). The score (78.5) is shown as "computed by formula" in the
   initial facts (line 1981) and as "supporting evidence, from weighted factor
   formula" in the final output (line 2034-2035). The prior "Score: 60 + 20 =
   80 (from rule contributions)" line is gone.

4. **The weighted factor formula is the single scoring model** (Section 7.9,
   lines 2192-2232). The formula uses `skill_coverage` (30%),
   `core_skill_coverage` (25%), `proficiency_level` (20%), `learning_progress`
   (15%), and `experience` (10%). No alternative "sum of rule contributions"
   model exists anywhere in the document.

5. **Test coverage verifies the removal** (Section 13.3, lines 3351-3353):
   `test_no_contributes_to_score` verifies rules do NOT have the field, and
   `test_score_computed_before_fc` verifies the score is computed by the
   formula before FC runs.

**Conclusion:** The dual scoring model is eliminated. F-FC-2 is fully resolved.

---

### 2.4 F-ASTAR-2 - g(n) Cost Definition Consistency (MEDIUM)

**Prior Problem:** `g(n)` was defined two ways (path-sum via `came_from` vs.
set-difference `state - start_state`) that could diverge, and the "learned at
most once" invariant was not stated explicitly.

**Disposition: FIXED**

**Evidence (Section 6.7, lines 1196-1233; Section 6.6, lines 1187-1189):**

1. **g(n) is consistently defined as accumulated path cost** (lines 1198-1203):
   "g(n) is now explicitly defined as the **accumulated path cost** - the sum
   of learning costs for all skills learned along the path from the start state
   to the current state."

2. **The "learned at most once" invariant is stated explicitly** in two
   places:
   - Section 6.6 (lines 1187-1189): "Each skill is acquired **at most once** per
     path. The successor function enforces `X not in S`, so a skill can never be
     're-learned.' This invariant is essential for the consistency of g(n)."
   - Section 6.7 (lines 1214-1216, 1233): The docstring and the bullet list
     both restate the invariant.

3. **The two definitions are reconciled** (lines 1218-1227): The docstring
   explains that the incremental `came_from` tracking
   (`g(successor) = g(current) + cost`) is "equivalent to recomputing from the
   state because of the 'learned at most once' invariant," and the state-based
   formula `sum(learning_cost(skill) for skill in (state - start_state))` is
   shown as the mathematically equal alternative.

4. **The A* implementation (Section 6.10, line 1387)** uses the incremental
   form `tentative_g = came_from[current_state][0] + cost`, consistent with the
   definition.

**Conclusion:** The two definitions are reconciled and the invariant is
explicit. F-ASTAR-2 is fully resolved.

---

### 2.5 F-ASTAR-3 - Optimality Claim Precision / `edge_cost` Removal (MEDIUM)

**Prior Problem:** The "optimal path" claim was overstated, and `edge_cost` was
defined on `SkillEdge` but unused.

**Disposition: FIXED**

**Evidence:**

1. **`edge_cost` is removed from `SkillEdge`** (Section 6.2, lines 1060-1067).
   The class now has only `from_skill` and `to_skill`, with an inline comment:
   "Note: edge_cost is NOT used in the cost model." The Revision Note (lines
   1074-1079) explicitly states the removal.

2. **The optimality claim is precisely stated** in a dedicated Section 6.15
   (lines 1558-1586): "A* with an admissible and consistent heuristic guarantees
   finding the **minimum-total-learning-cost path** from the start state to the
   goal state." It then explicitly lists what "optimal" does NOT mean (lines
   1576-1580): not real-world educational effectiveness, not pedagogical
   optimality, not time-to-completion.

3. **The worked example restates the precise claim** (lines 1503-1507): "A*
   finds the minimum-total-learning-cost path (85 hours) subject to prerequisite
   ordering constraints, given the configured cost model (learning hours per
   skill). This is 'optimal' with respect to the modeled learning cost, NOT with
   respect to real-world educational value."

4. **Appendix C (line 4423)** summarizes the precise claim: "A* finds the
   minimum-total-learning-cost path subject to prerequisite ordering, given the
   configured cost model. NOT a claim about real-world educational
   effectiveness."

**Conclusion:** The claim is precise and `edge_cost` is removed. F-ASTAR-3 is
fully resolved.

---

### 2.6 F-ASTAR-4 / F-MOD-2 - Weak-Skill / Proficiency Handling (MEDIUM)

**Prior Problem:** The binary A* state could not represent proficiency levels,
so weak skills were not planned; and the goal construction (Section 6.14)
conflated missing and weak skills.

**Disposition: FIXED**

**Evidence:**

1. **The binary state design choice is documented as deliberate** (Section 6.3,
   lines 1109-1121): "The state representation is **binary** (skill present or
   absent). A* plans only for **MISSING** skills... **Weak skills**... are NOT
   planned by A* because the binary state cannot represent proficiency levels.
   Weak skills are addressed by Module 4's proficiency facts and readiness
   scoring." It explicitly identifies this as "Option A from the review"
   appropriate for the 4-week scope.

2. **The goal construction is fixed to use ONLY missing skills** (Section 6.5,
   lines 1138-1170): `goal_required_skill_ids = set(missing_skill_ids from
   SkillGapReport)`. The Revision Note (lines 1153-1159) explicitly states weak
   skills are excluded because "their IDs are already in the start state... so
   adding them to the goal would make the goal test pass immediately without
   generating any learning steps."

3. **A worked example clarifies the distinction** (lines 1161-1170):
   `missing_skills = {"docker", "rest_apis", "system_design"}` vs
   `weak_skills = {"sql"}`, with the goal built only from missing skills.

4. **Section 6.14 (lines 1525-1531)** confirms the input assembly uses only
   `missing_skills` from the SkillGapReport, with an explicit note that weak
   skills are NOT included.

5. **The roadmap output (Section 6.12, lines 1441-1446)** clarifies that
   `current_proficiency` is `None` for missing skills and is display-only for
   weak skills (which do not get a learning step).

6. **Module 4 handles weak skills** via proficiency facts
   (`average_proficiency`, `min_core_proficiency`, `advanced_skills_count`) and
   the scoring formula (Section 7.9, line 2226).

7. **Tests verify the behavior** (Section 13.2, lines 3288-3296):
   `test_weak_skills_not_in_goal` and `test_non_required_prerequisite_in_path`.

**Conclusion:** The weak-skill handling is explicitly documented, the goal
construction is fixed, and the design choice is justified. F-ASTAR-4 and
F-MOD-2 are fully resolved.

---

### 2.7 F-FC-3 - Forward Chaining Multi-Step Inference (MEDIUM)

**Prior Problem:** The example rule base had no rules where one rule's
conclusion enables another - all rules concluded the same fact key
(`readiness_classification`), so the engine demonstrated only single-step
inference.

**Disposition: FIXED (with the caveat that the chaining exposes F-NEW-1)**

**Evidence (Section 7.4, lines 1731-1861):**

1. **Genuine multi-step chains exist.** The rule base now contains:
   - `rule_core_skills_satisfied` (priority 100): conditions on
     `core_skill_coverage_percent >= 90` AND `min_core_proficiency >= 2`;
     concludes `core_skills_satisfied = true`.
   - `rule_progress_on_track` (priority 90): condition on
     `learning_progress_percent >= 70`; concludes `progress_on_track = true`.
   - `rule_role_ready` (priority 80): conditions on
     `core_skills_satisfied == true` AND `progress_on_track == true` AND
     `skill_coverage_percent >= 80`; concludes
     `readiness_classification = "role_ready"`.

2. **At least one rule's conclusion enables another.** `rule_role_ready`'s
   conditions depend on `core_skills_satisfied` and `progress_on_track`, both
   of which are *derived by inference* (asserted by the two intermediate rules),
   not raw input facts. This is a genuine forward chain.

3. **The inference trace is documented** (Section 7.6, lines 1987-2037; Section
   7.4, lines 1827-1846): The process diagram shows iterations 1-3 with each
   intermediate rule firing and enabling the next. The explanation (lines
   1827-1846) explicitly states: "This is a genuine forward chain:
   `rule_role_ready`'s conditions depend on facts **derived by inference**...
   not just on raw input facts."

4. **Tests verify the chain** (Section 13.3, lines 3320-3329):
   `test_rule_chain_multi_step` and `test_intermediate_fact_enables_downstream_rule`.

**Caveat:** The multi-step chain is genuine, but it is precisely this chain that
exposes the classification-overwrite bug (F-NEW-1). The intermediate rules
(`core_skills_satisfied`, `progress_on_track`) fire correctly; the problem is
that the *classification* rules (`rule_nearly_ready`, default) fire afterward
and overwrite the `role_ready` conclusion. So F-FC-3's *intent* (multi-step
chaining) is met, but the chaining reveals a separate engine defect.

**Conclusion:** The rule base now contains genuine multi-step inference chains
with intermediate facts enabling downstream rules. F-FC-3 is fully resolved
(on its own terms). The overwrite issue is tracked separately as F-NEW-1.

---

### 2.8 F-SCORE-1 - Experience Factor Grading (MEDIUM)

**Prior Problem:** The experience factor was binary (`100 if has_projects else
50`), ignoring the `project_count` fact.

**Disposition: FIXED**

**Evidence (Section 7.9, lines 2218-2228):**

```python
project_count = facts.get("project_count", 0)
experience_score = min(100, project_count * 33)
```

The formula is graded: 0 projects -> 0, 1 -> 33, 2 -> 67, 3+ -> 100 (capped). The
Revision Note (lines 2179-2181) and the key design decisions table (line 2374)
both document this. The `has_projects` fact is retained for rule conditions
(line 1693-1695) but is no longer used in the score.

**Conclusion:** F-SCORE-1 is fully resolved.

---

### 2.9 F-MOD-1 - Module 4 Dependency on Module 2 Coverage Metrics (MEDIUM)

**Prior Problem:** Module 4 recomputed Module 2's coverage metrics
(`skill_coverage_percent`, etc.) from Module 2's data, creating backward
coupling and a risk of divergent definitions.

**Disposition: FIXED**

**Evidence:**

1. **The `SkillGapReport` contract (Section 5.6, lines 952-970)** now includes
   precomputed coverage metrics: `skill_coverage_percent`,
   `core_skill_coverage_percent`, `critical_skill_coverage_percent`,
   `total_skills_acquired`, `total_skills_required`. The Revision Note (lines
   947-950) and the coverage metric definitions (lines 991-1008) are in Module
   2's section.

2. **Module 4 consumes rather than recomputes** (Section 7.7, lines 2074-2080):
   "Consume precomputed coverage metrics from the `SkillGapReport` contract:
   `skill_coverage_percent` (from contract, NOT recomputed)..." The fact
   representation (Section 7.2, lines 1658-1661) labels them "From Module 2's
   SkillGapReport."

3. **A `CoverageCalculator` is added to Module 2's internal components**
   (Section 3.4, line 534; Section 14.1, line 3469).

4. **No remaining backward coupling.** Module 4 calls Module 2's service
   interface to get the SkillGapReport (which now contains the metrics) and
   reads the metrics from the contract. It does not recompute them.

5. **Tests verify consumption** (Section 13.3, lines 3370-3372):
   `test_fact_generation_from_student_data` checks "Coverage metrics should come
   from SkillGapReport (not recomputed)."

**Conclusion:** F-MOD-1 is fully resolved.

---

### 2.10 F-DB-1 - Progress Data Duplication (MEDIUM)

**Prior Problem:** `roadmap_items.status` and `learning_progress.progress_percent`
stored overlapping progress state with no synchronization rule.

**Disposition: FIXED**

**Evidence:**

1. **`roadmap_items.status` is the authoritative progress state** (Section
   8.2.11, lines 2576-2599; Decision 16.10, lines 4109-4139). The Revision
   Note (lines 2578-2581) states this explicitly.

2. **`learning_progress` is repurposed as `progress_audit_log`** (Section
   8.2.12, lines 2601-2624) - an append-only audit table recording
   `previous_status`, `new_status`, `notes`, `created_at`. The Revision Note
   (lines 2603-2606) states it is "NOT a second source of current progress."

3. **The fact generator derives progress from `roadmap_items.status`**
   (Section 7.7, lines 2082-2087): "Load roadmap items and their `status`...
   Compute `learning_progress_percent = (completed_items / total_items) * 100`."

4. **The API updates `roadmap_items.status` and appends to the audit log**
   (Section 9.5, lines 2777-2780): "The progress update endpoint updates
   `roadmap_items.status` (the authoritative progress state) and appends an
   entry to `progress_audit_log`."

5. **The ER diagram (Section 8.3, lines 2664-2674)** reflects the change:
   `LearningProgress` is replaced with `ProgressAuditLog`.

6. **Decision 16.10 (lines 4109-4139)** documents the single source of truth
   and the trade-off (no separate `progress_percent` field; progress is derived
   from status).

**Conclusion:** There is a single source of truth. F-DB-1 is fully resolved.

---

### 2.11 F-DB-2 - Missing Project Entity (MEDIUM)

**Prior Problem:** The spec lists projects as a Module 1 input and Module 4
fact, but no `projects` table existed in the schema.

**Disposition: FIXED**

**Evidence:**

1. **The `projects` table is added** (Section 8.2.3, lines 2429-2446) with
   `id`, `student_id`, `title`, `description`, `technologies` (JSON array),
   `created_at`, and a FK to `students`.

2. **It is wired into Module 4 facts** (Section 7.7, lines 2089-2093): "Load
   projects (from Module 1 via service interface): Query the `projects` table
   for this student. `has_projects` = True if student has any projects.
   `project_count` = number of projects."

3. **The ER diagram includes `Project`** (Section 8.3, line 2666):
   `Student --1:N--> Project`.

4. **API endpoints exist** (Section 9.3, lines 2743-2745): `POST /projects`,
   `GET /projects`, `DELETE /projects/{id}`.

5. **Module 1's database entities and responsibilities are updated** (Section
   3.3, lines 511, 514-517; Section 4.2, lines 640, 646-649).

6. **An index is recommended** (Section 8.4, line 2688): `projects (student_id)`.

**Conclusion:** F-DB-2 is fully resolved.

---

## 3. LOW/INFO Findings Quick Check

The prior review issued 10 LOW findings and 2 INFO confirmations. The
architect's revision summary (Section 19) claims all are RESOLVED or CONFIRMED.
The reviewer performed a quick verification of each:

| Finding | Severity | Status | Verification |
|---------|----------|--------|--------------|
| F-ASTAR-5 | LOW | FIXED | Worked example (Section 6.13) now shows g, h, f separately with correct values. Verified in Section 2.1 above. |
| F-FC-4 | LOW | FIXED | Default rule priority dependency documented (Section 7.4, lines 1848-1857) with explicit warning not to change to fire-all-applicable. Test `test_default_rule_lowest_priority` added. |
| F-SCORE-2 | LOW | FIXED | `MAX_PROFICIENCY_LEVEL = 3` named constant defined (Section 7.9, line 2194) and used in the formula (line 2226). Mapping documented in Section 5.3 (lines 909-912). |
| F-STACK-1 | LOW | FIXED | Custom spaCy `EntityRuler` added as primary NER (Section 4.4, lines 700-704; Section 4.5, lines 738-739). `en_core_web_md` noted as optional (Appendix A, line 4357). |
| F-STACK-2 | LOW | FIXED | `ruff` added to backend tooling (Section 18.6, line 4336); `eslint` + `prettier` to frontend (line 4337). Revision Note at line 265. |
| F-DB-3 | LOW | FIXED | `readiness_rules` table removed (Section 8.2, Revision Note lines 2649-2654; Decision 16.6, lines 3996-4025). JSON file is sole source of truth. |
| F-DB-4 | LOW | FIXED | Supersession semantics documented (Section 8.2.10, lines 2550-2553, 2569-2573). Application-level enforcement recommended. |
| F-API-1 | LOW | FIXED | `gap_reports` table added (Section 8.2.9, lines 2528-2546). `POST /gap-analysis` persists; `GET /gap-analysis` reads latest; `GET /gap-analysis/history` added (Section 9.4, lines 2764-2766). |
| F-API-2 | LOW | FIXED | Resume reprocessing semantics documented (Section 4.3, lines 678-683; Section 8.2.5, lines 2463-2483): delete prior `source='resume'` skills, re-insert fresh; `resume_id` FK added to `student_skills`. |
| F-SCOPE-2 | LOW | FIXED | "Optional/Stretch" column added to weekly map (Section 14.2, lines 3578-3583). Core vs. optional distinction stated (lines 3585-3588). |
| F-ACAD-2 | LOW | FIXED | Required structure of `docs/algorithms.md` specified (Section 18.5, lines 4298-4328) per AGENTS.md Section 12, including all required sections and additional content (admissibility proof, optimality claim, scoring formula, etc.). |
| F-SCOPE-1 | INFO | CONFIRMED | AI Role-Specific Assessment remains correctly excluded (Section 11.3, lines 3086-3094). No assessment endpoints or tables. |
| F-ACAD-1 | INFO | CONFIRMED | A* and FC remain genuinely designed. Prior caveats (F-ASTAR-1, F-FC-1, F-FC-2, F-FC-3, F-ASTAR-5) are resolved (with the F-NEW-1 caveat for FC). |

**Conclusion:** All LOW and INFO findings are genuinely addressed. No residual
issues at the LOW level.

---

## 4. Documentation Bloat Assessment

The document grew from 3,481 lines (v2.0) to 4,509 lines (v2.1) - an increase
of 1,028 lines (~29.5%). The reviewer assessed whether this growth is justified
or represents bloat.

### 4.1 Justified Growth

| Source | Approx. Lines | Justified? |
|--------|---------------|------------|
| A* admissibility proof rewrite (Section 6.8) | ~90 | Yes - the proof was the highest-severity finding and needed rigor. |
| A* consistency proof (new, Section 6.8) | ~14 | Yes - strengthens the academic defense. |
| A* worked example rewrite (Section 6.13) | ~55 | Yes - corrects a factual error and adds the Linux step. |
| A* optimality claim section (new Section 6.15) | ~30 | Yes - needed for precision. |
| FC multi-step chain explanation (Section 7.4) | ~35 | Yes - needed to demonstrate genuine chaining. |
| FC process diagram rewrite (Section 7.6) | ~70 | Yes - shows the multi-step chain. |
| `projects` table + wiring | ~30 | Yes - closes a correctness gap. |
| `progress_audit_log` table + wiring | ~30 | Yes - closes a correctness gap. |
| `gap_reports` table + wiring | ~20 | Yes - closes an API/schema gap. |
| Test strategy expansion (Sections 13.2, 13.3) | ~60 | Yes - verifies the new behaviors. |
| `docs/algorithms.md` structure spec (Section 18.5) | ~30 | Yes - satisfies AGENTS.md Section 12. |
| Revision Summary (Section 19) | ~62 | Useful for traceability but could be trimmed (see below). |

**Subtotal justified:** ~526 lines. This accounts for roughly half the growth.

### 4.2 Revision Note Callouts (Moderate Bloat)

The document contains **66 `Revision Note` callouts** scattered throughout.
Each callout is a blockquote (`> **Revision Note (F-XXX, SEV):** ...`) typically
3-6 lines long, totaling roughly **250-300 lines** of revision-note prose.

**Assessment:** These callouts are valuable for *auditability* (the reviewer can
trace each change to a finding), but they are **bloat for ongoing use**. Once
the review is accepted, a future reader does not need 66 callouts explaining what
changed from v2.0 - they need the current state. Many callouts are redundant
with the Section 19 revision summary.

**Recommendation (INFO, not a defect):** After this verification is accepted,
consider a v2.2 "clean" revision that removes the inline Revision Note callouts
(retaining only the Section 19 summary) to reduce the document to ~4,200 lines.
This is optional and should not delay implementation.

### 4.3 Redundancy Observed

| Redundancy | Location | Severity |
|------------|----------|----------|
| The "FC is sole classification authority" statement is repeated in ~8 places (Sections 7.1, 7.8, 7.10, 7.12, 16.4, Appendix B Q7, Appendix C, data flow). | Throughout Module 4 | LOW - repetition aids clarity but is verbose. |
| The "weak skills not planned by A*" statement is repeated in ~6 places (Sections 3.5, 6.3, 6.5, 6.12, 6.14, 16.3, Appendix C). | Throughout Module 3 | LOW - same as above. |
| The "binary state is Option A from the review" justification is repeated in ~4 places. | Sections 6.3, 6.16, 16.3, 17.4 | LOW - could be stated once and referenced. |
| The coverage metric definitions appear in Section 5.6 (lines 991-1008) AND are referenced in Section 7.2, 7.7, 7.12, 16.4. | Module 2 + Module 4 | Not redundant - single definition in Module 2, references elsewhere. This is correct. |

**Assessment:** The redundancy is mostly *intentional reinforcement* of key
design decisions, not accidental duplication. It is verbose but not harmful.
The document is long but remains navigable due to the Table of Contents and
clear section structure.

### 4.4 Overall Bloat Verdict

**Moderate bloat, mostly from Revision Note callouts.** The document is ~250-300
lines longer than necessary due to the 66 inline callouts, but the core content
is not bloated - the growth is driven by substantive fixes (proofs, examples,
new tables, tests). The document is usable as-is. A future "clean" revision
removing the callouts is recommended but not required.

---

## 5. New Issues Identified During Verification

### 5.1 F-NEW-1 - Forward Chaining Engine Overwrites Classification (HIGH)

**Severity: HIGH**

**Location:** Section 7.5 (Forward Chaining Engine, lines 1896-1922) and
Section 7.6 (Process Diagram, lines 2023-2037).

**Problem:**

The Forward Chaining engine fires *every* applicable, not-yet-fired rule (one
per iteration, highest priority first) until no more rules can fire. The rule
base (Section 7.4) has three classification rules that all conclude the *same*
fact key (`readiness_classification`):

- `rule_role_ready` (priority 80): concludes `readiness_classification =
  "role_ready"`
- `rule_nearly_ready` (priority 70): concludes `readiness_classification =
  "nearly_ready"`
- `rule_needs_improvement_default` (priority 10, empty conditions): concludes
  `readiness_classification = "needs_improvement"`

Consider the worked example in the process diagram (Section 7.6, lines
1972-2037) with facts: `skill_coverage_percent = 85.0`,
`learning_progress_percent = 75.0`, `core_skill_coverage_percent = 92.0`,
`min_core_proficiency = 2`.

Tracing the actual engine code (lines 1896-1922):

1. **Iteration 1:** `rule_core_skills_satisfied` (pri 100) - conditions met
   (92 >= 90, 2 >= 2). Fires. Asserts `core_skills_satisfied = true`. Marked
   fired.
2. **Iteration 2:** `rule_progress_on_track` (pri 90) - condition met (75 >=
   70). Fires. Asserts `progress_on_track = true`. Marked fired.
3. **Iteration 3:** `rule_role_ready` (pri 80) - conditions met
   (`core_skills_satisfied == true`, `progress_on_track == true`, 85 >= 80).
   Fires. Asserts `readiness_classification = "role_ready"`. Marked fired.
4. **Iteration 4:** `rule_nearly_ready` (pri 70) - conditions: `skill_coverage
   >= 60` (85 >= 60 YES) AND `learning_progress >= 50` (75 >= 50 YES).
   **Conditions are STILL MET.** Rule has NOT fired yet. Engine selects it
   (highest priority among applicable). **Fires. Asserts
   `readiness_classification = "nearly_ready"`. OVERWRITES the "role_ready"
   classification.** Marked fired.
5. **Iteration 5:** `rule_needs_improvement_default` (pri 10) - empty
   conditions, always applicable. Has NOT fired yet. **Fires. Asserts
   `readiness_classification = "needs_improvement"`. OVERWRITES again.** Marked
   fired.
6. **Iteration 6:** No more unfired rules. Stop.

**Final classification: `"needs_improvement"`** - NOT `"role_ready"` as the
process diagram (line 2033) claims.

**The process diagram is wrong.** Iteration 4 (lines 2024-2031) states:
"rule_nearly_ready: conditions NOT met (skill_coverage 85 >= 60 YES, but rule
already fired OR classification set)" and "No more NEW rules can fire -> STOP."
But the engine code:

- Does NOT check whether `readiness_classification` is already set before
  firing a rule.
- Does NOT skip rules whose conclusion would overwrite an existing fact.
- The `fired_ids` set only prevents the *same* rule from firing twice - it does
  not prevent *different* rules from overwriting the same fact key.

**Why it matters:**

This is a **correctness flaw in the core required algorithm**. The engine as
designed will *always* end with the lowest-priority classification rule's
conclusion (the default rule), because the default rule has empty conditions
and will always fire last, overwriting any prior classification. This means:

- The "Role Ready" and "Nearly Ready" classifications would *never* be the
  final output in practice.
- The entire FC pipeline is broken - it always produces "Needs Improvement."
- This directly contradicts the spec (PROJECT_SPEC.md Section 6) and the
  architecture's own claims (Section 7.10, Appendix C).
- In a viva, an examiner asking "show me the FC engine producing 'Role Ready'"
  would find it cannot.

This is the single most important issue in v2.1. It must be fixed before
implementation.

**Recommended Fix (one of):**

1. **Add a guard in the engine** (preferred): Before firing a rule whose
   `conclusion.fact_key == "readiness_classification"`, check whether
   `readiness_classification` is already set in working memory. If so, skip the
   rule. This makes the first classification authoritative.

   ```python
   def _fire_rule(self, rule: Rule):
       # Guard: do not overwrite an already-asserted classification
       if (rule.conclusion.fact_key == "readiness_classification"
           and "readiness_classification" in self.working_memory):
           return  # Classification already determined; skip
       self.working_memory[rule.conclusion.fact_key] = rule.conclusion.fact_value
       ...
   ```

2. **Add a condition to the lower-priority classification rules** requiring
   that the higher classification is NOT already set. For example,
   `rule_nearly_ready` could add a condition
   `{"fact_key": "readiness_classification", "operator": "==", "value": null}`
   (i.e., only fire if no classification is set yet). This requires supporting
   a "not set" check in `_conditions_met`.

3. **Change the engine to stop as soon as `readiness_classification` is
   asserted.** After each rule fires, check if
   `readiness_classification` is in working memory; if so, break. This is the
   simplest fix but changes the engine's termination semantics (it would no
   longer fire all possible rules - acceptable for this use case since
   classification is the terminal goal).

4. **Make the classification rules mutually exclusive** by adding negated
   conditions. For example, `rule_nearly_ready` adds
   `core_skills_satisfied != true` or `progress_on_track != true` as a
   condition, so it only fires if the role_ready conditions were NOT met. This
   is the most "rule-pure" approach but requires the engine to support
   "fact not present" or "fact != value" checks (the current `_conditions_met`
   returns False if a fact is None, which handles "not present" correctly).

**Recommendation:** Option 1 (engine guard) or Option 3 (early termination) is
simplest and most robust. Option 4 (mutual exclusion) is most academically
defensible as "genuine rule-based reasoning" but requires more rule
configuration discipline. The architect should choose one and update both the
engine code (Section 7.5) and the process diagram (Section 7.6) to match.

**Note:** This issue was *not* present in v2.0 because v2.0 had a separate
score-threshold if/else classifier that took precedence - so even if the FC
rules overwrote each other, the final classification came from the score
thresholds. By removing the score-threshold classifier (F-FC-1 fix), the
architect made FC the sole authority - which exposed this latent engine bug.
The fix for F-FC-1 is correct in intent; the engine just needs a guard to
realize that intent.

---

## 6. Architecture Status Verdict

```
ARCHITECTURE VERDICT: APPROVE WITH ONE REQUIRED FIX
```

### Justification

The Architect has done **excellent revision work**. Of the 3 HIGH and 8 MEDIUM
findings from the prior review:

- **2 of 3 HIGH findings are fully FIXED** (F-ASTAR-1, F-FC-2).
- **1 HIGH finding (F-FC-1) is fixed in intent** (FC is the sole classifier;
  score-threshold if/else is removed) **but the engine design has a new
  HIGH-severity defect** (F-NEW-1) that must be corrected before the fix is
  complete.
- **All 8 MEDIUM findings are fully FIXED** (F-ASTAR-2, F-ASTAR-3, F-ASTAR-4,
  F-MOD-2, F-FC-3, F-SCORE-1, F-MOD-1, F-DB-1, F-DB-2).
- **All 10 LOW findings are FIXED** and **both INFO confirmations hold**.

The A* pipeline is now internally consistent and academically defensible: the
heuristic is provably admissible and consistent, the cost function is
well-defined, the optimality claim is precise, weak-skill handling is
documented, and the worked example is correct.

The Forward Chaining pipeline is *almost* internally consistent: the rule base
has genuine multi-step inference chains, the dual scoring model is eliminated,
and FC is the sole classification authority. **However, the engine code does
not produce the classification the document claims** because lower-priority
classification rules overwrite the higher-priority conclusion. This is a
localized fix (add a guard or change rule conditions) and does not require
rearchitecting.

The database schema, API contracts, data flow, and module boundaries are all
consistent with the revised design. No new contradictions were found between
sections (other than the engine-vs-diagram contradiction in F-NEW-1).

### Required Action Before Implementation

**Fix F-NEW-1** (Forward Chaining engine classification overwrite). The
architect should:

1. Choose one of the four fix options in Section 5.1.
2. Update the engine code (Section 7.5) to implement the chosen fix.
3. Update the process diagram (Section 7.6, iteration 4) to accurately reflect
   the engine's behavior with the fix applied.
4. Add a test case (Section 13.3) verifying that once a classification is
   asserted, lower-priority classification rules do NOT overwrite it.
5. Re-submit for a quick verification of this single fix.

### Optional Improvements (Non-blocking)

- **Documentation bloat:** Consider a v2.2 "clean" revision removing the 66
  inline Revision Note callouts after this verification is accepted, reducing
  the document by ~250-300 lines. Not required for implementation.
- **Redundancy:** The "FC is sole authority" and "weak skills not planned"
  statements are repeated in 6-8 places each. Consolidating to a single
  authoritative statement with cross-references would improve maintainability
  but is not urgent.

### Status

```
Architecture v2.1 Status: APPROVED WITH ONE REQUIRED FIX (F-NEW-1)

Once F-NEW-1 is corrected, the architecture is READY FOR IMPLEMENTATION.

All prior HIGH and MEDIUM findings are resolved (F-FC-1's resolution is
complete pending the F-NEW-1 engine fix, which is part of realizing F-FC-1's
intent).
```

---

*End of Architecture Verification Report.*
