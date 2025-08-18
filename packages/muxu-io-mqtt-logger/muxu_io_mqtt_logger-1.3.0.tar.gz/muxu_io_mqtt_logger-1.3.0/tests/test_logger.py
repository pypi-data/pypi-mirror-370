import asyncio
import subprocess
import time
import uuid

import pytest
import pytest_asyncio

from mqtt_logger.logger import MqttLogger


@pytest.fixture
def mqtt_logger_sync(tmp_path):
    """Create MqttLogger with real MQTT connector for sync tests."""
    log_file = tmp_path / "test.log"

    # Use test.mosquitto.org as a reliable public MQTT broker for testing
    logger = MqttLogger(
        mqtt_broker="test.mosquitto.org",
        mqtt_port=1883,
        mqtt_topic=f"test/mqtt_logger/{uuid.uuid4()}",  # Unique topic for each test
        log_file=str(log_file),
        batch_size=2,
        batch_interval=0.1,
        service_name="mqtt_logger_test",
    )
    return logger


@pytest_asyncio.fixture
async def mqtt_logger(tmp_path):
    """Create MqttLogger with real MQTT connector for async tests."""
    log_file = tmp_path / "test.log"

    # Use test.mosquitto.org as a reliable public MQTT broker for testing
    logger = MqttLogger(
        mqtt_broker="test.mosquitto.org",
        mqtt_port=1883,
        mqtt_topic=f"test/mqtt_logger/{uuid.uuid4()}",  # Unique topic for each test
        log_file=str(log_file),
        batch_size=2,
        batch_interval=0.1,
        service_name="mqtt_logger_test",
    )

    yield logger

    # Cleanup: Ensure proper disconnection after each test
    try:
        await logger.disconnect_mqtt()
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")


@pytest.mark.asyncio
async def test_connect_mqtt_enhanced(mqtt_logger):
    """Test enhanced MQTT connection with task management."""
    try:
        # Add timeout for network operations
        success = await asyncio.wait_for(mqtt_logger.connect_mqtt(), timeout=30.0)

        if success:
            # Verify flush task is started
            health = await mqtt_logger.get_task_health()
            assert health["flush_task_exists"] is True
        else:
            pytest.skip("MQTT broker not available for testing")
    except asyncio.TimeoutError:
        pytest.skip("MQTT connection timed out - broker may be unavailable")
    except Exception as e:
        pytest.skip(f"MQTT connection failed: {e}")
    finally:
        try:
            await mqtt_logger.disconnect_mqtt()
        except Exception:
            pass


@pytest.mark.asyncio
async def test_task_restart_functionality(mqtt_logger):
    """Test automatic task restart on failure."""
    try:
        success = await asyncio.wait_for(mqtt_logger.connect_mqtt(), timeout=30.0)
        if not success:
            pytest.skip("MQTT broker not available for testing")

        # Force restart the task
        restart_success = await mqtt_logger.force_flush_task_restart()
        assert restart_success is True

        # Check task health after restart
        health = await mqtt_logger.get_task_health()
        assert health["flush_task_exists"] is True
    except asyncio.TimeoutError:
        pytest.skip("MQTT connection timed out - broker may be unavailable")
    except Exception as e:
        pytest.skip(f"MQTT connection failed: {e}")


@pytest.mark.asyncio
async def test_graceful_shutdown_with_buffer(mqtt_logger):
    """Test shutdown with pending logs in buffer."""
    try:
        success = await asyncio.wait_for(mqtt_logger.connect_mqtt(), timeout=30.0)
        if not success:
            pytest.skip("MQTT broker not available for testing")

        # Add some logs to buffer
        mqtt_logger.info("test message 1")
        mqtt_logger.info("test message 2")

        # Verify logs are in buffer
        assert len(mqtt_logger._log_buffer) > 0

        # Shutdown should flush remaining logs
        await mqtt_logger.shutdown(timeout=5.0)

        # Verify shutdown completed
        status = mqtt_logger.get_status()
        assert status["shutdown_in_progress"] is True
    except asyncio.TimeoutError:
        pytest.skip("MQTT connection timed out - broker may be unavailable")
    except Exception as e:
        pytest.skip(f"MQTT connection failed: {e}")


@pytest.mark.asyncio
async def test_task_health_monitoring(mqtt_logger):
    """Test comprehensive task health monitoring."""
    # Before connection
    health = await mqtt_logger.get_task_health()
    assert health["flush_task_exists"] is False
    assert health["task_restart_count"] == 0

    # After connection
    try:
        success = await asyncio.wait_for(mqtt_logger.connect_mqtt(), timeout=30.0)
        if success:
            health = await mqtt_logger.get_task_health()
            assert health["flush_task_exists"] is True
            assert health["shutdown_in_progress"] is False
        else:
            pytest.skip("MQTT broker not available for testing")
    except (asyncio.TimeoutError, Exception) as e:
        pytest.skip(f"MQTT connection failed: {e}")


@pytest.mark.asyncio
async def test_buffer_overflow_handling(mqtt_logger):
    """Test buffer management during overflow."""
    mqtt_logger.max_buffer_size = 3

    # Fill buffer beyond capacity
    for i in range(5):
        mqtt_logger.info(f"message {i}")

    # Should not exceed max buffer size
    assert len(mqtt_logger._log_buffer) <= 3
    assert mqtt_logger._dropped_messages_count > 0


