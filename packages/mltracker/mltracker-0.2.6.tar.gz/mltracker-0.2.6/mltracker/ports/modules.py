from uuid import UUID
from abc import ABC, abstractmethod
from typing import Any
from typing import Protocol
from typing import Optional


class Module(Protocol):

    @property
    def name(self) -> str:
        """
        Defines a non unique identifier for a module owned by a model.

        Returns:
            str: The name of the module.
        """

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Relevant hyperparameters used at initialization of a given module.

        Returns:
            dict[str, Any]: The arguments with which the module was initialized.
        """
        

class Modules(ABC):

    @abstractmethod
    def add(self, name: str, arguments: Optional[dict[str, Any]] = None):
        """
        Adds a module to the modules collection.

        Args:
            name (str): The name of the module
            arguments (Optional[dict[str, Any]], optional): Relevant arguments used to initialize the module. Defaults to None.
        """
        ...

    @abstractmethod
    def list(self) -> list[Module]:
        """
        A list of the modules owned by the model.

        Returns:
            list[Module]: The modules owned by the model as a list.
        """


