# test_jardiff.py
# Thorough tests for jardiff (Option B: subcommands with `help` + `diff`)
# Place this file alongside jardiff.py and run:  pytest -q

import os
import sys
import zipfile
import subprocess
import textwrap
from pathlib import Path

import pytest

# If you renamed jardiff.py, adjust this constant:
SCRIPT_NAME = "jardiff.py"

# Import the module to test internal functions as well
# (Relies on jardiff.py being next to this test file)
sys.path.insert(0, str(Path(__file__).parent))
import jardiff  # noqa: E402


# -----------------------------
# Helpers to build test fixtures
# -----------------------------

def make_class_bytes():
    # Minimal bytes; not a real class, just a placeholder
    return b"\xCA\xFE\xBA\xBE\x00\x00\x00\x34" + b"\x00" * 32


def make_jar(dirpath: Path, name: str, entries: dict):
    """
    Create a jar at dirpath/name with entries mapping path->bytes.
    Returns the Path to the jar.
    """
    jar_path = dirpath / name
    with zipfile.ZipFile(jar_path, "w") as z:
        for p, data in entries.items():
            z.writestr(p, data)
    return jar_path


def make_pom_jar(dirpath: Path, filename: str, group: str, artifact: str, version: str, pkgs=None):
    pkgs = pkgs or ["com/acme", "com/acme/util"]
    entries = {
        f"META-INF/maven/{group}/{artifact}/pom.properties": (
            f"groupId={group}\nartifactId={artifact}\nversion={version}\n"
        ).encode()
    }
    # add a couple of class files under provided packages
    for pkg in pkgs:
        entries[f"{pkg}/Foo.class"] = make_class_bytes()
        entries[f"{pkg}/Bar.class"] = make_class_bytes()
    return make_jar(dirpath, filename, entries)


def make_manifest_jar(dirpath: Path, filename: str, title: str, version: str, folded=False, pkgs=None):
    pkgs = pkgs or ["org/example"]
    # A simple manifest with optional folded title
    if folded:
        # Continuation lines start with a single space per spec
        manifest = textwrap.dedent(f"""\
            Manifest-Version: 1.0
            Implementation-Title: {title[:20]}
             {title[20:]}
            Implementation-Version: {version}
        """)
    else:
        manifest = textwrap.dedent(f"""\
            Manifest-Version: 1.0
            Implementation-Title: {title}
            Implementation-Version: {version}
        """)
    entries = {"META-INF/MANIFEST.MF": manifest.replace("\n", "\r\n").encode()}
    for pkg in pkgs:
        entries[f"{pkg}/Main.class"] = make_class_bytes()
    return make_jar(dirpath, filename, entries)


def make_filename_only_jar(dirpath: Path, filename: str, pkgs=None):
    pkgs = pkgs or ["x/y"]
    entries = {}
    for pkg in pkgs:
        entries[f"{pkg}/Thing.class"] = make_class_bytes()
    return make_jar(dirpath, filename, entries)


def make_invalid_jar(dirpath: Path, filename: str):
    p = dirpath / filename
    p.write_bytes(b"not a zip at all\n")
    return p


