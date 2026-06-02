"""Utilities for formatting and emitting scan reports."""

from utils.report import generate_html_report, generate_markdown_report
from utils.gitignore import WORKSPACE
from configs import OUTPUT_FORMATS


def _strip_workspace_prefix(uri: str) -> str:
    prefix = WORKSPACE.rstrip("/") + "/"
    if uri.startswith(prefix):
        return uri[len(prefix):]
    return uri


def _normalise_uris(runs: list) -> None:
    """Strip the workspace path prefix from every artifactLocation.uri in-place."""
    for run in runs:
        for result in run.get("results", []):
            for loc in result.get("locations", []):
                phys = loc.get("physicalLocation", {})
                art = phys.get("artifactLocation")
                if art and "uri" in art:
                    art["uri"] = _strip_workspace_prefix(art["uri"])


def merge_sarif(results: list) -> dict:
    """Merge multiple SARIF documents into a single SARIF 2.1.0 document.

    Each element of *results* is expected to be a SARIF document dict with a
    ``runs`` key.  All runs are collected into one top-level ``runs`` array so
    consumers see a single unified report.
    """
    merged_runs = []
    for sarif in results:
        runs = sarif.get("runs") if isinstance(sarif, dict) else None
        if isinstance(runs, list):
            merged_runs.extend(runs)

    _normalise_uris(merged_runs)

    return {
        "$schema": "https://www.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": merged_runs,
    }


def generate_report(digest: str, languages: list, results: list, elapsed: float = 0.0) -> dict:
    """Merge all SARIF tool outputs and return the combined SARIF document.

    Also prints a brief summary to stdout so CI logs remain informative.
    The caller is responsible for writing the returned document to disk.
    """
    merged = merge_sarif(results)

    total_findings = sum(len(run.get("results", [])) for run in merged["runs"])
    print(f"SHA256 hash of target directory: {digest}")
    print(f"Languages found in target directory: {', '.join(languages)}")
    print(f"Tools run: {len(merged['runs'])}")
    print(f"Total findings: {total_findings}")
    print(f"Elapsed time: {elapsed:.2f}s")

    if "html" in OUTPUT_FORMATS:
        merged["_html_report"] = generate_html_report(merged, digest, languages, elapsed)
    if "markdown" in OUTPUT_FORMATS:
        merged["_markdown_report"] = generate_markdown_report(merged, digest, languages, elapsed)
    return merged
