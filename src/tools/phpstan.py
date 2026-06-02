"""PHPStan SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)
TMP_OUTPUT_FILE = "/tmp/phpstan_results.json"


class PHPStan(Tool):
    """Wrap the PHPStan static analyser.

    PHPStan's JSON output is written to stdout, so :meth:`run` redirects it to
    the temp file.  :meth:`__parse` converts the proprietary JSON schema into
    SARIF 2.1.0 before the results are stored.
    """

    name = "PHPStan"
    description = "PHP Static Analysis Tool - discover bugs in your code without running it!"
    link = "https://github.com/phpstan/phpstan"
    languages = [ "php" ]

    def __init__(self, config=None):
        super().__init__(config)

    def __parse(self, raw_output: dict) -> dict:
        """Convert PHPStan JSON output into a SARIF 2.1.0 document."""
        rules = {}
        results = []

        for file_path, file_data in raw_output.get("files", {}).items():
            for msg in file_data.get("messages", []):
                rule_id = msg.get("identifier", "unknown")

                if rule_id not in rules:
                    rules[rule_id] = {
                        "id": rule_id,
                        "shortDescription": {"text": rule_id},
                    }

                results.append({
                    "ruleId": rule_id,
                    "message": {"text": msg["message"]},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": file_path},
                                "region": {"startLine": msg["line"]},
                            }
                        }
                    ],
                })

        return {
            "$schema": "https://www.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.name,
                            "informationUri": self.link,
                            "rules": list(rules.values()),
                        }
                    },
                    "results": results,
                }
            ],
        }

    def run(self):
        """Run PHPStan and collect SARIF results.

        Captures stdout to ``TMP_OUTPUT_FILE`` because PHPStan writes its
        ``--error-format=json`` output to stdout rather than a file.
        Return True if output was produced, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        # PHPStan writes JSON to stdout; redirect into the temp file.
        with open(TMP_OUTPUT_FILE, "w") as outputFile:
            subprocess.run(
                [
                    "phpstan", "analyse", TARGET_DIR,
                    "--error-format=json"
                ],
                check=False,
                stdout=outputFile,
                stderr=subprocess.DEVNULL,
            )

        logging.info(f"{self.name} scan completed in {time.perf_counter() - start_time:.2f} seconds.")

        if os.path.isfile(TMP_OUTPUT_FILE):
            with open(TMP_OUTPUT_FILE, "r") as f:
                raw_output = json.load(f)
                parsed_output = self.__parse(raw_output)
                self.results.append(parsed_output)
                return True

        logging.error(f"{self.name} scan did not produce output file.")
        return False
