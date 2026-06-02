"""Bearer SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/bearer_results.json"


class Bearer(Tool):
    """Wrap the Bearer security scanner.

    Invokes ``bearer scan`` against the target directory and writes SARIF
    output to a temporary file before loading the results into :attr:`results`.
    """

    name = "Bearer"
    description = "Code security scanning tool (SAST) to discover, filter and prioritize security and privacy risks."
    link = "https://github.com/bearer/bearer"
    languages = [ "go", "java", "javascript", "typescript", "php", "python", "ruby" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run Bearer and collect SARIF results.

        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "bearer", "scan", TARGET_DIR,
                "--format", "sarif",
                "--output", TMP_OUTPUT_FILE
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
