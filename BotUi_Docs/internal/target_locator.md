# BotTargetLocator (Detection Engine)

## 1. Overview

`BotTargetLocator` is the perception engine of BotUI.

It is responsible for locating targets on the screen using different detection strategies, such as:

- image matching
- text recognition (OCR)
- future extensible methods

It abstracts how targets are found and returns a unified result to the action layer.

---

## 2. Core Purpose

The goal of this component is to:

- locate UI elements based on different detection strategies
- unify detection outputs into a standard format
- provide coordinate resolution for actions
- support debugging and visualization
- allow easy extension for new detection methods

---

## 3. Detection Types

Detection is controlled by the `DETECTOR_TYPES` registry:

```python
DETECTOR_TYPES = {
    "IMG": {"required": {"template_path"}, "function": "image_target_center"},
    "TEXT": {"required": {"target_text"}, "function": "text_target_center"}
}
```

Each type defines:
- required input parameters
- the function used for detection

---

## 4. Supported Detection Methods

### 4.1 Image Detection (IMG)
Locates a target by matching a template image against the current screen.

Strategies used:
- template matching
- feature-based matching (e.g. SIFT)

The system attempts multiple strategies sequentially until one succeeds.

### 4.2 Text Detection (TEXT)
Locates a target by detecting text within the screen.

Strategy used:
- OCR-based detection (e.g. RapidOCR)

Supports:
- partial text matching (in_text)
- positional selection (position)
    - Given that you might have the same word or text repeated on the screen, you can activate debug mode and view all positions. Once you've done that, you can select exactly the one you need.
- directional filtering (side)
    - ``LEFT`` or ``RIGHT``

---

## 5. Standard Detection Output
All detection methods must return a standardized result:

```text
(target_found, error_log, target_center, debug_image)
```

Where:
- target_found → boolean indicating success
- error_log → error message (if any)
- target_center → (x, y) coordinate of the detected target
- debug_image → optional debug visualization

This standardization ensures consistency across all detection strategies.

---

## 6. Detection Flow
The main entry point is the dealer() method:

```text
validate inputs → select detection method → execute → post-process → return result
```

**Step-by-step:**
- Validate detector_type
- Validate required parameters
- Select detection function dynamically
- Execute detection strategy
- Store original coordinates
- Apply coordinate shift (if any)
- Generate debug output (if enabled)
- Return unified result

---

## 7. Coordinate System

The locator returns the center of the detected target:
```text
(x, y)
```

This coordinate is used by the driver for interactions (e.g. click).

**Offset System**
Coordinates can be adjusted using:
- offset_x
- offset_y

This allows shifting the interaction point relative to the detected target, example:

```text
original: (100, 200)
offset: (+10, -5)
result: (110, 195)
```

---

## 7. Debug System
If debug mode is enabled:
- detection results can be visualized
- coordinates are marked on the image
- shift between original and final position is displayed

Two modes exist:
- use provided debug image (if available)
- generate debug visualization manually

---


## 8. Validation System
Each detector enforces required arguments based on its configuration.

Example:
- IMG requires: template_path
- TEXT requires: target_text

Missing parameters result in immediate failure.

---

## 9. Extensibility
The system is designed to be easily extensible.

To add a new detection method:

1. Implement a new detection function
2. Ensure it returns the standard output format
3. Register it in DETECTOR_TYPES

**Example (future extension)**
```python
"HTML_ID": {
    "required": {"element_id"},
    "function": "html_id_target_center"
}
```

This allows integration with:
- DOM-based detection
- accessibility APIs
- custom drivers

---

## 10. Relationship with FIND Action
``BotTargetLocator`` does not perform any UI interaction.
It only:
- detects targets
- returns coordinates

The FIND action is responsible for:
- deciding what to do with the result
- clicking
- scrolling
- retrying

---

## Summary
``BotTargetLocator`` is the core detection engine of BotUI.

It provides:
- flexible detection strategies
- standardized outputs
- coordinate resolution
- debugging capabilities
- extensibility for future detection methods

It enables the system to "see" the interface in a structured and reliable way.