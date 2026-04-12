# STOP_IF Action

## Description

The `STOP_IF` action conditionally stops the execution of the pipeline.

If the provided condition evaluates to `True`, the pipeline is immediately terminated.

---

## Required Fields

- `condition` → string expression to be evaluated

---

## Behavior

1. The condition string is evaluated at runtime
2. If the condition evaluates to `True`:
   - the pipeline stops immediately
   - the action returns a failure state to interrupt execution
3. If the condition evaluates to `False`:
   - execution continues normally
4. If an error occurs during evaluation:
   - the action returns an error log

---

## Condition Evaluation

The condition is evaluated as a Python-like expression.

Supported elements include:

- `True`, `False`, `None`
- basic functions:
  - `str()`
  - `len()`
  - `bool()`

The result is always converted to a boolean.

---

## Examples

### Example 1 — Stop unconditionally (debug)

```yaml
- action: STOP_IF
  condition: "True"
```

### Example 2 — Stop based on variable

```yaml
- action: STOP_IF
  condition: "$ERROR_FLAG == True"
```

### Example 3 — Stop if string is empty
```yaml
- action: STOP_IF
  condition: "len($USERNAME) == 0"
```

---

## Execution Details (Simplified)

```text
evaluate condition → if True → stop pipeline
```

Important Notes
- This action intentionally interrupts the pipeline
- A ``True`` condition is treated as a controlled stop (not a crash)
- Invalid expressions will produce an error log
- Variables used in the condition must already exist

---

## Common Use Cases
- Debugging pipelines
- Early exit on error conditions
- Conditional flow control
- Validating state before continuing execution