import asyncio
from unittest.mock import AsyncMock, Mock

from helpers import AnotherEvent, DummyEvent
from pydantic import BaseModel
import pytest

from line import Bridge, Bus, Message

# Fixtures and helpers


@pytest.fixture
def mock_node():
    node = Mock()
    node.id = "mock_node"
    return node


def create_message(source: str = "test", event: BaseModel = None) -> Message:
    """Helper to create test messages."""
    if event is None:
        event = DummyEvent()
    return Message(source=source, event=event)


# Message class tests


def test_message_creation():
    event = DummyEvent()
    message = create_message(source="test", event=event)
    assert isinstance(message.timestamp, float)
    assert isinstance(message.id, str)
    assert len(message.id) > 0
    assert message.event == event


# Bus lifecycle tests


def test_bus_init():
    """Test initial Bus state after creation."""
    bus = Bus()
    assert not bus.running
    assert bus.message_queue.maxsize == 1000, "Expected max size of 1000 by default"
    assert len(bus.bridges) == 0, "Expected no bridges at initialization"
    assert len(bus.pending_requests) == 0, "Expected no pending requests at initialization"
    assert isinstance(bus.message_queue, asyncio.Queue), "Expected message queue to be an asyncio.Queue"
    assert bus.shutdown_event is not None, "Expected shutdown event to be set"


@pytest.mark.asyncio
async def test_start_and_cleanup():
    """Tests the start and cleanup lifecycle methods."""
    bus = Bus()

    await bus.start()
    assert bus.running, "Expected bus to be running after start"
    assert isinstance(bus.router_task, asyncio.Task), "Expected router task to be an asyncio.Task"
    assert not bus.router_task.done(), "Expected router task to not be done"

    await bus.cleanup()
    assert not bus.running, "Expected bus to not be running after cleanup"
    assert bus.router_task.cancelled(), "Expected router task to be cancelled"


@pytest.mark.asyncio
async def test_register_bridge(mock_node):
    """Tests that a bridge can be registered correctly."""
    bus = Bus()
    bridge = Bridge(node=mock_node)
    node_id = "agent_a"
    bridge.node.id = node_id

    bus.register_bridge(node_id, bridge)

    assert node_id in bus.bridges, f"Expected {node_id} to be registered in bus.bridges"
    assert bus.bridges[node_id] is bridge, f"Expected {node_id} to be registered as {bridge}"
    assert bridge.bus is bus, f"Expected {bridge.bus} to be {bus}"


@pytest.mark.asyncio
async def test_bus_start_when_already_running():
    """Test start() when already running."""
    bus = Bus()
    await bus.start()
    assert bus.running, "Bus should be marked running after start"
    existing_router_task = bus.router_task
    await bus.start()
    assert bus.router_task is existing_router_task


# Message broadcasting tests.


@pytest.mark.asyncio
async def test_broadcast_message_triggers_bridges():
    """Test that broadcasting a message calls handle_event on the right bridges."""
    bus = Bus()
    try:
        # Create and configure two bridges
        bridge_a = Bridge(node=Mock(id="agent_a"))
        bridge_a.on(DummyEvent)
        bridge_a.handle_event = AsyncMock()

        bridge_b = Bridge(node=Mock(id="agent_b"))
        bridge_b.on(DummyEvent)
        bridge_b.handle_event = AsyncMock()

        brudge_not_subscribed = Bridge(node=Mock(id="agent_c"))
        brudge_not_subscribed.on(DummyEvent)
        brudge_not_subscribed.handle_event = AsyncMock()

        # Register the bridges with the bus
        bus.register_bridge("agent_a", bridge_a)
        bus.register_bridge("agent_b", bridge_b)
        await bus.start()

        message = Message(source="foo", event=DummyEvent(data="broadcast"))
        await bus.broadcast(message)

        await asyncio.sleep(0.01)  # Allow the router (bus+bridges) to process

        bridge_a.handle_event.assert_called_once()
        bridge_b.handle_event.assert_called_once()
        brudge_not_subscribed.handle_event.assert_not_called()

    finally:
        await bus.cleanup()


@pytest.mark.asyncio
async def test_queue_does_not_exceed_max_size():
    bus = Bus(max_queue_size=1)
    assert bus.message_queue.qsize() == 0, "Expected message queue to be empty at start"

    await bus.broadcast(Message(source="test", event="message 1"))

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            bus.broadcast(Message(source="test", event="second message")),
            timeout=0.01,  # seconds
        )


# Error handling tests.


@pytest.mark.asyncio
async def test_bus_runs_through_exceptions():
    """Test handling of exceptions in bridge.handle_event()."""
    # Setup
    bus = Bus()

    failing_handler = Mock(side_effect=RuntimeError("Handler processing failed"))
    success_handler = Mock(return_value=True)

    bridge_a = Bridge(node="agent_a")
    bridge_a.on(DummyEvent).map(failing_handler)

    bridge_b = Bridge(node="agent_b")
    bridge_b.on(DummyEvent).map(success_handler)
    bridge_b.on(AnotherEvent).map(success_handler)  # AnotherEvent only hits success_handler

    bus.register_bridge("agent_a", bridge_a)
    bus.register_bridge("agent_b", bridge_b)

    await bus.start()

    # Broadcast a message
    await bus.broadcast(Message(source="test", event=DummyEvent()))

    # Allow time for processing
    await asyncio.sleep(0.1)

    # Verify both handlers were called
    failing_handler.assert_called_once()
    success_handler.assert_called_once()

    # Bus should still be running despite the exception in failing_handler
    assert bus.running, "Expected bus to be running after exception"
    await bus.broadcast(Message(source="test", event=AnotherEvent()))
    await asyncio.sleep(0.1)
    assert success_handler.call_count == 2, "Expected success_handler to be called twice"


# Edge cases


@pytest.mark.asyncio
async def test_broadcast_after_cleanup():
    """Test that broadcast after cleanup doesn't cause errors."""
    bus = Bus()

    # Start and then cleanup
    await bus.start()
    await bus.cleanup()

    # Bus should not be running
    assert not bus.running, "Expected bus to not be running after cleanup"

    # Try to broadcast a message after cleanup
    message = Message(source="test", event=DummyEvent())

    # This should not raise an exception but the message won't be processed
    await bus.broadcast(message)

    # Message should be queued but won't be processed since router is stopped
    assert bus.message_queue.qsize() == 1, "Expected messages to not be broadcast after cleanup"


@pytest.mark.asyncio
async def test_register_bridge_after_start():
    """Test registering bridges after bus has started."""
    bus = Bus()
    # Create initial bridge
    fn_before_start = Mock(return_value="a")
    bridge_before = Bridge(node="agent_a")
    bridge_before.on(DummyEvent).map(fn_before_start)

    # Register and start
    bus.register_bridge("agent_a", bridge_before)
    await bus.start()

    # Broadcast a message
    await bus.broadcast(Message(source="test", event=DummyEvent()))
    await asyncio.sleep(0.05)

    # Verify initial bridge received message
    fn_before_start.assert_called_once()

    # Now register a new bridge after start
    fn_after_start = Mock(return_value="b")
    bridge_after = Bridge(node="agent_b")
    bridge_after.on(DummyEvent).map(fn_after_start)
    bus.register_bridge("agent_b", bridge_after)

    # Broadcast another message
    await bus.broadcast(Message(source="test", event=DummyEvent()))
    await asyncio.sleep(0.05)

    # Both bridges should receive the second message
    assert fn_before_start.call_count == 2, "Expected before_start to be called twice"
    assert fn_after_start.call_count == 1, "Expected after_start to be called once"
