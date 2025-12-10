# Modular Design Philosophy

This document outlines the modular design philosophy that guides software development.

## Core Concept: Bricks and Studs

Think of software like interlocking building blocks:

- A **brick** = a self-contained directory or file set delivering one clear responsibility
- A **stud** = the public contract (function signatures, CLI, API schema, data model) that other bricks connect to

## Building Principles

### 1. Start with the Contract

Create or update a short README or top-level docstring inside each brick that states:
- Purpose
- Inputs
- Outputs
- Side-effects
- Dependencies

Keep it small enough to hold in one prompt; future code-gen tools rely on this spec.

### 2. Build in Isolation

- Put code, tests, and fixtures inside the brick's folder
- Expose only the contract via `__all__` or an interface file
- No other brick may import internals

### 3. Verify with Lightweight Tests

- Focus on behavior at the contract level
- Integration tests live beside the brick

### 4. Regenerate, Don't Patch

When a change is needed inside a brick:
- Rewrite the whole brick from its spec instead of line-editing scattered files
- If the contract itself must change, locate every brick that consumes that contract and regenerate them too

### 5. Parallel Variants are Allowed

To experiment:
- Create sibling folders like `auth_v2/`
- Run tests to choose a winner
- Retire the loser

## Human-AI Collaboration

- **Human (architect/QA)**: writes or tweaks the spec, reviews behavior
- **Agent (builder)**: generates the brick, runs tests, reports results

Humans rarely need to read the code unless tests fail.

## The Loop

```
spec → isolated build → behavior test → regenerate
```

This produces code that stays modular today and is ready for automated regeneration tomorrow.

## Benefits

- Code is always in sync with its specification
- Each module can be rebuilt independently
- AI tools can work with "right-sized" tasks
- Context windows aren't overwhelmed
- Complex systems emerge from simple, well-defined components
