from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, Set, Optional, List, Coroutine, Union
import time

# -------------------- Custom Errors --------------------

class ServiceBusError(Exception):
    """Base exception for ServiceBus errors."""
    pass

class SubscriptionError(ServiceBusError):
    """Raised when there is a problem with subscribing a service."""
    pass

class MessageNotFoundError(ServiceBusError):
    """Raised when a message with a given ID is not found."""
    pass

class GroupNotFoundError(ServiceBusError):
    """Raised when a group does not exist."""
    pass

# -------------------- Data Structures --------------------

@dataclass(order=True)
class Message:
    """
    Represents a message in the Service Bus/Event Bus.

    Attributes:
        priority (int): Priority of the message (lower is higher priority).
        msg_id (int): Unique identifier for the message.
        group (str): Target group for the message.
        data (Any): Payload of the message.
        expiration (Optional[float]): Expiration timestamp (epoch seconds), or None for no expiration.
    """
    priority: int
    msg_id: int = field(compare=False)
    group: str = field(compare=False)
    data: Any = field(compare=False)
    expiration: Optional[float] = field(compare=False, default=None)

    def is_expired(self) -> bool:
        """
        Check if the message has expired.

        Returns:
            bool: True if expired, False otherwise.
        """
        return self.expiration is not None and time.time() > self.expiration

class IServiceBus(ABC):
    """
    Abstract base class for a professional Service Bus/Event Bus interface.

    This interface enforces SOLID principles by separating concerns, allowing for
    extensibility, and providing clear contracts for implementations.
    """

    @abstractmethod
    def subscribe(self, group: str, service_name: str, callback: Callable[[int, Any], None]) -> None:
        """
        Subscribe a service to a group with a callback.

        Args:
            group (str): The group to subscribe to.
            service_name (str): The name of the subscribing service.
            callback (Callable): The callback to invoke when a message is delivered.
        """
        pass

    @abstractmethod
    def unsubscribe(self, group: str, service_name: str) -> None:
        """
        Unsubscribe a service from a group.

        Args:
            group (str): The group to unsubscribe from.
            service_name (str): The name of the service to remove.
        """
        pass

    @abstractmethod
    def publish(self, group: str, data: Any, priority: int = 0, ttl: Optional[float] = None, broadcast: bool = False) -> Union[int, List[int]]:
        """
        Publish a message to a group or broadcast to all groups.

        Args:
            group (str): Target group (ignored if broadcast=True).
            data (Any): Message payload.
            priority (int): Lower values are higher priority.
            ttl (Optional[float]): Time-to-live in seconds (None for no expiration).
            broadcast (bool): If True, send to all groups.

        Returns:
            int or list of int: message id(s).
        """
        pass

    @abstractmethod
    def pending_count(self) -> int:
        """
        Return the number of pending messages.

        Returns:
            int: Number of pending messages.
        """
        pass

    @abstractmethod
    def get_unread_services(self, msg_id: int) -> Optional[Set[str]]:
        """
        Get the set of services that have not read the message.

        Args:
            msg_id (int): The message ID.

        Returns:
            Optional[Set[str]]: Set of unread service names, or None if not found.
        """
        pass

    @abstractmethod
    def set_on_subscribe(self, hook: Callable[..., None]):
        """
        Set a hook for subscribe events.

        Args:
            hook (Callable): The hook to call on subscribe.
        """
        pass

    @abstractmethod
    def set_on_unsubscribe(self, hook: Callable[..., None]):
        """
        Set a hook for unsubscribe events.

        Args:
            hook (Callable): The hook to call on unsubscribe.
        """
        pass

    @abstractmethod
    def set_on_message(self, hook: Callable[..., None]):
        """
        Set a hook for message events.

        Args:
            hook (Callable): The hook to call on message delivery.
        """
        pass

    @abstractmethod
    def set_on_error(self, hook: Callable[..., None]):
        """
        Set a hook for error events.

        Args:
            hook (Callable): The hook to call on error.
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, int]:
        """
        Return metrics for the bus.

        Returns:
            Dict[str, int]: Dictionary of metric names and values.
        """
        pass