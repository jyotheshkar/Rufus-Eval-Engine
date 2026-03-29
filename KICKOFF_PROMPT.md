# KICKOFF PROMPT — paste this once into Claude Code in VS Code

---

Read the file `.claude/CLAUDE.md` in full before doing anything else.

This is the Rufus Eval Engine project — a production-style LLM evaluation
framework for an AI shopping assistant. The entire project context, architecture,
file structure, tech stack, rules, and phase plan live in that file.

After reading CLAUDE.md, confirm you understand:
1. What the project does
2. The full file structure you will build
3. The CRITICAL budget rule (USE_MOCK=true during all development)
4. The 9-phase build plan

Do not write any code yet. Just read, confirm understanding, and wait for me
to say "start phase 1".

When I say "start phase X" — read .claude/commands/phaseX.md and follow it
exactly, step by step, until phase complete criteria are met.

When I say "I need help with the backend" — read .claude/agents/backend-agent.md
When I say "I need help with the frontend" — read .claude/agents/frontend-agent.md

---

IMPORTANT RULES FOR THIS SESSION:
- Never call the Anthropic API in a loop during development
- Always use mock responses (USE_MOCK=true) unless I explicitly say "run live"
- Ask me before running any script that costs API credits
- Tell me clearly when a phase is complete and what was built
