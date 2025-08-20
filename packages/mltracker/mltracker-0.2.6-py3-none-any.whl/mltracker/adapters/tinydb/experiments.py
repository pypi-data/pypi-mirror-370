from uuid import uuid4, UUID
from typing import override
from typing import Optional 
from tinydb import TinyDB, where
 
from mltracker.ports.experiments import Experiment
from mltracker.ports.experiments import Experiments as Repository  


from uuid import UUID, uuid4
from attrs import define, field
from typing import Optional
from mltracker.exceptions import Conflict
from mltracker.adapters.tinydb.models import Models


@define
class Experiment:
    id: UUID
    name: str
    models: Models

    def __eq__(self, __value: object):
        if not isinstance(__value, self.__class__):
            return False
        return self.id == __value.id
        
    def __hash__(self):
        return hash(self.id)

class Experiments:
    def __init__(self, database: TinyDB):
        self.database = database
        self.table = self.database.table('experiments')    
    
    @override
    def create(self, name: str) -> Experiment:
        if self.table.search(where('name') == name):
            raise ValueError(f"Experiment with name {name} already exists")
        id = uuid4()
        self.table.insert({'id': str(id), 'name': name})
        return Experiment(
            id=id, 
            name=name,  
            models=Models(self.database, name)
        ) 

    @override    
    def read(self, name) -> Optional[Experiment]: 
        data = self.table.get(where('name') == name)  
        return Experiment(
            id=UUID(data['id']),
            name=data['name'],   
            models=Models(self.database, name)
        ) if data else None