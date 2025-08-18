from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath


# default replacements for common "smart" characters often produced by LLMs
DEFAULT_REPLACEMENTS: dict[str, str] = {
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2212": "-",  # minus sign
    "\u2018": "'",  # left single quotation mark
    #  "\u2019": "'",  # right single quotation mark / apostrophe
    "\u201C": '"',  # left double quotation mark
    "\u201D": '"',  # right double quotation mark
    "\u00A0": " ",  # no-break space
    "\u2007": " ",  # figure space
    "\u2009": " ",  # thin space
    "\u200A": " ",  # hair space
    "\u202F": " ",  # narrow no-break space
    "\u200B": "",   # zero width space
    "\u200C": "",   # zero width non-joiner
    "\u200D": "",   # zero width joiner
    "\u2060": "",   # word joiner
    "\uFEFF": "",   # zero width no-break space / BOM
    "\u2026": "...",  # horizontal ellipsis
}


def parse_kv(s: str) -> tuple[str, str]:
    if "=" not in s:
        raise argparse.ArgumentTypeError(
            f"Invalid mapping '{s}'. Expected format key=value (values may be unicode escapes, e.g., \\u2014=-)."
        )
    k, v = s.split("=", 1)
    # Support python-style escapes like \u2014 in both key and value
    k = k.encode("utf-8").decode("unicode_escape")
    v = v.encode("utf-8").decode("unicode_escape")
    return k, v


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="purifyllm",
        description=(
            "Replace common UTF-8 special characters (smart quotes, dashes, ellipsis, non-breaking spaces, zero-width) "
            "with safe equivalents. Accepts additional mappings via --map key=value."
        ),
    )
    p.add_argument(
        "filenames",
        nargs="*",
        help="Files to process (provided by pre-commit).",
    )
    p.add_argument(
        "--ignore-files",
        dest="ignore_files",
        action="append",
        default=[],
        help=(
            "Glob pattern of files to ignore (repeatable). Matches against the full path. "
            "Examples: --ignore-files 'LICENSES/**' --ignore-files '**/vendor/**' --ignore-files '*.md'"
        ),
    )
    p.add_argument(
        "--no-defaults",
        action="store_true",
        help="Disable default replacement mappings and use only custom --map entries.",
    )
    p.add_argument(
        "--map",
        dest="maps",
        action="append",
        type=parse_kv,
        help=(
            "Additional replacement mapping. Repeatable. Example: --map "
            "\\u2014=- --map \\u201C=\\\" --map \\u2019='"
        ),
    )
    return p


def apply_replacements(text: str, mapping: dict[str, str]) -> str:
    # Apply in a deterministic order to stabilize diffs
    for src, dst in mapping.items():
        if src in text:
            text = text.replace(src, dst)
    return text


def _load_text(path: Path) -> str | None:
    try:
        # try utf-8 first
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # fall back to binary-safe read and attempt to decode ignoring errors
        try:
            data = path.read_bytes()
        except Exception:
            return None
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return None
    except Exception:
        return None


def _ignored_by_globs(path: Path, patterns: list[str]) -> bool:
    """Return True if the file path matches any ignore glob pattern.

    Matching rules:
    - Patterns are POSIX-style globs (supporting **, *, ?).
    - Matched against the full path using forward slashes.
    - For convenience, also try with an implicit "**/" prefix so that
      patterns like "docs/vendor/**" match anywhere in the path.
    - A trailing slash in the pattern is treated as a directory and expanded
      to match all files under it (appends "**").
    """
    posix = PurePosixPath(path.as_posix())
    for raw in patterns or []:
        if not raw:
            continue
        pat = raw
        # Treat trailing slash as directory
        if pat.endswith("/"):
            pat = pat + "**"
        # first try as-is
        if posix.match(pat):
            return True
        # also try with implicit **/ prefix (unless already anchored)
        imp = "**/" + pat.lstrip("/")
        if posix.match(imp):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    ns = parser.parse_args(argv)

    # build mapping
    mapping: dict[str, str] = {} if ns.no_defaults else dict(DEFAULT_REPLACEMENTS)
    if ns.maps:
        for k, v in ns.maps:
            mapping[k] = v

    # No files: nothing to do, succeed
    if not ns.filenames:
        return 0

    retcode = 0
    for filename in ns.filenames:
        path = Path(filename)
        if not path.is_file():
            continue
        if _ignored_by_globs(path, ns.ignore_files):
            continue
        content = _load_text(path)
        if content is None:
            # non-text or unreadable; skip
            continue
        new_content = apply_replacements(content, mapping)
        if new_content != content:
            try:
                path.write_text(new_content, encoding="utf-8")
                # Modify files -> exit code 1 to signal changes (pre-commit will show diff)
                retcode = 1
            except Exception as e:
                print(f"purifyllm: failed to write {filename}: {e}", file=sys.stderr)
                retcode = 1

    return retcode

if __name__ == "__main__":
    raise SystemExit(main())