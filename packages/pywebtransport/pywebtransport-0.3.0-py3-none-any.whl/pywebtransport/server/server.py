"""
WebTransport Server Implementation.
"""

from __future__ import annotations

import asyncio
import weakref
from dataclasses import asdict, dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Self, Type, cast

from aioquic.asyncio import serve as quic_serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.asyncio.server import QuicServer
from aioquic.quic.events import QuicEvent

from pywebtransport.config import ServerConfig
from pywebtransport.connection import ConnectionManager, WebTransportConnection
from pywebtransport.events import Event, EventEmitter
from pywebtransport.exceptions import ServerError
from pywebtransport.protocol.utils import create_quic_configuration
from pywebtransport.session import SessionManager
from pywebtransport.types import Address, EventType
from pywebtransport.utils import get_logger, get_timestamp

__all__ = [
    "ServerStats",
    "WebTransportServer",
    "WebTransportServerProtocol",
]

logger = get_logger("server.server")


@dataclass
class ServerStats:
    """A data class for storing server statistics."""

    connections_accepted: int = 0
    connections_rejected: int = 0
    connection_errors: int = 0
    protocol_errors: int = 0
    uptime: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to a dictionary."""
        return asdict(self)


class WebTransportServerProtocol(QuicConnectionProtocol):
    """An aioquic protocol wrapper that handles incoming connections and event buffering."""

    _server_ref: weakref.ReferenceType[WebTransportServer]
    _connection_ref: weakref.ReferenceType[WebTransportConnection] | None
    _pending_events: list[QuicEvent]

    def __init__(self, server: WebTransportServer, *args: Any, **kwargs: Any):
        """Initialize the server protocol."""
        super().__init__(*args, **kwargs)
        self._server_ref = weakref.ref(server)
        self._connection_ref: weakref.ReferenceType[WebTransportConnection] | None = None
        self._pending_events = []

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Handle a new transport connection."""
        super().connection_made(transport)
        if server := self._server_ref():
            asyncio.create_task(server._handle_new_connection(transport, self))

    def connection_lost(self, exc: Exception | None) -> None:
        """Handle the underlying transport connection being lost."""
        super().connection_lost(exc)
        if self._connection_ref and (connection := self._connection_ref()):
            connection._on_connection_lost(exc)

    def quic_event_received(self, event: QuicEvent) -> None:
        """Receive QUIC events and either forward them or buffer them."""
        conn = self._connection_ref() if self._connection_ref else None
        if conn and conn.protocol_handler:
            asyncio.create_task(conn.protocol_handler.handle_quic_event(event))
        else:
            logger.debug(f"Buffering QUIC event until connection is set: {event!r}")
            self._pending_events.append(event)

    def set_connection(self, connection: WebTransportConnection) -> None:
        """Link the protocol to its WebTransportConnection and process buffered events."""
        self._connection_ref = weakref.ref(connection)
        if self._pending_events and connection.protocol_handler:
            logger.debug(f"Processing {len(self._pending_events)} buffered QUIC events for {connection.connection_id}")
            for event in self._pending_events:
                asyncio.create_task(connection.protocol_handler.handle_quic_event(event))
            self._pending_events.clear()

    def transmit(self) -> None:
        """Send pending datagrams."""
        if self._transport is not None and not self._transport.is_closing():
            super().transmit()


