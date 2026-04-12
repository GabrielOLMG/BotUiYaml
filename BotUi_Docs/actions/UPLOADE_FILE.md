# UPLOAD_FILE Action

## Description

The `UPLOAD_FILE` action uploads a file to the UI by interacting with a specific screen coordinate.

It simulates a click on the provided coordinate and sends the file to the system file picker.

---

## Required Fields

- `file_path` → path to the file to be uploaded
- `coord` → screen coordinate where the upload interaction will occur

---

## Constraints

- Both `file_path` and `coord` are required
- The file must exist at the specified path
- The coordinate must be valid and correctly formatted

---

## Behavior

1. The action validates the provided inputs:
   - parses and validates the coordinate
   - checks if the file exists

2. If validation passes:
   - the driver performs the upload using `upload_file(file_path, coord)`

3. If validation fails:
   - the action stops and returns an error

---

## Examples

### Example 1 — Using saved coordinates

```yaml
- action: UPLOAD_FILE
  file_path: "data/file.csv"
  coord: $UPLOAD_COORD
```

### Example 2 — Using direct coordinates

```yaml
- action: UPLOAD_FILE
  file_path: "data/file.csv"
  coord: "[400, 300]"
```

---

## Coordinate Format

Coordinates can be provided as:
- a list: ``[x, y]``
- a string: ``"[x, y]"``
- a variable: ``$COORD_VAR``

They are internally parsed into a numeric format.

---

## Common Usage Pattern

Typically used after locating an upload button:

```yaml
- action: FIND
  object_type: TEXT
  text: Upload
  save_as: UPLOAD_COORD

- action: UPLOAD_FILE
  file_path: "dataset.csv"
  coord: $UPLOAD_COORD
```

---

## Execution Details (Simplified)

```text
validate coord → validate file_path → driver.upload_file(file_path, coord)
```

Notes
- This action does not locate elements — it relies on coordinates
- Coordinates are usually obtained from a previous FIND action
- If the file does not exist, the action will fail immediately
- If the coordinate is invalid, the action will not execute