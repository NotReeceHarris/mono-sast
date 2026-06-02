"""DevSkim SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/devskim_results.json"


class DevSkim(Tool):
    """Wrap the Microsoft DevSkim security linter.

    Invokes ``devskim analyze`` against the target directory and writes SARIF
    output to a temporary file before loading the results into :attr:`results`.
    """

    name = "DevSkim"
    description = "DevSkim is a set of IDE plugins, language analyzers, and rules that provide security \"linting\" capabilities. "
    link = "https://github.com/microsoft/DevSkim"
    languages = [ "c", "c++", "objective c", "c#", "cobol", "go", "java", "javascript", "typescript", "php", "powershell", "python", "ruby", "rust", "sql", "swift", "basic", "visual basic", "c header" ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run DevSkim and collect SARIF results.

        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "devskim", "analyze",
                "--source-code", TARGET_DIR,
                "--file-format", "sarif",
                "--output-file", TMP_OUTPUT_FILE
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
