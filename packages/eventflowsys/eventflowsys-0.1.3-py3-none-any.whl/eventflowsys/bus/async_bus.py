import asyncio, time
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Union

from eventflow.bus.base_bus import IServiceBus, Message, SubscriptionError, MessageNotFoundError


class AsyncServiceBus(IServiceBus):
    """
    Asyncio-based, thread-safe Service Bus/Event Bus for coroutine-based applications.

    Features:
        - Async subscription and message delivery.
        - Message TTL (time-to-live) and priority support.
        - Event hooks for subscribe, unsubscribe, message, and error events.
        - Unsubscribe, broadcast, and delivery metrics.

    SOLID Principles:
        - Single Responsibility: Handles only async message bus logic.
        - Open/Closed: Extensible via hooks and subclassing.
        - Liskov Substitution: Follows IServiceBus contract.
        - Interface Segregation: Only exposes relevant methods.
        - Dependency Inversion: Uses callbacks/hooks for extensibility.
    """

    def __init__(self):
        """
        Initialize the AsyncServiceBus.
        """
        self._lock = asyncio.Lock()
        self._subscribers: Dict[str, Dict[str, Callable[[int, Any], Coroutine[Any, Any, None]]]] = {}
        self._messages: List[Message] = []
        self._next_message_id = 0
        self._message_readers: Dict[int, Set[str]] = {}
        # Event hooks
        self._on_subscribe: Optional[Callable[..., None]] = None
        self._on_unsubscribe: Optional[Callable[..., None]] = None
        self._on_message: Optional[Callable[..., None]] = None
        self._on_error: Optional[Callable[..., None]] = None
        # Metrics
        self._metrics = {
            "delivered": 0,
            "failed": 0,
            "pending": 0,
            "expired": 0,
        }

    # --- Event Hook Registration ---
    def set_on_subscribe(self, hook: Callable[..., None]):
        """
        Set a hook to be called when a service subscribes.

        Args:
            hook (Callable): The hook function.
        """
        self._on_subscribe = hook

    def set_on_unsubscribe(self, hook: Callable[..., None]):
        """
        Set a hook to be called when a service unsubscribes.

        Args:
            hook (Callable): The hook function.
        """
        self._on_unsubscribe = hook

    def set_on_message(self, hook: Callable[..., None]):
        """
        Set a hook to be called when a message is published.

        Args:
            hook (Callable): The hook function.
        """
        self._on_message = hook

    def set_on_error(self, hook: Callable[..., None]):
        """
        Set a hook to be called when an error occurs.

        Args:
            hook (Callable): The hook function.
        """
        self._on_error = hook

    # --- Subscription Management ---
    async def subscribe(
        self,
        group: str,
        service_name: str,
        callback: Callable[[int, Any], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Subscribe a service to a group.

        Args:
            group (str): The group to subscribe to.
            service_name (str): The name of the subscribing service.
            callback (Callable): The async callback to invoke when a message is delivered.

        Raises:
            SubscriptionError: If the callback is not callable.
        """
        if not callable(callback):
            raise SubscriptionError("Callback must be callable.")
        async with self._lock:
            if group not in self._subscribers:
                self._subscribers[group] = {}
            self._subscribers[group][service_name] = callback
        if self._on_subscribe:
            try:
                self._on_subscribe(group, service_name)
            except Exception as e:
                if self._on_error:
                    self._on_error(e)

    async def unsubscribe(self, group: str, service_name: str) -> None:
        """
        Unsubscribe a service from a group.

        Args:
            group (str): The group to unsubscribe from.
            service_name (str): The name of the service to remove.
        """
        async with self._lock:
            if group in self._subscribers and service_name in self._subscribers[group]:
                del self._subscribers[group][service_name]
                if not self._subscribers[group]:
                    del self._subscribers[group]
        if self._on_unsubscribe:
            try:
                self._on_unsubscribe(group, service_name)
            except Exception as e:
                if self._on_error:
                    self._on_error(e)

    # --- Message Publishing ---
    async def publish(
        self,
        group: str,
        data: Any,
        priority: int = 0,
        ttl: Optional[float] = None,
        broadcast: bool = False,
    ) -> Union[int, List[int]]:
        """
        Publish a new message to the bus for a group (or all groups if broadcast).

        Args:
            group (str): Target group (ignored if broadcast=True).
            data (Any): Message payload.
            priority (int): Lower values are higher priority.
            ttl (Optional[float]): Time-to-live in seconds (None for no expiration).
            broadcast (bool): If True, send to all groups.

        Returns:
            int or list of int: message id(s).
        """
        async with self._lock:
            await self._cleanup()
            target_groups = list(self._subscribers.keys()) if broadcast else [group]
            message_ids = []
            for tgt_group in target_groups:
                if tgt_group not in self._subscribers or not self._subscribers[tgt_group]:
                    continue
                msg_id = self._next_message_id
                self._next_message_id += 1
                expiration = time.time() + ttl if ttl else None
                message = Message(
                    priority=priority,
                    msg_id=msg_id,
                    group=tgt_group,
                    data=data,
                    expiration=expiration,
                )
                self._messages.append(message)
                self._message_readers[msg_id] = set()
                for service_name, callback in self._subscribers.get(tgt_group, {}).items():
                    asyncio.create_task(
                        self._deliver(tgt_group, service_name, callback, msg_id, data)
                    )
                message_ids.append(msg_id)
                if self._on_message:
                    try:
                        self._on_message(msg_id, tgt_group, data)
                    except Exception as e:
                        if self._on_error:
                            self._on_error(e)
            self._messages.sort()
            self._metrics["pending"] = len(self._messages)
            return message_ids[0] if len(message_ids) == 1 else message_ids

    async def _deliver(
        self,
        group: str,
        service_name: str,
        callback: Callable[[int, Any], Coroutine[Any, Any, None]],
        msg_id: int,
        data: Any,
    ):
        """
        Internal method to deliver a message to a service.

        Args:
            group (str): The group of the service.
            service_name (str): The name of the service.
            callback (Callable): The async callback to invoke.
            msg_id (int): The message ID.
            data (Any): The message payload.
        """
        try:
            await callback(msg_id, data)
            async with self._lock:
                self._message_readers[msg_id].add(service_name)
                self._metrics["delivered"] += 1
                await self._cleanup()
        except Exception as e:
            async with self._lock:
                self._metrics["failed"] += 1
            if self._on_error:
                self._on_error(e)

    async def _cleanup(self):
        """
        Remove messages that have been read by all registered services in their group,
        or have expired.
        """
        now = time.time()
        to_remove = [
            message
            for message in self._messages
            if message.is_expired()
            or self._message_readers[message.msg_id]
            == set(self._subscribers.get(message.group, {}).keys())
        ]
        for message in to_remove:
            if message.is_expired():
                self._metrics["expired"] += 1
            self._messages.remove(message)
            del self._message_readers[message.msg_id]
        self._metrics["pending"] = len(self._messages)

    async def pending_count(self) -> int:
        """
        Return the number of pending messages.

        Returns:
            int: Number of pending messages.
        """
        async with self._lock:
            await self._cleanup()
            return len(self._messages)

    async def get_unread_services(self, msg_id: int) -> Optional[Set[str]]:
        """
        Get the set of services that have not read the message.

        Args:
            msg_id (int): The message ID.

        Returns:
            Optional[Set[str]]: Set of unread service names, or None if not found.

        Raises:
            MessageNotFoundError: If the message ID does not exist.
        """
        async with self._lock:
            for message in self._messages:
                if message.msg_id == msg_id:
                    group = message.group
                    all_services = set(self._subscribers.get(group, {}).keys())
                    return all_services - self._message_readers.get(msg_id, set())
            raise MessageNotFoundError(f"Message ID {msg_id} not found.")

    def get_metrics(self) -> Dict[str, int]:
        """
        Return metrics for the bus.

        Returns:
            Dict[str, int]: Dictionary of metric names and values.
        """
        return dict(self._metrics)


def __init__():
    """
    AsyncServiceBus module initializer.
    """
    pass