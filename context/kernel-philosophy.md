# Kernel Philosophy

The kernel's north star: a tiny, stable kernel that provides only mechanisms; all policies and features live at the edges as replaceable modules. The center stays still so the edges can move fast.

## Core Tenets

1. **Mechanism, not policy**
   The kernel exposes capabilities and stable contracts. Decisions about behavior belong outside the kernel.

2. **Small, stable, and boring**
   The kernel is intentionally minimal and changes rarely. Easy to reason about by a single maintainer.

3. **Don't break modules**
   Backward compatibility in kernel interfaces is sacred. Additive evolution, clear deprecation.

4. **Separation of concerns via explicit boundaries**
   Narrow, well-documented interfaces. No hidden backchannels.

5. **Extensibility through composition, not configuration**
   New behavior comes from plugging in different modules, not toggling flags.

6. **Policy lives at the edges**
   Scheduling, orchestration, provider choices, formatting - all belong in modules.

7. **Text-first, inspectable surfaces**
   Human-readable, deterministic, versionable representations.

8. **Determinism before parallelism**
   Simple, deterministic flows over clever concurrency.

9. **Observability as a built-in mechanism**
   The kernel provides events/hooks to observe. Policies for what to record live in modules.

10. **Security by construction**
    Least privilege, deny-by-default, non-interference as invariants.

## What Belongs in the Kernel

### Kernel Responsibilities (Mechanisms)
- Stable contracts and core interfaces
- Lifecycle & coordination (loading, unloading, dispatching)
- Capability enforcement (limits, permissions)
- Minimal context plumbing
- Observability hooks

### Explicit Non-Goals (Policies)
- Orchestration strategies or heuristics
- Provider/model selection logic
- Tool behavior or domain rules
- Formatting, UX, or log policies
- Business or product defaults

**Litmus test**: If two reasonable teams could want different behavior, it's a policy - keep it out of kernel.

## Invariants

- **Backward compatibility**: Modules continue to work across updates
- **Non-interference**: Faulty modules cannot crash the kernel
- **Bounded side-effects**: No irreversible external changes
- **Deterministic semantics**: Same inputs produce predictable behavior
- **Minimal dependencies**: Avoid heavy third-party dependencies

## Evolution Rules

1. **Additive first**: Extend without breaking
2. **Two-implementation rule**: Don't add until multiple modules converge
3. **Deprecation discipline**: Announce, document, dual path, remove
4. **Spec before code**: Purpose, alternatives, impact, rollback
5. **No policy leaks**: Move policy to modules
6. **Complexity ledger**: Justify additions, retire equivalent complexity

## North Star Outcomes

- **Unshakeable center**: Kernel maintainable by one person, auditable in an afternoon
- **Explosive edges**: Flourishing ecosystem of competing, evolving modules
- **Forever-upgradeable**: Weekly edge releases, rare boring kernel updates
