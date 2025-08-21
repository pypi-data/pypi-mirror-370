# jardiff

`jardiff` is a command-line tool for comparing two directories of Java
archive (JAR) files.  It attempts to identify matching libraries by
examining Maven metadata (`pom.properties` inside the JAR), manifest
attributes, and heuristics based on the filename.  Versions are parsed
robustly, including common qualifiers such as `SNAPSHOT` or `alpha`, and
classifier suffixes like `sources` or `tests` are accounted for when
present.

The tool can output human-readable text summaries or structured JSON/XML
reports.  It optionally computes cryptographic hashes of the JAR files
to detect content changes even when the version string remains the same.

## Installation

The package is available on PyPI.  The recommended way to install
command-line utilities is with [`pipx`](https://pypi.org/project/pipx/):

```bash
pipx install jardiff
```

Alternatively, you can use `pip` directly:

```bash
pip install jardiff
```

## Usage

To compare two directories of JAR files:

```bash
jardiff diff path/to/libA path/to/libB
```

Key options include:

| Option           | Description                                              |
|------------------|----------------------------------------------------------|
| `-r`, `--recurse`| Scan subdirectories recursively                         |
| `--packages`     | Compare Java package sets to detect API differences      |
| `--hash`         | Compute file hashes (`sha1`, `sha256`, `md5`)            |
| `--format`       | Output format: `text` (default), `json`, or `xml`        |
| `--output`       | Write the output to the specified file instead of stdout |

For example, to produce a JSON report of the differences:

```bash
jardiff diff --format json --output report.json /opt/app/lib_old /opt/app/lib_new
```

See the command-line help for more details:

```bash
jardiff diff --help
```
