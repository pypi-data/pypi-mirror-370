from uuid import UUID
from abc import ABC, abstractmethod
from typing import Any
from typing import Protocol
from typing import Optional

from mltracker.ports.metrics import Metrics
from mltracker.ports.modules import Modules

class Model(Protocol):

    @property
    def id(self) -> Any:
        """A globally unique identifier for the models that can be used for 
        referencing the model outside the experiment namespace. 

        Returns:
            Any: The id of the model.
        """

    @property
    def name(self) -> str:
        """A human redable non unique identifier for a model type. 

        Returns:
            str: The name of the model.
        """

    @property
    def hash(self) -> str:
        """A hash is a fixed length value that uniquely represents information. It acts
        as a locally unique identifier for a model under an experiment namespace. 

        Returns:
            str: The hash of the model.
        """

    @property
    def epoch(self) -> str:
        """An epoch is a discrete unit of time that marks a transition between 
        successive states of the model. 

        Returns:
            str: The epoch of the model.
        """

    @property
    def metrics(self) -> Metrics:
        """Each model owns a collection of metrics. 

        Returns:
            Metrics: The collection of metrics of the model.
        """

    @property
    def modules(self) -> Modules:
        """
        A model is an aggregate of modules.

        Returns:
            Modules: The modules of the model.
        """

class Models(ABC):
    
    @abstractmethod
    def create(self, hash: str, name: Optional[str] = None) -> Model:
        """
        Creates a record of a model in the database, retrieving
        an instance of the entity representing it. 

        Args:
            hash (Any): A locally unique identifier for the model. 
            name (Optional[str]): The name of the model.

        Returns:
            Model: The entity representing a model. 
        """

    @abstractmethod
    def read(self, hash: str) -> Optional[Model]:
        """
        Retrieves a model for a given hash if any. 

        Args:
            hash (str): The hash of the model. 

        Returns:
            Optional[Model]: The model found if any. 
        """

    @abstractmethod
    def update(self, hash: str, name: str):
        """
        Update the name of a model for a given hash. 

        Args:
            hash (str): The hash of the model.
            name (str): The new name of the model.
        """