def run_cli(tmp, *args):
    """
    Run the jardiff CLI via subprocess. Returns (returncode, stdout, stderr)
    """
    script = Path(tmp) / SCRIPT_NAME
    if not script.exists():
        # Copy the local jardiff.py into tmp so imports of packages can find it
        src = Path(__file__).parent / SCRIPT_NAME
        script.write_text(src.read_text(), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(tmp),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ------------------
# Unit-level testing
# ------------------

def test_read_jar_info_from_pom(tmp_path: Path):
    jar = make_pom_jar(tmp_path, "foo-1.2.3.jar", "com.acme", "foo", "1.2.3")
    info = jardiff.read_jar_info(str(jar))
    assert info.source == "pom.properties"
    assert info.key == "com.acme:foo"
    assert info.version == "1.2.3"
    assert info.filename == "foo-1.2.3.jar"


def test_read_jar_info_multiple_pom_picks_best(tmp_path: Path):
    # filename stem 'core-2.0' should bias selection to artifactId 'core'
    entries = {
        "META-INF/maven/com/acme/core/pom.properties": b"groupId=com.acme\nartifactId=core\nversion=2.0\n",
        "META-INF/maven/com/other/dep/pom.properties": b"groupId=com.other\nartifactId=dep\nversion=9.9\n",
        "com/acme/Core.class": make_class_bytes(),
    }
    jar = make_jar(tmp_path, "core-2.0.jar", entries)
    info = jardiff.read_jar_info(str(jar))
    assert info.key == "com.acme:core"
    assert info.version == "2.0"
    assert info.source == "pom.properties"


def test_read_jar_info_from_manifest_with_folding(tmp_path: Path):
    title = "bar-lib-extremely-long-title"
    jar = make_manifest_jar(tmp_path, "bar-3.4.jar", title=title, version="3.4", folded=True)
    info = jardiff.read_jar_info(str(jar))
    # The folded title should be concatenated back
    assert info.key.replace(" ", "") == title.replace(" ", "")
    assert info.version == "3.4"
    assert info.source == "manifest"


def test_read_jar_info_from_filename_and_invalid(tmp_path: Path):
    # No pom, no manifest -> fallback to filename
    jar = make_filename_only_jar(tmp_path, "name-only-9.9.9.jar")
    info = jardiff.read_jar_info(str(jar))
    assert info.source == "filename"
    assert info.version == "9.9.9"
    assert info.key == "name-only"

    # Invalid jar file (not a zip)
    bad = make_invalid_jar(tmp_path, "broken-1.0.jar")
    info2 = jardiff.read_jar_info(str(bad))
    assert info2.source == "invalid-jar"
    assert info2.version == "1.0"
    assert info2.key == "broken"


def test_index_and_compare_sets(tmp_path: Path):
    libA = tmp_path / "libA"
    libB = tmp_path / "libB"
    libA.mkdir()
    libB.mkdir()

    # A has foo 1.0 and commons (unchanged)
    make_pom_jar(libA, "foo-1.0.jar", "com.acme", "foo", "1.0")
    make_manifest_jar(libA, "commons-2.1.jar", title="commons", version="2.1")

    # B has foo 2.0 (changed), commons 2.1 (unchanged), and extra (added)
    make_pom_jar(libB, "foo-2.0.jar", "com.acme", "foo", "2.0")
    make_manifest_jar(libB, "commons-2.1.jar", title="commons", version="2.1")
    make_filename_only_jar(libB, "extra-0.1.jar")

    A = jardiff.index_lib_dir(str(libA))
    B = jardiff.index_lib_dir(str(libB))

    removed, added, changed, same = jardiff.compare(A, B)
    assert removed == []  # nothing only in A
    assert added == ["extra"]  # filename-key fallback
    # Changed should show com.acme:foo from 1.0 -> 2.0
    change_map = {k: (va, vb) for k, va, vb in changed}
    assert change_map["com.acme:foo"] == ("1.0", "2.0")
    assert "commons" in same


def test_recursive_scan(tmp_path: Path):
    libA = tmp_path / "libA"
    libB = tmp_path / "libB"
    (libA / "nested").mkdir(parents=True)
    (libB / "nested/deeper").mkdir(parents=True)

    make_pom_jar(libA / "nested", "foo-1.0.jar", "com.acme", "foo", "1.0")
    make_pom_jar(libB / "nested/deeper", "foo-2.0.jar", "com.acme", "foo", "2.0")

    A = jardiff.index_lib_dir(str(libA), recurse=True)
    B = jardiff.index_lib_dir(str(libB), recurse=True)
    _, _, changed, _ = jardiff.compare(A, B)
    change_map = {k: (va, vb) for k, va, vb in changed}
    assert change_map["com.acme:foo"] == ("1.0", "2.0")


def test_packages_in_dir_and_delta(tmp_path: Path):
    libA = tmp_path / "libA"
    libB = tmp_path / "libB"
    libA.mkdir()
    libB.mkdir()

    # A defines com.acme and org.alpha; B defines com.acme and org.beta
    make_filename_only_jar(libA, "a-1.0.jar", pkgs=["com/acme", "org/alpha"])
    make_filename_only_jar(libB, "b-1.0.jar", pkgs=["com/acme", "org/beta"])

    pkgsA = jardiff.packages_in_dir(str(libA))
    pkgsB = jardiff.packages_in_dir(str(libB))
    assert "com.acme" in pkgsA and "com.acme" in pkgsB
    assert "org.alpha" in pkgsA and "org.alpha" not in pkgsB
    assert "org.beta" in pkgsB and "org.beta" not in pkgsA


# -------------
# CLI-level tests
# -------------

def test_cli_help_and_version(tmp_path: Path):
    rc, out, err = run_cli(tmp_path, "--help")
    assert rc == 0
    assert "usage:" in out.lower()
    assert "jardiff" in out

    rc, out, err = run_cli(tmp_path, "--version")
    assert rc == 0
    assert jardiff.__version__ in out

    rc, out, err = run_cli(tmp_path, "help")
    assert rc == 0
    assert "Examples:" in out

    rc, out, err = run_cli(tmp_path, "help", "diff")
    assert rc == 0
    assert "Compare two lib directories" in out


def test_cli_diff_default_subcommand(tmp_path: Path):
    libA = tmp_path / "A"
    libB = tmp_path / "B"
    libA.mkdir(); libB.mkdir()
    make_pom_jar(libA, "foo-1.0.jar", "com.acme", "foo", "1.0")
    make_pom_jar(libB, "foo-2.0.jar", "com.acme", "foo", "2.0")

    # No explicit subcommand: should default to "diff"
    rc, out, err = run_cli(tmp_path, str(libA), str(libB))
    assert rc == 0
    assert "=== Summary ===" in out
    assert "Version Changes" in out


def test_cli_diff_and_packages_and_recurse(tmp_path: Path):
    libA = tmp_path / "A"
    libB = tmp_path / "B"
    (libA / "nested").mkdir(parents=True)
    (libB / "nested").mkdir(parents=True)

    make_filename_only_jar(libA / "nested", "a-1.0.jar", pkgs=["x/y", "p/q"])
    make_filename_only_jar(libB / "nested", "b-1.0.jar", pkgs=["x/y", "r/s"])

    rc, out, err = run_cli(tmp_path, "diff", "-r", "--packages", str(libA), str(libB))
    assert rc == 0
    assert "Package Delta" in out
    assert "Only in A:" in out and "Only in B:" in out


def test_cli_error_missing_dir(tmp_path: Path):
    libA = tmp_path / "A"
    libA.mkdir()
    # B doesn't exist
    rc, out, err = run_cli(tmp_path, "diff", str(libA), str(tmp_path / "NOPE"))
    assert rc == 2
    assert "is not a directory" in err
