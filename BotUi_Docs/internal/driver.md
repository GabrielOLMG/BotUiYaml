# BotDriver (Abstract Layer)

## Overview

The `BotDriver` is the **core abstraction layer** of BotUi.

It defines a unified interface for interacting with external environments such as:

- Web browsers (e.g. Playwright, Selenium)
- Desktop automation tools
- Future integrations (mobile, APIs, etc.)

Instead of the system depending on a specific automation tool, all interactions are routed through this abstraction.

This design ensures:

- Interchangeability between drivers
- Decoupling between logic and execution engine
- Extensibility for new automation backends

---

## Design Principle

The system is built around the idea:

> “BotUi does not interact with the environment directly — it delegates everything to a driver.”

All actions (`FIND`, `WRITE`, `CLICK`, etc.) depend exclusively on this interface.

---

## Responsibilities

A `BotDriver` implementation is responsible for:

### 1. Navigation

- Opening URLs
- Reloading pages
- Maintaining session state

### 2. Interaction

- Clicking elements
- Writing text
- Uploading files
- Sending keyboard shortcuts
- Scrolling pages

### 3. Observation

- Taking screenshots
- Reading current URL
- Providing visual state for detection systems

### 4. Lifecycle management

- Closing sessions cleanly

---

## Interface Definition

All concrete drivers must implement the following methods:

### Navigation

| Method | Description |
|--------|------------|
| `goto(url, wait_time)` | Navigates to a URL |
| `reload()` | Reloads current page |

---

### Interaction

| Method | Description |
|--------|------------|
| `click(coord, delay_ms)` | Clicks at screen coordinates |
| `write(text)` | Writes text into focused input |
| `upload_file(file_path, coord)` | Uploads file via UI interaction |
| `scroll(direction, delta_x, delta_y, coord)` | Scrolls page |
| `key_sequence(keys)` | Executes keyboard shortcuts |

---

### Observation

| Method | Description |
|--------|------------|
| `get_url()` | Returns current URL |
| `get_screenshot(output_path)` | Captures screen and returns image data |

---

### Lifecycle

| Method | Description |
|--------|------------|
| `close()` | Terminates driver session |

---

## Key Design Decision

### 1. Coordinate-based interaction

All interactions use **coordinates instead of DOM selectors**.

This is intentional:

- Works for any UI (web, desktop, virtual environments)
- Enables image-based automation (`FIND` + click)
- Removes dependency on HTML structure

---

### 2. Screenshot-first architecture

The system assumes:

> “Everything starts from a screenshot.”

Detection systems (`TEXT`, `IMG`, OCR, SIFT, etc.) operate on images provided by this driver.

---

### 3. Stateless execution layer

The driver does NOT:

- interpret YAML
- manage pipelines
- decide logic

It only executes primitive actions.

---

## Relationship with BotUi

The architecture is layered:

```text
Pipeline (YAML)
↓
BotUI Engine (Flow control)
↓
Actions (Find, Write, Upload...)
↓
BotDriver (execution layer)
↓
External system (browser / OS)
```

---

## Extensibility

To support a new automation backend:

You only need to implement `BotDriver`.

Example:

- `PlaywrightDriver` (web)
- `DesktopDriver` (PyAutoGUI / OS-level automation) (not implemented)
- `MobileDriver` (not implemented)

No changes are required in:

- Actions
- Pipeline engine
- Target locator
- YAML structure

---

## Why this abstraction matters

Without this layer:

- Every action would depend on a specific tool
- Switching Playwright → Selenium would break everything
- Testing would be harder

With this layer:

- The system becomes tool-agnostic
- You can evolve the engine without rewriting logic

---

## Summary

`BotDriver` is the **execution backbone** of BotUi.

It is intentionally minimal, stable, and replaceable — everything else is built on top of it.
