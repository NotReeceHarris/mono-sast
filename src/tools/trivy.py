"""Trivy SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/trivy_results.json"


class Trivy(Tool):
    """Wrap the Aquasecurity Trivy vulnerability scanner.

    Invokes ``trivy filesystem`` against the target directory and writes SARIF
    output to a temporary file before loading the results into :attr:`results`.
    """

    name = "Trivy"
    description = "Find vulnerabilities, misconfigurations, secrets, SBOM in containers, Kubernetes, code repositories, clouds and more "
    link = "https://github.com/aquasecurity/trivy"
    # Full language coverage list: https://trivy.dev/docs/latest/coverage/language/
    languages = [ "ruby", "python", "php", "javascript", "typescript", "java", "rust", "c", "c++", "elixir", "dart", "swift", "julia", "dockerfile" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run Trivy and collect SARIF results.

        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "trivy", "filesystem",
                "-f", "sarif",
                "-o", TMP_OUTPUT_FILE,
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
