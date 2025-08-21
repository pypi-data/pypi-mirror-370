from abc import ABC, abstractmethod

class BaseModule(ABC):
    """Abstract base class for all command modules."""
    def __init__(self, shell):
        self.shell = shell
        self.console = shell.console
        self.conn = shell.conn

    @property
    @abstractmethod
    def commands(self) -> list[str]:
        """A list of command names this module handles."""
        pass

    @abstractmethod
    def execute(self, args: list[str]):
        """The main execution method for the module's commands."""
        pass

    @abstractmethod
    def get_help(self) -> dict:
        """Return help text for each command in a structured dict."""
        pass