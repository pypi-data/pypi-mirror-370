# Pytoma — Repo text rendering

Pytoma condenses your python repo into one concise, LLM-friendly, text file.
You choose **what to show** (full code, signature + docstring, partial bodies ...) **per function, class, file, or folder**. 

You can configure what will be shown via a small YAML config or CLI options, and the output is a single text file divided in fenced code blocks, ideal for prompting an LLM or sharing a focused snapshot with collaborators. You can also use it to hide sensitive code snippets to protect your innovative ideas.

Note from the author : I originally vibe-coded a basic tool for myself because ChatGPT wouldn't accept more than 10 files and the files-to-prompts lib didn't allow me to hide certain sections ... but it turned out to be very handy and useful, so I refined it and it became this project.


---

## Highlights

* **Policy-driven slicing**: `full`, `sig`, `sig+doc`, `body:levels=k`, `hide` to omit sections, `file:no-imports` to omit imports
* **Targets**:

  * by **qualname** (e.g. `pkg.mod:Class.method` or `pkg.mod:*`),
  * by **path glob** (e.g. `**/repo/pkg/**/*.py`),
  * or via a **global default**.
* **Multiple engines**:

  * Python (`.py`): granular per function/method/class.
  * Markdown (`.md`): per heading or whole document (supports `full`/`hide`).
  * YAML will soon be added
  * A description or short extract of heavy files, ML artifacts, etc., is also to be expected

---

## Installation

**Prerequisites:** Python ≥ 3.9

```bash
pip install pytoma
```

If you can't directly call pip : 

```bash
python -m pip install pytoma
```

Of course, if your pip alias is pip3, replace pip by pip3 in the command (and if your python alias is python3, replace python by python3 ...)

You can verify your installation with

```bash
pytoma --version
pytoma --help
```

During installation, if `pip` prints a **warning** like:

```
The script 'pytoma' is installed in '…' which is not on PATH
```

Then you must permanently add **that folder** to your `PATH` (in your .bashrc or .zshrc), and then reopen the terminal.


As a fallback, you may also install from source :

```bash
git clone https://github.com/nathanap2/pytoma.git
cd pytoma
python -m pip install .
```

---

## Quick Start (CLI)

```bash
# Basic: pack a repo with defaults (same behaviour as files-to-prompt)
pytoma ./path/to/repo > PACK.txt

# Now we use a YAML config to customize the render (skip sections, etc.)
pytoma ./repo --config config.yml --out PACK.txt

```

The pack looks like:

````text
### pkg/module.py

```python
def foo(a: int, b: int) -> int:
    """Adds two numbers."""
    # … lines 12–37 body omitted (26 lines) …
```

### docs/guide.md

<!-- … lines 1–120 document omitted (120 lines) … -->

````


---

## Configuration (YAML)

