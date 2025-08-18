from __future__ import annotations

from pathlib import Path

from purifyllm.main import main


def write(p: Path, s: str) -> Path:
	p.write_text(s, encoding="utf-8")
	return p


def read(p: Path) -> str:
	return p.read_text(encoding="utf-8")


def test_default_replacements_changes_file(tmp_path: Path) -> None:
	# content contains em dash (\u2014), ellipsis (\u2026), nbsp (\u00A0), zero width space (\u200B)
	original = "\u201CHello\u201D \u2014 world\u2026\nNBSP: X\u00A0Y\nZW: A\u200BB\n"
	f = write(tmp_path / "a.txt", original)

	rc = main([str(f)])
	assert rc == 1  # file modified

	out = read(f)
	assert out == '"Hello" - world...\nNBSP: X Y\nZW: AB\n'


def test_no_changes_exit_zero(tmp_path: Path) -> None:
	f = write(tmp_path / "b.txt", 'plain ascii line\n')
	rc = main([str(f)])
	assert rc == 0
	assert read(f) == 'plain ascii line\n'


def test_custom_map_only_no_defaults(tmp_path: Path) -> None:
	# star (\u2605) should be mapped to '*' only when specified
	content = "rating: \u2605\u2605\u2605\n"
	f = write(tmp_path / "c.txt", content)

	rc = main(["--no-defaults", "--map", "\\u2605=*", str(f)])
	assert rc == 1
	assert read(f) == "rating: ***\n"


def test_multiple_files_exit_code(tmp_path: Path) -> None:
	changed = write(tmp_path / "c1.txt", "dash: \u2014\n")
	unchanged = write(tmp_path / "c2.txt", "ok\n")
	rc = main([str(changed), str(unchanged)])
	assert rc == 1
	assert read(changed) == "dash: -\n"
	assert read(unchanged) == "ok\n"


def test_no_files_returns_zero() -> None:
	assert main([]) == 0


def test_ignore_files_by_dirname_glob(tmp_path: Path) -> None:
	# Create a directory named LICENSES and a file inside
	d = tmp_path / "LICENSES"
	d.mkdir()
	f = d / "notice.txt"
	write(f, "dash: \u2014\n")

	# same content in allowed dir
	g = tmp_path / "src" / "file.txt"
	g.parent.mkdir(parents=True)
	write(g, "dash: \u2014\n")

	rc = main(["--ignore-files", "**/LICENSES/**", str(f), str(g)])
	# g should be modified, f skipped
	assert rc == 1
	assert read(f) == "dash: \u2014\n"
	assert read(g) == "dash: -\n"


def test_ignore_files_by_subpath_glob(tmp_path: Path) -> None:
	d = tmp_path / "docs" / "vendor"
	d.mkdir(parents=True)
	f = d / "x.txt"
	write(f, "…\n")

	other = tmp_path / "docs" / "ours" / "y.txt"
	other.parent.mkdir(parents=True)
	write(other, "…\n")

	rc = main(["--ignore-files", "docs/vendor/**", str(f), str(other)])
	assert rc == 1
	assert read(f) == "…\n"  # ignored
	assert read(other) == "...\n"  # processed

