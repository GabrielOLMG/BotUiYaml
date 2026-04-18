# FIND Action

## Overview

The `FIND` action is responsible for locating elements on the screen using visual or text-based detection.

It is the core interaction mechanism of BotUi, as it enables the system to:

- Locate UI elements
- Retrieve coordinates
- Trigger clicks
- Drive conditional flows (retry, scroll, optional logic)

---

## Supported Detection Types

The `FIND` action supports multiple detection strategies via the `object_type` field:

- `TEXT` → finds elements based on OCR text detection
- `IMG` → finds elements based on image template matching

Internally, all detection methods are delegated to the `BotTargetLocator`, which abstracts how targets are found.

---

## Step Structure

```yaml
- action: FIND
  object_type: TEXT | IMG
```

---

## Fields

### Required Fields

| Field       | Type | Description                      |
| ----------- | ---- | -------------------------------- |
| action      | str  | Must be `FIND`                   |
| object_type | str  | Detection mode (`TEXT` or `IMG`) |

### TEXT Mode Fields

Used when ``object_type: TEXT``

| Field    | Type | Description                                  |
| -------- | ---- | -------------------------------------------- |
| text     | str  | Target text to locate                        |
| in_text  | bool | If true, allows partial match                |
| position | int  | Occurrence index when multiple matches exist |
| side     | str  | Optional directional constraint              |

### IMG Mode Fields

Used when ``object_type: IMG``

| Field      | Type | Description                              |
| ---------- | ---- | ---------------------------------------- |
| image_path | str  | Path to template image used for matching |

### Optional Interaction Fields

| Field   | Type | Description                                 |
| ------- | ---- | ------------------------------------------- |
| click   | bool | Click on the detected element               |
| save_as | str  | Stores detected coordinates into a variable |
| x_coord | int  | X offset applied to detected center         |
| y_coord | int  | Y offset applied to detected center         |

### Optional Flow Control Fields

| Field      | Type | Description                               |
| ---------- | ---- | ----------------------------------------- |
| scroll     | bool | Enables scrolling if element is not found |
| debug      | bool | Saves debug image output                  |

---

## Execution Flow

1. A screenshot is captured
2. ``BotTargetLocator`` is initialized
3. Detection method is selected based on object_type
4. Target is searched using:
    - TEXT → OCR-based detection
    - IMG → template matching / SIFT
5. If found:
    - Coordinates are returned
    - Optional click or save is executed
6. If not found:
    - Scroll or retry logic may be applied
    - Or step fails depending on configuration

---

## Examples

### 1. Basic text search and click

```yaml
- action: FIND
  object_type: TEXT
  text: "Login"
  click: true
```

### 2. Image-based detection

```yaml
- action: FIND
  object_type: IMG
  image_path: "buttons/login_button.png"
  click: true
```

### 3. Find with partial text match

Useful when the UI text is dynamic or slightly different.

```yaml
- action: FIND
  object_type: TEXT
  text: "Welcome"
  in_text: true
```

In this example, if "Welcome" is in a phrase like "Welcome User", it will still be able to find it because it contains the located text.

### 4. Save coordinates for later use

```yaml
- action: FIND
  object_type: TEXT
  text: "Upload"
  save_as: UPLOAD_BUTTON_COORD

- action: UPLOAD_FILE
  file_path: "data.csv"
  coord: $UPLOAD_BUTTON_COORD
```

In this case, what we're doing is finding the Upload button so we can then use it in conjunction with the UPLOAD_FILE action, for example.

### 5. Find with click + offset adjustment

Useful when the clickable area is not exactly centered.

```yaml
- action: FIND
  object_type: TEXT
  text: "Submit"
  click: true
  x_coord: 10
  y_coord: -5
```


### 7. Scroll until element is found

```yaml
- action: FIND
  object_type: TEXT
  text: "End Of Page"
  scroll: true
```



### 9. Debug mode (visual inspection)

```yaml
- action: FIND
  object_type: IMG
  image_path: "icon.png"
  debug: true
```

### 10. Complex interaction (real-world flow)

```yaml
- action: FIND
  object_type: TEXT
  text: "Username"
  click: true

- action: WRITE
  text: $USERNAME

- action: FIND
  object_type: TEXT
  text: "Password"
  click: true

- action: WRITE
  text: $PASSWORD

- action: FIND
  object_type: TEXT
  text: "Login"
  click: true

- action: FIND
  object_type: TEXT
  text: "Welcome $USERNAME"
  until_find: retry
```

---

## Tip

The `FIND` action is designed to be robust against UI changes.

Prefer:

- `TEXT` when possible (more stable across layouts)
- `IMG` when text is dynamic or not accessible via OCR

---

## Constraints & Invalid Configurations

The following combinations are not allowed:

### scroll + until_find

These two mechanisms conflict because both control retry behavior in different ways.

```yaml
- action: FIND
  object_type: TEXT
  text: "Login"
  scroll: true
  until_find: retry  # Invalid
```

---

## Retry & Scroll Behavior

When an element is not found, the `FIND` action can recover using different strategies.

### Retry behavior (`until_find: retry`)

- Re-executes the FIND action immediately
- Limited by internal retry counter
- Does not perform page interaction


### Scroll behavior (`scroll: true`)

- Performs a page scroll action
- Captures a new screenshot
- Re-attempts detection after scroll


### Page change validation

After scrolling, the system verifies if the page changed using screenshot comparison.

If no visual change is detected:

- Scroll attempts are stopped
- FIND fails or falls back to retry logic

---

## Failure Modes

A FIND action can fail due to:

- Element not present in current viewport
- OCR mismatch (TEXT mode)
- Image mismatch (IMG mode)
- Page not fully loaded
- Scroll limit reached
- Retry limit exceeded

In these cases, behavior depends on configuration:

- `scroll`
