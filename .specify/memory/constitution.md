<!--
SYNC IMPACT REPORT
==================
Version change: [template placeholders] → 1.0.0 (initial population)
Modified principles: none (first constitution ratification)
Added sections:
  - Core Principles: I. Markdown as Single Source of Truth
  - Core Principles: II. RAG Replacement via Direct File I/O
  - Core Principles: III. Zero Tolerance for Hallucinations
  - Security & Architecture Guidelines (3 rules: sandbox, append-only, local privacy)
  - Technical Standards & Modernization (3 rules: Python 3.14, uv, I/O resilience)
  - Governance
Removed sections: none
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ aligned — Constitution Check gates are dynamic
  - .specify/templates/spec-template.md ✅ aligned — no mandatory sections to add
  - .specify/templates/tasks-template.md ✅ aligned — security/I/O task types already present
  - .specify/templates/checklist-template.md ✅ aligned — no changes required
  - docs/Projeto.md ✅ aligned — existing implementation reflects all constitution principles
Follow-up TODOs: none — all placeholders resolved
-->

# Agente Nexus (LLM-Wiki) Constitution

## Core Principles

### I. Markdown as Single Source of Truth

The system MUST strictly follow the LLM-Wiki pattern. All agent identity, context, and memory
MUST reside in local Obsidian Markdown files within the vault (`./meu_vault/`). No external
databases, vector stores, or cloud-synced state are permitted as primary knowledge sources.
External services MUST NOT be used as the authoritative record of agent state.

### II. RAG Replacement via Direct File I/O

This project explicitly discards the complexity of vector databases, chunking pipelines, and
embedding models. Knowledge retrieval MUST occur through direct text file I/O operations on
the vault. Any proposal to introduce RAG components MUST be rejected unless a formal
constitution amendment is ratified with full written justification.

### III. Zero Tolerance for Hallucinations

The Nexus Agent MUST NOT fabricate characteristics about itself or assert facts not grounded
in vault content. When information is absent from the vault, the agent MUST respond that it
does not know, or MUST invoke the appropriate vault-reading tool to retrieve the information
before answering. Speculative or invented responses about agent identity or history are
strictly prohibited.

## Security & Architecture Guidelines

1. **Directory Isolation (Sandbox):** The agent MUST only read from and write to the
   `./meu_vault/` directory. All tool functions MUST validate that resolved paths remain
   within this boundary before any file system access occurs. Any path containing directory
   traversal sequences (e.g., `../../`) MUST be rejected — this protection applies to
   both intentional requests and prompt-injection attempts.

2. **Append-Only Memory:** Memory writes MUST NEVER overwrite prior history. All new
   knowledge entries MUST be appended to the end of the history file using Markdown
   bullet-point format (`- `). Destructive overwrites of `memoria/historico.md` are
   strictly forbidden.

3. **Local-by-Default Privacy:** All processing MUST occur strictly on the local machine.
   No user data, vault content, or agent state may be transmitted to external services or
   APIs unless a future amendment explicitly authorizes a specific integration with a
   clearly defined scope and rationale.

## Technical Standards & Modernization

1. **Runtime Environment:** The project MUST use **Python 3.14** exclusively. All code,
   scripts, and tooling MUST target this version. Compatibility shims for older Python
   versions are not permitted.

2. **Package Management:** **uv (Astral)** is the mandatory tool for virtual environment
   management and dependency resolution. All dependencies MUST be declared and locked via
   `uv.lock`. No other package managers (pip, poetry, pipenv) may be used as the primary
   tool for this project.

3. **I/O Resilience:** All disk-access tool functions MUST handle exceptions gracefully.
   Conditions such as `FileNotFoundError`, `PermissionError`, and encoding errors MUST be
   caught and returned as human-readable error strings so the LLM can understand and
   communicate the failure without crashing the agent loop.

## Governance

This constitution supersedes all other project practices and documentation. Amendments require:

- A written rationale explaining what principle is changing and why.
- An updated version number following semantic versioning (MAJOR.MINOR.PATCH).
- A review of all dependent templates to propagate consistency.

**Versioning Policy:**
- MAJOR: Backward-incompatible governance changes — removal or redefinition of a principle.
- MINOR: New principle or section added, or materially expanded guidance.
- PATCH: Clarifications, wording corrections, or non-semantic refinements.

**Compliance:** All implementation plans, specs, and task lists MUST verify alignment with
this constitution before proceeding. The `## Constitution Check` gate in `plan.md` is the
primary enforcement point. Violations MUST be documented in the Complexity Tracking section
of `plan.md` with a full justification and a description of simpler alternatives that were
rejected.

**Version**: 1.0.0 | **Ratified**: 2026-04-29 | **Last Amended**: 2026-04-29
