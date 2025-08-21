import platform
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

from mirrai.core.constants import IS_LINUX, IS_MACOS, IS_WINDOWS

T = TypeVar("T")


class Singleton(type):
    """Metaclass for creating singleton classes."""

    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset_instance(cls) -> None:
        """Reset the singleton instance."""
        if cls in cls._instances:
            del cls._instances[cls]


class PlatformFactory(Generic[T], ABC):
    """Base class for platform-specific factory implementations."""

    _instance: Optional[T] = None

    @classmethod
    @abstractmethod
    def _create_windows(cls) -> T:
        """Create Windows implementation. Must be overridden by subclasses."""
        pass

    @classmethod
    def _create_macos(cls) -> T:
        """Create macOS implementation. Override when macOS is supported."""
        raise NotImplementedError(f"macOS {cls.__name__} not yet implemented")

    @classmethod
    def _create_linux(cls) -> T:
        """Create Linux implementation. Override when Linux is supported."""
        raise NotImplementedError(f"Linux {cls.__name__} not yet implemented")

    @classmethod
    def get(cls) -> T:
        """Get the platform-specific instance."""
        if cls._instance is None:
            if IS_WINDOWS:
                cls._instance = cls._create_windows()
            elif IS_MACOS:
                cls._instance = cls._create_macos()
            elif IS_LINUX:
                cls._instance = cls._create_linux()
            else:
                raise NotImplementedError(f"Platform {platform.system()} is not supported")

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the cached instance. Useful for testing."""
        cls._instance = None
