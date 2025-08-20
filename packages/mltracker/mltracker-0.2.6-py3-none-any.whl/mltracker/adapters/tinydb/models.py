from uuid import UUID, uuid4
from typing import Optional, override
from tinydb import TinyDB, where
from tinydb.table import Table
from attrs import define, field

from mltracker.exceptions import Conflict
from mltracker.ports.models import Model, Models as Repository 
from mltracker.adapters.tinydb.metrics import Metrics
from mltracker.adapters.tinydb.modules import Modules


@define
class Model:
    id: UUID
    name: str
    hash: str 
    metrics: Metrics
    modules: Modules 
    
    def __eq__(self, __value: object):
        if not isinstance(__value, self.__class__):
            return False
        return self.id == __value.id
        
    def __hash__(self):
        return hash(self.id) 


    table: Table


    @property
    def epoch(self) -> int:
        data = self.table.get(where('hash') == self.hash)
        return data.get("epoch", 0) if data else 0

    @epoch.setter
    def epoch(self, value: int):
        self.table.update({"epoch": value}, where("hash") == self.hash)
 

class Models(Repository):
    def __init__(self, database: TinyDB, experiment_name: str):
        self.database = database
        self.experiment_name = experiment_name
        self.table = self.database.table(f'{experiment_name}/models')

    @override
    def create(self, hash: str, name: Optional[str] = None) -> Model:
        if self.table.search(where('hash') == hash):
            raise Conflict(f"Model with hash '{hash}' already exists")

        id = uuid4()
        self.table.insert({
            'id': str(id),
            'name': name,
            'hash': hash,  
        })
        return Model(
            id=id,
            name=name,
            hash=hash, 
            metrics=Metrics(self.database, self.experiment_name, name),
            modules=Modules(self.database, self.experiment_name, name),   
            table=self.table
        )

    @override
    def read(self, hash: str) -> Optional[Model]:
        data = self.table.get(where('hash') == hash)
        if not data:
            return None
        return Model(
            id=UUID(data['id']),
            name=data['name'],
            hash=data['hash'], 
            metrics=Metrics(self.database, self.experiment_name, data['name']),
            modules=Modules(self.database, self.experiment_name, data['name']),
            table=self.table
        )

    @override
    def update(self, hash: str, name: str) -> Optional[Model]:
        data = self.table.get(where('hash') == hash)
        if not data:
            return None

        self.table.update({'name': name}, where('hash') == hash) 
        return Model(
            id=UUID(data['id']),
            name=name,
            hash=hash, 
            metrics=Metrics(self.database, self.experiment_name, data['name']),
            modules=Modules(self.database, self.experiment_name, data['name']),
            table=self.table
        )

    @override
    def delete(self, hash: str):
        self.table.remove(where('hash') == hash) 

    @override
    def list(self) -> list[Model]: 
        models = []
        for data in self.table.all():
            models.append(Model(
                id=UUID(data['id']),
                name=data['name'],
                hash=data['hash'],
                metrics=Metrics(self.database, self.experiment_name, data['name']),
                modules=Modules(self.database, self.experiment_name, data['name']),
                table=self.table
            ))
        return models