# PurifyLLM

CLI and pre-commit hook to normalize “smart” punctuation and invisible Unicode produced by LLMs.

## What it does

Replaces common UTF-8 special characters with safe equivalents:

- smart quotes “ ” ‘ ’ -> " and '
- dashes – — − -> -
- ellipsis … -> ...
- non-breaking spaces and thin spaces -> regular space
- zero-width and BOM characters -> removed

You can add your own mappings in the hook config.

## Install (as a hook consumer)

Add this repo to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/wdroz/PurifyLLM
  rev: v0.1.1
  hooks:
  - id: purify-llm
    # optional: ignore folders/files via glob and add extra replacements
    exclude: '(^|/)(LICENSES|licenses)/'
  args:
  # add custom mappings
  - --map
  - "\u00AB=\""   # « to "
  - --map
  - "\u00BB=\""   # » to "
```

Then install hooks:

```bash
pre-commit install
```

Run on all files at any time:

```bash
pre-commit run --all-files
```

## CLI usage

```bash
purifyllm [--no-defaults] [--map KEY=VALUE ...] [--ignore-files GLOB ...] [FILES ...]
```

Examples:

```bash
purifyllm README.md
purifyllm --map "\u00B7=-" file.txt
purifyllm --no-defaults --map "…=..." --map "—=-" src/
purifyllm --ignore-files '**/LICENSES/**' --ignore-files 'docs/vendor/**' $(git ls-files)
```

Exit codes:

- 0: no changes needed
- 1: files were modified or an error occurred

### Ignoring files and folders (glob)

Use one or more `--ignore-files` flags to skip files by glob pattern. Matching is against the full path using forward slashes.

Examples:

- `--ignore-files '**/LICENSES/**'` ignore any files under a `LICENSES` directory anywhere.
- `--ignore-files 'docs/vendor/**'` ignore files under `docs/vendor`.
- `--ignore-files '*.md'` ignore markdown files.
