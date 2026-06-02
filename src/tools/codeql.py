"""CodeQL SAST tool wrapper."""

from configs import TARGET_DIR
from classes.tool import Tool
import os, json, logging, subprocess, time

logger = logging.getLogger(__name__)

# Per-language path templates; the language identifier is interpolated at runtime.
TMP_OUTPUT_FILE = "/tmp/codeql_results_{}.json"
TMP_DATABASE_FILE = "/tmp/codeql_database_{}"

# Maps the lowercase language names produced by scc to CodeQL's own identifiers.
# C and C++ share a single CodeQL language pack ("c-cpp"), so both map to the
# same value; the set comprehension in ``supported`` deduplicates them.
SUPPORTED_LANGUAGE_MAP = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "c#": "csharp",
    "go": "go",
    "ruby": "ruby",
    "c": "c-cpp",
    "c++": "c-cpp",
    "rust": "rust",
    "swift": "swift",
}


class CodeQL(Tool):
    """Wrap the GitHub CodeQL scanner.

    CodeQL requires a compiled database per language before it can analyse
    code.  :meth:`supported` builds the deduplicated list of CodeQL language
    identifiers as a side-effect so that :meth:`run` knows which databases to
    create and analyse.
    """

    name = "CodeQL"
    description = "CodeQL: the libraries and queries that power security researchers around the world, as well as code scanning in GitHub Advanced Security "
    link = "https://github.com/github/codeql"
    languages = [ "python", "javascript", "typescript", "java", "c#", "go", "ruby", "c", "c++", "rust", "swift" ]

    __codebase_languages: list

    def __init__(self, config=None):
        super().__init__(config)

    def supported(self, codebase_languages: list) -> bool:
        """Return True if any codebase language is supported, and cache the CodeQL identifiers.

        As a side-effect, translates and deduplicates the detected languages
        into CodeQL identifiers stored in ``__codebase_languages`` so that
        :meth:`run` can iterate over them without repeating the translation.
        """
        self.__codebase_languages = list({
            SUPPORTED_LANGUAGE_MAP[lang]
            for lang in codebase_languages
            if lang in SUPPORTED_LANGUAGE_MAP
        })

        return any(lang in self.languages for lang in codebase_languages)

    def run(self):
        """Run CodeQL database creation and analysis for each detected language.

        Creates a separate CodeQL database per language, runs the default query
        suite against it, and writes SARIF output to a per-language temp file.
        Return True if at least one language produced output, False otherwise.
        """
        logging.info(f"Running {self.name}...")
        global_start_time = time.perf_counter()

        results_collected = False

        for lang in self.__codebase_languages:
            logging.info(f"Running {self.name} for {lang}...")
            start_time = time.perf_counter()

            subprocess.run(
                [
                    "codeql", "database",
                    "create", TMP_DATABASE_FILE.format(lang),
                    f"--language={lang}",
                    "--source-root", TARGET_DIR
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            subprocess.run(
                [
                    "codeql", "database",
                    "analyze", TMP_DATABASE_FILE.format(lang),
                    "--format=sarif-latest",
                    f"--output={TMP_OUTPUT_FILE.format(lang)}"
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            logging.info(f"{self.name} scan for {lang} completed in {time.perf_counter() - start_time:.2f} seconds.")
            if os.path.isfile(TMP_OUTPUT_FILE.format(lang)):
                with open(TMP_OUTPUT_FILE.format(lang), "r") as f:
                    self.results.append(json.load(f))
                    results_collected = True
            else:
                logging.error(f"{self.name} scan for {lang} did not produce output file.")

        logging.info(f"{self.name} total scan completed in {time.perf_counter() - global_start_time:.2f} seconds.")
        return results_collected