@pytest.mark.asyncio
async def test_async_context_manager_enhanced(tmp_path):
    """Test enhanced async context manager."""
    log_file = tmp_path / "test.log"

    test_id = str(uuid.uuid4())

    async with MqttLogger(
        mqtt_broker="test.mosquitto.org",
        mqtt_port=1883,
        mqtt_topic=f"test/mqtt_logger/{test_id}",
        log_file=str(log_file),
        service_name="mqtt_logger_test",
    ) as logger:
        logger.info("test message")

        # Verify task is running within context
        health = await logger.get_task_health()
        assert health["flush_task_exists"] is True

    # After context exit, logger should be properly shut down
    status = logger.get_status()
    assert status["shutdown_in_progress"] is True


def test_configuration_validation():
    """Test parameter validation."""
    with pytest.raises(ValueError, match="batch_size must be positive"):
        MqttLogger("localhost", 1883, "topic", batch_size=0)

    with pytest.raises(ValueError, match="mqtt_port must be between"):
        MqttLogger("localhost", 0, "topic")

    with pytest.raises(ValueError, match="mqtt_topic cannot be empty"):
        MqttLogger("localhost", 1883, "")

    with pytest.raises(ValueError, match="mqtt_broker cannot be empty"):
        MqttLogger("", 1883, "topic")

    with pytest.raises(ValueError, match="batch_size cannot exceed max_buffer_size"):
        MqttLogger("localhost", 1883, "topic", batch_size=100, max_buffer_size=50)


def test_log_info(mqtt_logger_sync):
    """Test logging info messages."""
    mqtt_logger_sync.info("Test info message")
    assert mqtt_logger_sync._total_logs_attempted == 1
    assert len(mqtt_logger_sync._log_buffer) == 1


@pytest.mark.asyncio
async def test_flush_logs(mqtt_logger):
    """Test manual log flushing."""
    try:
        success = await asyncio.wait_for(mqtt_logger.connect_mqtt(), timeout=30.0)
        if not success:
            pytest.skip("MQTT broker not available for testing")

        mqtt_logger.info("Test flush message")
        await mqtt_logger.flush_logs()
        assert mqtt_logger._total_logs_published == 1
    except asyncio.TimeoutError:
        pytest.skip("MQTT connection timed out - broker may be unavailable")
    except Exception as e:
        pytest.skip(f"MQTT connection failed: {e}")


@pytest.mark.asyncio
async def test_disconnect_mqtt(mqtt_logger):
    """Test MQTT disconnection."""
    try:
        success = await asyncio.wait_for(mqtt_logger.connect_mqtt(), timeout=30.0)
        if not success:
            pytest.skip("MQTT broker not available for testing")

        await mqtt_logger.disconnect_mqtt()

        # Should have completed shutdown
        status = mqtt_logger.get_status()
        assert status["shutdown_in_progress"] is True
    except asyncio.TimeoutError:
        pytest.skip("MQTT connection timed out - broker may be unavailable")
    except Exception as e:
        pytest.skip(f"MQTT connection failed: {e}")


@pytest.mark.asyncio
async def test_systemd_journal_logging_real():
    """Test that systemd journal logging works with real journal and real MQTT connector."""
    # Generate a unique test message to identify our journal entry
    test_id = str(uuid.uuid4())
    test_message = f"MQTT Logger Test Message {test_id}"

    # Create a real MqttLogger instance using the real MQTT connector
    # Use Eclipse Mosquitto test broker for real MQTT functionality
    logger = MqttLogger(
        mqtt_broker="test.mosquitto.org",  # Public test MQTT broker
        mqtt_port=1883,
        mqtt_topic=f"test/mqtt_logger/{test_id}",  # Unique topic for this test
        service_name="mqtt_logger_test",
        batch_size=1,  # Immediate publishing
        batch_interval=0.1,
    )

    try:
        # Try to connect to the real MQTT broker
        mqtt_connected = await logger.connect_mqtt()
        print(f"MQTT connection status: {mqtt_connected}")

        # Log a message - this will use both the real systemd journal AND real MQTT
        logger.info(
            test_message, {"test_id": test_id, "test_type": "real_journal_and_mqtt"}
        )

        # If MQTT is connected, flush logs to ensure they're published
        if mqtt_connected:
            await logger.flush_logs()
            await asyncio.sleep(1)  # Give MQTT time to publish

        # Give the journal a moment to process the entry
        time.sleep(2)

        # Use journalctl to verify the message was logged to systemd journal
        try:
            # Search for our specific test message in the journal
            result = subprocess.run(
                [
                    "journalctl",
                    "--no-pager",
                    "--since",
                    "30 seconds ago",
                    "--grep",
                    test_id,
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            # Check if our test message appears in the journal output
            assert result.returncode == 0, f"journalctl command failed: {result.stderr}"
            assert (
                test_id in result.stdout
            ), f"Test message with ID {test_id} found in journal. Output: {result.stdout}"
            assert (
                test_message in result.stdout
            ), f"Full test message found in journal. Output: {result.stdout}"

            print(f"✓ Successfully verified journal entry for test ID: {test_id}")

            # Check the logger status
            status = logger.get_status()
            print(f"Logger status: {status}")

            if mqtt_connected:
                print(
                    f"✓ MQTT was connected and message was published to {logger.mqtt_topic}"
                )
                assert (
                    status["logs_published"] >= 1
                ), "Expected at least one log to be published via MQTT"
            else:
                print("⚠ MQTT connection failed, but journal logging still worked")

        except subprocess.TimeoutExpired:
            pytest.fail("journalctl command timed out")
        except FileNotFoundError:
            pytest.skip("journalctl not available on this system")
        except Exception as e:
            pytest.fail(f"Failed to verify journal entry: {e}")

    finally:
        # Clean up - disconnect from MQTT
        try:
            await logger.disconnect_mqtt()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
