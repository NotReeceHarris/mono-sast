"""FlawFinder SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/flawfinder_results.json"


class FlawFinder(Tool):
    """Wrap the FlawFinder C/C++ vulnerability scanner.

    FlawFinder does not support a ``--output`` flag; SARIF is written to
    stdout, so :meth:`run` redirects it to the temp file directly.
    """

    name = "FlawFinder"
    description = "a static analysis tool for finding vulnerabilities in C/C++ source code "
    link = "https://github.com/david-a-wheeler/flawfinder"
    languages = [ "c", "c++" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run FlawFinder and collect SARIF results.

        Captures stdout to ``TMP_OUTPUT_FILE`` because FlawFinder lacks a
        dedicated output-file flag.  Return True if output was produced,
        False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        # FlawFinder emits SARIF to stdout; redirect into the temp file.
        with open(TMP_OUTPUT_FILE, "w") as outputFile:
            subprocess.run(
                [
                    "flawfinder",
                    "--sarif", TARGET_DIR
                ],
                check=False,
                stdout=outputFile,
                stderr=subprocess.DEVNULL,
            )

        logging.info(f"{self.name} scan completed in {time.perf_counter() - start_time:.2f} seconds.")

        if os.path.isfile(TMP_OUTPUT_FILE):
            with open(TMP_OUTPUT_FILE, "r") as f:
                self.results.append(json.load(f))
                return True

        logging.error(f"{self.name} scan did not produce output file.")
        return False
