# BaseAction

## 1. Overview

`BaseAction` is the abstract base class that defines the common structure and behavior for all BotUI actions.

Every executable action in BotUI (e.g. FIND, WRITE, UPLOAD_FILE) inherits from this class.

It ensures a consistent execution interface and provides shared utilities for all actions.

---

## 2. Purpose

The BaseAction layer exists to:

- standardize action execution
- provide shared utilities (driver, logger, variable management)
- enforce a consistent `run()` interface
- reduce duplication across action implementations
- centralize access to BotUI runtime context

---

## 3. Core Concept

Every action in BotUI follows the same lifecycle:

```text
Initialize → Execute run() → Return (success, log)
```
The BaseAction class defines this contract.

---

## 4. Class Structure

Constructor

Each action receives:
- bot_driver → UI automation interface
- bot_app → global application context
- step_info → parsed YAML step definition
These are stored as instance attributes and used throughout execution.

---

## 5. Required Interface

**run()**

Each action MUST implement:

``def run(self) -> tuple[bool, str | None]``

The BaseAction class defines this contract.

---

## 6. Example Usage (Conceptual)
A typical action implementation:

```python
class ExampleAction(BaseAction):
    def run(self):
        self.get_logger().info("Executing action")

        self.capture("before")

        result = self.bot_driver.do_something()

        self.set_var("result", result)

        self.capture("after")

        return True, None
```

---

## 7. Summary
BaseAction is the foundational abstraction of the BotUI action system.

It ensures that all actions:
- follow a consistent interface
- share common utilities
- remain decoupled from each other
- integrate cleanly with the execution engine