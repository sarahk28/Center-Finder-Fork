# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A CLI tool that searches for nearby businesses using SerpAPI's Google Maps engine. The user is prompted for a business type, location, and radius; results are printed as raw JSON.

## Running

```bash
python baba.py
# or directly
python krish.py
```

**Dependency:** `serpapi` — install with:
```bash
pip install google-search-results
```

## Architecture

Two-file structure:

- **`krish.py`** — core logic. Contains `search_businesses()`, which prompts the user for input, builds SerpAPI `google_maps` query params, calls `GoogleSearch(params).get_dict()`, and pretty-prints the result.
- **`baba.py`** — thin entry point that imports and calls `search_businesses()` from `krish`.

Data flow: `baba.py` → `search_businesses()` → SerpAPI `google_maps` engine → raw JSON printed to stdout.

## Notes

- The SerpAPI key is hardcoded in `krish.py`. If rotating or replacing it, update that file directly.
- There are no tests, linting config, or requirements file in this repo.
