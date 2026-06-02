"""Entry point for the mono-sast orchestrator.

Detects languages in the target directory, runs every applicable SAST tool,
and emits a consolidated report.
"""

import subprocess
import json
import logging
import os
import time

# Workspace prep must happen before tool modules are imported, because every
# tool binds TARGET_DIR as a local name at import time via
#   from configs import TARGET_DIR
# Patching configs.TARGET_DIR after the fact would have no effect on those
# already-bound names.  Setting the env var here means configs.__init__ reads
# the updated value when the tools package is imported below.
from utils.gitignore import prepare_workspace

_ORIGINAL_TARGET_DIR = os.environ.get("TARGET_DIR", "/target")

def _configure_logging():
    """Configure the root logger with a timestamped INFO-level format."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

_configure_logging()
_workspace = prepare_workspace(_ORIGINAL_TARGET_DIR)
os.environ["TARGET_DIR"] = _workspace

# Now import tools — they will bind TARGET_DIR to the clean workspace path.
from utils.output import generate_report
from itertools import chain
from configs import TARGET_DIR, OUTPUT_FORMATS, OUTPUT_DIR
from tools import TOOLS

logger = logging.getLogger(__name__)


def _hash_target_directory() -> str:
    """Return a stable SHA-256 digest that represents the original source tree.

    Hashes every file's content (sorted by path) and then hashes the
    concatenation of those hashes, producing a single fingerprint that changes
    whenever any file is added, removed, or modified.

    Uses the original target directory so the digest reflects exactly what was
    submitted, not the filtered workspace copy.
    """
    cmd = (
        f"find {_ORIGINAL_TARGET_DIR} -type f -print0 "
        f"| sort -z "
        f"| xargs -0 sha256sum "
        f"| sha256sum"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    return result.stdout.split()[0]


def _run_scc():
    """Run scc against the workspace and return a sorted list of detected language names.

    Language names are normalised to lowercase so they match the ``languages``
    attribute on each :class:`~classes.tool.Tool` subclass.  Raises if scc
    produces no output or finds no languages.
    """
    logger.info("Running scc to get language breakdown...")
    subprocess.run(["scc", TARGET_DIR, "--output", "/tmp/scc_output.json", "--format", "json"], check=True)

    if not os.path.isfile("/tmp/scc_output.json"):
        raise Exception("scc did not produce output file")

    with open("/tmp/scc_output.json", "r") as f:
        results = json.loads(f.read().lower())
        languages = [entry["name"] for entry in results if entry["count"] > 0]
        if not languages:
            raise Exception("scc did not find any languages in the target directory")

        # Sorted so that tool support checks and report output are deterministic.
        return sorted(languages)


def main():
    """Orchestrate language detection, tool execution, and report generation."""

    digest = _hash_target_directory()
    languages = _run_scc()

    # Only run tools that declare support for at least one detected language.
    start_time = time.perf_counter()
    results = list(chain.from_iterable(
        tool.results for tool in TOOLS if tool.supported(languages) and tool.run()
    ))
    elapsed = time.perf_counter() - start_time
    logger.info(f"All tools completed in {elapsed:.2f} seconds.")

    merged_sarif = generate_report(digest, languages, results, elapsed)

    html_report     = merged_sarif.pop("_html_report", None)
    markdown_report = merged_sarif.pop("_markdown_report", None)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if "sarif" in OUTPUT_FORMATS:
        dest = os.path.join(OUTPUT_DIR, "results.json")
        with open("/tmp/results.json", "w") as f:
            json.dump(merged_sarif, f)
        subprocess.run(["cp", "/tmp/results.json", dest], check=True)
        logger.info(f"SARIF report written to {dest}")

    if html_report:
        dest = os.path.join(OUTPUT_DIR, "report.html")
        with open("/tmp/report.html", "w") as f:
            f.write(html_report)
        subprocess.run(["cp", "/tmp/report.html", dest], check=True)
        logger.info(f"HTML report written to {dest}")

    if markdown_report:
        dest = os.path.join(OUTPUT_DIR, "report.md")
        with open("/tmp/report.md", "w") as f:
            f.write(markdown_report)
        subprocess.run(["cp", "/tmp/report.md", dest], check=True)
        logger.info(f"Markdown report written to {dest}")

if __name__ == "__main__":

    # Validate prerequisites before handing off to main().
    if not os.path.isdir(_ORIGINAL_TARGET_DIR):
        logger.error(f"Error: Target directory '{_ORIGINAL_TARGET_DIR}' does not exist.")
        exit(1)

    if not any(os.listdir(_ORIGINAL_TARGET_DIR)):
        logger.error(f"Error: Target directory '{_ORIGINAL_TARGET_DIR}' is empty.")
        exit(1)

    # Tools write interim results to /tmp; abort early if it is not writable.
    tmp_check = subprocess.run(["test", "-w", "/tmp"], check=False)
    if tmp_check.returncode != 0:
        logger.error("Error: /tmp directory is not writable.")
        exit(1)

    main()
