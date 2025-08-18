import asyncio
import json
import random
from typing import Dict, Optional
from structlog import BoundLogger

from zenx.clients.database import DBClient
from zenx.settings import Settings
from zenx.pipelines.base import Pipeline
from zenx.utils import log_processing_time


try:
    import websockets
    from websockets import ConnectionClosed

    class SynopticWebSocketPipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_websocket"
        required_settings = ["SYNOPTIC_API_KEY", "SYNOPTIC_STREAM_ID"]
        

        def __init__(self, logger: BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._endpoint = f"wss://api.synoptic.com/v1/ws?apiKey={self.settings.SYNOPTIC_API_KEY}"
            self._connected = asyncio.Event()
            self._ws_client: Optional[websockets.ClientConnection] = None
            self._monitor_state_task: Optional[asyncio.Task] = None
            self._listening_task: Optional[asyncio.Task] = None


        async def open(self) -> None:
            for setting in self.required_settings:
                if not getattr(self.settings, setting):
                    raise ValueError(f"Missing required setting: {setting}")
            try:
                await self._connect()
            except Exception:
                self.logger.exception("pipeline_open_failed", pipeline=self.name)
                raise
            else:
                self._monitor_state_task = asyncio.create_task(self._monitor_state())
                self._listening_task = asyncio.create_task(self._listen())

        
        async def _monitor_state(self) -> None:
            while True:
                await self._ws_client.wait_closed()
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)
                

        async def _listen(self) -> None:
            try:
                await self._connected.wait()
                self.logger.debug("listening", pipeline=self.name)
                async for msg in self._ws_client:
                    self.logger.debug("response", msg=msg, pipeline=self.name)
            except Exception:
                await asyncio.sleep(1)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._ws_client = await websockets.connect(self._endpoint) 
            msg = json.loads(await self._ws_client.recv())['data']['message']
            if "Invalid secret key" in msg:
                raise Exception(msg)
            self.logger.info("connected", pipeline=self.name, msg=msg)
            self._connected.set()

            
        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            await self._process(item, producer)
            return item
        
        
        async def _process(self, item: Dict, producer: str) -> None:
            _item = {
                "event": "add-stream-post",
                "data": {
                    "id": item.get("_id"),
                    "idempotencyKey": item.get("_id"),
                    "streamId": self.settings.SYNOPTIC_STREAM_ID,
                    "content": item.get("_content"),
                    "createdAt": item.get("published_at"),
                },
            }
            await self._connected.wait()
            try:
                await self._ws_client.send(json.dumps(_item))
            except ConnectionClosed as e:
                self.logger.error("processing", exception=str(e), id=item.get("_id"), pipeline=self.name)
            

        async def close(self) -> None:
            for t in [self._monitor_state_task, self._listening_task]:
                if t and not t.done():
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        pass
            await self._ws_client.close()
            self.logger.debug("closed", pipeline=self.name)

except ModuleNotFoundError:
    # proxy pattern
    class SynopticWebSocketPipeline(Pipeline):
        name = "synoptic_websocket"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[websocket]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)
        
        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def close(self) -> None: pass


try:
    import websockets
    from websockets import ConnectionClosed

    class SynopticWebSocketPipeline2(Pipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_websocket_2"
        required_settings = ["SYNOPTIC_API_KEY_2", "SYNOPTIC_STREAM_ID_2"]
        

        def __init__(self, logger: BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._endpoint = f"wss://api.synoptic.com/v1/ws?apiKey={self.settings.SYNOPTIC_API_KEY_2}"
            self._connected = asyncio.Event()
            self._ws_client: Optional[websockets.ClientConnection] = None
            self._monitor_state_task: Optional[asyncio.Task] = None
            self._listening_task: Optional[asyncio.Task] = None


        async def open(self) -> None:
            for setting in self.required_settings:
                if not getattr(self.settings, setting):
                    raise ValueError(f"Missing required setting: {setting}")
            try:
                await self._connect()
            except Exception:
                self.logger.exception("pipeline_open_failed", pipeline=self.name)
                raise
            else:
                self._monitor_state_task = asyncio.create_task(self._monitor_state())
                self._listening_task = asyncio.create_task(self._listen())

        
        async def _monitor_state(self) -> None:
            while True:
                await self._ws_client.wait_closed()
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)
                

        async def _listen(self) -> None:
            try:
                await self._connected.wait()
                self.logger.debug("listening", pipeline=self.name)
                async for msg in self._ws_client:
                    self.logger.debug("response", msg=msg, pipeline=self.name)
            except Exception:
                await asyncio.sleep(1)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._ws_client = await websockets.connect(self._endpoint) 
            msg = json.loads(await self._ws_client.recv())['data']['message']
            if "Invalid secret key" in msg:
                raise Exception(msg)
            self.logger.info("connected", pipeline=self.name, msg=msg)
            self._connected.set()

            
        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            time_diff = (item['scraped_at'] - item['published_at']) / 1000
            sleep_time = random.uniform(0.6, 1.5) - time_diff
            if sleep_time > 0:
                self.logger.debug("sleep", time=f"{sleep_time:.2f}", pipeline=self.name)
                await asyncio.sleep(sleep_time)
            await self._process(item, producer)
            return item
        
        
        async def _process(self, item: Dict, producer: str) -> None:
            _item = {
                "event": "add-stream-post",
                "data": {
                    "id": item.get("_id"),
                    "idempotencyKey": item.get("_id"),
                    "streamId": self.settings.SYNOPTIC_STREAM_ID_2,
                    "content": item.get("_content"),
                    "createdAt": item.get("published_at"),
                },
            }
            await self._connected.wait()
            try:
                await self._ws_client.send(json.dumps(_item))
            except ConnectionClosed as e:
                self.logger.error("processing", exception=str(e), id=item.get("_id"), pipeline=self.name)
            

        async def close(self) -> None:
            for t in [self._monitor_state_task, self._listening_task]:
                if t and not t.done():
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        pass
            await self._ws_client.close()
            self.logger.debug("closed", pipeline=self.name)

except ModuleNotFoundError:
    # proxy pattern
    class SynopticWebSocketPipeline2(Pipeline):
        name = "synoptic_websocket_2"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[websocket]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)
        
        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def close(self) -> None: pass
