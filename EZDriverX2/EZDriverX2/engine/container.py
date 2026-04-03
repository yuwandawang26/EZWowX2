"""Dependency injection container.

Provides a simple DI container for managing service lifecycles.
"""

from typing import TypeVar, Callable, Type, Any
from dataclasses import dataclass


T = TypeVar("T")


@dataclass
class ServiceDescriptor:
    """Describes a registered service."""
    service_type: Type
    factory: Callable[[], Any]
    singleton: bool
    instance: Any = None


class DIContainer:
    """Simple dependency injection container.

    Supports singleton and transient (factory) registration.
    """

    def __init__(self) -> None:
        self._services: dict[Type, ServiceDescriptor] = {}
        self._registration_order: list[Type] = []

    def register_singleton(self, service_type: Type[T], factory: Callable[[], T]) -> "DIContainer":
        """Register a singleton service.

        The factory is called once and the same instance is returned
        for all subsequent resolutions.

        Args:
            service_type: The interface or base type to register.
            factory: Factory function to create the instance.

        Returns:
            Self for chaining.
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            singleton=True,
        )
        self._registration_order.append(service_type)
        return self

    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> "DIContainer":
        """Register a factory (transient) service.

        The factory is called each time the service is resolved.

        Args:
            service_type: The interface or base type to register.
            factory: Factory function to create the instance.

        Returns:
            Self for chaining.
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            singleton=False,
        )
        self._registration_order.append(service_type)
        return self

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service by type.

        Args:
            service_type: The type to resolve.

        Returns:
            The service instance.

        Raises:
            KeyError: If the service is not registered.
            CircularDependencyError: If circular dependencies are detected.
        """
        if service_type not in self._services:
            raise KeyError(f"Service {service_type.__name__} is not registered")

        descriptor = self._services[service_type]

        if descriptor.singleton:
            if descriptor.instance is None:
                descriptor.instance = descriptor.factory()
            return descriptor.instance
        else:
            return descriptor.factory()

    def resolve_many(self) -> list[Any]:
        """Resolve all registered services in registration order.

        Returns:
            List of all service instances.
        """
        return [self.resolve(t) for t in self._registration_order]

    def clear(self) -> None:
        """Clear all registrations and reset the container."""
        self._services.clear()
        self._registration_order.clear()

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered.

        Args:
            service_type: The type to check.

        Returns:
            True if registered, False otherwise.
        """
        return service_type in self._services


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""
    pass


def create_container() -> DIContainer:
    """Create a new DI container with common services.

    Returns:
        Configured DIContainer instance.
    """
    container = DIContainer()
    return container


__all__ = ["DIContainer", "CircularDependencyError", "create_container"]
