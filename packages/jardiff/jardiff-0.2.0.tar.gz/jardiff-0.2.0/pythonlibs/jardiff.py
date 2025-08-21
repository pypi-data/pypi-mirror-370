#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

__version__ = "0.2.0"

# ----- Data model -----
@dataclass
class JarInfo:
    key: str
    version: str
    source: str  # 'pom.properties' | 'manifest' | 'filename' | 'invalid-jar'
    filename: str
    path: str
    groupId: Optional[str] = None
    artifactId: Optional[str] = None
    classifier: Optional[str] = None
    file_hash: Optional[str] = None
    hash_algo: Optional[str] = None  # e.g., 'sha1'

VERSION_KEYS = [
    "Implementation-Version",
    "Bundle-Version",
    "Specification-Version",
    "Version",
]

# Qualifiers that should be treated as part of the version, not as classifier
KNOWN_VERSION_QUALIFIERS = {
    "SNAPSHOT", "ALPHA", "BETA", "RC", "CR", "M", "EA", "FINAL", "GA", "SP",
    "RELEASE", "BUILD",
}

# Typical classifier tokens (not exhaustive, but common)
LIKELY_CLASSIFIERS = {
    "sources", "source", "javadoc", "tests", "test", "all", "with-dependencies",
    "shaded", "uber", "minimal", "lite", "slim", "fat", "native",
    "linux", "windows", "win32", "mac", "macos", "x86", "x64", "x86_64",
    "arm", "arm64", "aarch64", "nodeps", "no-deps",
}

# ----- Utilities -----
class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawTextHelpFormatter):
    pass

def _read_text(zf: zipfile.ZipFile, name: str) -> Optional[str]:
    try:
        with zf.open(name) as f:
            return f.read().decode("utf-8", errors="replace")
    except KeyError:
        return None

def parse_properties(text: Optional[str]) -> Dict[str, str]:
    """Parse simple key=value .properties content."""
    props: Dict[str, str] = {}
    if not text:
        return props
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        props[k.strip()] = v.strip()
    return props

def parse_manifest(text: Optional[str]) -> Dict[str, str]:
    """Parse MANIFEST.MF (key: value, continuation lines start with a space)."""
    if not text:
        return {}
    lines = text.splitlines()
    folded: List[str] = []
    buf = ""
    for line in lines:
        if line == "":
            # blank line flushes current header (per spec)
            if buf:
                folded.append(buf)
                buf = ""
            continue
        if line.startswith(" "):  # continuation
            buf += line[1:]
        else:
            if buf:
                folded.append(buf)
            buf = line
    if buf:
        folded.append(buf)
    props: Dict[str, str] = {}
    for line in folded:
        if ":" in line:
            k, v = line.split(":", 1)
            props[k.strip()] = v.strip()
    return props

