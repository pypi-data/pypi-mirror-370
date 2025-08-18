# MQTT Logger

MQTT Logger is a Python package designed for logging messages to an MQTT topic. It provides an easy-to-use interface for connecting to an MQTT broker and logging messages at various levels (debug, info, warning, error, critical). The logger supports batching of log messages and can be used both as a standalone logger and as an asynchronous context manager.

## Features

- Log messages to an MQTT topic.
- Support for multiple logging levels.
- Automatic batching of log messages.
- Asynchronous operation with support for context management.
- Metrics tracking for logging performance.
- Systemd journal integration for structured logging.
- Optional file-based logging.

## Requirements

- Python 3.7+
- systemd development libraries (for systemd journal integration)
- MQTT broker access

## Installation

### System Dependencies

On Ubuntu/Debian systems, install the required systemd development libraries:

```bash
sudo apt-get install libsystemd-dev pkg-config
```

On CentOS/RHEL/Fedora systems:

```bash
sudo yum install systemd-devel pkgconfig
# or on newer versions:
sudo dnf install systemd-devel pkgconfig
```

### Python Package

To install the MQTT Logger package, you can use pip:

```bash
pip install .
```

Note: This package depends on the `muxu-io-mqtt-connector` PyPI package and requires systemd to be available.

Make sure to run this command in the root directory of the project where the `setup.py` file is located.

## Usage

### Basic Usage

You can use the `MqttLogger` class to log messages as follows:

```python
from mqtt_logger.logger import MqttLogger

async def main():
    logger = MqttLogger(
        mqtt_broker="mqtt.example.com",
        mqtt_port=1883,
        mqtt_topic="logs/myapp",
        log_file="app.log"
    )
    await logger.connect_mqtt()
    logger.info("Application started")
    await logger.shutdown()
```

### Context Manager Usage

The `MqttLogger` can also be used as an asynchronous context manager:

```python
from mqtt_logger.logger import MqttLogger

async def main():
    async with MqttLogger(
        mqtt_broker="mqtt.example.com",
        mqtt_port=1883,
        mqtt_topic="logs/myapp"
    ) as logger:
        logger.info("In context manager")
```

## Running Tests

To run the tests for the MQTT Logger, you can use the following command:

```bash
python3 -m venv .venv
source .venv/bin/activate && pip install -r requirements.txt
pytest tests/
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
