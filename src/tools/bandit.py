"""Bandit SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/bandit_results.json"


class Bandit(Tool):
    """Wrap the Bandit Python security scanner.

    Invokes ``bandit`` recursively over the target directory and writes SARIF
    output to a temporary file before loading the results into :attr:`results`.
    """

    name = "Bandit"
    description = "Bandit is a tool designed to find common security issues in Python code."
    link = "https://github.com/PyCQA/bandit"
    languages = [ "python" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run Bandit and collect SARIF results.

        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "bandit",
                "-r", TARGET_DIR,
                "-f", "sarif",
                "-o", TMP_OUTPUT_FILE
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