_version_re = re.compile(
    r"""
    ^(?P<name>.+?)-
    (?P<version>                    # core version starts here
        (?:v)?\d+(?:[._]\d+)*       # 1, 1.2, 1_2_3, optionally 'v' prefix
        (?:                         # allow hyphen-qualifiers (alpha, rc, etc.)
            -
            (?:
                (?:
                    (?:(?:SNAPSHOT|ALPHA|BETA|RC|CR|M|EA|FINAL|GA|SP|RELEASE|BUILD))\d*
                )
                |                   # or numeric token like '-1' (e.g., alpha-1)
                \d+
            )
        )*
    )
    (?:-
        (?P<classifier>[A-Za-z][A-Za-z0-9._-]*)
    )?
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

def parse_version_from_filename(filename: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse <name>-<version>(-<classifier>)?.jar robustly.
    - Keeps SNAPSHOT/alpha/beta/rc/etc. inside version.
    - Treats trailing token as classifier only if not a version-like qualifier.
    Returns (name, version|None, classifier|None).
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    m = _version_re.match(base)
    if m:
        name = m.group("name")
        ver = m.group("version")
        classifier = m.group("classifier")
        # If classifier looks like a version qualifier, merge it into version
        if classifier:
            # If classifier looks numeric or versiony, it's probably part of version; merge back
            cl_up = classifier.upper()
            if (cl_up in KNOWN_VERSION_QUALIFIERS or
                re.fullmatch(r"(?:RC|CR|M|ALPHA|BETA|SP|BUILD)\d*", cl_up) or
                re.fullmatch(r"\d+(?:[._-]\d+)*", classifier)):
                ver = f"{ver}-{classifier}"
                classifier = None
        return name, ver, classifier

    # Fallback: split on dashes, try from right
    parts = base.split("-")
    if len(parts) == 1:
        return base, None, None
    # Heuristic: last token is classifier if purely alpha and not a known version word
    last = parts[-1]
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]*", last) and last.upper() not in KNOWN_VERSION_QUALIFIERS:
        name = "-".join(parts[:-2]) if len(parts) >= 3 else parts[0]
        version = parts[-2] if len(parts) >= 2 else None
        classifier = last
    else:
        name = "-".join(parts[:-1])
        version = parts[-1]
        classifier = None
    return name or base, version, classifier

def _best_pom_props(zf: zipfile.ZipFile, filename: str, pom_paths: List[str], base_name: str) -> Dict[str, str]:
    """Pick the most likely pom.properties when multiple exist (e.g., shaded jars)."""
    stem = os.path.splitext(filename)[0].lower()
    base = base_name.lower()
    best_props: Dict[str, str] = {}
    best_score = (-10**9, -10**9)  # (score, -path_len)
    for p in pom_paths:
        props = parse_properties(_read_text(zf, p))
        gid = (props.get("groupId") or "").lower()
        aid = (props.get("artifactId") or "").lower()
        score = 0
        # Prefer artifactId that equals or appears in the stem/base
        if aid:
            if aid == base or aid == stem or aid in stem or aid in base:
                score += 4
        # Prefer groupId appearing as reverse-dns in symbol names
        if gid and gid.replace(".", "-") in stem:
            score += 1
        # Slight bump if path structure matches META-INF/maven/<gid>/<aid>/pom.properties
        try:
            parts = p.split("/")
            idx = parts.index("maven")
            if idx + 3 < len(parts):
                pgid, paid = parts[idx + 1], parts[idx + 2]
                if paid.lower() == aid and pgid.lower() == gid:
                    score += 1
        except ValueError:
            pass
        candidate = (score, -len(p))
        if candidate > best_score:
            best_score = candidate
            best_props = props
    return best_props

def _compute_hash(path: str, algo: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not algo or algo.lower() == "none":
        return None, None
    h = None
    algo = algo.lower()
    if   algo == "sha1":   h = hashlib.sha1()
    elif algo == "sha256": h = hashlib.sha256()
    elif algo == "md5":    h = hashlib.md5()
    else:
        raise ValueError(f"Unsupported hash algo: {algo}")
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest(), algo
    except Exception as e:
        logging.warning("Failed to hash %s: %s", path, e)
        return None, None

def read_jar_info(jar_path: str, hash_algo: Optional[str] = None) -> JarInfo:
    filename = os.path.basename(jar_path)
    base_name, fname_ver, classifier_from_name = parse_version_from_filename(filename)

    def _finalize(key: str, version: Optional[str], source: str,
                  groupId: Optional[str] = None, artifactId: Optional[str] = None,
                  classifier: Optional[str] = classifier_from_name,
                  invalid: bool = False) -> JarInfo:
        v = (version or fname_ver or "UNKNOWN").strip()
        # Append classifier into key identity if present
        k = key if not classifier else f"{key}:{classifier}"
        file_hash, algo_used = _compute_hash(jar_path, hash_algo)
        return JarInfo(
            key=k, version=v, source=("invalid-jar" if invalid else source),
            filename=filename, path=jar_path,
            groupId=groupId, artifactId=artifactId,
            classifier=classifier,
            file_hash=file_hash, hash_algo=algo_used
        )

    try:
        with zipfile.ZipFile(jar_path, "r") as zf:
            # 1) Try pom.properties (most reliable)
            pom_paths = [n for n in zf.namelist()
                         if n.startswith("META-INF/maven/") and n.endswith("pom.properties")]
            if pom_paths:
                props = _best_pom_props(zf, filename, pom_paths, base_name)
                groupId = props.get("groupId")
                artifactId = props.get("artifactId")
                version = props.get("version")
                if artifactId:
                    key = f"{groupId}:{artifactId}" if groupId else artifactId
                else:
                    key = base_name
                return _finalize(key, version, "pom.properties",
                                 groupId=groupId, artifactId=artifactId)

            # 2) Try MANIFEST.MF (OSGi/Maven-ish)
            man = parse_manifest(_read_text(zf, "META-INF/MANIFEST.MF"))
            version = next((man.get(k) for k in VERSION_KEYS if man.get(k)), None)
            impl_title = (man.get("Implementation-Title")
                          or man.get("Bundle-SymbolicName")
                          or man.get("Bundle-Name"))
            if impl_title:
                key = impl_title.strip()
            else:
                key = base_name
            if version:
                return _finalize(key, version, "manifest")

            # 3) Fallback: parsed filename
            return _finalize(base_name, fname_ver, "filename")

    except zipfile.BadZipFile:
        logging.warning("BadZipFile for %s", jar_path)
        return _finalize(base_name, fname_ver, "invalid-jar", invalid=True)
    except Exception as e:
        logging.warning("Error reading jar %s: %s", jar_path, e)
        return _finalize(base_name, fname_ver, "invalid-jar", invalid=True)

def iter_jars(dir_path: str, recurse: bool = False) -> Iterable[str]:
    if recurse:
        for root, _, files in os.walk(dir_path):
            for f in files:
                if f.lower().endswith(".jar"):
                    yield os.path.join(root, f)
    else:
        with os.scandir(dir_path) as it:
            for e in it:
                if e.is_file() and e.name.lower().endswith(".jar"):
                    yield e.path

def index_lib_dir(dir_path: str, recurse: bool = False, hash_algo: Optional[str] = None
                  ) -> Dict[str, JarInfo]:
    jar_infos: Dict[str, JarInfo] = {}
    rank = {"pom.properties": 3, "manifest": 2, "filename": 1, "invalid-jar": 0}
    for jar_path in iter_jars(dir_path, recurse=recurse):
        info = read_jar_info(jar_path, hash_algo=hash_algo)
        existing = jar_infos.get(info.key)
        if existing is None or rank[info.source] > rank[existing.source]:
            jar_infos[info.key] = info
        elif existing and rank[info.source] == rank[existing.source]:
            # Same rank: prefer the one with version not UNKNOWN, or keep shortest filename
            if existing.version == "UNKNOWN" and info.version != "UNKNOWN":
                jar_infos[info.key] = info
            elif len(info.filename) < len(existing.filename):
                jar_infos[info.key] = info
    return jar_infos

def compare(a: Dict[str, JarInfo], b: Dict[str, JarInfo]):
    keys_a = set(a.keys())
    keys_b = set(b.keys())
    removed = sorted(keys_a - keys_b)
    added   = sorted(keys_b - keys_a)
    common  = sorted(keys_a & keys_b)

    changed: List[Tuple[str, str, str]] = []
    same: List[str] = []
    for k in common:
        va = (a[k].version or "").strip()
        vb = (b[k].version or "").strip()
        if va != vb:
            changed.append((k, va, vb))
        else:
            same.append(k)
    return removed, added, changed, same

# ----- Optional: package surface comparison -----
def extract_packages_from_jar(jar_path: str) -> Set[str]:
    pkgs: Set[str] = set()
    with zipfile.ZipFile(jar_path, 'r') as z:
        for n in z.namelist():
            if n.endswith(".class") and not n.startswith("META-INF/"):
                pkg = os.path.dirname(n).replace("/", ".")
                if pkg:
                    pkgs.add(pkg)
    return pkgs

def packages_in_dir(dir_path: str, recurse: bool = False) -> Set[str]:
    all_pkgs: Set[str] = set()
    for jar in iter_jars(dir_path, recurse=recurse):
        try:
            all_pkgs |= extract_packages_from_jar(jar)
        except zipfile.BadZipFile:
            logging.warning("BadZipFile while scanning packages: %s", jar)
        except Exception as e:
            logging.warning("Error scanning packages in %s: %s", jar, e)
    return all_pkgs

# ----- Output helpers -----
def _jarinfo_to_public_dict(j: JarInfo) -> Dict[str, Optional[str]]:
    d = asdict(j)
    # Keep only useful fields for output
    keep = ["key", "version", "source", "filename", "path", "groupId",
            "artifactId", "classifier", "file_hash", "hash_algo"]
    return {k: d.get(k) for k in keep}

def build_structured_result(a: Dict[str, JarInfo], b: Dict[str, JarInfo],
                            removed: List[str], added: List[str],
                            changed: List[Tuple[str, str, str]], same: List[str],
                            hash_enabled: bool,
                            pkgsA: Optional[Set[str]] = None,
                            pkgsB: Optional[Set[str]] = None) -> Dict:
    result = {
        "summary": {
            "removed": len(removed),
            "added": len(added),
            "changed": len(changed),
            "unchanged": len(same),
        },
        "removed": [_jarinfo_to_public_dict(a[k]) for k in removed],
        "added": [_jarinfo_to_public_dict(b[k]) for k in added],
        "changed": [
            {
                "key": k,
                "old_version": va, "new_version": vb,
                "old_source": a[k].source, "new_source": b[k].source,
                "old_filename": a[k].filename, "new_filename": b[k].filename,
                "groupId": a[k].groupId or b[k].groupId,
                "artifactId": a[k].artifactId or b[k].artifactId,
                "classifier": a[k].classifier or b[k].classifier,
                "old_hash": a[k].file_hash, "new_hash": b[k].file_hash,
                "hash_algo": a[k].hash_algo or b[k].hash_algo,
            }
            for (k, va, vb) in changed
        ],
        "unchanged": [_jarinfo_to_public_dict(a[k]) for k in same],
    }

    # Content-changed detection (same version but different hash)
    if hash_enabled:
        content_changed = []
        for k in same:
            ia, ib = a[k], b[k]
            if ia.file_hash and ib.file_hash and ia.file_hash != ib.file_hash:
                content_changed.append({
                    "key": k,
                    "version": ia.version,
                    "filename_a": ia.filename, "filename_b": ib.filename,
                    "hash_a": ia.file_hash, "hash_b": ib.file_hash,
                    "hash_algo": ia.hash_algo or ib.hash_algo
                })
        if content_changed:
            result["content_changed_same_version"] = content_changed

    # Packages
    if pkgsA is not None and pkgsB is not None:
        result["package_delta"] = {
            "only_in_a": len(pkgsA - pkgsB),
            "only_in_b": len(pkgsB - pkgsA),
            # If you want full lists, uncomment:
            # "packages_only_in_a": sorted(pkgsA - pkgsB),
            # "packages_only_in_b": sorted(pkgsB - pkgsA),
        }
    return result

def emit_text(a: Dict[str, JarInfo], b: Dict[str, JarInfo],
              removed: List[str], added: List[str],
              changed: List[Tuple[str, str, str]], same: List[str],
              hash_enabled: bool,
              pkgsA: Optional[Set[str]] = None, pkgsB: Optional[Set[str]] = None) -> str:
    out_lines: List[str] = []
    out_lines.append("=== Summary ===")
    out_lines.append(f"Removed:   {len(removed)}")
    out_lines.append(f"Added:     {len(added)}")
    out_lines.append(f"Changed:   {len(changed)}")
    out_lines.append(f"Unchanged: {len(same)}")
    out_lines.append("")

    if removed:
        out_lines.append("=== Removed (present in A, missing in B) ===")
        for k in removed:
            info = a[k]
            out_lines.append(f"- {k}  @ {info.version}  [{info.source}]  ({info.filename})")
        out_lines.append("")

    if added:
        out_lines.append("=== Added (present in B, missing in A) ===")
        for k in added:
            info = b[k]
            out_lines.append(f"+ {k}  @ {info.version}  [{info.source}]  ({info.filename})")
        out_lines.append("")

    if changed:
        out_lines.append("=== Version Changes (A → B) ===")
        for k, va, vb in changed:
            sa = a[k].source; sb = b[k].source
            fa = a[k].filename; fb = b[k].filename
            out_lines.append(f"* {k}: {va} [{sa}] ({fa})  →  {vb} [{sb}] ({fb})")
        out_lines.append("")

    if hash_enabled and same:
        # Show same-version content changes via hash
        content_changed = []
        for k in same:
            ia, ib = a[k], b[k]
            if ia.file_hash and ib.file_hash and ia.file_hash != ib.file_hash:
                content_changed.append((k, ia, ib))
        if content_changed:
            out_lines.append("=== Content Changes (same version, different file hash) ===")
            for k, ia, ib in content_changed:
                out_lines.append(f"! {k}: {ia.version}  {ia.file_hash} ({ia.filename})  ≠  {ib.file_hash} ({ib.filename}) [{ia.hash_algo or ib.hash_algo}]")
            out_lines.append("")

    if pkgsA is not None and pkgsB is not None:
        onlyA = sorted(pkgsA - pkgsB)
        onlyB = sorted(pkgsB - pkgsA)
        out_lines.append("=== Package Delta (by .class paths) ===")
        out_lines.append(f"Only in A: {len(onlyA)}")
        out_lines.append(f"Only in B: {len(onlyB)}")
        # Uncomment to list packages:
        # for p in onlyA: out_lines.append(f"  - {p}")
        # for p in onlyB: out_lines.append(f"  + {p}")

    return "\n".join(out_lines) + ("\n" if out_lines else "")

def emit_json(result: Dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n"

def emit_xml(result: Dict) -> str:
    root = ET.Element("jardiff", version=__version__)
    summary = ET.SubElement(root, "summary")
    for k, v in result["summary"].items():
        ET.SubElement(summary, k).text = str(v)

    def _add_list(tag: str, items: List[Dict]):
        parent = ET.SubElement(root, tag)
        for it in items:
            elem = ET.SubElement(parent, "jar")
            for k, v in it.items():
                if v is None:
                    continue
                elem.set(k, str(v))

    _add_list("removed", result["removed"])
    _add_list("added", result["added"])

    changed_parent = ET.SubElement(root, "changed")
    for ch in result["changed"]:
        elem = ET.SubElement(changed_parent, "jar")
        for k, v in ch.items():
            if v is None:
                continue
            elem.set(k, str(v))

    _add_list("unchanged", result["unchanged"])

    if "content_changed_same_version" in result:
        _add_list("content_changed_same_version", result["content_changed_same_version"])

    if "package_delta" in result:
        pd = ET.SubElement(root, "package_delta")
        for k, v in result["package_delta"].items():
            ET.SubElement(pd, k).text = str(v)

    xml_str = ET.tostring(root, encoding="utf-8")
    try:
        # pretty-print without external deps
        import xml.dom.minidom as minidom
        return minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    except Exception:
        return xml_str.decode("utf-8")

# ----- CLI -----
def build_parser():
    parser = argparse.ArgumentParser(
        prog="jardiff",
        description="Compare JAR libraries (with versions) between two lib directories.",
        formatter_class=HelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              jardiff diff libA libB
              jardiff diff -r --packages libA libB
              jardiff diff --format json --output report.json libA libB
              jardiff diff --hash sha1 libA libB
              jardiff help
              jardiff help diff
        """),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="command")

    # diff command (main behavior)
    diff = sub.add_parser("diff", help="Compare two lib directories", formatter_class=HelpFormatter)
    diff.add_argument("lib_a", help="Path to first lib directory (baseline)")
    diff.add_argument("lib_b", help="Path to second lib directory (target)")
    diff.add_argument("-r", "--recurse", action="store_true", help="Scan subdirectories recursively")
    diff.add_argument("--packages", action="store_true", help="Also compare class package sets")
    diff.add_argument("--hash", choices=["none", "sha1", "sha256", "md5"], default="none",
                      help="Compute file hash to detect content changes even if versions match")
    diff.add_argument("--format", choices=["text", "json", "xml"], default="text",
                      help="Output format")
    diff.add_argument("--output", metavar="PATH", help="Write output to file (instead of stdout)")
    diff.add_argument("--log-level", default="WARNING",
                      choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
                      help="Logging verbosity (warnings include invalid/corrupt jars)")
    diff.epilog = textwrap.dedent("""\
        Examples:
          jardiff diff libA libB
          jardiff diff -r --packages /opt/app/lib_old /opt/app/lib_new
          jardiff diff --format json --output diff.json libA libB
          jardiff diff --hash sha1 libA libB
    """)

    # help command
    help_p = sub.add_parser(
        "help",
        help="Show general help or help for a command",
        description="Show general help or help for a command",
        formatter_class=HelpFormatter
    )
    help_p.add_argument("topic", nargs="?", choices=["diff"], help="Command to show help for")

    return parser, diff