```yaml
# config.yml
default: full        # fallback policy

# optional: exclude patterns (relative to the provided roots)
excludes:
  - ".venv/**"
  - "**/__pycache__/**"
  - "dist/**"
  - "build/**"
  - "site-packages/**"
  - "**/*.pyi"

rules:
  # Apply a file-level filter first (removes top-level imports, keeps __future__)
  - match: "/abs/path/to/repo/pkg/**/*.py"
    mode: "file:no-imports"

  # Then apply function-level policy to the same files
  - match: "/abs/path/to/repo/pkg/**/*.py"
    mode: "sig+doc"

  # Hide an entire module (replaced by an omission marker)
  - match: "/abs/path/to/repo/legacy/big_module.py"
    mode: "hide"

  # Target all defs in a given module by qualname
  - match: "pkg.special:*"
    mode: "body:levels=1"

  # Markdown supports only "full" and "hide"
  - match: "/abs/path/to/repo/README.md"
    mode: "hide"
````

Note : when Pytoma walks each document’s nodes, it decides a policy with this order: qualname rules > path rules > global default.

---

## Policies

* `full` — leave the node as is.
* `hide` — remove and insert an omission marker:

  * On a **module**: replaces the whole file content.
  * On a **class**: replaces the whole class block.
  * On a **function/method**: replaces the definition or its body depending on engine mode.
* `sig` — one-line header (`def …:`), body omitted with a marker.
* `sig+doc` — header + docstring (or `"""…"""` placeholder), body omitted.
* `body:levels=k` — keep code with indentation ≤ `base + 4*k`, collapse deeper blocks with markers.
* `file:no-imports` — strip top-level `import`/`from … import …` except `from __future__ import …`.
* `file:no-legacy-strings` — remove **top-level** triple-quoted strings that are
  **not** the module docstring. These are often used to “comment out” legacy code blocks.
* `file:no-path-defs` — remove or condense **top-level** path-setup assignments
  (RHS matching `os.path.*`, `pathlib.Path(...)`, `__file__`, or `Path(...)` when
  imported from `pathlib`). A compact marker summarizes a few removed variables.
* `file:no-sys-path` — remove `sys.path` manipulations (`append`, `insert`, `extend`),
  direct assignments (`sys.path = ...`), and in-place updates (`sys.path += ...`).
* `file:tidy` — **composite** cleaner that applies `file:no-imports`,
  `file:no-legacy-strings`, `file:no-path-defs`, and `file:no-sys-path`
  in one pass. Recommended when you want several file-level cleaners on the
  same file, since only one `file:*` rule is applied per file rule.


Markers are comment-style lines (or a light box) with line counts, e.g.:

```python
# … lines 42–97 body omitted (56 lines) …
```


---

## Applying a policy to a whole file or folder

**Three options:**

1. **Global default**

```bash
pytoma /abs/repo --default "sig+doc"
```

2. **Path glob rule** (absolute POSIX)

```yaml
rules:
  - match: "/abs/repo/pkg/**/*.py"
    mode: "sig+doc"
```

3. **Qualname wildcard for a module**

```yaml
rules:
  - match: "pkg.module:*"
    mode: "sig+doc"
```

> For file-level effects like removing imports or hiding an entire file, use `file:no-imports` or `hide` on the path glob; these apply to the module root.

---

## Excludes

By default, Pytoma skips:

```
.venv/**, **/__pycache__/**, dist/**, build/**, site-packages/**, **/*.pyi
```

You can override in `config.yml → excludes`.

---

## Pitfalls

- **Rule order can still be tricky** when several rules are about the same file. I'm looking forward to improving that soon. For the moment, prefer being as explicit as possible, and for tricky setups, you can simply ask an LLM to draft the rules for you (from your repo tree and goals).
- To name a markdown section in the config file, you still **need to give the slugified version** of the section
- **Only one `file:*` action per rule target.** If you need to combine cleaners (imports + sys.path + path vars + legacy strings), prefer `file:tidy` instead of stacking multiple `file:*` rules on the same files.


## Roadmap

* Engine for **YAML / JSON** (keys/tables granularity), **CSV** (short preview like pandas does), etc.
* Better summary of skipped lines (for instance, when skipping imports, in the examples of skipped imports, we should probably prioritize unexpected imports over classic ones such as sys, os ...)
* Propose the automatic addition of inferred rules: in particular, functions that are only called by hidden functions should probably be hidden by default.
* More markers + Let the user choose their markers, rule by rule, using the configuration
* A “custom:alternative_version” rule to simply replace a block with an alternative version of the block provided by the user.
* Heuristics to suggest rules (and possibility to condition it by a section which we want to focus on) -> may actually become another independent tool ... 
* ... and even smarter module targeting via **dependency graphs , embeddings**, git edit correlations, etc.

---

## Current engines & support matrix

| Engine / Mode    | full | hide | sig | sig+doc | body\:levels=k | file\:no-imports |
| ---------------- | :--: | :--: | :-: | :-----: | :------------: | :--------------: |
| Python (`.py`)   |   ✅  |   ✅  |  ✅  |    ✅    |        ✅       |         ✅        |
| Markdown (`.md`) |   ✅  |   ✅  |  –  |    –    |        –       |         –        |

---

## How it works (short)

* Each engine parses a file into a lightweight IR:

  * `Document` with a flat list of `Node`s (module, class, function, etc.).
* A decision step maps nodes to `Action`s (`full`, `sig+doc`, …) using the precedence above.
* Engines render actions into concrete `Edit`s (byte spans + replacements).
* Edits are **merged**.
* The final pack concatenates per-file sections with language fences.

---

## License

[MIT](LICENCE)
