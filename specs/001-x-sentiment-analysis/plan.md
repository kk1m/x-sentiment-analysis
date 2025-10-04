
# Implementation Plan: X Sentiment Analysis System

**Branch**: `001-x-sentiment-analysis` | **Date**: 2025-10-04 | **Spec**: `/specs/001-x-sentiment-analysis/spec.md`
**Input**: Feature specification from `/specs/001-x-sentiment-analysis/spec.md`

**Implementation Status (2025-10-04 EOD):**
- ✅ 43/57 tasks completed (75%)
- ⚠️ Implementation deviated from original plan (see spec.md for updated requirements)
- ✅ Core system working: community collection, sentiment analysis, weighting, API
- 📝 This plan reflects original design; see root docs for as-built documentation

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a sentiment analysis system for X (Twitter) focusing on the "Irresponsibly Long $MSTR" community. Collect top 5 posts 4x per week (Mon/Wed/Fri/Sun), classify as Bullish/Bearish/Neutral, weight by visibility, influence, verification, and bot-likelihood, store raw and aggregate data, and expose historical trends via API. Support multiple algorithms and design for future public web deployment.

**Note:** Original plan was daily collection from hashtags; actual implementation is community-focused with 4x weekly schedule due to free tier constraints (100 tweets/month).

## Technical Context
**Language/Version**: Python 3.10+  
**Primary Dependencies**: FastAPI (API), pandas/numpy (processing), APScheduler (scheduling), httpx or tweepy (X API), matplotlib/plotly (viz), pydantic (models)  
**Storage**: SQLite (dev), PostgreSQL-ready (prod) via SQLAlchemy  
**Testing**: pytest, pytest-mock  
**Target Platform**: Local dev; deployable to Linux cloud (API + job runner)
**Project Type**: web (backend API now; optional frontend later)  
**Performance Goals**: Daily batch completes < 1 hour for 500 posts; API p95 < 2s for 30-day queries  
**Constraints**: LLM budget $0/month (MVP uses keyword-based); X API free tier 100 tweets/month read; English-only v1.0  
**Scale/Scope**: Initial dataset small (free tier: ~85 tweets/month). Architecture must scale to paid tiers.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Signal Quality Over Noise: Plan includes bot detection and weighting to reduce artificial engagement.
- Multi-Dimensional Weighted Analysis: Weighting by visibility, influence, verification is planned and configurable.
- Algorithm Flexibility & Comparison: Multiple algorithms supported with tracking and comparison.
- Batch Processing & Historical: EOD batch job, raw+aggregate storage, 1+ year retention.
- Web-Ready Architecture: API-first backend, separable presentation layer.
- Iterative Refinement: Versioned models/weights, reprocessing supported.
- Complete Data Capture: Full post metadata + daily aggregates stored; lineage tracked.

Initial Check: PASS

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── api/                 # FastAPI routers
│   ├── jobs/                # batch jobs (daily collection)
│   ├── models/              # ORM models / pydantic schemas
│   ├── services/            # X API client, sentiment, bot detection, weighting
│   ├── storage/             # repositories / DB session mgmt
│   └── main.py              # app entrypoint
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

scripts/
└── run_daily_batch.sh       # helper to trigger job locally/cron

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh windsurf`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v1.1.0 - See `/memory/constitution.md`*
