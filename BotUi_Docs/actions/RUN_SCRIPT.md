# RUN_SCRIPT Action

## Description

The `RUN_SCRIPT` action executes an external script and optionally stores its output for later use.

It allows BotUI to integrate with external systems, APIs, or custom logic outside the YAML environment.

---

## Required Fields

- `script_path` → path to the script to be executed

---

## Optional Fields

- `flags` → arguments passed to the script
- `save_as` → variable name to store the script output

---

## Behavior

1. The action validates that the script exists
2. The script is executed using a shell (`bash`)
3. Optional flags are passed as command-line arguments
4. The script output (`stdout`) is captured
5. If `save_as` is provided:
   - the output is stored in a variable
6. If execution fails:
   - an error log is returned

---

## Output Handling

- The output corresponds to what the script prints (`stdout`)
- The output is always treated as a string
- It can be reused in later steps via variables

---

## Examples

### Example 1 — Simple script execution

```yaml
- action: RUN_SCRIPT
  script_path: "scripts/test.sh"
```

### Example 2 — Script with flags

```yaml
- action: RUN_SCRIPT
  script_path: "scripts/api_call.sh"
  flags: "--user Luciano --verbose"
```
### Example 3 - Save output to variable

```yaml
- action: RUN_SCRIPT
  script_path: "scripts/check_status.sh"
  save_as: STATUS
```

### Example 4 — Use output in STOP_IF

```yaml
- action: RUN_SCRIPT
  script_path: "scripts/check_error.sh"
  save_as: ERROR_FLAG

- action: STOP_IF
  condition: "$ERROR_FLAG == True"
```

### Example 5 — Use output in WRITE

```yaml
- action: RUN_SCRIPT
  script_path: "scripts/get_username.sh"
  save_as: USERNAME

- action: WRITE
  text: $USERNAME
```

---

## Execution Details (Simplified)

```text
validate script → run script → capture stdout → optionally store output
```

**Notes**
- Scripts are executed using bash
- Flags can be provided as:
    - a string (split into arguments)
    - a list of arguments
- Only stdout is captured as output
- If the script fails, the action returns an error
- The output is not automatically parsed (remains a string)

---

## Common Use Cases
- Calling external APIs
- Running custom business logic
- Fetching dynamic data
- Integrating with external systems
- Pre-processing values before UI interaction