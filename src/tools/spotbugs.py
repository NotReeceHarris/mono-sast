"""SpotBugs SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time
from pathlib import Path
from utils.convert import xml_to_json

logger = logging.getLogger(__name__)

# SpotBugs writes XML natively; the result is converted to JSON before storage.
TMP_OUTPUT_FILE = "/tmp/spotbugs_results.xml"


class SpotBugs(Tool):
    """Wrap the SpotBugs Java bytecode analyser.

    SpotBugs operates on compiled artefacts (.class, .jar, .war, .ear) rather
    than source files, so :meth:`run` first walks the target directory to
    collect them.  The native XML output is converted to JSON then parsed into
    SARIF 2.1.0 by :meth:`__parse` before being stored in :attr:`results`.
    """

    name = "SpotBugs"
    description = "SpotBugs is FindBugs' successor. A tool for static analysis to look for bugs in Java code."
    link = "https://github.com/spotbugs/spotbugs"
    languages = [ "java" ]

    def __init__(self, config=None):
        super().__init__(config)

    def __parse(self, raw_output: dict) -> dict:
        """Convert SpotBugs XML/JSON output into a SARIF 2.1.0 document."""
        PRIORITY_TO_LEVEL = {"1": "error", "2": "warning", "3": "note"}

        rules = {}
        results = []

        bugs = raw_output.get("BugCollection", {}).get("BugInstance", [])
        if isinstance(bugs, dict):
            bugs = [bugs]

        for bug in bugs:
            rule_id = bug.get("@type", "unknown")
            category = bug.get("@category", "")

            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "shortDescription": {"text": f"{rule_id} ({category})"},
                }

            # SourceLine can be a list, a dict, or absent; fall back to Class.SourceLine.
            sl = bug.get("SourceLine")
            if isinstance(sl, list):
                sl = sl[0]
            if not sl:
                sl = (bug.get("Class") or {}).get("SourceLine")

            location = {}
            if sl and sl.get("@sourcepath"):
                region = {}
                if sl.get("@start"):
                    region["startLine"] = int(sl["@start"])
                if sl.get("@end") and sl["@end"] != sl.get("@start"):
                    region["endLine"] = int(sl["@end"])
                location = {
                    "physicalLocation": {
                        "artifactLocation": {"uri": sl["@sourcepath"]},
                        "region": region,
                    }
                }

            results.append({
                "ruleId": rule_id,
                "level": PRIORITY_TO_LEVEL.get(bug.get("@priority", "2"), "warning"),
                "message": {"text": f"{rule_id} ({category})"},
                "locations": [location] if location else [],
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
        """Run SpotBugs against all compiled Java artefacts in the target directory.

        Skips execution if no .class/.jar/.war/.ear files are found.
        Return True if SpotBugs produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        start_time = time.perf_counter()

        # SpotBugs requires compiled bytecode; collect every eligible artefact.
        input_files = [
            str(path) for path in Path(TARGET_DIR).rglob("*")
            if path.suffix in [".class", ".jar", ".war", ".ear"] and path.is_file()
        ]

        if input_files:
            subprocess.run(
                [
                    "spotbugs", f"-xml={TMP_OUTPUT_FILE}",
                    *input_files
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            logger.info(f"No compiled Java artifacts found under {TARGET_DIR}; skipping spotBugs.")

        logging.info(f"{self.name} scan completed in {time.perf_counter() - start_time:.2f} seconds.")

        if os.path.isfile(TMP_OUTPUT_FILE):
            with open(TMP_OUTPUT_FILE, "r") as f:
                raw_output = f.read()
                json_output = json.loads(xml_to_json(raw_output))
                parse_output = self.__parse(json_output)
                self.results.append(parse_output)
                return True

        logging.error(f"{self.name} scan did not produce output file.")
        return False
