# PARADOX: Temporal Programming

PARADOX is a small, time-travel-themed programming language with its own compiler front end and a desktop IDE, written in Python.

You write PARADOX scripts in the built-in console. Each script goes through three compiler phases (lexical analysis, syntax analysis and semantic analysis), and the results show up live in a Universal Symbol Table panel. The IDE has two modes:

- **Story Mode** is an 11-mission narrative where you use the language to contain a paradox and repair a fractured timeline.
- **Sandbox Mode** is free play for testing any construct, with no mission events.

---

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Running PARADOX](#running-paradox)
- [Language reference](#language-reference)
- [Compiler pipeline](#compiler-pipeline)
- [Story Mode walkthrough](#story-mode-walkthrough)
- [Test case matrix](#test-case-matrix)
- [Repository contents](#repository-contents)

---

## Features

- Custom language with its own data types, operators, and keywords
- Three-phase compiler front end: lexer, parser, and semantic analyzer
- Symbol table with scope levels and byte offsets per variable
- Timeline commands: `snapshot`, `revert`, `prune`, and `branch`
- Object-oriented constructs: `entity` blueprints and `invoke` instantiation
- `bootstrap` loops (the language's while-loop equivalent)
- Tkinter GUI with a compiler console, a live symbol table, and an animated timeline visualizer
- Color-coded compiler output (lexer, parser, and semantic messages)

---

## Requirements

- Python 3.8 or newer
- Tkinter, which ships with the standard Python installer for Windows and macOS. On some Linux distributions you need to install it separately (for example `sudo apt install python3-tk`).


## Running PARADOX

```bash
python PARADOX_FINAL.py
```

Choose a mode from the start menu, type a script into the `Paradox >` input box, and press **[ EXECUTE SCRIPT ]**.

Other controls:

- **[ < MAIN MENU ]** returns to the start menu.
- **[ SYS.RESET ]** wipes the symbol table, snapshots, and entities. In Story Mode it also restarts the mission.

---

## Language reference

Every statement ends with the `@` delimiter.

### Data types

| PARADOX type | Equivalent | Description | Example |
|---|---|---|---|
| `cycle` | `int` | Numeric data | `2100` |
| `trace` | `string` | Residual text left in the timeline | `"Anomaly detected"` |
| `canon` | `boolean` | Unchangeable truth or falsehood | `fixed` (true), `erased` (false) |

### Operators and keywords

| PARADOX | Equivalent | Notes |
|---|---|---|
| `<<` | `=` | Assignment |
| `@` | `;` | Statement delimiter |
| `observe` | `print` | Outputs a variable's value |
| `+` `-` `*` `/` | Standard | Arithmetic |
| `==` `>` `<` `>=` `<=` | Standard | Comparison, used in `bootstrap` conditions |

### Core grammar

| Action | Structure | Example |
|---|---|---|
| Assignment | `[DATATYPE] [ID] << [LITERAL] @` | `cycle timeSkip << 2077 @` |
| Observation | `observe [ID] @` | `observe timeSkip @` |
| Chronomath | `[DATATYPE] [ID] << [LITERAL/ID] [MATH_OP] [LITERAL] @` | `cycle offset << 10 + 5 @` |

### Advanced mechanics

| Feature | Grammar | Description |
|---|---|---|
| Entity blueprint | `entity [NAME] { [DATATYPE] [ID] << [LITERAL] @ }` | Declares a blueprint for a complex timeline object |
| Object instantiation | `[CLASS_ID] [OBJECT_ID] << invoke [CLASS_ID] @` | Allocates isolated temporal memory for a new object from an entity blueprint |
| Bootstrap loop | `bootstrap ( [ID] [OP] [LITERAL] ) { [ID] << [ID] [MATH] [LITERAL] @ } origin @` | Loops until the condition fails |
| State snapshot | `snapshot [LITERAL] @` | Archives an exact copy of the Universal Symbol Table under a string name |
| State revert | `revert [LITERAL] @` | Wipes current memory and restores the Universal Symbol Table to the named snapshot |
| Variable pruning | `prune [ID] @` | Removes one variable from the Universal Symbol Table |
| Branching | `branch @` and `prune branch @` | `branch @` moves into a deeper scope level, like opening a block (`{`). `prune branch @` collapses back to the previous level, like closing a block (`}`) |

### Example

```
cycle enginePower << 100 @
snapshot "Baseline" @
entity Shield {
    canon active << fixed @
}
Shield aegis << invoke Shield @
bootstrap ( enginePower > 50 ) {
    enginePower << enginePower - 25 @
} origin @
observe enginePower @
```

---

## Compiler pipeline

Each script is processed in order, and compilation stops at the first error.

1. **Phase 1: Lexical analysis (`tokenize`).** Regular-expression token rules turn source text into tokens (`DATATYPE`, `STATE_COMMAND`, `RETROCAUSAL_ASSIGNMENT`, `ANCHOR_DELIMITER`, `NUMERIC_LITERAL`, `TRACE_LITERAL`, and so on). Characters that match no rule are reported as *foreign artifacts* and skipped.
2. **Phase 2: Syntax analysis (`Parser`).** The script is split into statements, and each one is checked against its grammar rule, such as a missing `<<` or a missing `@`.
3. **Phase 3: Semantic analysis (`SemanticAnalyzer`).** Valid statements are executed against the Universal Symbol Table. This phase covers type checking (for example, a `cycle` cannot hold a `trace` literal), scope tracking, snapshot and revert, entity registration, object instantiation, and `bootstrap` execution.

### Symbol table

Every variable records its **type**, **value**, **scope level**, and **byte offset**. Offsets grow within each scope level using these sizes:

| Type | Bytes |
|---|---|
| `cycle` | 4 |
| `trace` | 1 |
| `canon` | 1 |
| object (`Obj`) | 8 |

`snapshot` stores a deep copy of the symbol table and scope offsets, and `revert` restores it. `prune` removes a variable, or collapses a branch when the target is `branch`. A `bootstrap` loop is capped at 20 iterations to guard against infinite loops.

---

## Story Mode walkthrough

A rogue agent has erased a historical figure and the timeline is fracturing. Complete each directive in order to progress. The status indicator and timeline visualizer change as the timeline recovers.

| Mission | Objective | Solution |
|---|---|---|
| 1 | Initialize the core | `cycle energy << 50 @` |
| 2 | Send a distress signal | `trace beacon << "SOS" @` |
| 3 | Save the fractured timeline | `snapshot "Fracture" @` |
| 4 | Excise the corrupted variable | `prune energy @` |
| 5 | Time travel back | `revert "Fracture" @` |
| 6 | Reject the paradox | `canon paradox << erased @` |
| 7 | Design the containment shield | `entity Shield { canon active << fixed @ }` |
| 8 | Deploy the shield | `Shield aegis << invoke Shield @` |
| 9 | Inspect the shield | `observe aegis @` |
| 10 | Purge the temporal decay | `bootstrap ( energy > 0 ) { energy << energy - 10 @ } origin @` |

After Mission 10 the paradox is contained and Sandbox Mode is unlocked.

---

## Test case matrix

| Test | Input | Expected compiler narrative | Status |
|---|---|---|---|
| **TC1: Happy path** | The example script shown above | Verified all phases, data stored | PASS |
| **TC2: Syntax error** | `cycle velocity 88 @` followed by `observe velocity @` | Error: assignment operator missing | FAIL |
| **TC3: Semantic error** | `cycle temperature << "Critical" @` followed by `observe temperature @` | Error: type mismatch (`cycle` assigned a `trace` literal) | FAIL |
| **TC4: Lexical error** | `canon *checkTimeline << true @` | Error: foreign artifact `*` encountered | FAIL |

A status of FAIL means the compiler rejects the input, which is the expected result for the error cases.

---

## Repository contents

| File | Description |
|---|---|
| [PARADOX_FINAL.py](PARADOX_FINAL.py) | Complete source: lexer, parser, semantic analyzer, and Tkinter GUI |
| [PARADOX_SCREENSHOTS.pdf](PARADOX_SCREENSHOTS.pdf) | Screenshots of the application |
