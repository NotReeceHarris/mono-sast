"""OpenGrep SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/opengrep_results.json"


class OpenGrep(Tool):
    """Wrap the OpenGrep static analysis engine.

    Invokes ``opengrep scan`` against the target directory and writes SARIF
    output to a temporary file before loading the results into :attr:`results`.
    """

    name = "OpenGrep"
    description = "Static code analysis engine to find security issues in code. "
    link = "https://github.com/opengrep/opengrep"
    languages = [
        "apex", "bash", "c", "c++", "c#", "clojure", "dart", "dockerfile", "elixir",
        "go", "html", "java", "javascript", "typescript", "json", "jsonnet", "jsx",
        "julia", "kotlin", "lisp", "lua", "ocaml", "php", "python", "ruby", "r", "rust",
        "scala", "scheme", "solidity", "swift", "terraform", "tsx", "visual basic", "yaml",
        "generic", "c header"
    ]

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        """Run OpenGrep and collect SARIF results.

        Return True if the scan completed and produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        subprocess.run(
            [
                "opengrep", "scan",
                f"--sarif-output={TMP_OUTPUT_FILE}",
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
