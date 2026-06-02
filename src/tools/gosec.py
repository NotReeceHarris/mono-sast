"""GoSec SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/gosec_results.json"


class GoSec(Tool):
    """Wrap the GoSec Go security checker.

    Invokes ``gosec`` against the target directory and writes SARIF output to a
    temporary file before loading the results into :attr:`results`.
    """

    name = "GoSec"
    description = "Go security checker"
    link = "https://github.com/securego/gosec"
    languages = [ "go" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run GoSec and collect SARIF results.

        ``-no-fail`` is passed so gosec always exits 0 regardless of whether
        findings are present; the orchestrator determines success by checking
        for the output file rather than the process exit code.
        Return True if output was produced, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "gosec",
                "-fmt=sarif",
                "-out=/tmp/gosec_results.json",
                "-no-fail",
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