def run_diff(args):
    # Logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.WARNING),
                        format="%(levelname)s: %(message)s")

    # Validate dirs early for clearer errors
    for d in (args.lib_a, args.lib_b):
        if not os.path.isdir(d):
            print(f"error: '{d}' is not a directory or doesn't exist", file=sys.stderr)
            sys.exit(2)

    hash_algo = None if args.hash == "none" else args.hash

    a = index_lib_dir(args.lib_a, recurse=args.recurse, hash_algo=hash_algo)
    b = index_lib_dir(args.lib_b, recurse=args.recurse, hash_algo=hash_algo)

    removed, added, changed, same = compare(a, b)

    pkgsA = pkgsB = None
    if args.packages:
        pkgsA = packages_in_dir(args.lib_a, recurse=args.recurse)
        pkgsB = packages_in_dir(args.lib_b, recurse=args.recurse)

    # Prepare output
    if args.format == "text":
        text = emit_text(a, b, removed, added, changed, same, hash_enabled=bool(hash_algo),
                         pkgsA=pkgsA, pkgsB=pkgsB)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            sys.stdout.write(text)
    else:
        result = build_structured_result(
            a, b, removed, added, changed, same,
            hash_enabled=bool(hash_algo), pkgsA=pkgsA, pkgsB=pkgsB
        )
        payload = emit_json(result) if args.format == "json" else emit_xml(result)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload)
        else:
            sys.stdout.write(payload)

def main():
    parser, diff = build_parser()
    argv = sys.argv[1:]
    # Back-compat shortcut: allow `jardiff <args>` to mean `jardiff diff <args>`
    if argv and argv[0] not in {"diff", "help", "-h", "--help", "--version"}:
        sys.argv.insert(1, "diff")

    args = parser.parse_args()

    if args.command == "help":
        topic = getattr(args, "topic", None)
        if topic == "diff":
            print("Compare two lib directories")
            diff.print_help()
        else:
            parser.print_help()
        return

    if args.command == "diff":
        run_diff(args)
    else:
        parser.print_help()
        sys.exit(2)

if __name__ == "__main__":
    main()
