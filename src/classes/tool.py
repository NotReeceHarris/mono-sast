"""Abstract base class shared by every SAST tool wrapper."""

from abc import ABC, abstractmethod


class Tool(ABC):
    """Base class for all SAST tool wrappers.

    Subclasses declare which languages they support via :attr:`languages` and
    implement :meth:`run` to invoke the underlying scanner.  :meth:`setup` is
    available as an optional hook for one-time initialisation.
    """

    name: str = "unnamed_tool"
    description: str = "no description provided"
    link: str = "no link provided"
    languages: list = []

    config: dict = {}
    results: list = []

    def __init__(self, config: dict = None):
        self.config = config if config else {}
        self.setup()

    def setup(self):
        """Perform any one-time setup required before the tool can run.

        Override in subclasses to validate configuration or take other
        preparatory action.  The default implementation is a no-op.
        """
        pass

    def supported(self, codebase_languages: list) -> bool:
        """Return True if this tool supports at least one language in *codebase_languages*."""
        return any(lang in self.languages for lang in codebase_languages)

    @abstractmethod
    def run(self) -> bool:
        """Execute the scan and populate :attr:`results`.

        Return True if the scan completed and produced usable output,
        False otherwise.
        """
        pass
