"""
Port interface and factory functions for standman.

Ports are used on the implementation (sender) side to send
information to observers. Ports are created via SessionPolicy
and are responsible for linking sender functions to listener
callbacks in a fail-silent manner.


Design note:
    Ports are designed not to introduce unintended side effects
    into the implementation: exceptions never propagate back to
    the sender, and send() does not enforce serialization that
    could mask concurrency issues.

    Registration and removal of listeners are thread-safe, but this is
    provided for potential future changes and extensions. At present,
    only single-threaded usage is assumed.
    In contrast, Port.send() is always thread-unsafe, and this will never
    change, even with future modifications or extensions.

Scope of Port usage:
    Ports can be defined with different scopes depending on the use case:

    * Module-level:
        A Port shared across multiple functions within a module.
        Example:
            port = create_port()
            def func1():
                port.send("example", "func1")
            def func2():
                port.send("example", "func2")
    
    * Function-level:
        Each function holds its own Port.
        Example:
            def sender():
                port = sender._port
                port.send("example", "sender")
            sender.port = create_port()

    * Class-level:
        A Port shared across all instances of a class.
        Example:
            class Foo:
                port = create_port()
                def method(self):
                    Foo.port.send("example", "Foo.method")

            class Bar(Foo):
                def method(self):
                    super().method()
                    Foo.port.send("example", "Bar.method")
    
    * Instance-level:
        Each object instance has its own Port.
        Example:
            class Foo:
                def __init__(self):
                    self.port = create_port()
                
                def method(self):
                    self.port.send("example", id(self))
            
            class Bar(Foo):
                def __init__(self):
                    super().__init__()
                
                def method(self):
                    super().method()
                    self.port.send("example", id(self))

    Note:
        Apply encapsulation and access restrictions to Ports as needed.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Lock
from typing import TYPE_CHECKING, Protocol

from .protocols import ListenFunction
from .exceptions import OccupiedError, DeniedError

if TYPE_CHECKING:
    from .policy import _PortBridgeTOC

class Port(ABC):
    """Interface for sending information from the implementation side.

    Notes:
        - Thread-safe for listener registration/removal.
        - Thread-unsafe for send() execution to avoid unnecessary
          serialization in concurrent implementations.
    """
    __slots__ = ()
    @abstractmethod
    def send(self, tag: str, *args, **kwargs) -> None:
        """Send arbitrary information to the registered listener.

        Does nothing if no listener is registered.
        Never raises an exception to the sender.

        Note:
            This method is thread-unsafe.
            This is intentional, not for performance optimization,
            but to avoid introducing unintended serialization
            into the implementation through the use of port.send().
            Otherwise, concurrency issues or design flaws in the
            implementation could be hidden by forced serialization.
        
        Args:
            tag (str): Identifier string for the message.
            *args: Arbitrary positional arguments.
            **kwargs: Arbitrary keyword arguments.
        """

    @abstractmethod
    def _set_listen_func(self, key: object, listen: ListenFunction) -> None:
        """Register a listener callback (internal use only)."""

    @abstractmethod
    def _remove_listen_func(self, key: object) -> None:
        """Remove a listener callback (internal use only)."""

    @abstractmethod
    def _get_entry_permit(self) -> object:
        """Return the identifier of the SessionPolicy that created this Port."""


class _StateTOC(Protocol):
    lock: Lock
    listen_func: ListenFunction | None
    error: Exception | None


class _RoleTOC(Protocol):
    state: _StateTOC
    interface: Port


def _create_port_role(bridge: _PortBridgeTOC) -> _RoleTOC:

    @dataclass(slots = True)
    class _State(_StateTOC):
        lock: Lock = field(default_factory = Lock)
        listen_func: ListenFunction | None = field(default = None)
        error: Exception | None = field(default = None)
    
    state = _State()

    class _Interface(Port):
        __slots__ = ()
        
        def send(self, tag: str, *args, **kwargs) -> None:
            try:
                listen_func = state.listen_func
                error = state.error
                if listen_func and not error:
                    bridge.get_message_validator()(tag, *args, **kwargs)
                    listen_func(tag, *args, **kwargs)
            except Exception as e:
                state.error = e
                session = bridge.get_session(self)
                if session is not None:
                    session.set_error(e)
            finally:
                return None
        
        def _set_listen_func(self, key: object, listen: ListenFunction) -> None:
            with state.lock:
                # If an error has already occurred, do nothing instead of raising OccupiedError.
                if state.error:
                    return
                if key is not bridge.get_control_permit():
                    raise PermissionError("Verification failed")
                if state.listen_func is not None:
                    raise OccupiedError("Port is already occupied by another session.")
                state.listen_func = listen
        
        def _remove_listen_func(self, key: object) -> None:
            with state.lock:
                if key is not bridge.get_control_permit():
                    raise PermissionError("Verification failed")
                state.listen_func = None
                state.error = None
                
        
        def _get_entry_permit(self) -> object:
            return bridge.get_entry_permit()

    interface = _Interface()

    @dataclass(slots = True)
    class _Role(_RoleTOC):
        state: _StateTOC
        interface: Port

    return _Role(state = state, interface = interface)


def _create_port(bridge: _PortBridgeTOC) -> Port:
    """Factory: create a functional Port linked to a SessionPolicy."""
    role = _create_port_role(bridge)
    return role.interface


def _create_noop_port(bridge: _PortBridgeTOC) -> Port:
    """Factory: create a no-op Port that denies all connections."""

    class _Interface(Port):
        __slots__ = ()
        def send(self, tag: str, *args, **kwargs) -> None:
            pass
        
        def _set_listen_func(self, key: object, listen: ListenFunction) -> None:
            if key is not bridge.get_control_permit():
                raise PermissionError("Verification failed")
            raise DeniedError("Connection is denied by the policy.")
        
        def _remove_listen_func(self, key: object) -> None:
            if key is not bridge.get_control_permit():
                raise PermissionError("Verification failed")
        
        def _get_entry_permit(self) -> object:
            return bridge.get_entry_permit()

    interface = _Interface()

    return interface

