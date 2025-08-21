import asyncio
import time
from typing import Callable, List, Coroutine
from dotenv import load_dotenv
import pebble
from structlog import BoundLogger
import uvloop

from zenx.listeners.base import Listener
from zenx.logger import configure_logger
from zenx.pipelines.manager import PipelineManager
from zenx.clients.database import DBClient
from zenx.clients.http import HttpClient
from zenx.spiders import Spider
from zenx.settings import settings
load_dotenv()


class Engine:
    

    def __init__(self, forever: bool) -> None:
        self.forever = forever
    

    async def _schedule_task(self, t_func: Callable[[], Coroutine], start_time: float, logger: BoundLogger) -> None:
        while True:
            logger.debug("scheduled", start_time=start_time)
            delay = start_time - time.time()
            if delay > 0:
                await asyncio.sleep(delay)

            try:
                await t_func()
            except Exception:
                logger.exception("failed", task="crawl")

            start_time += settings.TASK_INTERVAL_SECONDS


    async def _execute_spider(self, spider_name: str) -> None:
        spider_cls = Spider.get_spider(spider_name)
        logger = configure_logger(spider_cls.name)
        client = HttpClient.get_client(spider_cls.client_name)(logger=logger, settings=settings) # type: ignore[call-arg]
        
        db = DBClient.get_db(settings.DB_TYPE)(logger=logger, settings=settings)
        await db.open()

        pm = PipelineManager(
            pipeline_names=spider_cls.pipelines, 
            logger=logger, 
            db=db, 
            settings=settings
        )
        await pm.open_pipelines()

        spider = spider_cls(client=client, pm=pm, logger=logger, settings=settings)
        try:
            if self.forever:
                start_time = int(time.time() / 60) * 60 + settings.START_OFFSET_SECONDS
                stagger_seconds = settings.TASK_INTERVAL_SECONDS / settings.CONCURRENCY
                async with asyncio.TaskGroup() as tg:
                    for i in range(settings.CONCURRENCY):
                        task_start_time = start_time + (i * stagger_seconds)
                        tg.create_task(self._schedule_task(spider.crawl, task_start_time, logger))
            else:
                await spider.crawl()
        except asyncio.CancelledError: # main func (_execute_spider) raises CancelledError instead of KeyboardInterrupt on ctrl+c
            logger.debug("cancelled", task="crawl")
        finally:
            logger.info("shutdown", spider=spider_name)
            if spider.background_tasks:
                for t in spider.background_tasks:
                    # tasks that are long-running e.g someting inside loop
                    if "cancellable" in t.get_name():
                        t.cancel()
                logger.debug("waiting", background_tasks=len(spider.background_tasks), belong_to="spider")
                await asyncio.gather(*spider.background_tasks, return_exceptions=True)
            await client.close()
            await db.close()
            await pm.close_pipelines()
    

    def run_spider(self, spider: str) -> None:
        uvloop.run(self._execute_spider(spider))


    def run_spiders(self, spiders: List[str]) -> None:
        with pebble.ProcessPool() as pool:
            for spider in spiders:
                pool.schedule(self.run_spider, [spider])


    async def _execute_listener(self, listener_name: str) -> None:
        listener_cls = Listener.get_listener(listener_name)
        logger = configure_logger(listener_cls.name)
        
        db = DBClient.get_db(settings.DB_TYPE)(logger=logger, settings=settings)
        await db.open()

        pm = PipelineManager(
            pipeline_names=listener_cls.pipelines, 
            logger=logger, 
            db=db, 
            settings=settings
        )
        await pm.open_pipelines()

        listener = listener_cls(pm=pm, logger=logger, settings=settings)
        listen_task = asyncio.create_task(listener.listen())
        try:
            await listen_task
        except asyncio.CancelledError: # main func (_execute_listener) raises CancelledError instead of KeyboardInterrupt on ctrl+c
            logger.debug("cancelled", task="listen")
            listen_task.cancel()
        except Exception: # task terminated on exception inside
            logger.exception("failed", task="listen")
        finally:
            if listener.background_tasks:
                for t in listener.background_tasks:
                    # tasks that are long-running e.g someting inside loop
                    if "cancellable" in t.get_name():
                        t.cancel()
                logger.debug("waiting", background_tasks=len(listener.background_tasks), belong_to="listener")
                await asyncio.gather(*listener.background_tasks, return_exceptions=True)
            await db.close()
            await pm.close_pipelines()


    def run_listener(self, listener: str) -> None:
        uvloop.run(self._execute_listener(listener))
