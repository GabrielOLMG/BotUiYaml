# PlaywrightDriver

## Overview

The `PlaywrightDriver` is the **default concrete implementation** of the `BotDriver` abstraction.

It is responsible for executing all automation actions in a **real web browser environment**, using Playwright as the underlying engine.

This driver enables BotUi to:

- Control a Chromium browser instance
- Interact with web pages via coordinates
- Capture screenshots for visual detection
- Simulate keyboard and mouse behavior
- Handle file uploads and scrolling

It is the current **primary execution backend** for BotUi.

---

## Architecture Role

The system is structured as:

```text
BotUi Engine
↓
Actions (Find, Write, Upload, etc.)
↓
BotDriver (interface)
↓
PlaywrightDriver (implementation)
↓
Chromium Browser
```

This driver is the **bridge between BotUi logic and the real browser**.

---

## Initialization

The driver starts a Playwright-controlled browser instance:

### Key parameters

| Parameter | Description |
|----------|------------|
| `viewport` | Browser window size |
| `headless` | Runs browser without UI if True |

### Behavior

- Launches Chromium
- Creates a browser context
- Opens a new page
- Keeps session alive for the entire BotUi execution

---

## Implemented Capabilities

### 1. Navigation

#### `goto(url, wait_time=5.0)`

Navigates to a URL and waits for network stabilization.

- Uses `networkidle` strategy
- Applies additional manual wait (`wait_time`)
- Returns success/failure status


#### `reload()`

Reloads the current page.

### 2. Interaction

#### `click(coord, delay_ms=100)`

Clicks at screen coordinates.

Behavior:

- Moves mouse to position
- Applies optional delay
- Executes click event

Supports:

- Tuple `(x, y)`
- Dictionary `{x: ..., y: ...}`


#### `write(text)`

Writes text into the currently focused input.

- Uses Playwright keyboard input
- Does not require selectors
- Works after a `click` or focus action


#### `upload_file(file_path, coord)`

Uploads a file via UI interaction.

Flow:

1. Resolves absolute file path
2. Clicks upload input via coordinates
3. Waits for file chooser
4. Injects file into dialog


#### `scroll(direction, delta_x=0, delta_y=100, coord=None)`

Simulates mouse scroll.

Behavior:

- Optional mouse positioning before scroll
- Direction-based inversion (`UP` reverses delta_y)
- Uses wheel events


#### `key_sequence(keys)`

Executes keyboard sequences.

Supports:

- Modifier keys (CTRL, ALT, SHIFT)
- Special keys (ENTER, TAB, BACKSPACE, etc.)
- Raw text typing

Behavior:

- Presses modifiers down
- Executes key actions
- Releases modifiers at end

---

## Observation Layer

### `get_url()`

Returns current browser URL.

### `get_screenshot(output_path)`

Captures a screenshot of the current page.

Returns:

- File path
- Raw image bytes

Behavior:

- Ensures `.png` extension
- Uses Playwright screenshot API
- Stores image for downstream detection (FIND action)

---

## Lifecycle Management

### `close()`

Safely terminates the driver session.

It performs multiple cleanup steps:

1. Closes browser instance
2. Stops Playwright engine
3. Kills orphan processes (zombie cleanup)

This ensures:

- No memory leaks
- No hanging browser processes
- Clean shutdown in automation pipelines

---

## Error Handling Strategy

Most methods return:

```text
(success: bool, error: str | None
```

This allows:

- Centralized error handling in Actions layer
- Pipeline-level decision making
- Optional retries and fallback logic

---

## Summary

The `PlaywrightDriver` is the **execution engine of BotUi for web automation**.

It translates high-level actions into real browser interactions using coordinate-based control and screenshot-driven logic.
