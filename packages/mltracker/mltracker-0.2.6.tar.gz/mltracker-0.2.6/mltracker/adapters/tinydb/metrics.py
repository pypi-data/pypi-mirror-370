from attrs import define 
from typing import Optional
from typing import Any 
from uuid import uuid4
from typing import Optional, Any, override
from tinydb import TinyDB, where
from attrs import define, asdict 

@define
class Metric:
    name: str
    value: Any
    epoch: Optional[int] = None
    phase: Optional[str] = None 

class Metrics:
    def __init__(self, database: TinyDB, experiment_name: str, model_name: str):
        self.database = database
        self.table = self.database.table(f"{experiment_name}/{model_name}/metrics")

    @override
    def add(self, name: str, value: Any, epoch: int | None = None, phase: str | None = None):
        metric = Metric(name=name, value=value, epoch=epoch, phase=phase)
        self.table.insert(asdict(metric))

    @override
    def list(self, name: Optional[str] = None) -> list[Metric]:
        if name:
            data = self.table.search(where("name") == name)
        else:
            data = self.table.all() 
        return [Metric(**item) for item in data]
