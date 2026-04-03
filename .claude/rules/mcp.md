# MCP (Model Context Protocol) — Rufus Eval Engine

## What is MCP

MCP lets Claude connect directly to external tools and data sources — databases, APIs,
file systems — without you having to copy-paste output into the chat. Claude can query
them directly and use the results in its reasoning.

---

## MCP server configured in this project

### SQLite Server

**Purpose:** Lets Claude query `backend/data/eval_results.db` directly to inspect eval
results, debug scoring issues, and verify data integrity — without needing you to run
queries and paste output.

**Config in settings.json:**
```json
"mcpServers": {
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "backend/data/eval_results.db"],
    "disabled": true
  }
}
```

**Status:** Disabled until Phase 6. The DB does not exist before Phase 6.

---

## How to enable the SQLite MCP server (Phase 6+)

In `.claude/settings.json`, change `"disabled": true` to `"disabled": false`:

```json
"mcpServers": {
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "backend/data/eval_results.db"],
    "disabled": false
  }
}
```

Then restart Claude Code. The server will install automatically via `npx` on first use.

---

## What Claude can do with SQLite MCP active

- Query `eval_results` to check that scores were saved correctly after a pipeline run
- Debug anomaly detection: query scores by category to verify the rolling window
- Count records to verify checkpoint criteria (e.g., "are there 200 results stored?")
- Inspect specific failing evals by `id` without you needing to open a DB browser

**Example queries Claude will run:**
```sql
SELECT COUNT(*) FROM eval_results;
SELECT category, AVG(score_overall) FROM eval_results GROUP BY category;
SELECT * FROM eval_results WHERE anomaly_flagged = 1 LIMIT 5;
```

---

## MCP and the mock guard

MCP gives Claude read access to the database — it cannot trigger API calls.
The mock guard (`USE_MOCK=true`) is unrelated to MCP and still applies to
all `run_eval.py` and `run_adversarial.py` script calls.

---

## Future MCP servers (not configured yet)

| Server | Purpose | When |
|--------|---------|------|
| Vercel MCP | Check deployment status, view logs | Phase 9 |
| Railway MCP | Monitor backend deployment | Phase 9 |

To add them, follow the same pattern in `settings.json` under `mcpServers`.