class WebTransportServer(EventEmitter):
    """The main WebTransport server, managing lifecycle and connections."""

    def __init__(self, *, config: ServerConfig | None = None):
        """Initialize the WebTransport server."""
        super().__init__()
        self._config = config or ServerConfig.create()
        self._config.validate()
        self._serving, self._closing = False, False
        self._server: QuicServer | None = None
        self._start_time: float | None = None
        self._connection_manager = ConnectionManager.create(
            max_connections=self._config.max_connections,
            connection_cleanup_interval=self._config.connection_cleanup_interval,
            connection_idle_check_interval=self._config.connection_idle_check_interval,
            connection_idle_timeout=self._config.connection_idle_timeout,
        )
        self._session_manager = SessionManager.create(
            max_sessions=self._config.max_sessions,
            session_cleanup_interval=self._config.session_cleanup_interval,
        )
        self._background_tasks: list[asyncio.Task[Any]] = []
        self._stats = ServerStats()
        self._setup_event_handlers()
        logger.info("WebTransport server initialized.")

    @property
    def is_serving(self) -> bool:
        """Check if the server is currently serving."""
        return self._serving

    @property
    def config(self) -> ServerConfig:
        """Get the server's configuration object."""
        return self._config

    @property
    def session_manager(self) -> SessionManager:
        """Get the server's session manager instance."""
        return self._session_manager

    @property
    def local_address(self) -> Address | None:
        """Get the local address the server is bound to."""
        if self._server and hasattr(self._server, "_transport") and self._server._transport:
            return cast(Address | None, self._server._transport.get_extra_info("sockname"))
        return None

    async def __aenter__(self) -> Self:
        """Enter the async context for the server."""
        await self._connection_manager.__aenter__()
        await self._session_manager.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context and close the server."""
        await self.close()

    async def listen(self, *, host: str | None = None, port: int | None = None) -> None:
        """Start the server and begin listening for connections."""
        if self._serving:
            raise ServerError("Server is already serving")
        bind_host, bind_port = host or self._config.bind_host, port or self._config.bind_port
        logger.info(f"Starting WebTransport server on {bind_host}:{bind_port}")
        try:
            quic_config = create_quic_configuration(is_client=False, **self._config.to_dict())
            quic_config.load_cert_chain(Path(self._config.certfile), Path(self._config.keyfile))
            if self._config.ca_certs:
                quic_config.load_verify_locations(cafile=self._config.ca_certs)
            quic_config.verify_mode = self._config.verify_mode
            self._server = await quic_serve(
                host=bind_host,
                port=bind_port,
                configuration=quic_config,
                create_protocol=lambda *a, **kw: WebTransportServerProtocol(self, *a, **kw),
            )
            self._serving, self._start_time = True, get_timestamp()
            self._start_background_tasks()
            logger.info(f"WebTransport server listening on {self.local_address}")
        except Exception as e:
            logger.critical(f"Failed to start server: {e}", exc_info=e)
            raise ServerError(f"Failed to start server: {e}") from e

    async def close(self) -> None:
        """Gracefully shut down the server and its resources."""
        if not self._serving or self._closing:
            return
        logger.info("Closing WebTransport server...")
        self._closing = True
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        await self._connection_manager.shutdown()
        await self._session_manager.shutdown()
        if self._server:
            self._server.close()
            if hasattr(self._server, "wait_closed"):
                await self._server.wait_closed()
        self._serving, self._closing = False, False
        logger.info("WebTransport server closed.")

    async def serve_forever(self) -> None:
        """Run the server indefinitely until interrupted."""
        if not self._serving or not self._server:
            raise ServerError("Server is not listening")
        logger.info("Server is running. Press Ctrl+C to stop.")
        try:
            if hasattr(self._server, "wait_closed"):
                await self._server.wait_closed()
            else:
                while self._serving:
                    await asyncio.sleep(3600)
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Server stop signal received.")
        finally:
            await self.close()

    async def get_server_stats(self) -> dict[str, Any]:
        """Get a snapshot of the server's performance statistics."""
        if self._start_time:
            self._stats.uptime = get_timestamp() - self._start_time
        base_stats = self._stats.to_dict()
        base_stats["connections"] = await self._connection_manager.get_stats()
        base_stats["sessions"] = await self._session_manager.get_stats()
        return base_stats

    async def debug_state(self) -> dict[str, Any]:
        """Get a detailed snapshot of the server's state for debugging."""
        stats = await self.get_server_stats()
        connections = await self._connection_manager.get_all_connections()
        sessions = await self._session_manager.get_all_sessions()
        return {
            "server_info": {"serving": self.is_serving, "local_address": self.local_address},
            "aggregated_stats": stats,
            "connections": [conn.info.to_dict() for conn in connections],
            "sessions": [await sess.get_session_stats() for sess in sessions],
        }

    async def diagnose_issues(self) -> list[str]:
        """Analyze server statistics and configuration to identify potential issues."""
        issues: list[str] = []
        stats = await self.get_server_stats()

        if not self.is_serving:
            issues.append("Server is not currently serving.")

        connections_stats = stats.get("connections", {})
        accepted = stats.get("connections_accepted", 0)
        rejected = stats.get("connections_rejected", 0)
        total_conn_attempts = accepted + rejected
        if total_conn_attempts > 20 and total_conn_attempts > 0 and (rejected / total_conn_attempts) > 0.1:
            issues.append(f"High connection rejection rate: {rejected}/{total_conn_attempts}")

        max_connections = self.config.max_connections
        active_connections = connections_stats.get("active", 0) if connections_stats else 0
        if max_connections > 0 and (active_connections / max_connections) > 0.9:
            issues.append(f"High connection usage: {active_connections / max_connections:.1%}")

        try:
            if not Path(self.config.certfile).exists():
                issues.append(f"Certificate file not found: {self.config.certfile}")
            if not Path(self.config.keyfile).exists():
                issues.append(f"Key file not found: {self.config.keyfile}")
        except Exception:
            issues.append("Certificate configuration appears invalid.")

        return issues

    async def _handle_new_connection(
        self, transport: asyncio.BaseTransport, protocol: WebTransportServerProtocol
    ) -> None:
        """Handle a new incoming connection and set up the event forwarding chain."""
        connection: WebTransportConnection | None = None
        try:
            connection = WebTransportConnection(self._config)

            server_ref = weakref.ref(self)
            conn_ref = weakref.ref(connection)

            async def forward_session_request(event: Event) -> None:
                server = server_ref()
                conn = conn_ref()
                if server and conn and isinstance(event.data, dict):
                    event_data = event.data.copy()
                    if "connection" not in event_data:
                        event_data["connection"] = conn
                    logger.debug(
                        f"Forwarding session request for path '{event_data.get('path')}' "
                        f"from connection {conn.connection_id} to server."
                    )
                    await server.emit(EventType.SESSION_REQUEST, data=event_data)

            connection.on(EventType.SESSION_REQUEST, forward_session_request)
            dgram_transport = cast(asyncio.DatagramTransport, transport)
            await connection.accept(transport=dgram_transport, protocol=protocol)
            await self._connection_manager.add_connection(connection)
            self._stats.connections_accepted += 1
            logger.info(f"New connection accepted: {connection.connection_id} from {connection.remote_address}")
        except Exception as e:
            self._stats.connections_rejected += 1
            self._stats.connection_errors += 1
            logger.error(f"Failed to handle new connection: {e}", exc_info=e)
            if connection and not connection.is_closed:
                await connection.close()
            try:
                transport.close()
            except Exception:
                pass

    def _setup_event_handlers(self) -> None:
        """Set up internal event handlers."""
        pass

    def _start_background_tasks(self) -> None:
        """Start all background tasks for the server."""
        pass

    def __str__(self) -> str:
        """Format a concise summary of server information for logging."""
        status = "serving" if self.is_serving else "stopped"
        address = self.local_address or ("unknown", 0)
        conn_count = self._connection_manager.get_connection_count()
        sess_count = self._session_manager.get_session_count()
        return (
            f"WebTransportServer(status={status}, "
            f"address={address[0]}:{address[1]}, "
            f"connections={conn_count}, "
            f"sessions={sess_count})"
        )
