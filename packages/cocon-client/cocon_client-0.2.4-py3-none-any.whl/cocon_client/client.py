# TELEVIC CoCon CLIENT
# client.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""Asynchronous client for the Televic CoCon REST API."""

import asyncio
import aiohttp
import random
import inspect
import logging
import json
from asyncio import Task, Future
from aiohttp import ClientSession, ClientTimeout, ClientResponseError
from typing import Callable, Awaitable, Any, Self
from types import TracebackType
from .errors import CoConConnectionError, CoConCommandError, CoConRetryError
from .types import (
    T,
    JSON,
    CommandParams,
    AsyncHandler,
    ErrorHandler,
    QueuedCommand,
    Model,
    _EP,
    Config,
)

logger = logging.getLogger(__name__)

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[{levelname}] {asctime} - {name} {message}",
        style="{",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


class CoConClient:
    """
    Asynchronous client for interacting with the Televic CoCon REST interface.

    Supports long-polling notifications, command sending, and model subscriptions.
    """

    def __init__(
        self,
        url: str,
        port: int = 8890,
        handler: AsyncHandler | None = None,
        on_handler_error: ErrorHandler | None = None,
        config: Config | None = None,
    ) -> None:
        """
        Initialize the CoConClient with connection settings and optional event handlers.

        Args:
            url (str): The hostname or IP address of the CoCon server.
            port (int): The port to connect to on the server. Defaults to 8890.
            handler (Callable[[dict], Awaitable[None]] | None): An async function to handle
                incoming notification data. Defaults to None
            on_handler_error (Callable[[Exception, dict], None] | None): A callback invoked when
                the handler raises an exception. Defaults to None
            config (Config): Optional Config object to override default timing and retry settings.
        """
        self.base_url: str = f"http://{url}:{port}/CoCon"
        self._connect_url: str = f"{self.base_url}/{_EP.CONNECT.value}"
        self._notify_url: str = f"{self.base_url}/{_EP.NOTIFICATION.value}"
        self._shutdown_event = asyncio.Event()
        self.session: ClientSession | None = None
        self._command_queue: asyncio.Queue[QueuedCommand] = asyncio.Queue(maxsize=1000)
        self._subscriptions: set[str] = set()
        self._handler: AsyncHandler | None = handler
        self._on_handler_error: ErrorHandler | None = on_handler_error
        self.config: Config = config or Config()
        self._connection_id: str = ""

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Initializes the aiohttp session and starts the supervisor task which manages polling and
        command processing.

        Returns:
            Self: The initialized CoConClient instance.
        """
        self.session = aiohttp.ClientSession(
            timeout=ClientTimeout(self.config.session_timeout)
        )

        self._supervisor_task: Task = asyncio.create_task(
            self._supervise(), name="supervisor"
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        Signals shutdown, cancels or completes the supervisor task, calls the close method to clean
        up the queue, and closes the HTTP session.

        Args:
            exc_type (type[BaseException] | None): Exception type if raised during the context.
            exc (BaseException | None): Exception instance.
            tb (TracebackType | None): Traceback object.

        Raises:
            Exception: If session is None raise.
        """
        if self.session is None:
            raise Exception("Session is None.")

        self._shutdown_event.set()
        if exc_type:
            self._supervisor_task.cancel()
            await asyncio.gather(self._supervisor_task, return_exceptions=True)
        else:
            await self._supervisor_task
        await self.close()
        await self.session.close()

    async def _supervise(self) -> None:
        """Supervises polling and command loop tasks, handling errors and task cancellation.


        Raises:
            Any exception raised by the polling or command loop.
        """
        poll_task: Task = asyncio.create_task(self._poll_loop(), name="poll_loop")
        command_task: Task = asyncio.create_task(
            self._command_loop(), name="command_loop"
        )

        done, pending = await asyncio.wait(
            {poll_task, command_task}, return_when=asyncio.FIRST_EXCEPTION
        )

        first_exc: BaseException | None = None
        for t in done:
            first_exc = t.exception()
            if first_exc:
                logger.error("supervisor-task %s failed: %s", t.get_name(), first_exc)

        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        if first_exc is not None:
            raise first_exc

    async def _poll_loop(self) -> None:
        """Handles long polling with automatic reconnection on failure."""
        while not self._shutdown_event.is_set():
            try:
                await self._connect_and_poll()
            except Exception as exc:
                logger.error("polling-loop fatal: %s", exc)
                await asyncio.sleep(1)  # avoid tight loop on fatal error

    async def _connect(self) -> str:
        """Request a new connection ID from the CoCon API.

        Raises:
            Exception: If the session is None, or if the call return 200 but the connect field in
            the response is set to False, or if the connection ID is missing from the response.
            CoConConnectionError: If the connection failed.

        Returns:
            str: A valid connection ID.
        """
        if self.session is None:
            raise Exception("Session is None.")

        async with self.session.get(self._connect_url) as resp:
            if resp.status != 200:
                raise CoConConnectionError(
                    f"'/{_EP.CONNECT.value}' failed with status {resp.status}"
                )
            # parse twice because televic return body as json but in quotes and the parser just reformat it
            resp_json = json.loads(await resp.json())
            if not resp_json.get("Connect"):
                raise Exception(
                    f"'/{_EP.CONNECT.value}' call returned 200 but connect in response is False"
                )

            conn_id: str = resp_json.get("id")
            if not conn_id:
                raise Exception(
                    f"'/{_EP.CONNECT.value}' missing connection id in response"
                )
            logger.info("/%s OK - connection established", _EP.CONNECT.value)
            logger.debug("/%s OK - connection id=%s", _EP.CONNECT.value, conn_id)
            return conn_id

    async def _notify(self) -> None:
        """Perform the notify long-poll request and dispatch data to the handler.

        Raises:
            Exception: If ``session`` is ``None``.
            ClientResponseError: If the server returns a non-200 status code.
        """
        if self.session is None:
            raise Exception("Session is None.")

        url = f"{self._notify_url}/id={self._connection_id}"
        async with self.session.get(url, timeout=ClientTimeout(total=35.0)) as resp:
            if resp.status != 200:
                raise ClientResponseError(resp.request_info, (), status=resp.status)
            data = json.loads(await resp.json())
            await self._handle_incoming(data)

    async def _resubscribe(self) -> None:
        """
        Resend subscriptions after reconnecting.

        This method is used internally after a dropped connection (eg. a 400 error) to re-establish
        all previous model subscriptions using the current connection ID.
        """
        for model in self._subscriptions:
            await self._send_command(
                "Subscribe",
                {"Model": model, "id": self._connection_id, "details": "true"},
            )

    async def _connect_and_poll(self) -> None:
        """
        Handles full connect-then-notify cycle including auto-reconnect on 400 errors.

        This method first obtains a connection ID from the server using `_connect`, then enters a
        loop that perform long-polling via `_notify`.
        If a 400 response is received (invalid connection ID), it will reconnect and re-subscribe
        to previously tracked models. Other errors are retried with delay.
        """
        self._connection_id = await self._retry_with_backoff(self._connect)

        while not self._shutdown_event.is_set():
            try:
                await self._notify()
            except ClientResponseError as exc:
                match exc.status:
                    case 400:
                        logger.warning(
                            "/%s 400 - invalid connection id, reconnecting",
                            _EP.NOTIFICATION.value,
                        )
                        logger.debug(
                            "/%s 400 - connection id used=%s",
                            _EP.NOTIFICATION.value,
                            self._connection_id,
                        )
                        self._connection_id = await self._retry_with_backoff(
                            self._connect
                        )
                        await self._resubscribe()
                    case 408:
                        logger.warning(
                            "/%s 408 - channel timed out, retrying notify",
                            _EP.NOTIFICATION.value,
                        )
                    case _:
                        logger.error(
                            "/%s %d- unexpected error: %s, retrying",
                            _EP.NOTIFICATION.value,
                            exc.status,
                            exc,
                        )
                        await asyncio.sleep(1)

    async def _send_command(
        self, endpoint: str, params: CommandParams | None
    ) -> JSON | str:
        """
        Internal method to send a command to a given endpoint with retry support.

        Args:
            endpoint (str): The CoCon API endpoint to send the command to (e.g. "Subscribe").
            params (dict[str,str]): Dictionary of query parameters to include in the request.

        Returns:
            Any: The parsed JSON response if the server returns JSON, otherwise the raw text.

        Raises:
            Exception: If session is None.
            CoConCommandError: If the server responds with a non-200 status code.
        """
        if self.session is None:
            raise Exception("Session is None.")

        url = f"{self.base_url}/{endpoint}"

        async def _send() -> JSON | str:
            """
            Inner coroutine that performs the actual HTTP POST request.

            Sends the request to the target URL with the provided parameters, checks for a
            successful response, and parses the response based on content type.

            Raises:
                Exception: If session is None.
                CoConCommandError: If the server responds with a non-200 HTTP status code.

            Returns:
                Any | str: Parsed JSON if the response is application/json , otherwise plain text.
            """
            if self.session is None:
                raise Exception("Session is None.")
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    body: str = await resp.text()
                    raise CoConCommandError(endpoint, resp.status, body)
                logger.info("/%s - sent successfully", endpoint)

                content_type: str = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return json.loads(await resp.json())
                else:
                    return await resp.text()

        return await self._retry_with_backoff(_send)

    async def _command_loop(self) -> None:
        """
        Continuously processes queued commands and sends them to the server.

        Waits for new commands in the internal queue, attempts to send them one by one, and marks
        them done whether successful or not. Timeouts are ignored to allow continuous polling
        without blocking indefinitely.
        """
        while not self._shutdown_event.is_set():
            try:
                qcmd: QueuedCommand = await asyncio.wait_for(
                    self._command_queue.get(), timeout=self.config.poll_interval
                )
                try:
                    result = await self._send_command(qcmd.endpoint, qcmd.params)
                    if not qcmd.future.done():
                        qcmd.future.set_result(result)
                except Exception as exc:
                    if not qcmd.future.done():
                        qcmd.future.set_exception(exc)
                    logger.error("error sending command: %s", exc)
                finally:
                    self._command_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.error("error sending command: %s", exc)

    async def _retry_with_backoff(self, task_func: Callable[[], Awaitable[T]]) -> T:
        """
        Retries a coroutine with exponential backoff and jitter until success or retry limit.

        This method is generic and works with any return type `T`, where `T` is the return type
        of the async function passed in.

        Args:
            task_func (Callable[[], Awaitable[T]]): An async callable that will be retried.

        Raises:
            CoCoonRetryError: If the retry limit is exceeded.

        Returns:
            T: The result returned by the successful execution of task_func.
        """
        attempt = 0
        while self.config.max_retries < 0 or attempt < self.config.max_retries:
            try:
                return await task_func()
            except Exception as exc:
                delay = min(
                    self.config.backoff_base * 2**attempt + random.uniform(0, 1), 30
                )
                logger.warning("retry %s after %.2fs - %s", attempt + 1, delay, exc)
                await asyncio.sleep(delay)
                attempt += 1
        raise CoConRetryError("Max retries exceeded.")

    async def _handle_incoming(self, data: dict) -> None:
        """
        Handles data received from the notify poll.

        If a handler is registered, the data is passed to it. If the handler raises an
        exception, an optional error hook is invoked and the data is logged. Otherwise, the data
        is logged.

        Args:
            data (dict): The dictionary received from the server containing event updates.
        """
        if self._handler:
            try:
                if inspect.iscoroutinefunction(self._handler):
                    await self._handler(data)
                else:
                    await asyncio.to_thread(self._handler, data)
            except Exception as exc:
                logger.error("handler raised %s (data=%s)", exc, data, exc_info=True)
                if self._on_handler_error is not None:
                    try:
                        self._on_handler_error(exc, data)
                    except Exception as hook_exc:
                        logger.error("on_handler_error failed - %s", hook_exc)
        else:
            logger.info("received: %s", data)

    async def open(self) -> None:
        """
        Manually open a client session and start supervision.

        This method creates an aiohttp session and begins background tasks for polling
        and command processing. It's intended for use outside of a context manager.

        Raises:
            Exception: If the session or supervision fails during startup.
        """
        async with aiohttp.ClientSession(
            timeout=ClientTimeout(self.config.session_timeout)
        ) as session:
            self.session = session
            await self._supervise()

    async def close(self) -> None:
        """
        Gracefully shut down the client and clean up resources.

        Cancels the supervisor task if running, drains and completes all remaining
        items in the command queue, and ensures shutdown is complete.
        """
        self._shutdown_event.set()

        if hasattr(self, "_supervisor_task"):
            self._supervisor_task.cancel()
            await asyncio.gather(self._supervisor_task, return_exceptions=True)

        while not self._command_queue.empty():
            try:
                self._command_queue.get_nowait()
                self._command_queue.task_done()
            except asyncio.QueueEmpty:
                break

        await self._command_queue.join()

    async def send(self, endpoint: str, params: CommandParams | None = None) -> Any:
        """
        Public method to queue a command for sending.

        Adds the command to the internal queue to be sent asynchronously.

        Args:
            endpoint (str): The API command endpoint.
            params (dict[str, str]): Dictionary of parameters to include in the request.
        """
        loop = asyncio.get_running_loop()
        fut: Future[Any] = loop.create_future()
        await self._command_queue.put(QueuedCommand(endpoint, params, fut))
        return await fut

    async def subscribe(
        self, models: list[str | Model], details: bool | str = True
    ) -> None:
        """
        Subscribe to one or more models to receive updates via long-polling.

        Args:
            models (list[str | Model]): List of model names or `Model` enums to subscribe to.
            details (bool | str): Whether to request detailed updates (default: True). If passed as
                a boolean, it is converted to a lowercase string.
        """
        for model in models:
            resp = await self._send_command(
                "Subscribe",
                {
                    "Model": str(model),
                    "id": self._connection_id,
                    "details": str(details).lower(),
                },
            )
            self._subscriptions.add(str(model))
            logger.debug("/Subscribe - %s", resp)

    async def unsubscribe(self, models: list[str | Model]) -> None:
        """
        Unsubscribe from one or more previously subscribed models.

        Args:
            models (list[str | Model]): List of model names or `Model` enums to unsubscribe from.
        """
        for model in models:
            resp = await self._send_command(
                "Unsubscribe",
                {
                    "Model": str(model),
                    "id": self._connection_id,
                },
            )
            self._subscriptions.discard(str(model))
            logger.debug("/UnSubscribe - %s", resp)

    async def set_handler(self, handler: AsyncHandler) -> None:
        """
        Update the handler used to process incoming notification messages.

        Args:
            handler (Callable[[dict], Awaitable[None]]): An async function that will be called
                with each incoming data payload.
        """
        self._handler = handler
