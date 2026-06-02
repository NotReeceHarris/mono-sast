![mono-sast](https://s6.imgcdn.dev/YdTyFy.png)

mono-sast (*monolithic static application security testing tool*) is a monolithic tool that runs multiple open-source SAST scanners against your codebase and normalises the output into various formats, fully configurable to support native tool configs. 

```bash
docker run --rm -v "$(pwd):/target:ro" ghcr.io/notreeceharris/mono-sast
```

### Options

Pass options as `key=value` arguments after the image name.

| Flag | Default | Description |
|---|---|---|
| `f=` | `sarif` | Comma-separated output formats: `sarif`, `html`, `markdown` |
| `o=` | `.` | Directory to write output files into |

| Format | File | Description |
|---|---|---|
| `sarif` | `results.json` | Merged SARIF 2.1.0 |
| `html` | `report.html` | Browsable HTML report |
| `markdown` | `report.md` | Markdown report with collapsible finding details |

```bash
# SARIF only (default) — writes results.json to the current directory
docker run --rm -v "$(pwd):/target:ro" ghcr.io/notreeceharris/mono-sast

# Using make dev (pass flags via ARGS=)
TARGET_DIR="/path/to/repo" make dev
TARGET_DIR="/path/to/repo" make dev ARGS="f=markdown"
TARGET_DIR="/path/to/repo" make dev ARGS="f=sarif,html,markdown o=/out"

# Markdown report only
docker run --rm -v "$(pwd):/target:ro" -v "$(pwd)/out:/out" ghcr.io/notreeceharris/mono-sast f=markdown o=/out

# All formats into a custom output directory
docker run --rm -v "$(pwd):/target:ro" -v "$(pwd)/out:/out" ghcr.io/notreeceharris/mono-sast f=sarif,html,markdown o=/out
```

## Scanners

Progress toward full scanner coverage. Checked scanners are active and producing output; unchecked are planned or in progress.

| Scanner | Language(s) | Implemented |
|---|---|---|
| [microsoft/DevSkim](https://github.com/microsoft/DevSkim) | multilanguage static code analyzer. | <ul><li>- [X] </li></ul> |
| [github/codeql](https://github.com/github/codeql) | GitHub's semantic analysis engine | <ul><li>- [X] </li></ul> |
| [opengrep/opengrep](https://github.com/opengrep/opengrep) | OSS Semgrep fork | <ul><li>- [X] </li></ul> |
| [semgrep/semgrep](https://github.com/semgrep/semgrep) | Multi-language pattern matching | <ul><li>- [X] </li></ul> |
| [bearer/bearer](https://github.com/bearer/bearer) | Privacy & security scanning | <ul><li>- [X] </li></ul> |
| [SonarQube CE](https://www.sonarsource.com/products/sonarqube) | Community edition | <ul><li>- [ ] </li></ul> |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Vulnerability & misconfiguration | <ul><li>- [X] </li></ul> |
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | Secret detection | <ul><li>- [ ] </li></ul> |
| [betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) | Secret detection | <ul><li>- [ ] </li></ul> |
| [boostsecurityio/poutine](https://github.com/boostsecurityio/poutine) | Supply chain vulnerability scanner for build pipelines | <ul><li>- [ ] </li></ul> |

| Scanner | Language(s) | Implemented |
|---|---|---|
| [facebook/infer](https://github.com/facebook/infer) | `Java` `C` `C++` `ObjC` `Erlang` `Swift` `Hack` | <ul><li>- [ ] </li></ul> |
| [rust-lang/rust-clippy](https://github.com/rust-lang/rust-clippy) | `Rust` | <ul><li>- [ ] </li></ul> |
| [joernio/joern](https://github.com/joernio/joern) | `C` `C++` `Java` `Binary` `Javascript` `Python` `Kotlin` | <ul><li>- [ ] </li></ul> |
| [pycqa/bandit](https://github.com/PyCQA/bandit) | `Python` | <ul><li>- [X] </li></ul> |
| [securego/gosec](https://github.com/securego/gosec) | `Go` | <ul><li>- [X] </li></ul> |
| [presidentbeef/brakeman](https://github.com/presidentbeef/brakeman) | `Ruby` | <ul><li>- [X] </li></ul> |
| [spotbugs/spotbugs](https://github.com/spotbugs/spotbugs) | `Java` | <ul><li>- [X] </li></ul> |
| [thesp0nge/dawnscanner](https://github.com/thesp0nge/dawnscanner) | `Ruby` | <ul><li>- [ ] </li></ul> |
| [phpstan/phpstan](https://github.com/phpstan/phpstan) | `PHP` | <ul><li>- [X] </li></ul> |
| [david-a-wheeler/flawfinder](https://github.com/david-a-wheeler/flawfinder) | `C` `C++` | <ul><li>- [X] </li></ul> |
| [cppcheck-opensource/cppcheck](https://github.com/cppcheck-opensource/cppcheck) | `C` `C++` | <ul><li>- [X] </li></ul> |
| [ajinabraham/njsscan](https://github.com/ajinabraham/njsscan) | `Node.js` | <ul><li>- [X] </li></ul> |
| [quay/clair](https://github.com/quay/clair) | `Containers` | <ul><li>- [ ] </li></ul> |

## Contributing

Scanner additions and output normalisers are the most valuable contributions. If you maintain or regularly use a SAST tool that isn't listed here, open an issue or a PR.

See [contributing.md](contributing.md) for the full guide.

## License

GPL-3.0. Use it, fork it, embed it, don't sell it as a SaaS without at least feeling a bit guilty.
