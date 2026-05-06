# Special Keys & Dynamic Data Resolution

## Overview
In the context of automated testing and stress testing, static data is often insufficient. The BotUi Expander implements "Special Keys"—dynamic tokens that are resolved during the YAML pre-processing phase.

These keys allow you to inject randomness, generate unique identifiers, and load external data payloads, transforming a single YAML template into thousands of unique execution scenarios.

**Why use Special Keys?**

- Data Driven Testing: Decouple your test logic from your test data.
- Collision Avoidance: Generate unique emails and IDs to prevent database constraint errors during concurrent stress tests.
- Scalability: Feed the bot with massive JSON files containing real-world data without cluttering the main configuration.

---

## Available Special Keys

### 1. ``{{RANDOM_ID}}``

Generates a unique UUID v4 (Universally Unique Identifier).

- Usage: Use it whenever you need a string that is guaranteed to be unique across multiple bot instances.

```yaml
config:
    variables:
        SESSION_NAME: "test_session_{{RANDOM_ID}}"
        USER_EMAIL: "bot_{{RANDOM_ID}}@staging.com"
```

In this case, a session name and a user email are generated with a certain level of randomness due to the creation and concatenation of identifiers

### 2. ``{{LOAD_FILE.<path>}}``

Loads content from an external JSON file.

- Mechanism:
  - If the tag is the entire value of the variable, the variable becomes a native Python list or dict.
  - If the tag is part of a larger string, it is replaced by the string representation of the file content.
- Constraint: The file path is relative to the bot_container_path.

```yaml
config:
    variables:
        USER_LIST: "{{LOAD_FILE.data/mass_users.json}}"
```

Here, the ``mass_users.json`` file is opened and its contents are loaded into the ``USER_LIST`` variable so that they can be used as intended later.

### 3. ``{{RANDOM_CHOICE.<variable_name>}}``

Selects a random item from a previously referenced list.

- Requirement: The referenced variable must be a `list`
- Usage: Perfect for simulating different user behaviors or inputs using a predefined pool of data.

```yaml
config:
    variables:
        CANDIDATES: "{{LOAD_FILE.data/names.json}}"
        SELECTED_NAME: "{{RANDOM_CHOICE.CANDIDATES}}"
```

Here, a file containing multiple names is loaded, and then ``RANDOM_CHOICE`` is used to select a random candidate from the list.

---

## Complex Examples

### 1. 

```yaml
config:
  variables:
    ID: "{{RANDOM_ID}}"
    USER_POOL: "{{LOAD_FILE.data/users.json}}"
    CURRENT_USER: "{{RANDOM_CHOICE.USER_POOL}}"

pipelines:
  stress_test:
    steps:
      - action: WRITE
        text: "Logging in as $CURRENT_USER with session $ID"
```