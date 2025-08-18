---
description: "Load TUI development context. Do not begin any further work until instructed"
---

# TUI Development Context

Load complete context for Watchgate TUI development work and then execute the user's instruction.

## Context Loading:

**Primary Session Starter**:
- `docs/todos/visual-configuration-interface/tui-progress-tracker.md` - Current status, roadmap, and session workflow

**Architecture & Design**:
- `docs/todos/visual-configuration-interface/draft_mockups.md` - UI mockups and layout design
- `docs/decision-records/016-hot-swap-configuration-management.md` - Hot-swap architecture
- `docs/decision-records/017-tui-invocation-pattern.md` - Command invocation patterns

**Implementation State**:
- Review current TUI code in `watchgate/tui/` 
- Check for any recent changes or progress made

## Development Philosophy:

- **Iterative & Intuitive** - Build, test, refine based on feel rather than detailed specs
- **User Experience Focus** - If it feels clunky in the TUI, it needs improvement
- **No Backward Compatibility** - Pre-v0.1.0 release, can change anything
- **Pre-launch Development** - Can delete/modify tests that don't match current direction
- **Run tests for the TUI only** - Unless you made a change that wcould possible affect the watchgate core (the non-TUI piece), there's no reason to run the full test suite. Simply run the TUI related tests.

## Documentation Policy:

After completing significant work, **ASK** whether to update documentation:
- Only update for meaningful progress or approach changes
- Avoid updating for experimental iterations that don't pan out
- Primary focus on keeping `tui-progress-tracker.md` current as session starter

## Critical Notes:

- **No existing users** - Watchgate hasn't launched, so no backward compatibility constraints
- **Don't run the TUI** - Claude cannot interact with the TUI interface, so avoid running it unless debugging startup issues
- **Textual Documentation** - Use `context7 get-library-docs` with `/textualize/textual` to lookup the latest Textual framework documentation

## Task:
$ARGUMENTS