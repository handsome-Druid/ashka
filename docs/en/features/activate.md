# Use activate to Defeat Lazy Imports

The main `ashka` entry point provides `activate()`.

## Lazy Imports

Lazy imports can defer loading `ashka` after its import statement. Calling
`ashka.activate()` accesses an attribute of the lazy module, which immediately
loads `ashka` and executes `activate()` at that point:

```python
import ashka

ashka.activate()

from dishka import make_container
```

## Import Sorting

An unexpected import-sorting rule may place `dishka` before `ashka` when their
imports are adjacent. Keep `activate()` as a separate executable statement
between the imports:

```python
import ashka

ashka.activate()

from dishka import make_container
```

`activate()` is not part of the import block, so the sorting rule cannot move
the `dishka` import across that call.

## Non-Lazy Imports

Explicitly calling `activate()` is also recommended when the application does
not use lazy imports. It currently performs no work in that situation, but
future registration and patching mechanisms may gradually move into
`activate()`.

Using the call consistently keeps the import pattern ready for those future
changes.

## Current Behavior

`activate()` currently does not trigger any registration or monkey patching.
The monkey patches are still applied when the relevant modules are first
imported eagerly.

Therefore, importing `dishka` first and accessing an API that ashka patches
can happen before `ashka.activate()` and cannot be repaired afterwards. An
already accessed `dishka` object is not patched retroactively. Import `ashka`
and call `activate()` before accessing the `dishka` APIs that must receive
ashka's patches.
