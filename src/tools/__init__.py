"""Tool registry — imports every scanner and exposes the ``TOOLS`` list.

``TOOLS`` is the single source of truth consumed by ``main.py``; add or
remove entries here to enable or disable a scanner globally.
"""
from .bandit import Bandit
from .bearer import Bearer
from .brakeman import Brakeman
from .codeql import CodeQL
from .cppcheck import Cppcheck
from .devskim import DevSkim
from .flawfinder import FlawFinder
from .gosec import GoSec
from .opengrep import OpenGrep
from .phpstan import PHPStan
from .semgrep import Semgrep
from .spotbugs import SpotBugs
from .trivy import Trivy

TOOLS = [
    Bandit(),
    Bearer(),
    Brakeman(),
    CodeQL(),
    Cppcheck(),
    DevSkim(),
    FlawFinder(),
    GoSec(),
    OpenGrep(),
    PHPStan(),
    Semgrep(),
    SpotBugs(),
    Trivy(),
]
