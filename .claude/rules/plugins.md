# Plugins — Rufus Eval Engine

## What are plugins

Plugins are packaged bundles of tools, skills, and instructions that extend what Claude
can do within a project. Think of a plugin as a self-contained capability — it knows
exactly how to do one thing well and can be invoked on demand.

In Claude Code, plugins live in `.claude/skills/` and are invoked via slash commands
or the Skill tool.

---

## Plugins planned for this project

### eval-runner (Phase 7+)

**Purpose:** Run a single end-to-end evaluation — question in, scored result out —
without needing to know which scripts to call, what flags to pass, or where the output lives.

**When to use:** During debugging in Phase 7 and Phase 8 when you want to generate
fresh eval data to test the API or dashboard.

**Invocation:** `/eval-runner --question-id q_001 --mock`

**What it does:**
1. Verifies `USE_MOCK=true` is set (refuses to run if not)
2. Runs `backend/scripts/run_eval.py` for the specified question
3. Fetches the result from SQLite
4. Prints a formatted score summary

**Status:** Not yet created. Build it at the start of Phase 7.

---

### adversarial-runner (Phase 7+)

**Purpose:** Run the full adversarial suite and display a formatted failure mode report.

**Invocation:** `/adversarial-runner --mock`

**Status:** Not yet created. Build it at the start of Phase 7.

---

## How to create a plugin

1. Create a folder: `.claude/skills/plugin-name/`
2. Add `SKILL.md` — describes what the plugin does, how to invoke it, and what it returns
3. Reference the plugin in CLAUDE.md so Claude knows it exists

Plugin structure:
```
.claude/skills/eval-runner/
  SKILL.md         # plugin definition
  references/      # any supporting docs the plugin needs
```

---

## Plugin vs slash command vs subagent

| | Best for |
|---|---|
| **Slash command** (`.claude/commands/`) | Triggering a specific workflow step (e.g., "document phase 2") |
| **Plugin / Skill** (`.claude/skills/`) | Encapsulating a reusable capability with its own knowledge |
| **Subagent** (`.claude/agents/`) | Delegating to a domain specialist (backend, frontend) |

Use a plugin when the capability is self-contained, reusable across phases, and has
its own supporting reference material.

---

## Current plugins

| Plugin | Location | Status |
|--------|----------|--------|
| anatomy-of-sde | `.claude/skills/anatomy-of-sde/` | Active (used to scaffold this project) |
| eval-runner | `.claude/skills/eval-runner/` | Planned — Phase 7 |
| adversarial-runner | `.claude/skills/adversarial-runner/` | Planned — Phase 7 |
