from attrs import define 
from typing import Optional
from typing import Any 

@define
class Metric:
    name: str
    value: Any 
    epoch: Optional[int]
    phase: Optional[str]

class Metrics:
    def __init__(self):
        self.values = list[Metric]()
    
    def add(self, name: str, value: Any, epoch: int | None = None, phase: str | None = None): 
        self.values.append(Metric(name, value, epoch, phase))

    def list(self, name: Optional[str] = None) -> list[Metric]: 
        if not name:
            return self.values
        else:
            return [metric for metric in self.values if metric.name == name]