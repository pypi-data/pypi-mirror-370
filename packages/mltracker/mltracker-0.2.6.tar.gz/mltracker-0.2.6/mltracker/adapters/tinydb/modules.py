from typing import Any, Optional, override
from tinydb import TinyDB, where
from attrs import define, asdict 

@define
class Module:
    name: str
    arguments: dict[str, Any]


class Modules:
    def __init__(self, database: TinyDB, experiment_name: str, model_name: str):
        self.database = database
        self.table = self.database.table(f"{experiment_name}/{model_name}/modules")

    @override
    def add(self, name: str, arguments: Optional[dict[str, Any]] = None):
        arguments = arguments or {}
        module = Module(name=name, arguments=arguments)
        self.table.insert(asdict(module))

    @override
    def list(self) -> list[Module]:
        data = self.table.all()
        return [Module(**item) for item in data]
