# Catalogue of Open-Source / Free SAST Tools for a Unified "mono-sast" Scanning System

## TL;DR
- A unified mono-sast pipeline can be assembled almost entirely from actively-maintained open-source tools: pair a polyglot core (Opengrep or Semgrep CE + CodeQL + Joern) with language-specific specialists (gosec, Brakeman, Bandit, dawnscanner, FindSecBugs/SpotBugs, detekt, Puma Scan, Roslyn Security Guard/Security Code Scan, MobSF/mobsfscan, Slither/Aderyn) and IaC/container scanners (Checkov, KICS, Trivy, Kubescape, Hadolint).
- The 2025 Semgrep relicensing produced **Opengrep** (LGPL-2.1, vendor-backed fork released Feb 2025, v1.20.0 in April 2026), which restores cross-function taint analysis and is now the strongest fully-open polyglot replacement; **Joern** (Apache-2.0, code-property-graph engine for C/C++/Java/JS/TS/Python/Kotlin/binaries) is the most powerful free deep-analysis option, while **CodeQL CLI** remains free for open-source.
- Avoid relying on **Insider** (effectively abandoned since 2023) and treat **dawnscanner** (last gem April 2024) and **detect-secrets** (v1.5.0, May 2024) as "stable but slowing" — verify before adoption.

## Key Findings

