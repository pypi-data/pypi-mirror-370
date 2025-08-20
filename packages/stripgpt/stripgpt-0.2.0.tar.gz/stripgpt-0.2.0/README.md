# stripgpt

CLI (and tiny library) to scrub ChatGPT / LLM conversation artifacts from text files or streams.

It removes:

- Private Use Area span markers used by ChatGPT export (U+E200 / U+E201) and the text inside them
- Any remaining private–use characters (Unicode category `Co`)
- Zero‑width & directionality control characters (ZWSP, ZWNJ, ZWJ, LRM, RLM, LRE, RLE, PDF, LRO, RLO, WJ, LRI, RLI, FSI, PDI)
- (Optional) "bare" leftover tokens like `turn2search5` and line range snippets `L10-L42`
- (Optional) Normalizes whitespace (collapses runs of spaces / tabs, removes trailing space, trims ends)

## Why?
Copying / exporting LLM answers often smuggles in hidden marker & control characters that pollute diffs and source control. `stripgpt` makes cleaning them automatic and scriptable.

## Features
- Stream or file mode (stdin→stdout or specified files)
- In‑place editing with optional backup suffix
- Conservative defaults (whitespace normalized unless `--no-normalize`)
- Optional removal of leftover token artifacts
- Simple Python API: `from stripgpt import clean_text`
- Tested on Python 3.12 (minimum supported)
- CI workflow already configured (GitHub Actions)

## Installation
Editable (development) install:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Once published to PyPI:

```bash
pip install stripgpt
```

## Command Line Usage
Read from stdin / write to stdout:

```bash
pbpaste | stripgpt | pbcopy
```

Clean one or more files (output to stdout):

```bash
stripgpt session.md > clean.md
stripgpt file1.txt file2.txt > merged-clean.txt
```

In place (overwrite):

```bash
stripgpt -i session.md
```

In place with backup:

```bash
stripgpt -i --backup-suffix .bak session.md
```

Remove bare tokens & line ranges too:

```bash
stripgpt --kill-bare transcript.txt > scrubbed.txt
```

Preserve original whitespace:

```bash
stripgpt --no-normalize notes.txt > cleaned.txt
```

Specify encoding (default utf-8):

```bash
stripgpt --encoding latin-1 legacy.txt > legacy-clean.txt
```

Detection only (no modification) – JSON report per input:

```bash
stripgpt --detect file1.txt file2.txt
# or
cat text.md | stripgpt --detect
```
Example output:

```json
{"pua_spans":1,"bare_tokens":2,"zero_width":3,"file":"file1.txt"}
```

Help:

```bash
stripgpt -h
```

## Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Unhandled / runtime error (message on stderr) |

## Library API
```python
from stripgpt import clean_text

cleaned = clean_text(text, kill_bare=True, normalize=True)
```

Signature:

```
clean_text(txt: str, *, kill_bare: bool, normalize: bool) -> str
```

Parameters:
- `kill_bare`: remove tokens like `turn12search5` and ranges `L10-L20`
- `normalize`: collapse repeated spaces / tabs, strip trailing & leading whitespace

## How It Works
1. Remove any span starting with U+E200 and ending with U+E201 (non-greedy), including enclosed text
2. Strip any remaining private-use characters (category `Co`)
3. Remove zero-width & bidi control characters
4. Optionally remove bare token artifacts & line ranges
5. Optionally normalize whitespace

All regexes compiled at import; performance is I/O bound for typical file sizes.

## Development
Requires Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

Or via tox:

```bash
tox
```

## Publishing (manual)
Requires `build` and `twine` (install via `pip install build twine`).

```bash
python -m build
twine check dist/*
twine upload dist/*  # set PYPI_TOKEN or enter credentials
```

Or use the provided GitHub Actions workflow (add `PYPI_API_TOKEN` secret).

Run CLI locally without install (editable already works):

```bash
python -m stripgpt --help
```

## Continuous Integration
GitHub Actions workflow (`.github/workflows/ci.yml`) runs tests on Python 3.12.

## Suggested Enhancements
- Streaming (line-by-line) processing to reduce memory
- Coverage & badge
- Pre-commit hook config
- Removal statistics / summary report
- Additional token pattern detection

## Troubleshooting
| Issue | Hint |
|-------|------|
| File unchanged | Use `-i` for in-place or redirect stdout to a file |
| Hidden chars remain | Inspect with `hexdump -C` or a Unicode viewer; open an issue with samples |
| Encoding errors | Pass `--encoding` matching the source file |
| "No tests ran" in CI | Ensure `tests/` present & `pytest.ini` unchanged |

## Safety
Use `--backup-suffix` during first runs for peace of mind.

## License
MIT License. See `LICENSE` file.

## Acknowledgements
Inspired by persistent invisible marker annoyances in exported ChatGPT conversations.

---
Happy clean diffs!

