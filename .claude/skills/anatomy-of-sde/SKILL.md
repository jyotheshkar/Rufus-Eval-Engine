---
name: anatomy-of-sde
description: >
  Build production-grade SDE (Software Development Environment) scaffolding using the Claude Code `.claude/` folder architecture — including CLAUDE.md files, commands, rules, skills, and agents. Use this skill whenever a user wants to set up or scaffold a `.claude/` folder, create CLAUDE.md project instructions, build custom slash commands, define modular rules files, create Claude skills, set up subagent personas, configure settings.json permissions, or structure a project so Claude Code understands it deeply. Also trigger for phrases like "set up Claude for my project", "create a CLAUDE.md", "make a custom command", "build a skill folder", "add an agent", "help Claude remember my project", or "configure Claude Code". For frontend work within this skill, always use Next.js + Tailwind CSS + shadcn/ui as the mandatory stack.
---

# Anatomy of SDE — Claude Code Project Structure Skill

This skill builds and scaffolds the full `.claude/` folder architecture for any software project, following the canonical Claude Code anatomy. It also handles frontend scaffolding using the mandatory stack: **Next.js + Tailwind CSS + shadcn/ui**.

---

## The `.claude/` Folder — Mental Model

```
your-project/
├── CLAUDE.md                    ← team instructions, committed to git
├── CLAUDE.local.md              ← personal overrides, gitignored
└── .claude/                     ← the control center
    ├── settings.json            ← permissions + config, committed
    ├── settings.local.json      ← personal permissions, gitignored
    ├── commands/                ← custom slash commands
    │   ├── review.md            → /project:review
    │   ├── fix-issue.md         → /project:fix-issue
    │   └── deploy.md            → /project:deploy
    ├── rules/                   ← modular instruction files
    │   ├── code-style.md
    │   ├── testing.md
    │   └── api-conventions.md
    ├── skills/                  ← auto-invoked workflows
    │   ├── security-review/
    │   │   └── SKILL.md
    │   └── deploy/
    │       └── SKILL.md
    └── agents/                  ← subagent personas (isolated)
        ├── code-reviewer.md
        └── security-auditor.md
```

---

## Component Reference

### 1. CLAUDE.md (Team Instructions)
- Committed to git — visible to everyone
- Contains: project overview, tech stack, conventions, workflow rules
- Written in Markdown; Claude reads it at session start
- Loading order (highest priority wins): `CLAUDE.local.md` → `./CLAUDE.md` → `~/.claude/CLAUDE.md` → Managed Policy
- All layers merge into the system prompt at session start

**Template:**
```markdown
# Project: [Name]

## Stack
[List tech stack]

## Conventions
[Code style, naming, file structure rules]

## Workflow
[PR process, testing requirements, deploy steps]

## Claude Instructions
[Specific instructions for Claude behavior in this project]
```

---

### 2. Custom Commands (`.claude/commands/`)
- Each `.md` file becomes a `/project:<filename>` slash command
- The `!` backtick prefix runs shell commands before Claude sees the prompt — injects real context
- Always a single `.md` file

**Example — `review.md`:**
```markdown
description: Review the current diff for bugs and security issues

!git diff HEAD~1

Review the above diff. Check for:
- Logic errors and edge cases
- Security vulnerabilities
- Performance regressions
- Missing tests
```

**Triggered as:** `/project:review`

---

### 3. Rules (`.claude/rules/`)
- Modular instruction files loaded into context
- Split by concern: style, testing, API conventions, etc.
- Referenced from CLAUDE.md or auto-loaded

---

### 4. Skills (`.claude/skills/`)
- Each skill is a **folder** with a `SKILL.md` plus optional supporting files
- Claude invokes them **automatically** based on context matching the description
- Good for: context-aware, multi-step, reusable workflows
- Structure: `SKILL.md` with YAML frontmatter (`name`, `description`) + optional `scripts/`, `references/`, `assets/`

**Difference from Commands:**
| | Commands | Skills |
|---|---|---|
| Trigger | You type `/project:name` | Claude detects context automatically |
| Structure | Single `.md` file | Folder with SKILL.md + supporting files |
| Best for | Repeatable manual workflows | Context-aware automatic workflows |

---

### 5. Agents (`.claude/agents/`)
- Subagent personas — fully isolated (fresh context window)
- Main agent spawns subagent with a task; subagent returns compressed findings
- Prevents context pollution on long tasks
- Each agent file defines: role, capabilities, output format

