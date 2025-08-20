from attrs import define  
from typing import Any 

@define
class Module:
    name: str 
    arguments: dict[str, Any]

class Modules:
    def __init__(self):
        self.values = list[Module]()
    
    def add(self, name: str, arguments: dict[str|Any] | None = None): 
        self.values.append(Module(name, arguments))

    def list(self) -> list[Module]:  
        return self.values