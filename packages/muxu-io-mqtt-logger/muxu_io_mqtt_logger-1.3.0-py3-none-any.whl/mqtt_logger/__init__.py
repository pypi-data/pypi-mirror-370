# This file marks the directory as a Python package.
# It can be used to define what is exported when the package is imported.

from .logger import MqttLogger

try:
    import importlib.metadata

    __version__ = importlib.metadata.version("muxu-io-mqtt-logger")
except (importlib.metadata.PackageNotFoundError, ImportError):
    __version__ = "unknown"
__author__ = "Alex Gonzalez"
__email__ = "alex@muxu.io"
__description__ = "MQTT-enabled logging with systemd journal integration"
__license__ = "MIT"

__all__ = ["MqttLogger", "__version__"]