**Example — `code-reviewer.md`:**
```markdown
# Code Reviewer Agent

You are a senior code reviewer. You receive a diff or file and return a structured review.

## Output Format
- **Summary**: One-line verdict
- **Issues**: Bullet list of problems (severity: high/medium/low)
- **Suggestions**: Actionable fixes
- **Verdict**: APPROVE / REQUEST_CHANGES
```

---

### 6. Settings (`settings.json` / `settings.local.json`)
```json
{
  "permissions": {
    "allow": ["Bash(git:*)", "Read(**)", "Write(src/**)"],
    "deny": ["Bash(rm -rf *)"]
  }
}
```
- `settings.json` → committed, shared with team
- `settings.local.json` → personal, gitignored

---

### 7. Two-Folder Scope Model
- `your-project/.claude/` → **team config**, committed to git, whole team shares
- `~/.claude/` → **personal config**, never committed, only you see it
  - Contains: `CLAUDE.md` (global preferences), `projects/`, `commands/`
- Both load on every session

---

## Frontend Scaffolding — Mandatory Stack

When the SDE skill involves frontend work, **always use**:

### Required Stack
- **Next.js** (App Router) — framework
- **Tailwind CSS** — utility-first styling
- **shadcn/ui** — component library

### Recommended Additions (choose as appropriate)
- **TypeScript** — always, no exceptions
- **Zod** — schema validation
- **React Hook Form** — form handling
- **Tanstack Query** — server state
- **Prisma** — ORM if DB is needed
- **next-auth / Clerk** — authentication
- **Lucide React** — icons
- **Framer Motion** — animations

### Project Structure (Next.js App Router)
```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── (routes)/
├── components/
│   ├── ui/          ← shadcn components live here
│   └── [feature]/   ← feature-specific components
├── lib/
│   ├── utils.ts     ← cn() helper etc.
│   └── [domain].ts
├── hooks/
└── types/
```

### shadcn/ui Setup Commands
```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint --app
cd my-app
npx shadcn@latest init
npx shadcn@latest add button card input label form table dialog
```

### CLAUDE.md Template for Next.js Projects
```markdown
# [Project Name]

## Stack
- Next.js 14+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- shadcn/ui components

## Conventions
- All components in `src/components/`
- shadcn components in `src/components/ui/` — never edit these directly
- Custom components in `src/components/[feature]/`
- Use `cn()` from `lib/utils` for conditional classes
- Server components by default; add `"use client"` only when needed
- All API routes in `src/app/api/`

## Code Style
- No default exports except for pages and layouts
- Prefer named exports for components
- Props interfaces defined above the component
- Use Zod for all external data validation
```

---

## Workflow — How to Use This Skill

### Step 1: Identify Scope
Ask or infer:
- Solo developer or team project?
- Existing project or greenfield?
- Frontend involved? (triggers mandatory Next.js/Tailwind/shadcn stack)
- What workflows need automation? (→ commands or skills)
- Any autonomous agents needed?

### Step 2: Build the Structure
Create in order:
1. `CLAUDE.md` — project context first
2. `settings.json` — permissions
3. `commands/` — any repeatable manual workflows
4. `rules/` — style, testing, conventions
5. `skills/` — auto-invoked workflows
6. `agents/` — if autonomous subagents needed

### Step 3: For Frontend Projects
- Scaffold Next.js + Tailwind + shadcn/ui
- Generate `CLAUDE.md` with stack-specific conventions
- Create commands for common workflows (`/project:dev`, `/project:build`, `/project:lint`)
- Add rules for component patterns, TypeScript conventions

### Step 4: Git Strategy
```
# Commit these:
CLAUDE.md
.claude/settings.json
.claude/commands/
.claude/rules/
.claude/skills/
.claude/agents/

# Gitignore these:
CLAUDE.local.md
.claude/settings.local.json
```

---

## Quick Reference — When to Use What

| Goal | Tool |
|---|---|
| Project-wide Claude instructions | `CLAUDE.md` |
| Personal tweaks only you need | `CLAUDE.local.md` |
| Automate a repeatable task | Command in `.claude/commands/` |
| Context-aware auto workflow | Skill in `.claude/skills/` |
| Isolated complex sub-task | Agent in `.claude/agents/` |
| Control what Claude can touch | `settings.json` permissions |
| Frontend project scaffolding | Next.js + Tailwind + shadcn/ui |

---

## Reference Files

- `references/nextjs-conventions.md` — Detailed Next.js App Router patterns
- `references/shadcn-patterns.md` — Component usage patterns
- `references/settings-schema.md` — Full settings.json schema

Read these when the user needs deep-dive detail on a specific area.
