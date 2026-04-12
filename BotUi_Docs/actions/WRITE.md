# WRITE Action

## Description

The `WRITE` action inputs text into the currently focused UI element.

It can either:

- write a direct string
- load content from a file and write it

This action assumes that the correct input field is already focused.

---

## Required Fields

One of the following fields must be provided:

- `text` → string value to be written
- `file_path` → path to a file whose content will be written

---

## Constraints

- Exactly one of `text` or `file_path` must be provided
- Using both fields at the same time is not allowed
- Providing none of them will result in failure

---

## Behavior

1. The action validates which field is present (`text` or `file_path`)
2. If `file_path` is used:
   - the file is opened
   - its content is loaded into memory
3. The resolved value is sent to the driver via `write()`
4. The driver handles the actual UI interaction

---

## Examples

### Example 1 — Writing a variable
```yaml
- action: WRITE
  text: $NAME
```

### Example 2 — Writing static text
```yaml
- action: WRITE
  text: "Hello World"
```

### Example 3 — Writing from a file
```yaml
- action: WRITE
  file_path: "data/input.txt"
```
---

## Common Usage Pattern
Typically used after a ``FIND`` action that focuses an input field:

```yaml
- action: FIND
  object_type: TEXT
  text: Username
  click: true

- action: WRITE
  text: admin
```

---

## Execution Details (Simplified)

```text
validate input → resolve value → driver.write(value)
```

Notes
- This action does not handle focus or navigation
- It only writes content to the active element
- File reading is handled internally before writing
- Any failure in file loading or driver execution will cause the step to fail