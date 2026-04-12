# KEYS_SELECTIONS Action

## Description

The `KEYS_SELECTIONS` action sends a sequence of keyboard inputs to the system.

It allows simulating user interactions such as typing shortcuts, navigation, and key combinations.

---

## Required Fields

- `keys` → list of keys to be executed in sequence

---

## Behavior

1. The action validates that a list of keys is provided
2. The keys are sent to the driver in the specified order
3. The driver executes the key sequence
4. If an error occurs, it is returned as a log

---

## Examples

### Example 1 — Press Enter

```yaml
- action: KEYS_SELECTIONS
  keys:
    - Enter
```

### Example 2 — Select all (Ctrl + A) and Clear input field

```yaml
- action: KEYS_SELECTIONS
  keys:
    - CTRL
    - A
    - DELETE
```

### Example 3 — Navigate using TAB

```yaml
- action: KEYS_SELECTIONS
  keys:
    - TAB
    - TAB
    - TAB
```

---

## Execution Details (Simplified)

```text
send keys → driver.key_sequence(keys)
```

**Notes**
- Keys are executed in the exact order provided
- This action depends on the current UI focus
- It does not locate elements (use FIND if needed)
- It can be used as an alternative to FIND in some navigation scenarios
- Complex keyboard interactions depend on driver implementation

---

## Common Use Cases
- Form navigation using TAB
- Clearing input fields (CTRL + A + DELETE)
- Submitting forms (Enter)
- Triggering shortcuts (e.g. CTRL + C, CTRL + V)