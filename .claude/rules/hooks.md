# Hooks — Rufus Eval Engine

## What are hooks

Hooks are shell commands that Claude Code runs automatically before or after certain tool calls.
They fire silently in the background and output warnings or logs to keep you informed.
They do not block execution — they are informational guardrails.

---

## Hooks configured in settings.json

### 1. Budget Guard Hook (PreToolUse — Bash)

**Fires when:** Claude runs any Bash command containing `generate_products`, `run_eval`, or `run_adversarial`

**What it does:** Checks whether `USE_MOCK=true` is set in `backend/.env`. If not, prints a clear warning before the command runs.

**Why it exists:** These three scripts are the only ones that call the Anthropic API. A single careless `run_eval` on a large batch without mocks could burn the entire $10 budget. This hook makes that impossible to do silently.

**Expected output (safe):**
```
[BUDGET HOOK] USE_MOCK=true confirmed
```

**Expected output (warning):**
```
[BUDGET HOOK] WARNING: USE_MOCK is not true — this script may call the Anthropic API
and incur real costs. Set USE_MOCK=true in backend/.env to use mocks.
```

---

### 2. Test Reminder Hook (PostToolUse — Write)

**Fires when:** Claude writes any file (the hook checks if it was a `.py` file)

**What it does:** Prints a reminder that tests for this file will be run during the TDD gate at the end of the phase.

**Why it exists:** Keeps the workflow clean — tests are batched to the TDD gate, not run after every individual file write.

**Expected output:**
```
[TEST HOOK] Python file written. Tests will be run in the TDD gate at the end of this phase.
```

---

## Adding new hooks

To add a hook, edit `.claude/settings.json` under the `hooks` key:

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "ToolName",
      "hooks": [
        {
          "type": "command",
          "command": "your-shell-command"
        }
      ]
    }
  ]
}
```

Available hook events: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`

Matchers can be exact tool names (`Bash`, `Write`, `Read`) or glob patterns.

---

## Hook limitations

- Hooks cannot block or cancel a tool call — they are informational only
- Hook commands run in a shell; keep them fast (under 1 second)
- Hook output is shown to Claude as context, not directly to the user
- Do not write complex logic in hook commands — use a script file if needed
