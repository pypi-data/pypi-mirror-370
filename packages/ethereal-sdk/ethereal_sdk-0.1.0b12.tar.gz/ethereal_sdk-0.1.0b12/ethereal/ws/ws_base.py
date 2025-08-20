from typing import Union, Dict, Any, Optional, List, Callable
import asyncio
import threading
import socketio

from ethereal.models.config import WSBaseConfig
from ethereal.base_client import BaseClient


class WSBase(BaseClient):
    """Websocket client base class.

    Args:
        config (Union[Dict[str, Any], WSConfig]): Configuration dictionary or WSConfig object.
            Required fields include:
            - base_url (str): Base URL for websocket requests
            Optional fields include:
            - verbose (bool): Enables debug logging, defaults to False
    """

    def __init__(self, config: Union[Dict[str, Any], WSBaseConfig]):
        super().__init__(config)
        self.config = WSBaseConfig.model_validate(config)
        self.base_url = f"{self.config.base_url}"

        # Initialize socketio client
        self.sio = socketio.AsyncClient(
            logger=self.config.verbose, engineio_logger=self.config.verbose
        )
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self.callbacks: dict[str, List[Callable]] = {}

        # Setup basic event handlers
        @self.sio.event
        async def connect():
            self.logger.info("Connected to server")

        @self.sio.event
        async def disconnect():
            self.logger.info("Disconnected from server")

        # Setup generic message handler
        @self.sio.on(event="*", namespace="*")
        async def catch_all(event, namespace, data):
            self.logger.debug(
                f"Received event: {event} in namespace {namespace} with data: {data}"
            )
            if event in self.callbacks:
                for callback in self.callbacks[event]:
                    try:
                        callback(data)
                    except Exception as e:
                        self.logger.error(f"Error in callback for event {event}: {e}")

    def open(self, namespaces: Optional[List[str]] = None) -> None:
        """Open the websocket client connection."""
        if not self.loop or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self.loop.run_forever)
            self.thread.daemon = True
            self.thread.start()

        future = asyncio.run_coroutine_threadsafe(
            self.sio.connect(
                self.base_url,
                transports=["websocket"],
                namespaces=namespaces,
            ),
            self.loop,
        )
        future.result()

    def close(self) -> None:
        """Close the websocket client connection."""
        if self.thread and self.loop and not self.loop.is_closed():
            # Disconnect the socket
            future = asyncio.run_coroutine_threadsafe(self.sio.disconnect(), self.loop)
            future.result()

            # Stop the event loop
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()
            self.loop.close()
            self.loop = None
            self.thread = None

    def _emit(
        self, event: str, data: Dict[str, Any], namespace: Optional[str] = None
    ) -> Any:
        """Emit an event to the server.

        Args:
            event (str): Event name
            data (Dict[str, Any]): Event data

        Returns:
            Any: Response from the server
        """
        if not self.loop or self.loop.is_closed():
            raise RuntimeError("WebSocket is not connected")

        future = asyncio.run_coroutine_threadsafe(
            self.sio.emit(event, data, callback=True, namespace=namespace), self.loop
        )
        return future.result()
