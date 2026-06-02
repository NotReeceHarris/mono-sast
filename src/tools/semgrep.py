"""Semgrep SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/semgrep_results.json"


class Semgrep(Tool):
    """Wrap the Semgrep static analysis scanner.

    Invokes ``semgrep scan`` with ``--config auto`` (downloads the community
    rule set) against the target directory and writes SARIF output to a
    temporary file before loading the results into :attr:`results`.
    """

    name = "Semgrep"
    description = "Lightweight static analysis for many languages. Find bug variants with patterns that look like source code. "
    link = "https://github.com/semgrep/semgrep"
    languages = [
        "c", "go", "java", "javascript", "typescript", "kotlin", "python", "c++", "jsx", "ruby",
        "scala", "swift", "rust", "php", "terraform", "generic", "json", "elixir", "apex", "dart"
    ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run Semgrep and collect SARIF results.

        ``cwd`` is set to the target directory so that Semgrep picks up any
        ``.semgrepignore`` file that may be present there.
        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "semgrep", "scan",
                "--sarif",
                "--config", "auto",
                "-o", TMP_OUTPUT_FILE,
                TARGET_DIR
            ],
            cwd=TARGET_DIR,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        logging.info(f"{self.name} scan completed in {time.perf_counter() - start_time:.2f} seconds.")

        if os.path.isfile(TMP_OUTPUT_FILE):
            with open(TMP_OUTPUT_FILE, "r") as f:
                self.results.append(json.load(f))
                return True

        logging.error(f"{self.name} scan did not produce output file.")
        return False
