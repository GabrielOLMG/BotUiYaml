# Action System (BotActionDispatcher)

## 1. Overview

The Action System is responsible for routing YAML-defined actions to their corresponding Python implementations.

It acts as the bridge between:

- parsed YAML steps
- execution engine (BotUI)
- concrete action classes

Each step defines an `action` field, which is resolved at runtime by the dispatcher.

---

## 2. Core Component

### BotActionDispatcher

The `BotActionDispatcher` is the central routing component of the BotUI execution system.

It maps action names to their corresponding implementation classes and executes them.

---

## 3. Action Registry (ACTION_MAP)

Actions are registered in a static mapping:

- `WRITE` → WriteAction
- `FIND` → FindAction
- `KEYS_SELECTIONS` → KeySelectionsAction
- `RUN_SCRIPT` → RunScriptAction
- `FIND_TEXT_BY_COLOR` → FindTextByColorAction
- `STOP_IF` → StopIfAction
- `UPLOAD_FILE` → UploadAction
- `DO_WHILE` → DoWhileAction

### Key Concept

The system is fully declarative:
- YAML defines the action name
- Dispatcher resolves it into a Python class
- Class executes the behavior

No dynamic or user-defined actions are allowed.

---

## 4. Dispatch Flow

The execution flow inside the dispatcher is:

```text
step_info → extract action name → lookup ACTION_MAP → instantiate class → run() → return result
```

---

## 5. Dispatch Method

**dispatch(step_info)**

This method is responsible for executing a single step.

**Steps:**
1. Extract action field from step
2. Resolve corresponding action class from ACTION_MAP
3. Instantiate action class with:
    - bot_driver
    - bot_app
    - step_info
4. Execute run() method
5. Handle result and logs
6. Apply global step behaviors(including taking a screenshot after the action)

---

## 6. Global Step Behaviors

After execution, the dispatcher applies optional global behaviors:

**Supported behaviors:**
- ``refresh``
    - reloads the browser or UI context
- ``wait``
    - pauses execution for N seconds
- ``save_url``
    - stores the current URL into a variable

---

## 7. Debug Mode

If a step contains:

```yaml
debug: true
```

The execution is intentionally stopped after that step.

This is used for:
- debugging pipelines
- isolating step failures
- validating execution flow

---

## 8. Error Handling

If an action is not registered in ACTION_MAP:
- the dispatcher returns an error:
    - "Action Not Implemented: ``<action>``"

If an action fails during execution:
- the error is propagated from the action class
- dispatcher does not retry automatically

---

## 9. Integration with BotUI
The dispatcher is initialized inside the BotUI execution engine:
- BotUI creates the dispatcher once
- It is reused for all steps
- It depends on:
    - bot_driver (UI interface)
    - bot_app (state + config + variables)

--- 

## 10. Responsibilities Summary
The dispatcher is responsible for:
- action resolution
- action instantiation
- execution delegation
- global step behavior application
- basic execution flow control

It does NOT:
- interpret YAML
- manage pipelines
- handle variable preprocessing
- implement UI logic itself