1. **The polyglot tier is consolidating around four engines**: Semgrep CE (LGPL after Jan 2025 relicensing), its community fork Opengrep, GitHub's CodeQL, and Joern's Code Property Graph platform. These cover 20–30+ languages each and are the backbone of any mono-sast.
2. **IaC SAST is now broader than application SAST**: Checkov (1,000+ checks, graph-based), KICS (2,400+ Rego queries, 22+ platforms), and Trivy (which absorbed tfsec in 2023 and, per ARMO's March 2026 analysis, "the most widely used open-source vulnerability scanner in the cloud-native ecosystem, with 32,000+ GitHub stars and over 100 million Docker Hub pulls") collectively cover Terraform, CloudFormation, Kubernetes, Helm, Ansible, Dockerfile, ARM, and Serverless. Terrascan was archived by Tenable on November 20, 2025 — migrate users to Checkov/KICS/Trivy.
3. **Mobile and smart-contract niches have strong dedicated OSS**: MobSF/mobsfscan for Android/iOS (Java/Kotlin/Swift/Objective-C), Slither + Aderyn + Mythril for Solidity/Vyper. These are not duplicated by polyglot scanners.
4. **Several "household-name" tools are now in a marginal state** and should be selected with care: Insider (abandoned), dawnscanner (active gem but commits ~2021), FindBugs (replaced by SpotBugs), tfsec (absorbed by Trivy), Terrascan (archived November 2025).
5. **SARIF is the de-facto interchange format**: every well-maintained tool catalogued here either emits SARIF natively (Opengrep, Semgrep, CodeQL, detekt, Kubescape, Bandit, Trivy, Checkov, KICS, gosec, SpotBugs ≥4.7, Hadolint) or has a SARIF converter, making aggregation tractable.

---

## Section 1: Multi-Language / Polyglot SAST Tools

### Opengrep
- **Homepage / repo:** https://github.com/opengrep/opengrep
- **Primary SAST focus:** Injection (SQLi/XSS/command), insecure crypto, hardcoded secrets, unsafe deserialization, SSRF, path traversal, custom security rules — same vulnerability surface as Semgrep, plus restored cross-function taint analysis.
- **Languages:** 30+ — Apex, Bash, C, C++, C#, Clojure, Dockerfile, Elixir, Go, Java, JavaScript/TypeScript, Kotlin, PHP, Python, Ruby, Rust, Scala, Solidity, Swift, Terraform, Visual Basic (Opengrep-exclusive), YAML, and more. Taint tracking is available for ~12 of these.
- **Approach:** Pattern matching on a generic AST/IR with intra- and inter-procedural taint analysis; OCaml 5 engine with shared-memory parallelism.
- **Deployment:** Standalone CLI binary (Linux/macOS/Windows incl. ARM), Docker, GitHub Action; drop-in for existing Semgrep CI configs. Cosign-signed releases.
- **License:** LGPL-2.1 (engine).
- **Maintenance:** Very active. Per the January 23, 2025 Kodem launch press release, the founding consortium was nine co-founders — **Aikido Security, Arnica, Amplify Security, Endor Labs, Jit, Kodem, Legit Security, Mobb, and Orca Security** — with Phoenix Security subsequently listed as a 10th backer in the opengrep/opengrep README. Releases: v1.20.0 on 2026-04-21; v1.21.0 around mid-May 2026.
- **Integration:** SARIF 2.1.0, JSON, text. Designed for CI parity with Semgrep CE.
- **Unique strengths:** Re-introduces features Semgrep moved to its commercial product (cross-function taint, fingerprinting, tracking ignores); native Windows support; truly community-governed.

### Semgrep CE (post-2025 relicensing — for completeness)
Baseline tool, but worth noting that since January 2025 the core engine is LGPL-2.1 and **advanced cross-file / cross-function taint analysis was moved behind Semgrep Pro**. For a pure-OSS mono-sast, prefer Opengrep; for managed rule registry and team features, Semgrep CE still suffices for single-file analysis.

### CodeQL CLI
- **Homepage / repo:** https://codeql.github.com / https://github.com/github/codeql
- **Primary SAST focus:** Deep semantic vulnerability discovery — injection, taint, control-flow, dataflow, custom queries written in QL.
- **Languages:** C/C++, C#, Go, Java/Kotlin, JavaScript/TypeScript, Python, Ruby, Swift, and (beta) GitHub Actions workflows.
- **Approach:** Build a relational database from compiled or extracted source, query with Datalog-style QL; full interprocedural, taint, and dataflow analysis.
- **Deployment:** CLI + VS Code extension; GitHub Actions integration; Docker.
- **License:** CodeQL CLI is free for analysis of open-source projects under GitHub's CodeQL terms; not OSI-open. The QL queries and libraries are MIT (github/codeql repo).
- **Maintenance:** Continuous releases by GitHub.
- **Integration:** Native SARIF output, GitHub Code Scanning integration.
- **Unique strengths:** Deepest free taint/dataflow available; large library of community + GitHub Security Lab queries.

### Joern
- **Homepage / repo:** https://github.com/joernio/joern
- **Primary SAST focus:** Vulnerability research and deep static analysis — buffer overflows, taint flows, injection sinks, custom security patterns expressed as graph traversals.
- **Languages:** C/C++, Java (source + bytecode), JavaScript/TypeScript, Python, Kotlin, PHP, Ruby, Go, Swift, Solidity (community), LLVM bitcode, x86 binaries via Ghidra.
- **Approach:** Builds a Code Property Graph (CPG) combining AST + CFG + PDG + call graph; queryable in a Scala-based DSL with full interprocedural dataflow + taint.
- **Deployment:** CLI + interactive REPL; Docker; runs on JVM.
- **License:** Apache-2.0.
- **Maintenance:** Very active — v4.0.542 on 2026-05-19 (auto-versioned per merged commit).
- **Integration:** JSON exports; Neo4j/CSV graph export; can produce SARIF via wrappers. Best for batch/research workflows, not low-latency PR checks.
- **Unique strengths:** Only fully-open binary + bytecode + source CPG platform; allows custom dataflow queries comparable to CodeQL.

### PMD (Apache PMD)
- **Homepage:** https://pmd.github.io / https://github.com/pmd/pmd
- **Primary SAST focus:** Programmer-error patterns and a small set of security rules per language (e.g., Apex security ruleset covering CRUD/FLS checks, SOQL injection, sharing rules; Java security-adjacent rules around crypto and serialization).
- **Languages:** Java, JavaScript, Apex, Visualforce, Kotlin, Swift, Modelica, PL/SQL, Apache Velocity, JSP, WSDL, Maven POM, HTML, XML/XSL (with security rules strongest for Apex/Visualforce and reasonable for Java).
- **Approach:** AST-based pattern matching; XPath rules + Java-coded rules; CPD copy-paste detector.
- **Deployment:** CLI, Maven/Gradle/Ant plugins, IDE plugins.
- **License:** Apache-2.0 / BSD-style.
- **Maintenance:** Highly active — release cadence multiple per year; PMD 7.x stable; PMD For Eclipse 7.24 released 2026-04-24.
- **Integration:** SARIF, XML, HTML, CSV, text outputs; CI-friendly.
- **Unique strengths:** Only mature open-source security analyzer for Salesforce Apex/Visualforce; valuable for Java alongside SpotBugs.

### DevSkim (Microsoft)
- **Homepage / repo:** https://github.com/microsoft/DevSkim
- **Primary SAST focus:** Regex-based detection of insecure API usage, weak crypto, unsafe functions, hardcoded credentials, banned APIs.
- **Languages:** C/C++, C#, PHP, ASP, Python, Ruby, Java, JavaScript, Go, Rust, and others.
- **Approach:** Pattern/regex-based (lightweight). Not dataflow.
- **Deployment:** CLI, VS Code / Visual Studio / Sublime extensions, GitHub Action.
- **License:** MIT.
- **Maintenance:** Maintained by Microsoft.
- **Integration:** SARIF output; CI-friendly.
- **Unique strengths:** Extremely fast IDE-shift-left; complements heavier engines.

### Scanmycode CE (formerly QuantifiedCode / mztools)
- **Homepage / repo:** https://github.com/marcinguy/scanmycode-ce
- **Primary SAST focus:** Aggregator that runs many open-source scanners (Bandit, Brakeman, FindSecBugs, Semgrep/Opengrep, gosec, njsscan, etc.) and produces a deduplicated unified report.
- **Languages:** Multi (delegated).
- **Approach:** Orchestration of underlying tools.
- **Deployment:** Docker / self-hosted server with web UI + CLI / API.
- **License:** AGPL-3.0 (CE).
- **Maintenance:** Actively maintained community edition.
- **Integration:** JSON/HTML report; useful as a reference architecture for a mono-sast.

### graudit
- **Homepage / repo:** https://github.com/wireghoul/graudit
- **Primary SAST focus:** Grep-based pattern dictionaries for insecure code in C/C++, PHP, ASP, C#, Java, Perl, Python, Ruby, JSP, SQL.
- **Approach:** Regex/grep with curated signature databases.
- **License:** GPL-3.0.
- **Maintenance:** Active; useful for grep-based first-pass coverage and for Perl/legacy languages where dataflow tools are absent.

### Application Inspector (Microsoft)
- **Homepage / repo:** https://github.com/microsoft/ApplicationInspector
- **Primary SAST focus:** Surface-mapping of risky/sensitive API usage (crypto APIs, network calls, system access, secrets patterns) across a codebase — not vulnerability detection per se, but valuable as an intelligence input.
- **Languages:** 25+.
- **License:** MIT. **Note:** This is reconnaissance-oriented; include only if its output is consumed for triage/SBoM-like enrichment.

---

## Section 2: Language-Specific Tools

### Python
- **Bandit** *(baseline — still actively maintained by PyCQA, regular releases)*.
- **Dlint** — https://github.com/dlint-py/dlint — Flake8 plugin focused on security best practices (e.g., unsafe yaml.load, subprocess shell=True, tempfile races). MIT, AST-based, CI-friendly via Flake8.
- **Pysa** — Meta's taint analyzer built on top of the Pyre type-checker. https://github.com/facebook/pyre-check. MIT. Provides interprocedural taint analysis for Python; useful for large monorepos. Active.

### JavaScript / TypeScript (Node.js, browser, Deno, Bun)
- **njsscan / NodeJSScan** — https://github.com/ajinabraham/njsscan and https://github.com/ajinabraham/nodejsscan. SAST for Node.js using libsast + Semgrep rules; CLI + web UI. Covers SQLi, command injection, SSRF, XSS, hardcoded secrets, weak crypto. MIT/LGPL. Active.
- **ESLint security plugins** — `eslint-plugin-security`, `eslint-plugin-no-unsanitized`, `eslint-plugin-security-node`. AST-based; CI-friendly. (Included because they ship explicit security rules — distinguishes them from generic ESLint.)
- **GoatSAST / RetireJS** for known-vulnerable-library detection in JS code (SCA-adjacent, but commonly bundled).

### Java (including Android)
- **SpotBugs + FindSecBugs** *(baseline; still actively released — spotbugs-maven-plugin 4.9.8.2, findsecbugs-plugin v1.14.0 released April 20, 2025 per find-sec-bugs.github.io: "Download version 1.14.0 (Last updated: April 20th, 2025)")*. Bytecode analysis; OWASP Top 10 patterns; SARIF support added in modern versions.
- **PMD with Java security ruleset** — see polyglot section.
- **Error Prone (Google)** — https://errorprone.info — compile-time checks; some are security-adjacent (e.g., insecure random, unsafe formatting). Apache-2.0. Useful as a build-time gate.
- **Infer (Meta)** — https://github.com/facebook/infer. MIT. Bi-abductive interprocedural analysis for Java, C, C++, Objective-C, Erlang, Swift, Hack. The main branch shows continuous Meta commits through September 2025 (e.g., Pulse-infinite/INFINITE_LOOP checker), but the last tagged release is **v1.2.0 (mid-2024)** — flag for "active on main, slow on tags".

### Kotlin (incl. Android)
- **detekt** — https://github.com/detekt/detekt. Apache-2.0. Latest stable **v1.23.8 (Feb 2025)**; 2.0.0-alpha track in progress. **Important caveat**: detekt is primarily a code-smell analyzer; its core rule sets (complexity/style/potential-bugs/exceptions/performance/coroutines/formatting/comments) do **not** ship dedicated security detectors for hardcoded secrets or insecure crypto. Treat detekt as a quality gate and pair it with mobsfscan or Semgrep/Opengrep Kotlin rules for real security coverage. SARIF, HTML, MD, XML reports; first-party Gradle plugin.
- **mobsfscan** (also Java/Swift/Objective-C) — see Mobile section below; covers Kotlin Android security patterns.

### C / C++
- **Clang Static Analyzer + scan-build** — https://clang.llvm.org/docs/ClangStaticAnalyzer.html. Symbolic-execution-based path-sensitive interprocedural analysis; security checkers for taint propagation (`optin.taint.GenericTaint`) covering injection, out-of-bounds, hardcoded passwords, use-after-free. Apache-2.0 (LLVM).
- **CodeChecker (Ericsson)** — https://github.com/Ericsson/codechecker. Apache-2.0. Orchestrates Clang SA, Clang-Tidy, Cppcheck, GCC Static Analyzer, and Facebook Infer; provides web UI + CLI + result deduplication. **v6.27.3 released 2026-02-17**; v6.26.2 on 2025-09-22 included a CVE-2025-40843 fix.
- **GCC Static Analyzer (`-fanalyzer`)** — built into GCC 10+. Detects double-free, use-after-free, null deref, taint-aware buffer overflow, and (with `-fanalyzer-checker=taint`) injection sinks. GPL-3.0.
- **weggli** — https://github.com/weggli-rs/weggli. Apache-2.0. Fast semantic grep for C/C++ patterns; useful for custom security queries and vulnerability research.
- **Joern** — see polyglot section.
- **Infer** — see Java section.

### C# / .NET
- **Roslyn Security Guard / Security Code Scan (SCS)** — https://github.com/security-code-scan/security-code-scan. LGPL-3.0. Roslyn-based analyzer for SQLi, XSS, CSRF, XXE, open redirect, weak crypto, hardcoded passwords across C# and VB.NET; integrates as NuGet analyzer into MSBuild / CI.
- **Puma Scan Community Edition** — https://github.com/pumasecurity/puma-scan. MPL-2.0. Roslyn-based real-time C# analyzer for the OWASP Top 10 patterns (XSS, SQLi, CSRF, LDAPi, deserialization, crypto, password management). CLI for build servers exists in the paid Server Edition; the Community Edition runs inside Visual Studio and via `Puma.Security.Rules` NuGet package consumed by `dotnet build`.
- **DevSkim** — see polyglot section; strong .NET coverage.

### Go
- **gosec** *(baseline)* — actively maintained; SARIF output; CWE mappings; integrates via GitHub Action.
- **gokart (Praetorian)** — https://github.com/praetorian-inc/gokart. Apache-2.0. Source-to-sink taint analysis for Go with focus on low false-positive rate. Active.
- **CodeQL Go** — covers Go in CodeQL CLI.
- **golangci-lint** — meta-linter; bundle gosec inside it for performance in CI.

### Ruby / Rails
- **Brakeman** *(baseline)* — AST-based; active, MIT.
- **dawnscanner** — https://github.com/thesp0nge/dawnscanner. MIT. ~680 security checks for Rails/Sinatra/Padrino + plain Ruby; **latest release 2.3.4 on 2024-04-18**; commits have slowed (avg date of last 50 commits ~2021). Stable but not rapidly evolving — use as a complement to Brakeman, not a primary tool.
- **rubocop with `rubocop-gitlab-security`** rules — provides additional security cops.

### PHP
- **Psalm with taint analysis** *(baseline)*.
- **PHPStan with security extensions** *(baseline)*.
- **Progpilot** — https://github.com/designsecurity/progpilot. LGPL-3.0. Dedicated taint-analysis SAST for PHP; detects SQLi, XSS, XXE, file inclusion. AST + dataflow.
- **RIPS-A2 (open-source)** — older; check maintenance before adoption.

### Rust
- **Clippy** *(baseline, security-adjacent only)*.
- **cargo-audit** — https://github.com/rustsec/rustsec/tree/main/cargo-audit. Apache-2.0/MIT. Scans `Cargo.lock` against the RustSec Advisory Database; canonical SCA-style SAST input for Rust. Maintained by the Rust Secure Code WG.
- **cargo-deny** — https://github.com/EmbarkStudios/cargo-deny. Apache-2.0/MIT. Lints the dependency graph for advisories, licenses, banned crates, duplicate versions.
- **cargo-geiger** — https://github.com/geiger-rs/cargo-geiger. Apache-2.0/MIT. Counts `unsafe` blocks in your crates and transitive dependencies — material security signal in Rust.
- **cargo-vet** — Mozilla — enforces that every dependency is audited; supports importing Google/Mozilla audits.
- **Joern + Semgrep/Opengrep** rules cover source-level Rust patterns.

### Swift / Objective-C (iOS/macOS)
- **mobsfscan** — covers Swift, Objective-C, Kotlin, Java with MobSF rules powered by libsast + Semgrep. CLI; SARIF/JSON. LGPL.
- **MobSF (Mobile-Security-Framework)** — full IPA/APK static + dynamic analyzer; SAST extracts insecure crypto, ATS misconfigurations, insecure WebView, hardcoded keys, plist issues. GPL-3.0. Active.
- **Insider** *(legacy)* — claims Swift coverage but **abandoned** since 2023 (last release 2.1.0 in 2021, org `insider-action` last updated 2023-01-07) — do not adopt.
- **Clang SA** — covers Objective-C natively.

### Scala
- **Joern** — supports JVM bytecode (which covers Scala output).
- **Semgrep/Opengrep** — Scala support is limited; use carefully.
- **scapegoat** — Scala compiler plugin; primarily code quality but flags some unsafe patterns. Apache-2.0.

### Groovy
- **CodeNarc with security ruleset** — https://github.com/CodeNarc/CodeNarc. Apache-2.0. Includes security-relevant rules (`GroovyResultSet`, `SystemExit`, `JavaIoPackageAccess`, basic injection patterns). Active.
- **SpotBugs/FindSecBugs** — covers compiled Groovy bytecode.

### Shell / Bash
- **ShellCheck** — https://github.com/koalaman/shellcheck. GPL-3.0. Primarily a linter, but catches security-relevant issues (command injection from unquoted variables, race conditions, unsafe `eval`, world-writable paths). CheckStyle, JSON, GCC, SARIF (via converters).
- **shellharden** — paranoid quoting fixer.

### Terraform / Infrastructure as Code
- **Checkov (Bridgecrew/Palo Alto)** — https://github.com/bridgecrewio/checkov. Apache-2.0. 1,000+ Terraform-specific policies, including ~800 graph-based cross-resource checks. Also scans CloudFormation, Kubernetes, Helm, Serverless, ARM, Ansible, OpenAPI, Dockerfile, secrets. Python; SARIF, JSON, JUnit, CSV, GitHub PR output. Highly active.
- **KICS (Checkmarx)** — https://github.com/Checkmarx/kics. Apache-2.0. 2,400+ Rego queries across 22+ IaC platforms (Terraform, CloudFormation, Ansible, Kubernetes, Docker, Helm, OpenAPI, ARM, Serverless, Crossplane, Knative). Active.
- **Trivy (Aqua)** — https://github.com/aquasecurity/trivy. Apache-2.0. Absorbed tfsec in 2023; ~1,500 IaC misconfiguration rules carried over. Also handles container images, language SCA, secrets. Per ARMO's March 2026 analysis, it has "32,000+ GitHub stars and over 100 million Docker Hub pulls." SARIF, JSON, CycloneDX, SPDX, GitHub PR output. Active.
- **tflint (with security plugins)** — https://github.com/terraform-linters/tflint. MPL-2.0. Primarily a linter, but with `tflint-ruleset-aws` and similar provides security-relevant checks (deprecated instance types, missing encryption flags). Active.
- **Terrascan** — archived by Tenable on November 20, 2025, per the tenable/terrascan GitHub banner: "This repository was archived by the owner on Nov 20, 2025. It is now read-only." Do not adopt for new pipelines; migrate to Checkov/KICS/Trivy.

### Kubernetes manifests / Helm charts
- **Kubescape (CNCF, ARMO)** — https://github.com/kubescape/kubescape. Apache-2.0. Rego/OPA-based scanning of YAML manifests, Helm charts, Kustomize, and live clusters against NSA-CISA, MITRE ATT&CK, CIS, SOC 2, FedRAMP frameworks. SARIF, JUnit, JSON, HTML, PDF outputs. Image scanning via Grype. Very active CNCF incubating project.
- **kube-linter (StackRox / Red Hat)** — https://github.com/stackrox/kube-linter. Apache-2.0. Checks manifests/Helm for security and reliability anti-patterns (running as root, host networking, missing resource limits). CLI; SARIF output.
- **Datree** — https://github.com/datreeio/datree. Apache-2.0. Policy-driven manifest scanning; integrates schema validation and security policies. (Note: Datree was acquired by Mend; verify governance.)
- **Polaris (Fairwinds)** — https://github.com/FairwindsOps/polaris. Apache-2.0. Validates security and best practices in clusters and manifests; admission controller mode available.
- **kubeaudit** — https://github.com/Shopify/kubeaudit. MIT. CLI auditor for manifests/live clusters covering common Kubernetes security controls.

### Dockerfile / container images
- **Hadolint** — https://github.com/hadolint/hadolint. GPL-3.0. AST-based Dockerfile linter that wraps ShellCheck for embedded RUN scripts; rules cover security (untrusted registries, unpinned `latest` tags, running as root, sensitive env vars, missing `--no-install-recommends`). SARIF, JSON, Checkstyle, GitLab Code Climate, SonarQube outputs. Active.
- **Trivy** — for image OS+language vulnerability scanning (mentioned above).
- **Grype (Anchore)** — https://github.com/anchore/grype. Apache-2.0. Image vulnerability scanner; pairs with Syft for SBOM. Image SAST companion to Hadolint.
- **Docker Scout / Dockle** — Dockle (https://github.com/goodwithtech/dockle, Apache-2.0) provides CIS Docker Benchmark + best-practice checks on built images.

### CloudFormation / ARM / Bicep templates
- **cfn-nag** — https://github.com/stelligent/cfn-nag. MIT. Rule-based scanner for insecure CloudFormation templates (open security groups, IAM wildcards, unencrypted storage). Ruby. Active.
- **Checkov, KICS, Trivy** — all cover CloudFormation and ARM (and Bicep via conversion).
- **CloudFormation Guard (AWS)** — https://github.com/aws-cloudformation/cloudformation-guard. Apache-2.0. Policy-as-code DSL.

### Solidity / smart contracts
- **Slither (Trail of Bits / crytic)** — https://github.com/crytic/slither. AGPL-3.0. Solidity + Vyper static analysis framework with ~80 detectors (reentrancy, uninitialized storage, suicidal contracts, arbitrary send, incorrect ERC implementations). Python; Foundry/Hardhat/Truffle/Brownie support; SARIF + JSON; GitHub Action.
- **Aderyn (Cyfrin)** — https://github.com/Cyfrin/aderyn. MIT. Rust-based Solidity static analyzer focused on auditor-grade detectors with low false-positive rates; Markdown + JSON output; VS Code extension. Very active.
- **Mythril (ConsenSys)** — https://github.com/Consensys/mythril. MIT. Symbolic execution + SMT + taint analysis on EVM bytecode (incl. deployed contracts). Slower than Slither but catches deeper logic flaws.
- **Solhint** — https://github.com/protofire/solhint. MIT. Linter with security rules (avoid-tx-origin, reentrancy, no-inline-assembly, etc.). Active.

### COBOL (legacy)
- Limited OSS coverage. **GnuCOBOL** ships a compiler; static analysis is dominated by commercial tools (Micro Focus, SonarQube COBOL plugin — commercial). For an OSS pipeline, treat COBOL via grep-based pattern matching (graudit-style) and the **SonarQube Community Edition with the open-source COBOL plugin** (community-maintained, not first-party) as a best-effort gate. Be transparent that COBOL SAST coverage is the weakest tier in any OSS mono-sast.

### Apex (Salesforce)
- **PMD with Apex/Visualforce rulesets** — see polyglot section; the open-source rule set covers CRUD/FLS bypass, SOQL/SOSL injection, sharing rules, SharingNotPermitted, and Visualforce XSS. Bundled inside **Salesforce Code Analyzer (sf scanner)**.
- **Salesforce Code Analyzer (sf scanner)** — Salesforce's free, MIT-licensed wrapper over PMD, ESLint, RetireJS, plus the `pmd-appexchange` ruleset prepared for the AppExchange Security Review.

### Lua
- **luacheck** — https://github.com/mpeterv/luacheck. MIT. Primarily a linter; security coverage is limited. For Lua security, rely on **Semgrep/Opengrep** rules and grep-based tools.
- **GLuaLint** for game scripting environments.

### R
- **lintr** (https://github.com/r-lib/lintr) — primarily a linter; no dedicated security rules. R is not a strong SAST target; if R code interacts with shell/DB, audit via Semgrep/Opengrep rules for command injection and SQL string concatenation.

### Perl
- **Perl::Critic** with security policies — https://metacpan.org/dist/Perl-Critic. Some security-relevant policies (`InputOutput::ProhibitBacktickOperators`, `BuiltinFunctions::ProhibitStringyEval`, `Subroutines::ProhibitSubroutinePrototypes`). Active on CPAN.
- **graudit** Perl signature set as a complement.
- **DevSkim** — Perl coverage via regex rules.

### Other ecosystems
- **Erlang / Elixir:** **Sobelow** — https://github.com/nccgroup/sobelow. Apache-2.0. Security-focused static analyzer for Phoenix/Elixir applications covering XSS, SQLi, command injection, weak crypto, config issues. Active.
- **Dart / Flutter:** Built-in `dart analyze`; for security patterns use Opengrep/Semgrep Dart rules and **Snyk OSS** for SCA.
- **Solidity-Vyper hybrid:** Slither covers Vyper.
- **GitHub Actions / CI workflows:** **CodeQL `actions` (beta)**, **Poutine** (https://github.com/boostsecurityio/poutine, Apache-2.0) — actively maintained scanner for malicious/risky GitHub Actions and GitLab CI workflows.

---

## Secrets Detection (cross-cutting, often shipped alongside SAST)

- **Gitleaks** *(baseline)* — fast Git history scanner, MIT.
- **TruffleHog (trufflesecurity/trufflehog)** — https://github.com/trufflesecurity/trufflehog. AGPL-3.0. Per Truffle Security's official detectors page (trufflesecurity.com/detectors): "TruffleHog supports more than 800 secrets detectors, directly verified with key providers for unmatched scan accuracy." For 20+ common credential types it adds "deep analysis that maps permissions and access scope" (per Truffle Security's product page). Scans Git, GitHub/GitLab orgs (including issues, PRs, gists, wiki), filesystem, Docker images, S3, GCS, Slack, Postman, Jenkins, Elasticsearch, CircleCI, Travis CI. Latest release v3.95.3 around May 2026. Recommended alongside Gitleaks for verified-secret coverage.
- **detect-secrets (Yelp)** — https://github.com/Yelp/detect-secrets. Apache-2.0. Baseline-file-driven scanner designed to suppress pre-existing findings and gate only *new* secrets. Detectors for AWS, Azure, GitHub, GitLab, Stripe, Slack, SendGrid, Twilio, OpenAI, JWT, Discord, Telegram, Artifactory, Mailchimp, IBM Cloud, plus high-entropy base64/hex and (optional) ML-based gibberish-detection. **Latest release v1.5.0 on 2024-05-06** — slowing cadence; still works well in pre-commit and CI.
- **ggshield (GitGuardian)** — https://github.com/GitGuardian/ggshield. MIT. CLI for GitGuardian's secrets-detection API; free tier available; covers 400+ secret types.

---

## Section 3: Summary Table

| Tool | Languages / Targets | Approach | License | CI/CD Ready | Output Formats |
|---|---|---|---|---|---|
| Opengrep | 30+ (polyglot) | Pattern + taint (interproc.) | LGPL-2.1 | Yes (CLI, GH Action, Docker) | SARIF, JSON, text |
| Semgrep CE | 30+ (polyglot) | Pattern + intra-file taint | LGPL-2.1 | Yes | SARIF, JSON |
| CodeQL CLI | C/C++, C#, Go, Java, Kotlin, JS/TS, Python, Ruby, Swift | QL semantic queries, dataflow, taint, interproc. | Free for OSS (proprietary CLI; queries MIT) | Yes | SARIF |
| Joern | C/C++, Java, JS/TS, Python, Kotlin, PHP, Ruby, Go, Swift, binaries | Code Property Graph, dataflow, taint | Apache-2.0 | Yes (CLI, Docker) | JSON, Neo4j, SARIF (wrapper) |
| PMD | Java, Apex, Visualforce, Kotlin, Swift, JS, PL/SQL, others | AST + XPath rules | Apache-2.0/BSD | Yes | SARIF, XML, HTML, CSV |
| DevSkim | C/C++, C#, PHP, ASP, Python, Ruby, Java, JS, Go, Rust, Perl | Regex/pattern | MIT | Yes (CLI + GH Action) | SARIF, JSON |
| Application Inspector | 25+ | Pattern (recon-oriented) | MIT | Yes | JSON, HTML, SARIF |
| Scanmycode CE | Multi (aggregator) | Orchestrates other scanners | AGPL-3.0 | Yes (Docker) | HTML, JSON |
| graudit | C/C++, PHP, ASP, C#, Java, Perl, Python, Ruby, JSP, SQL | Grep signatures | GPL-3.0 | Yes | text |
| Dlint | Python | AST (Flake8 plugin) | MIT | Yes | Flake8 |
| Pysa | Python | Pyre-based taint, interproc. | MIT | Yes | JSON |
| njsscan | Node.js | libsast + Semgrep | LGPL-3.0/MIT | Yes | JSON, SARIF |
| SpotBugs + FindSecBugs | Java bytecode (incl. Android, Kotlin/Scala/Groovy compiled) | Bytecode analysis | LGPL-2.1 / Apache-2.0 | Yes (Maven/Gradle, GH Action) | SARIF, XML, HTML |
| Error Prone | Java | Compiler plugin (AST) | Apache-2.0 | Yes (Maven/Gradle/Bazel) | Compiler diagnostics |
| Infer | Java, C, C++, ObjC, Erlang, Swift, Hack | Bi-abduction, interproc. | MIT | Yes | JSON, text |
| detekt | Kotlin | AST rules | Apache-2.0 | Yes (Gradle plugin) | SARIF, HTML, MD, XML |
| Clang SA / scan-build | C/C++/ObjC | Symbolic execution + taint | Apache-2.0 (LLVM) | Yes (scan-build) | HTML, plist |
| CodeChecker | C/C++/ObjC (+ Infer integration) | Orchestrator over Clang SA, Clang-Tidy, Cppcheck, GCC-SA, Infer | Apache-2.0 | Yes | Web UI, JSON, SARIF |
| GCC `-fanalyzer` | C/C++ | Symbolic + taint | GPL-3.0 | Yes (compile flag) | Compiler diagnostics |
| weggli | C/C++ | Semantic grep | Apache-2.0 | Yes | text, JSON |
| Security Code Scan | C#, VB.NET | Roslyn AST + dataflow | LGPL-3.0 | Yes (NuGet analyzer) | MSBuild diagnostics, SARIF |
| Puma Scan CE | C# | Roslyn AST | MPL-2.0 | Yes (VS extension + NuGet) | MSBuild diagnostics |
| gokart | Go | Source-to-sink taint | Apache-2.0 | Yes | JSON, SARIF |
| dawnscanner | Ruby (Rails/Sinatra/Padrino) | CVE + AST checks | MIT | Yes (Rake) | text, JSON, HTML |
| Progpilot | PHP | AST + dataflow taint | LGPL-3.0 | Yes | JSON, SARIF |
| cargo-audit | Rust deps | Advisory DB | Apache-2.0/MIT | Yes | JSON |
| cargo-deny | Rust deps | Advisory + license + ban | Apache-2.0/MIT | Yes | text, JSON |
| cargo-geiger | Rust | `unsafe` block counting | Apache-2.0/MIT | Yes | JSON |
| MobSF / mobsfscan | Android (Java/Kotlin), iOS (Swift/ObjC) | libsast + Semgrep rules, manifest/plist analysis | GPL-3.0 / LGPL | Yes (CLI, REST API) | JSON, SARIF, PDF |
| CodeNarc | Groovy | AST rules | Apache-2.0 | Yes | HTML, XML, JSON |
| ShellCheck | Bash/sh/ksh/dash | AST + lint rules | GPL-3.0 | Yes | JSON, CheckStyle, GCC, SARIF (converter) |
| Checkov | Terraform, CFN, K8s, Helm, ARM, Ansible, Serverless, Dockerfile, secrets | Graph-based policy | Apache-2.0 | Yes | SARIF, JSON, JUnit, CSV |
| KICS | Terraform, CFN, K8s, Helm, ARM, Ansible, Docker, OpenAPI, Crossplane | Rego over JSON IR | Apache-2.0 | Yes (Docker, GH Action) | SARIF, JSON, HTML |
| Trivy | Containers, IaC (Terraform/CFN/K8s/Helm/Dockerfile/ARM/Ansible), SCA, secrets | Hybrid | Apache-2.0 | Yes | SARIF, JSON, CycloneDX, SPDX |
| tflint | Terraform | Lint + provider plugins | MPL-2.0 | Yes | JSON, SARIF, JUnit |
| Kubescape | K8s manifests, Helm, live clusters | Rego (OPA) | Apache-2.0 (CNCF) | Yes | SARIF, JSON, JUnit, HTML, PDF |
| kube-linter | K8s manifests, Helm | AST/YAML rules | Apache-2.0 | Yes | SARIF, JSON |
| Polaris | K8s manifests + clusters | YAML rules | Apache-2.0 | Yes | JSON, score |
| kubeaudit | K8s manifests + clusters | Rule-based | MIT | Yes | JSON |
| Hadolint | Dockerfile | AST + ShellCheck | GPL-3.0 | Yes | SARIF, JSON, Checkstyle |
| Dockle | Container images | CIS Docker Benchmark | Apache-2.0 | Yes | JSON, SARIF |
| cfn-nag | CloudFormation | Rule-based | MIT | Yes | JSON, text |
| CloudFormation Guard | CFN, K8s, generic JSON/YAML | Rego-like DSL | Apache-2.0 | Yes | JSON, SARIF |
| Slither | Solidity, Vyper | AST + dataflow + taint | AGPL-3.0 | Yes (GH Action) | JSON, SARIF, text |
| Aderyn | Solidity | AST detectors (Rust) | MIT | Yes | Markdown, JSON |
| Mythril | EVM bytecode | Symbolic execution + SMT + taint | MIT | Yes | JSON, Markdown |
| Solhint | Solidity | Linter w/ security rules | MIT | Yes | JSON, text |
| Sobelow | Elixir/Phoenix | AST | Apache-2.0 | Yes | JSON |
| Poutine | GitHub Actions, GitLab CI | YAML + DSL rules | Apache-2.0 | Yes | SARIF, JSON |
| TruffleHog | All (secrets) | 800+ detectors + live verification | AGPL-3.0 | Yes (GH Action, pre-commit) | JSON |
| detect-secrets | All (secrets) | Regex + entropy + ML | Apache-2.0 | Yes (pre-commit) | JSON baseline |
| ggshield | All (secrets) | 400+ detectors via GitGuardian API | MIT | Yes | JSON, SARIF |

---

## Recommendations

**Stage 1 — Minimum viable mono-sast (week 1–2):**
- Polyglot core: **Opengrep** (or Semgrep CE if your enterprise needs the managed Pro path later) + **CodeQL CLI** for public repos.
- Secrets: **Gitleaks** + **TruffleHog** (TruffleHog adds verified-secret signal).
- IaC: **Trivy** as the single binary covering containers + IaC + SCA + secrets; add **Checkov** if Terraform depth matters.
- Containers: **Hadolint** for Dockerfiles + **Trivy image** for image layers.
- This combination covers ~80% of OWASP Top 10 with SARIF-native outputs that can be deduplicated.

**Stage 2 — Language-depth additions (week 3–6):**
- Java: **SpotBugs + FindSecBugs**, plus **PMD** Java security rules.
- Python: **Bandit** + **Pysa** (for any service handling untrusted input).
- Go: **gosec** + **gokart**.
- Rust: **cargo-audit** + **cargo-deny** in CI.
- JS/TS/Node: **njsscan** + ESLint security plugins.
- Ruby/Rails: **Brakeman** (+ dawnscanner if Sinatra/Padrino is in scope).
- C#/.NET: **Security Code Scan**.
- Kotlin: **detekt** for code quality + Opengrep Kotlin rules for security (do not rely on detekt alone for security).
- Mobile: **MobSF/mobsfscan** for Android + iOS.
- Solidity (if applicable): **Slither + Aderyn + Mythril**.

**Stage 3 — Deep-analysis tier (when speed budget allows):**
- **Joern** for nightly batch deep-dataflow runs on security-critical services.
- **CodeChecker** orchestrating Clang SA + Infer + GCC `-fanalyzer` for C/C++ services.
- **Pysa** with custom taint models for Python services exposing untrusted-input surfaces.

**Decision thresholds — when to add or replace a tool:**
- *Add a language-specific tool* when polyglot tools (Opengrep + CodeQL) miss >20% of curated benchmark vulnerabilities for that language on your codebase.
- *Replace Semgrep CE with Opengrep* if your team writes custom taint rules and requires cross-function taint analysis without paying Semgrep Pro.
- *Drop a tool* when its findings achieve <5% true-positive triage rate over a quarter and a better-tuned alternative exists.
- *Stop relying on a tool* if no commit has landed in 12 months AND no maintainer responds to a security issue within 90 days — this is the bar for moving Insider, dawnscanner, and any other "slowing" tool to legacy status.

**Aggregation layer:** Normalize everything to SARIF; persist findings in DefectDojo, Sonatype Lifecycle, or a homemade SARIF-aggregating store. Use Scanmycode CE as a reference implementation if you want a turnkey orchestrator before building your own.

---

## Caveats

- **Semgrep relicensing (Jan 2025) is still settling.** The Semgrep CE engine is LGPL-2.1, but cross-file taint and several advanced features now require Semgrep Pro. Opengrep restores some of these but is a young project (first release Feb 2025); evaluate stability before adopting in business-critical pipelines.
- **CodeQL is not OSI-open.** The CLI is free for OSS analysis but proprietary; the QL queries and standard libraries are MIT. Confirm with legal whether CodeQL fits your "fully open-source" criterion. If not, Joern is the closest free alternative.
- **detekt is NOT a security tool out-of-the-box.** Multiple sources describe it as a "code smell" analyzer; security rules require custom configuration or pairing with mobsfscan/Opengrep. Do not assume detekt covers OWASP Mobile Top 10 for Android.
- **Insider, Terrascan, FindBugs, and tfsec are no longer viable choices.** Insider has had no meaningful release since 2021 and no activity since early 2023; Terrascan was archived by Tenable on November 20, 2025; FindBugs has been superseded by SpotBugs since 2017; tfsec was merged into Trivy in 2023 — use `trivy config`.
- **dawnscanner and detect-secrets are "stable but slowing"** (last releases April 2024 and May 2024 respectively). They still work, but plan for replacement if community activity does not resume by late 2026.
- **OSS Benchmark scores are vendor-published**: claims like "100% true positive rate" come from individual vendors (e.g., Xygeni's marketing on the OWASP Benchmark). Run your own benchmark on your codebase before believing such claims.
- **Infer's release cadence has diverged from its commit cadence**: master branch shows active Meta development through September 2025, but the last tagged release (v1.2.0) is from mid-2024. Use the main branch with caution or pin to a known-good commit.
- **COBOL, R, Lua, and Perl SAST coverage in OSS is thin.** Plan to supplement with manual review, grep-based dictionaries (graudit), Semgrep/Opengrep custom rules, or commercial tools for these ecosystems.
- **Smart contract analysis tools have a higher false-positive rate** than general SAST (Mythril is notable for this); pair Slither (fast, low FP) with Aderyn and Mythril for layered coverage rather than relying on any single one.