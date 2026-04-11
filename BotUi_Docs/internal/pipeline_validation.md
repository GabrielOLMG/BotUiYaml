# Pipeline Configuration System

## 1. Overview

The Pipeline Configuration System defines the formal schema of a BotUI automation file.

It is responsible for validating and enforcing the structure of all YAML inputs before execution.

This layer ensures that every pipeline, step, and action conforms to a strict contract defined by the system.

---

## 2. Core Purpose

This module acts as the **schema enforcement layer** of BotUI.

It guarantees:

- valid pipeline structure
- valid step definitions
- strict action field validation
- prevention of unknown or unsupported fields

No execution can happen without passing this validation layer.

---

## 3. GlobalConfig

### Description

The `GlobalConfig` class defines optional global configuration for the entire BotUI execution.

### Structure

- `variables` → optional dictionary of global variables

### Purpose

Used to define shared variables accessible across pipelines.

---

## 4. Step Model

### Description

The `Step` model represents the smallest executable unit in BotUI.

Each step corresponds to a single action execution.

---

### Core Field

- `action` (string)
  - defines which action will be executed
  - must exist in `ACTION_SCHEMA`

---

### Dynamic Schema Validation

Each step is validated against a predefined schema (`ACTION_SCHEMA`).

This schema defines:

- required fields
- optional fields
- mutually required fields (`required_one_of`)

---

### Validation Rules

Each step must satisfy:

#### 1. Action validation
- Action must exist in `ACTION_SCHEMA`

#### 2. Required fields
- All required fields must be present
- Must match expected types

#### 3. Required-one-of fields
- At least one field in the group must be present
- If present, must match expected types

#### 4. Optional fields
- If provided, must match expected types

#### 5. Unknown fields protection
- Any field not defined in schema is rejected

---

### Design Intent

This strict validation system ensures:

- deterministic execution
- no unexpected runtime behavior
- full control over YAML structure
- early failure on invalid definitions

---

## 5. Pipeline Model

### Description

A Pipeline represents a sequence of ordered steps executed sequentially.

---

### Structure

- `url` (optional)
  - initial navigation target

- `steps`
  - list of Step objects
  - must contain at least one step

---

### Validation Rules

- A pipeline must contain at least one step
- Steps are validated individually using the Step model

---

### Execution Meaning

A pipeline represents a single automation flow.

Each pipeline runs independently and sequentially.

---

## 6. PipelineConfig (Root Model)

### Description

`PipelineConfig` is the root model of a BotUI YAML file.

It defines the full structure of an automation file.

---

### Structure

- `config` → optional global configuration
- `pipelines` → dictionary of named pipelines

---

### Pipeline Constraints

- Pipeline names must be unique
- Duplicate pipeline names are rejected

---

## 7. Validation Flow

The validation process happens in layers:

### Step 1 — Root validation
- PipelineConfig is validated first

### Step 2 — Pipeline validation
- Each pipeline is validated individually

### Step 3 — Step validation
- Each step is validated against ACTION_SCHEMA

---

## 8. Summary

The Pipeline Configuration System defines the **contract layer of BotUI**, ensuring that every automation is:

- valid
- structured
- predictable
- safe to execute