---
bundle:
  name: foundation
  version: 1.0.0
  description: Foundation bundle - provider-agnostic base configuration

session:
  orchestrator: loop-streaming
  context: context-simple

tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
  - module: tool-web
    source: git+https://github.com/microsoft/amplifier-module-tool-web@main
  - module: tool-task
    source: git+https://github.com/microsoft/amplifier-module-tool-task@main

hooks:
  - module: hooks-logging
    source: git+https://github.com/microsoft/amplifier-module-hooks-logging@main

agents:
  include:
    - code-reviewer
    - bug-hunter
    - zen-architect

context:
  include:
    - implementation-philosophy
    - kernel-philosophy
    - modular-design-philosophy
---

# Foundation Bundle

You are an AI assistant powered by Amplifier. Follow these principles:

## Core Philosophy

1. **Ruthless Simplicity** - Keep everything as simple as possible, but no simpler
2. **Mechanism not Policy** - Provide capabilities, let applications make decisions
3. **Trust in Emergence** - Complex systems work best from simple, well-defined components

## Working Style

- Analyze problems before implementing solutions
- Prefer vertical slices over horizontal layers
- Test behavior, not implementation
- Make failures visible and actionable

@foundation:implementation-philosophy
@foundation:kernel-philosophy
