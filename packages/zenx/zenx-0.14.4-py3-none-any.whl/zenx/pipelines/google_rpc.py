import asyncio
import random
import importlib
import json
from typing import Dict, Optional
import structlog

from zenx.pipelines.base import Pipeline
from zenx.clients.database import DBClient
from zenx.settings import Settings
from zenx.utils import log_processing_time


try:
    import grpc

    class SynopticGoogleRPCPipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc"
        required_settings = ["SYNOPTIC_GRPC_SERVER_URI", "SYNOPTIC_GRPC_TOKEN", "SYNOPTIC_GRPC_ID"]


        def __init__(self, logger: structlog.BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._uri = self.settings.SYNOPTIC_GRPC_SERVER_URI
            self._feed_token = self.settings.SYNOPTIC_GRPC_TOKEN
            self._feed_id = self.settings.SYNOPTIC_GRPC_ID
            self._feed_pb2 = importlib.import_module("zenx.resources.proto.feed_pb2")
            self._feed_pb2_grpc = importlib.import_module("zenx.resources.proto.feed_pb2_grpc")

            self._channel = grpc.aio.secure_channel(self._uri, grpc.ssl_channel_credentials())
            self._stub = self._feed_pb2_grpc.IngressServiceStub(self._channel)
            self._connected = asyncio.Event()
            self._monitor_state_task: Optional[asyncio.Task] = None


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
                state = self._channel.get_state()
                self._monitor_state_task = asyncio.create_task(self._monitor_state(state))


        async def _monitor_state(self, ready_state: grpc.ChannelConnectivity) -> None:
            while True:
                await self._channel.wait_for_state_change(ready_state)
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._channel.get_state(try_to_connect=True)
            await self._channel.channel_ready()
            self.logger.info("connected", pipeline=self.name)
            self._connected.set()


        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            await self._process(item)
            return item


        async def _process(self, item: Dict) -> None:
            _item = {k: v for k, v in item.items() if not k.startswith("_")}
            feed_message = self._feed_pb2.FeedMessage(
                token=self._feed_token,
                feedId=self._feed_id,
                messageId=item['_id'],
                message=json.dumps(_item),
            )
            await self._connected.wait()
            try:
                await self._stub.SubmitFeedMessage(feed_message)
            except grpc.RpcError as e:
                self.logger.error("processing", exception=str(e), id=item['_id'], feed=self._feed_id, pipeline=self.name)


        async def close(self) -> None:
            if self._monitor_state_task and not self._monitor_state_task.done():
                self._monitor_state_task.cancel()
                try:
                    await self._monitor_state_task
                except asyncio.CancelledError:
                    pass
            await self._channel.close()
            self.logger.debug("closed", pipeline=self.name)

except ModuleNotFoundError:
    # proxy pattern
    class SynopticGoogleRPCPipeline(Pipeline):
        name = "synoptic_grpc"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[grpc]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)

        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def close(self) -> None: pass




try:
    import grpc

    class SynopticGoogleRPCEnterprisePipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_enterprise"
        required_settings = ["SYNOPTIC_GRPC_ENTERPRISE_SERVER_URI", "SYNOPTIC_GRPC_ENTERPRISE_TOKEN", "SYNOPTIC_GRPC_ENTERPRISE_ID"]


        def __init__(self, logger: structlog.BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._uri = self.settings.SYNOPTIC_GRPC_SERVER_ENTERPRISE_URI
            self._feed_token = self.settings.SYNOPTIC_GRPC_ENTERPRISE_TOKEN
            self._feed_id = self.settings.SYNOPTIC_GRPC_ENTERPRISE_ID
            self._feed_pb2 = importlib.import_module("zenx.resources.proto.feed_pb2")
            self._feed_pb2_grpc = importlib.import_module("zenx.resources.proto.feed_pb2_grpc")

            self._channel = grpc.aio.secure_channel(self._uri, grpc.ssl_channel_credentials())
            self._stub = self._feed_pb2_grpc.IngressServiceStub(self._channel)
            self._connected = asyncio.Event()
            self._monitor_state_task: Optional[asyncio.Task] = None


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
                state = self._channel.get_state()
                self._monitor_state_task = asyncio.create_task(self._monitor_state(state))


        async def _monitor_state(self, ready_state: grpc.ChannelConnectivity) -> None:
            while True:
                await self._channel.wait_for_state_change(ready_state)
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._channel.get_state(try_to_connect=True)
            await self._channel.channel_ready()
            self.logger.info("connected", pipeline=self.name)
            self._connected.set()


        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            await self._process(item)
            return item


        async def _process(self, item: Dict) -> None:
            _item = {k: v for k, v in item.items() if not k.startswith("_")}
            feed_message = self._feed_pb2.FeedMessage(
                token=self._feed_token,
                feedId=self._feed_id,
                messageId=item['_id'],
                message=json.dumps(_item),
            )
            await self._connected.wait()
            try:
                await self._stub.SubmitFeedMessage(feed_message)
            except grpc.RpcError as e:
                self.logger.error("processing", exception=str(e), id=item['_id'], feed=self._feed_id, pipeline=self.name)


        async def close(self) -> None:
            if self._monitor_state_task and not self._monitor_state_task.done():
                self._monitor_state_task.cancel()
                try:
                    await self._monitor_state_task
                except asyncio.CancelledError:
                    pass
            await self._channel.close()
            self.logger.debug("closed", pipeline=self.name)

except ModuleNotFoundError:
    # proxy pattern
    class SynopticGoogleRPCEnterprisePipeline(Pipeline):
        name = "synoptic_grpc_enterprise"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[grpc]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)

        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def close(self) -> None: pass

