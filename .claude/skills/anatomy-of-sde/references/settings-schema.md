# settings.json Schema Reference

## Full Schema

```json
{
  "permissions": {
    "allow": [],
    "deny": []
  },
  "env": {},
  "includeCoAuthoredBy": true,
  "cleanupPeriodDays": 30
}
```

## Permissions — Tool Patterns

### Bash Permissions
```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",              // All git commands
      "Bash(npm:*)",              // All npm commands
      "Bash(npx:*)",              // All npx commands
      "Bash(node:*)",             // All node commands
      "Bash(python:*)",           // All python commands
      "Bash(ls:*)",               // ls commands
      "Bash(cat:*)",              // cat commands
      "Bash(echo:*)"              // echo commands
    ],
    "deny": [
      "Bash(rm -rf *)",           // Destructive delete
      "Bash(sudo:*)",             // No sudo
      "Bash(curl:*)",             // No external requests
      "Bash(wget:*)"              // No downloads
    ]
  }
}
```

### File Permissions
```json
{
  "permissions": {
    "allow": [
      "Read(**)",                  // Read anything
      "Write(src/**)",             // Write only in src/
      "Write(tests/**)",           // Write only in tests/
      "Write(.claude/**)"          // Can update own config
    ],
    "deny": [
      "Write(.env*)",              // Never touch env files
      "Write(*.secret)",           // Never touch secret files
      "Read(/etc/**)"              // No system files
    ]
  }
}
```

## Common Permission Profiles

### Web Dev Project
```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(node:*)",
      "Read(**)",
      "Write(src/**)",
      "Write(public/**)",
      "Write(tests/**)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Write(.env*)"
    ]
  }
}
```

### Python / ML Project
```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(pip:*)",
      "Bash(python:*)",
      "Bash(pytest:*)",
      "Read(**)",
      "Write(src/**)",
      "Write(tests/**)",
      "Write(notebooks/**)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Write(.env*)",
      "Write(data/raw/**)"
    ]
  }
}
```

### Read-Only Audit Mode
```json
{
  "permissions": {
    "allow": ["Read(**)"],
    "deny": ["Write(**)", "Bash(**)"]
  }
}
```

## Environment Variables
```json
{
  "env": {
    "NODE_ENV": "development",
    "LOG_LEVEL": "debug"
  }
}
```
These are injected into every Bash session Claude runs.

## includeCoAuthoredBy
```json
{ "includeCoAuthoredBy": true }
```
When `true`, Claude appends a `Co-authored-by: Claude` trailer to git commits. Set to `false` to suppress.

## File Locations
- `.claude/settings.json` — project-level, commit to git
- `.claude/settings.local.json` — personal overrides, gitignore
- `~/.claude/settings.json` — global personal defaults
