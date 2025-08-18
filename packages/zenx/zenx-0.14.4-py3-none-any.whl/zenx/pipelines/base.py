from __future__ import annotations
from abc import ABC, abstractmethod
from typing import ClassVar, Dict, List, Type
from structlog import BoundLogger

from zenx.clients.database import DBClient
from zenx.exceptions import DropItem
from zenx.settings import Settings


class Pipeline(ABC):
    # central registry
    name: ClassVar[str]
    required_settings: ClassVar[List[str]]
    _registry: ClassVar[Dict[str, Type[Pipeline]]] = {}


    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"Pipeline subclass {cls.__name__} must have a 'name' attribute.")
        cls._registry[cls.name] = cls


    @classmethod
    def get_pipeline(cls, name: str) -> Type[Pipeline]:
        if name not in cls._registry:
            raise ValueError(f"Pipeline '{name}' is not registered. Available pipelines: {list(cls._registry.keys())}")
        return cls._registry[name]


    def __init__(self, logger: BoundLogger, db: DBClient, settings: Settings) -> None:
        self.logger = logger
        self.db = db
        self.settings = settings


    def drop_if_scraped_too_late(self, item: Dict) -> None:
        published_at = item.get("published_at") 
        scraped_at = item.get("scraped_at") 
        if not published_at or not scraped_at:
            return
        if (scraped_at - published_at) > (1000 * self.settings.MAX_SCRAPE_DELAY):
            # self.logger.debug("scraped_too_late", id=item.get("_id"), pipeline=self.name)
            raise DropItem
        
    
    @abstractmethod
    async def open(self) -> None:
        """ connect the pipeline """
        ...


    @abstractmethod
    async def process_item(self, item: Dict, producer: str) -> Dict:
        ...


    @abstractmethod
    async def close(self) -> None:
        ...
