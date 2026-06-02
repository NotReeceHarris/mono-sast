"""Cppcheck SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/cppcheck_results.json"


class Cppcheck(Tool):
    """Wrap the Cppcheck C/C++ static analyser.

    Invokes ``cppcheck`` against the target directory and writes SARIF output
    to a temporary file before loading the results into :attr:`results`.
    """

    name = "Cppcheck"
    description = "static analysis of C/C++ code "
    link = "https://github.com/cppcheck-opensource/cppcheck"
    languages = [ "c", "c++" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run Cppcheck and collect SARIF results.

        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "cppcheck",
                "--output-format=sarif",
                f"--output-file={TMP_OUTPUT_FILE}",
                TARGET_DIR
            ],
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
