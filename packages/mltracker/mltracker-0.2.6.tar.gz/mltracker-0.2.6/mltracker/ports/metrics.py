from abc import ABC, abstractmethod
from typing import Protocol 
from typing import Optional
from typing import Any

class Metric(Protocol):
    
    @property
    def name(self) -> str:
        """
        A metric is categorized by it's name. 

        Returns:
            str: The name of the metric.
        """

    @property
    def value(self) -> Any:
        """
        A quantitative value representing the model's performance.

        Returns:
            Any: The value of the metric. 
        """

    @property
    def epoch(self) -> Optional[int]:
        """
        An epoch is a discrete unit of time that marks a transition between 
        successive states of a machine learning model. Each metric value is associated 
        with some stage of the model indexed by the epoch. 

        Returns:
            int: The epoch of the metric. 
        """

    @property
    def phase(self) -> Optional[str]:
        """
        The operational stage of the model when the metric was produced. The phase helps 
        interpret the metric in context of the model's lifecycle. 

        Returns:
            Optional[str]: The phase of the model in wich the metric was produced.
        """


class Metrics(ABC):
    
    @abstractmethod
    def add(self, name: str, value: Any, epoch: Optional[int] = None, phase: Optional[str] = None):
        """
        Add a metric to the model. 
        
        Args:
            name (str): The name of the metric. 
            value (Any): The value of the metric.
            epoch (int): The epoch in wich the metric was produced. 
            phase (Optional[str]): The phase in wich the metric was produced. 
        """

    @abstractmethod
    def list(self, name: Optional[str] = None) -> list[Metric]:
        """
        Get a list of metrics of a model. 

        
        Args:
            name (Optional[str]): The name of the metrics to be listed.  

        Returns:
            list[Metric]: The list of metric of the model. 
        """