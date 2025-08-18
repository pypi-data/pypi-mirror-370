# This file marks the directory as a Python package.
# It can be used to define what is exported when the package is imported.

from .connector import MqttConnector

try:
    import importlib.metadata

    __version__ = importlib.metadata.version("muxu-io-mqtt-connector")
except (importlib.metadata.PackageNotFoundError, ImportError):
    __version__ = "unknown"
__author__ = "Alex Gonzalez"
__email__ = "alex@muxu.io"
__description__ = "Low-level MQTT connection management"
__license__ = "MIT"

__all__ = ["MqttConnector", "__version__"]
