"""MQTT logger module for MQTT topic logging."""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

from mqtt_connector import MqttConnector
from systemd import journal


class MqttLogger:
    """A logger that logs to an MQTT topic."""

    def __init__(
        self,
        mqtt_broker: str,
        mqtt_port: int,
        mqtt_topic: str,
        log_file: Optional[str] = None,
        log_level: int = logging.INFO,
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = -1,
        throttle_interval: float = 0.1,
        service_name: Optional[str] = None,
        batch_size: int = 10,
        batch_interval: float = 2.0,
        max_buffer_size: int = 1000,
        enable_stdout: bool = False,
    ) -> None:
        """Initialize the MqttLogger.

        Args:
            mqtt_broker (str): The MQTT broker's address.
            mqtt_port (int): The MQTT broker's port.
            mqtt_topic (str): The MQTT topic for logging.
            log_file (str, optional): Path to the log file. If None, file logging
                is disabled.
            log_level (int): The log level (e.g., logging.INFO, logging.DEBUG).
            reconnect_interval (int): Seconds between reconnection attempts.
            max_reconnect_attempts (int): Maximum reconnection attempts
                (-1 for infinite).
            throttle_interval (float): Minimum seconds between MQTT publishes.
            service_name (str, optional): Service name for structured logging.
            batch_size (int): Maximum batch size before auto-flush.
            batch_interval (float): Maximum seconds before auto-flush.
            max_buffer_size (int): Maximum buffer size before dropping logs.
            enable_stdout (bool): Whether to also print log messages to stdout.
        """
        # Validate parameters
        if not mqtt_broker or not mqtt_broker.strip():
            raise ValueError("mqtt_broker cannot be empty")
        if mqtt_port <= 0 or mqtt_port > 65535:
            raise ValueError("mqtt_port must be between 1 and 65535")
        if not mqtt_topic or not mqtt_topic.strip():
            raise ValueError("mqtt_topic cannot be empty")
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_interval <= 0:
            raise ValueError("batch_interval must be positive")
        if max_buffer_size <= 0:
            raise ValueError("max_buffer_size must be positive")
        if throttle_interval < 0:
            raise ValueError("throttle_interval must be non-negative")
        if reconnect_interval <= 0:
            raise ValueError("reconnect_interval must be positive")
        if batch_size > max_buffer_size:
            raise ValueError("batch_size cannot exceed max_buffer_size")

        # Store validated parameters
        self.mqtt_broker = mqtt_broker.strip()
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic.strip()
        self.log_file = log_file
        self.log_level = log_level
        self.service_name = service_name or os.path.basename(sys.argv[0])
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.max_buffer_size = max_buffer_size
        self.enable_stdout = enable_stdout

        # Set up the MQTT connector
        self.mqtt_connector = MqttConnector(
            mqtt_broker=mqtt_broker,
            mqtt_port=mqtt_port,
            client_id=f"{self.service_name}_logger_{id(self)}",
        )
        self.mqtt_connector.set_log_callback(self._handle_connector_log)

        # Set up the log buffer and flush task
        self._log_buffer = []
        self._flush_task = None
        self._flush_event = asyncio.Event()
        self._task_lock = asyncio.Lock()
        self._shutdown_in_progress = False

        # Metrics
        self._total_logs_attempted = 0
        self._total_logs_published = 0
        self._dropped_messages_count = 0
        self._last_metrics_time = time.time()
        self._task_restart_count = 0

        # Set up file logging if required
        if log_file:
            logging.basicConfig(
                filename=log_file,
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

    async def flush_logs(self, timeout: float = 5.0) -> None:
        """Flush all pending logs to MQTT.

        Args:
            timeout: Maximum time to wait for flush to complete in seconds.
        """
        if not self._log_buffer or self._shutdown_in_progress:
            return

        # Try to connect if not connected
        if not self.is_connected():
            try:
                connected = await asyncio.wait_for(
                    self.mqtt_connector.connect(), timeout=timeout / 2
                )
                if not connected:
                    self._log_error("Failed to connect for flushing logs")
                    return
            except asyncio.TimeoutError:
                self._log_error("Connection timeout during flush")
                return
            except Exception as e:
                self._log_error(f"Connection error during flush: {e}")
                return

        # Create a copy of the buffer and clear it atomically
        logs_to_flush = self._log_buffer.copy()
        self._log_buffer.clear()

        # Try to publish logs in batch
        try:
            # Convert logs to JSON string for MQTT payload
            import json

            batch_data = {"logs": logs_to_flush, "batch_timestamp": time.time()}
            payload = json.dumps(batch_data)

            success = await asyncio.wait_for(
                self.mqtt_connector.publish(self.mqtt_topic, payload),
                timeout=timeout / 2,
            )

            if success:
                self._total_logs_published += len(logs_to_flush)
            else:
                self._handle_failed_publish(logs_to_flush)

        except asyncio.TimeoutError:
            self._log_error("Publish timeout during flush")
            self._handle_failed_publish(logs_to_flush)
        except Exception as e:
            self._log_error(f"Publish error during flush: {e}")
            self._handle_failed_publish(logs_to_flush)

    def _handle_failed_publish(self, failed_logs: List[Dict[str, Any]]) -> None:
        """Handle failed log publishing by re-queuing with limits."""
        if self._shutdown_in_progress:
            return

        # Put logs back in buffer, but respect max buffer size
        combined_logs = failed_logs + self._log_buffer
        if len(combined_logs) > self.max_buffer_size:
            # Keep newest logs, drop oldest
            dropped = len(combined_logs) - self.max_buffer_size
            self._log_buffer = combined_logs[-self.max_buffer_size :]
            self._dropped_messages_count += dropped
            self._log_error(f"Buffer overflow: dropped {dropped} old log messages")
        else:
            self._log_buffer = combined_logs

    async def _delayed_flush(self) -> None:
        """Background task that periodically flushes logs."""
        task_name = f"flush_task_{id(self)}"
        try:
            self._log_info(f"Starting flush task: {task_name}")
            while not self._shutdown_in_progress:
                try:
                    # Wait for the flush interval or until explicitly triggered
                    try:
                        await asyncio.wait_for(
                            self._flush_event.wait(), self.batch_interval
                        )
                    except asyncio.TimeoutError:
                        # Timeout is expected for periodic flushing
                        pass

                    self._flush_event.clear()

                    if self._log_buffer and not self._shutdown_in_progress:
                        await self.flush_logs()

                except Exception as e:
                    self._log_error(f"Error in flush task {task_name}: {e}")
                    # Wait a bit before retrying to avoid tight error loops
                    await asyncio.sleep(min(self.batch_interval, 1.0))

        except asyncio.CancelledError:
            self._log_info(f"Flush task {task_name} cancelled")
            # Final flush when cancelled
            if self._log_buffer and not self._shutdown_in_progress:
                try:
                    await asyncio.wait_for(self.flush_logs(), timeout=5.0)
                except asyncio.TimeoutError:
                    self._log_error("Timeout during final flush in cancelled task")
                except Exception as e:
                    self._log_error(f"Error during final flush in cancelled task: {e}")
            raise
        finally:
            self._log_info(f"Flush task {task_name} finished")

    async def shutdown(self, timeout: float = 10.0) -> None:
        """Shutdown the logger and disconnect from MQTT.

        Args:
            timeout: Maximum time to wait for shutdown to complete in seconds.
        """
        if self._shutdown_in_progress:
            return

        self._shutdown_in_progress = True
        self._log_info("Starting logger shutdown")

        try:
            async with self._task_lock:
                # Cancel the flush task if it's running
                if self._flush_task and not self._flush_task.done():
                    self._log_info("Cancelling flush task")
                    self._flush_task.cancel()

                    try:
                        await asyncio.wait_for(self._flush_task, timeout=timeout / 2)
                    except asyncio.CancelledError:
                        self._log_info("Flush task cancelled successfully")
                    except asyncio.TimeoutError:
                        self._log_error("Timeout waiting for flush task to cancel")
                    except Exception as e:
                        self._log_error(f"Error waiting for flush task to cancel: {e}")

            # Final flush with timeout
            if self._log_buffer:
                self._log_info("Performing final flush")
                try:
                    await asyncio.wait_for(self.flush_logs(), timeout=timeout / 2)
                except asyncio.TimeoutError:
                    self._log_error("Timeout during final flush")
                except Exception as e:
                    self._log_error(f"Error during final flush: {e}")

            # Disconnect from MQTT
            try:
                await self.mqtt_connector.disconnect()
                self._log_info("Disconnected from MQTT broker")
            except Exception as e:
                self._log_error(f"Error disconnecting from MQTT: {e}")

        finally:
            self._log_info(
                f"Logger shutdown complete. Published: {self._total_logs_published}, "
                f"Dropped: {self._dropped_messages_count}, "
                f"Task restarts: {self._task_restart_count}"
            )

    def _handle_connector_log(self, level: str, message: str) -> None:
        """Handle log messages from the MQTT connector."""
        # Convert string level to logging level
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        # Log to file if enabled
        if self.log_file and level in log_levels:
            logging.log(log_levels[level], f"MQTT: {message}")

    def is_connected(self) -> bool:
        """Check if the logger is connected to the MQTT broker.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.mqtt_connector.is_connected()

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the logger.

        Returns:
            A dictionary containing status information about the logger,
            including connection state, buffer sizes, and metrics.
        """
        return {
            "mqtt_connected": self.is_connected(),
            "buffer_size": len(self._log_buffer),
            "max_buffer_size": self.max_buffer_size,
            "buffer_utilization": (
                len(self._log_buffer) / self.max_buffer_size
                if self.max_buffer_size > 0
                else 0.0
            ),
            "logs_attempted": self._total_logs_attempted,
            "logs_published": self._total_logs_published,
            "logs_dropped": self._dropped_messages_count,
            "batch_size": self.batch_size,
            "batch_interval": self.batch_interval,
            "service_name": self.service_name,
            "log_level": logging.getLevelName(self.log_level),
            "uptime": time.time() - self._last_metrics_time,
            "flush_task_running": self._flush_task and not self._flush_task.done(),
            "task_restart_count": self._task_restart_count,
            "shutdown_in_progress": self._shutdown_in_progress,
        }

    @staticmethod
    def register_shutdown_hook(logger_instance: "MqttLogger") -> None:
        """Register a shutdown hook to ensure logs are flushed on exit.

        Args:
            logger_instance: The MqttLogger instance to register the shutdown hook for.
        """
        import asyncio
        import atexit

        async def _shutdown():
            await logger_instance.shutdown()

        def _sync_shutdown():
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_shutdown())
            finally:
                loop.close()

        atexit.register(_sync_shutdown)

    @classmethod
    def from_env(cls, prefix: str = "MQTT_LOGGER_", **kwargs):
        """Create a logger instance from environment variables.

        Environment variables are read using the specified prefix.
        Available variables:
        - {PREFIX}LOG_FILE: Path to the log file (if not provided, file logging
            is disabled)
        - {PREFIX}MQTT_BROKER: MQTT broker address
        - {PREFIX}MQTT_PORT: MQTT broker port
        - {PREFIX}MQTT_TOPIC: MQTT topic for logs
        - {PREFIX}LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - {PREFIX}SERVICE_NAME: Service name for structured logging
        - {PREFIX}BATCH_SIZE: Maximum batch size before auto-flush
        - {PREFIX}BATCH_INTERVAL: Maximum seconds before auto-flush
        - {PREFIX}MAX_BUFFER_SIZE: Maximum buffer size before dropping logs
        - {PREFIX}RECONNECT_INTERVAL: Seconds between reconnection attempts
        - {PREFIX}MAX_RECONNECT_ATTEMPTS: Max reconnection attempts (-1 for infinite)
        - {PREFIX}THROTTLE_INTERVAL: Minimum seconds between MQTT publishes
        - {PREFIX}ENABLE_STDOUT: Enable stdout printing (true/false)

        Args:
            prefix: Environment variable prefix
            **kwargs: Override any configuration from environment variables

        Returns:
            A new MqttLogger instance
        """

        # Map string level names to logging levels
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        # Build config from environment with defaults
        config = {
            "mqtt_broker": os.environ.get(f"{prefix}MQTT_BROKER", "localhost"),
            "mqtt_port": int(os.environ.get(f"{prefix}MQTT_PORT", "1883")),
            "mqtt_topic": os.environ.get(f"{prefix}MQTT_TOPIC", "logs"),
            "log_level": level_map.get(
                os.environ.get(f"{prefix}LOG_LEVEL", "INFO"), logging.INFO
            ),
            "service_name": os.environ.get(f"{prefix}SERVICE_NAME", None),
            "batch_size": int(os.environ.get(f"{prefix}BATCH_SIZE", "10")),
            "batch_interval": float(os.environ.get(f"{prefix}BATCH_INTERVAL", "2.0")),
            "max_buffer_size": int(os.environ.get(f"{prefix}MAX_BUFFER_SIZE", "1000")),
            "reconnect_interval": int(
                os.environ.get(f"{prefix}RECONNECT_INTERVAL", "5")
            ),
            "max_reconnect_attempts": int(
                os.environ.get(f"{prefix}MAX_RECONNECT_ATTEMPTS", "-1")
            ),
            "throttle_interval": float(
                os.environ.get(f"{prefix}THROTTLE_INTERVAL", "0.1")
            ),
            "enable_stdout": os.environ.get(f"{prefix}ENABLE_STDOUT", "false").lower()
            in ("true", "1", "yes", "on"),
        }

        # Only set log_file if it's explicitly defined
        if f"{prefix}LOG_FILE" in os.environ:
            config["log_file"] = os.environ[f"{prefix}LOG_FILE"]

        # Override with any kwargs provided
        config.update(kwargs)

        return cls(**config)

    # Methods for different log levels
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug message.

        Args:
            message: The log message
            data: Optional structured data to include with the log
        """
        self._log(logging.DEBUG, message, data)

    def info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message.

        Args:
            message: The log message
            data: Optional structured data to include with the log
        """
        self._log(logging.INFO, message, data)

    def warning(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message.

        Args:
            message: The log message
            data: Optional structured data to include with the log
        """
        self._log(logging.WARNING, message, data)

    def error(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message.

        Args:
            message: The log message
            data: Optional structured data to include with the log
        """
        self._log(logging.ERROR, message, data)

    def critical(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log a critical message.

        Args:
            message: The log message
            data: Optional structured data to include with the log
        """
        self._log(logging.CRITICAL, message, data)

    def _log(
        self, level: int, message: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Internal method to handle logging.

        Args:
            level: The log level (from logging module)
            message: The log message
            data: Optional structured data to include with the log
        """
        # Skip if below log level
        if level < self.log_level:
            return

        self._total_logs_attempted += 1

        # Create structured log entry
        log_entry = {
            "timestamp": time.time(),
            "level": logging.getLevelName(level),
            "message": message,
            "service": self.service_name,
        }

        # Add data if provided
        if data:
            log_entry["data"] = data

        # Add to buffer first, then check overflow to prevent race conditions
        self._log_buffer.append(log_entry)
        current_buffer_size = len(self._log_buffer)

        # Check buffer overflow AFTER adding to handle race conditions properly
        if current_buffer_size > self.max_buffer_size:
            # Drop oldest logs to make room
            dropped = current_buffer_size - self.max_buffer_size
            self._log_buffer = self._log_buffer[-self.max_buffer_size :]
            self._dropped_messages_count += dropped
            self._log_error(f"Buffer overflow: dropped {dropped} old log messages")

        # Log to file if enabled
        if self.log_file:
            logging.log(
                level, message, exc_info=data.get("exc_info", None) if data else None
            )

        # Log to systemd journal
        self._log_to_systemd_journal(level, message, data)

        # Log to stdout if enabled
        if self.enable_stdout:
            self._log_to_stdout(level, message, data)

        # Trigger flush if buffer size exceeds batch size
        if len(self._log_buffer) >= self.batch_size:
            # Ensure flush task is running
            if not self._shutdown_in_progress:
                self._schedule_flush_task_check()

    def _schedule_flush_task_check(self) -> None:
        """Schedule a flush task check without creating orphaned coroutines."""
        # Simply set the flush event - the background task will handle the rest
        # This avoids creating any new tasks from synchronous context
        if not self._shutdown_in_progress:
            self._flush_event.set()

    async def connect_mqtt(self, force_reconnect: bool = False) -> bool:
        """Connect to the MQTT broker.

        Args:
            force_reconnect: Force reconnection even if already connected

        Returns:
            True if connected, False otherwise
        """
        if self._shutdown_in_progress:
            return False

        # Handle force reconnect
        if force_reconnect and self.is_connected():
            await self.mqtt_connector.disconnect()

        # Log connection attempt if stdout is enabled - this prints immediately
        # before any network operations
        if self.enable_stdout:
            import sys

            print(
                f"[INFO] MqttLogger: Attempting to connect to "
                f"{self.mqtt_broker}: {self.mqtt_port}",
                file=sys.stderr,
            )
            sys.stderr.flush()  # Ensure immediate output

        connected = await self.mqtt_connector.connect()

        # Start the flush task if connected and not already running
        if connected:
            await self._ensure_flush_task_running()

        return connected

    async def _ensure_flush_task_running(self) -> None:
        """Ensure the flush task is running, restart if necessary."""
        try:
            await asyncio.wait_for(self._task_lock.acquire(), timeout=5.0)
            try:
                # Check if task needs to be started or restarted
                should_start_task = (
                    self._flush_task is None
                    or self._flush_task.done()
                    or self._flush_task.cancelled()
                )

                if should_start_task and not self._shutdown_in_progress:
                    # Clean up previous task if it exists
                    if self._flush_task is not None:
                        await self._cleanup_previous_task()

                    # Start new flush task with better error handling
                    try:
                        self._flush_task = asyncio.create_task(
                            self._delayed_flush(), name=f"mqtt_logger_flush_{id(self)}"
                        )
                        self._log_info("Flush task started/restarted")
                    except Exception as e:
                        self._log_error(f"Failed to create flush task: {e}")
                        raise

            finally:
                self._task_lock.release()

        except asyncio.TimeoutError:
            self._log_error("Timeout acquiring task lock")
            raise
        except Exception as e:
            self._log_error(f"Error ensuring flush task running: {e}")
            raise

    async def _cleanup_previous_task(self) -> None:
        """Clean up previous task with proper error handling."""
        if self._flush_task.done() and not self._flush_task.cancelled():
            try:
                # Check if the task completed with an exception
                exception = self._flush_task.exception()
                if exception:
                    self._log_error(f"Previous flush task failed: {exception}")
                    self._task_restart_count += 1
            except asyncio.InvalidStateError:
                # Task is not done yet, this shouldn't happen but handle gracefully
                self._log_error("InvalidStateError when checking task exception")

        elif not self._flush_task.cancelled():
            # Cancel running task before starting new one
            self._flush_task.cancel()
            try:
                await asyncio.wait_for(self._flush_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                # Expected for cancelled tasks
                pass
            except Exception as e:
                self._log_error(f"Error waiting for task cancellation: {e}")

    def _log_to_systemd_journal(
        self, level: int, message: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log to systemd journal with appropriate priority level.

        Args:
            level: The log level (from logging module)
            message: The log message
            data: Optional structured data to include with the log
        """
        # Map Python logging levels to systemd journal priorities
        level_map = {
            logging.DEBUG: journal.LOG_DEBUG,
            logging.INFO: journal.LOG_INFO,
            logging.WARNING: journal.LOG_WARNING,
            logging.ERROR: journal.LOG_ERR,
            logging.CRITICAL: journal.LOG_CRIT,
        }

        priority = level_map.get(level, journal.LOG_INFO)

        # Prepare journal fields
        journal_fields = {
            "MESSAGE": message,
            "PRIORITY": priority,
            "SYSLOG_IDENTIFIER": self.service_name,
            "MQTT_BROKER": self.mqtt_broker,
            "MQTT_TOPIC": self.mqtt_topic,
        }

        # Add structured data if provided
        if data:
            for key, value in data.items():
                # Systemd journal field names must be uppercase and contain only
                # alphanumeric and underscore
                field_name = f"DATA_{key.upper().replace('-', '_').replace('.', '_')}"
                journal_fields[field_name] = str(value)

        # Send to systemd journal
        journal.send(**journal_fields)

    def _log_to_stdout(
        self, level: int, message: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log to stdout with formatted output.

        Args:
            level: The log level (from logging module)
            message: The log message
            data: Optional structured data to include with the log
        """
        import datetime

        # Format timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_name = logging.getLevelName(level)

        # Basic formatted message
        formatted_msg = f"[{timestamp}] {self.service_name} - {level_name} - {message}"

        # Add structured data if present
        if data:
            formatted_msg += f" | Data: {json.dumps(data, default=str)}"

        # Print to stdout (or stderr for errors)
        if level >= logging.ERROR:
            print(formatted_msg, file=sys.stderr)
        else:
            print(formatted_msg, file=sys.stdout)

    def _log_info(self, message: str) -> None:
        """Internal info logging."""
        if self.log_file:
            logging.info(f"MqttLogger: {message}")

    def _log_error(self, message: str) -> None:
        """Internal error logging."""
        if self.log_file:
            logging.error(f"MqttLogger: {message}")

    async def disconnect_mqtt(self) -> None:
        """Disconnect from the MQTT broker."""
        await self.shutdown()

    async def __aenter__(self) -> "MqttLogger":
        """Async context manager entry."""
        # Print version information on startup
        from . import __version__

        self.info(f"MqttLogger v{__version__} starting...")

        await self.connect_mqtt()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.shutdown()

    async def get_task_health(self) -> Dict[str, Any]:
        """Get detailed information about task health and status."""
        task_info = {
            "flush_task_exists": self._flush_task is not None,
            "flush_task_done": self._flush_task.done() if self._flush_task else None,
            "flush_task_cancelled": (
                self._flush_task.cancelled() if self._flush_task else None
            ),
            "task_restart_count": self._task_restart_count,
            "shutdown_in_progress": self._shutdown_in_progress,
            "buffer_size": len(self._log_buffer),
            "flush_event_set": self._flush_event.is_set(),
        }

        if self._flush_task and self._flush_task.done():
            try:
                exception = self._flush_task.exception()
                task_info["last_task_exception"] = str(exception) if exception else None
            except asyncio.InvalidStateError:
                task_info["last_task_exception"] = "InvalidStateError"

        return task_info

    async def force_flush_task_restart(self) -> bool:
        """Force restart the flush task. Returns True if successful."""
        if self._shutdown_in_progress:
            return False

        try:
            await self._ensure_flush_task_running()
            return True
        except Exception as e:
            self._log_error(f"Failed to restart flush task: {e}")
            return False
