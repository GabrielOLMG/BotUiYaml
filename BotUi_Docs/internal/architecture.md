# BotUI Architecture Overview

## 1. System Overview

BotUI is a declarative automation engine that executes UI workflows defined in YAML.

The system is divided into two main layers:

- **BotUIApp** → orchestration and configuration layer
- **BotUI** → execution engine

Together, they transform YAML definitions into deterministic UI automation flows.

---

## 2. High-Level Architecture

The execution flow can be summarized as:

```text
YAML → BotUIApp (setup & preprocessing) → BotUI (execution engine) → Actions → UI Driver
```

---

## 3. BotUIApp (Orchestration Layer)

BotUIApp is responsible for preparing the execution environment before runtime.

**Responsibilities**
- Load main YAML configuration
- Load optional global YAML configuration
- Validate YAML structure
- Initialize logging system
- Create output directories (logs, screenshots, debug files)
- Manage variable storage (data_store)
- Initialize UI driver instance
- Preprocess YAML (variable resolution + loop expansion)
- Expand FOR_EACH structures into executable steps
- Inject resolved variables into steps
- Instantiate supporting components (e.g., Media Manager)
- Launch BotUI execution engine

**Key Concept**

BotUIApp does not execute automation steps.
It prepares a fully resolved execution plan.

---

## 4. BotUI (Execution Engine)

BotUI is responsible for executing the preprocessed YAML.

**Responsibilities**
- Iterate over pipelines
- Execute pipelines sequentially
- Manage execution lifecycle
- Execute individual steps
- Dispatch actions via Action Dispatcher
- Interface with the UI driver
- Handle execution success/failure
- Ensure clean shutdown of the driver

**Key Concept**

BotUI executes a fully expanded and validated workflow with no dynamic structure changes at runtime.

---


## 5. Execution Flow (Step-by-Step)

**Step 1 — Initialization (BotUIApp)**

- Load YAML files
- Validate configuration schema
- Initialize global variables
- Resolve variable references
- Preprocess pipeline structure
    - Resolve Variables
    - Expand loops (FOR_EACH)


**Step 2 — Engine Start (BotUI)**

- Start execution logging
- Load pipelines
- Iterate through pipelines sequentially

**Step 3 — Pipeline Execution**

For each pipeline:
- Navigate to URL (if defined)
- Execute steps sequentially

**Step 4 — Step Execution**

For each step:
- Resolve runtime variables
- Dispatch action through ActionDispatcher
- Execute UI interaction via driver
- Log result

**Step 5 — Shutdown**
- Close driver
- Finalize execution logs

--- 

## 6. Separation of Concerns

| Component        | Responsibility                   |
| ---------------- | -------------------------------- |
| BotUIApp         | Setup, validation, preprocessing |
| BotUI            | Execution engine                 |
| ActionDispatcher | Maps actions to implementations  |
| Driver           | Executes UI interactions         |

## 7. Summary

BotUIApp prepares a fully expanded and validated execution plan.

BotUI executes that plan deterministically, step by step, using a controlled action system.