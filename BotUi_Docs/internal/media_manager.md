# Media Manager (BotMediaManager)

## 1. Overview

The `BotMediaManager` is responsible for capturing, storing, and analyzing visual state information during BotUI execution.

It acts as the media and observability layer of the system, enabling debugging, change detection, and execution traceability.

It is instantiated inside `BotUIApp` and used throughout the execution lifecycle.

---

## 2. Responsibilities

The BotMediaManager is responsible for:

- Capturing screenshots from the UI driver
- Storing captured media in memory (history)
- Tracking the latest screenshot path
- Recording metadata about each capture
- Computing image hashes for change detection
- Providing access to execution visual history
- Detecting UI state changes between steps
- Generate a final gif with all the process

---

## 3. Core Concept

Each capture represents a snapshot of the UI at a given execution moment.

A snapshot includes:

- image data
- file path
- optional label
- computed hash (for comparison)

---

## 4. Initialization

The manager is initialized inside `BotUIApp`:

- receives `bot_driver`
- receives `output_path`
- receives `logger`

It also initializes:

- `history` → list of captured media
- `last_path` → most recent screenshot path

---

## 5. Screenshot Capture

### capture(label: str | None)

This is the main method of the class.

### Flow:

1. Request screenshot from driver
2. Save image to disk
3. Compute hash from raw bytes
4. Store metadata in history
5. Log capture event (if label exists)
6. Update last captured path

### Stored metadata:

Each entry contains:

- type: "image"
- label: optional identifier
- data: raw image bytes
- path: file system path
- hash: image fingerprint

---

## 6. Change Detection

### has_page_changed(last_n: int = 2)

This method compares screenshot hashes to detect UI changes.

### Behavior:

- If history < 2 → returns True
- Otherwise compares:
  - latest image hash
  - previous image hash (or N steps back)

### Purpose:

Used to detect whether the UI state has changed between steps.

This is useful for:

- detecting page updates
- validating action effects
- debugging stuck states

---

## 7. History Management

### get_history()

Returns all captured media entries.

---

### get_last_image_info()

Returns the most recent image entry from history.

Iterates backwards through the history list.

---

### record(media)

Internal method used to append a media entry into history.

---

## 8. Output Path Tracking

The manager keeps track of:

- `last_path` → last saved screenshot file

This allows external components to reference the latest capture.

---

## 9. Integration with BotUI System

BotMediaManager is used by:

- BotUIApp (initialization)
- BotActionDispatcher (automatic capture after each step)
- Debug workflows

It acts as a shared observability layer across the entire execution engine.

---

## 11. Future Extensions (Optional Design Space)

The commented code suggests future capabilities such as:

- GIF generation of execution flow
- MP4 recording of automation sessions
- frame normalization via PIL/OpenCV
- video export of bot execution

These features would transform BotUI into a full execution recording system.

---

## 12. Summary

The BotMediaManager is a lightweight observability system that:

- captures UI snapshots
- stores execution history
- enables state comparison