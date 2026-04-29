# FIND Action

## Overview

The FIND action is the core of BotUi. It is responsible for locating elements on the screen using Computer Vision or OCR, enabling precise interactions, conditional flow control, and dynamic navigation.

The new structure clearly separates **what** to look for, **where** to focus the search, **how** to persist if not immediately found, and **which** action to execute upon success.

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
  text: "Target" # If TEXT
  image_path: "path/to/img.png" # If IMG
  name: str # Default: None
  
  search_area:      # Performance optimization
    row: int # Default: None
    column: int # Default: None
    grid_rows: int # Default: 3
    grid_cols: int # Default: 3
  
  search_strategy:  # Persistence & Navigation
    scroll: bool # Default: False
    direction: str # Default: DOWN
  
  interaction:      # Consequence If Find
    type: CLICK | UPLOAD
```

---

## Fields

### 1. Core Target Fields (The "What")

| Field | Type | Description |
| :--- | :--- | :--- |
| **action** | str | Must be `FIND`. |
| **object_type** | str | Detection mode: `TEXT` or `IMG`. |
| **text** | str | Target text (Required if `object_type: TEXT`). |
| **in_text** | bool | If `true`, allows partial text matching. |
| **position** | int | Index of the occurrence if multiple identical results exist (Default: `0`). |
| **image_path** | str | Path to the template image (Required if `object_type: IMG`). |

### 2. Search Area (The "Where")
Defines a grid over the image to process only a specific crop, increasing speed and accuracy.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **row** | int | `None` | The specific grid row to search within. |
| **column** | int | `None` | The specific grid column to search within. |
| **grid_rows** | int | `3` | How many horizontal slices the screen is divided into. |
| **grid_cols** | int | `3` | How many vertical slices the screen is divided into. |

### 3. Search Strategy (The "How to find")
Defines the bot's behavior if the element is not found in the current view.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **scroll** | bool | `false` | Whether to scroll the page to find the element. |
| **direction** | str | `DOWN` | Scroll direction (`UP`, `DOWN`). |

### 4. Interaction (The "Consequence")
Actions executed immediately after a successful localization.

| Field | Type | Description |
| :--- | :--- | :--- |
| **type** | str | Interaction type: `CLICK` or `UPLOAD`. |
| **file_path** | str | Path of the file to send (Required if `type: UPLOAD`). |
| **offset** | dict | Pixel fine-tuning from the detected center (`x`, `y`). |

---

## Execution Flow

1. **Area Cropping:** If ``search_area`` is defined, it will take the screenshot and divide it into grids using ``grid_rows`` or ``grid_cols``. If a ``row`` or ``column`` is defined, the find will ``only be applied to those positions``.

2. **Localization:** ``BotTargetLocator`` attempts to find the target (Text or Image).

3. **Strategy:** If not found and ``scroll: true``, the bot scrolls in the specified ``direction`` and repeats step 2.

4. **Interaction:** Upon success, the bot applies the ``offset`` (if any) and executes the interaction ``type``.

5. **Finalization:**
    - Saves coordinates if ``save_as`` is present.
    - Proceeds to the ``next`` step ``(True/False)`` if defined.

---

## Examples

### 1. Basic text search and click

```yaml
- action: FIND
  object_type: TEXT
  text: "Login"
  interaction:
    type: CLICK
```

### 2. Image-based detection

```yaml
- action: FIND
  object_type: IMG
  image_path: "buttons/login_button.png"
  interaction:
    type: CLICK
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
  name: "setup_upload"
  object_type: TEXT
  text: "upload"
  search_area:
    row: 2 
    column: 2
    grid_rows: 3    
    grid_cols: 3 
  interaction:
    type: UPLOAD  
    file_path: "data/dataset.csv"
```

In this case, what we're doing is finding the Upload button and making a upload action

### 5. Find with click + offset adjustment

Useful when the clickable area is not exactly centered.

```yaml
- action: FIND
  object_type: TEXT
  text: "Submit"
  interaction:
    type: CLICK  
    offset:
      y: 30
```

### 6. Next Condition

```yaml
- action: FIND
  object_type: TEXT
  text: "success"
  next: 
    True: case_true
    False: case_false

- action: WRITE
  name: case_true
  text: "NICE" 

- action: WRITE
  name: case_false
  text: "WRONG" 
```
In this example, we are checking if an object has been found. If it has, it goes to the step in the True branch(``True: case_true``); otherwise, it goes to the step in the False branch(``False: case_false``).

### 7. Scroll until element is found

```yaml
- action: FIND
  object_type: TEXT
  text: "End Of Page"
  search_strategy:
    scroll: true
```

### 8. Optional Find

```yaml
- action: FIND
  object_type: TEXT
  text: "Success"
  next: 
    True: write
    False: write

- action: WRITE
  name: write
  text: "Ok"
```

This is a case where we have a step that, regardless of whether or not it successfully finds the object, will proceed to the next step, simulating what would be an optional step.

### 9. Debug mode (visual inspection)

```yaml
- action: FIND
  object_type: IMG
  image_path: "icon.png"
  debug: true
```

### 10. Until Find object

```yaml
- action: FIND
  name: check_loaded_file
  object_type: TEXT
  text: "Loaded"
  next: 
    True: write
    False: check_loaded_file

- action: WRITE
  name: write
  text: "Ok"
```
This is a case where we are repeating the same find until we find the desired object; it will only continue when available.

---

## Tip

- The `FIND` action is designed to be robust against UI changes. Prefer:
    - `TEXT` when possible (more stable across layouts)
    - `IMG` when text is dynamic or not accessible via OCR
- Performance: Always use search_area when you know the approximate region of the element. Processing 1/9 of the image (3x3 grid) is significantly faster than a full-screen OCR.

- Robustness: Using position: 0 ensures that if two "Confirm" buttons appear in the same area, the bot always picks the first one.

- Debug: Set debug: true at the action level to see the [R_C] (Row/Column) visual markers on the generated debug image. This helps verify if your search_area configuration is correct.

---

## Scroll Behavior

When an element is not found, the `FIND` action can recover using different strategies.


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
