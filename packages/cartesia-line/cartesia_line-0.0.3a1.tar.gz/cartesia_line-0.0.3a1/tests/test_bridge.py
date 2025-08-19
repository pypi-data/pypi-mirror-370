from unittest.mock import Mock

from helpers import AnotherEvent, DummyEvent, SubDummyEvent
import pytest

from line import Bridge, Message
from line.events import EventsRegistry

# Routing tests


@pytest.mark.asyncio
async def test_invocation_on_event():
    """Test that sending an event calls the handler."""
    bridge = Bridge(node="agent")
    fn_to_invoke = Mock()
    bridge.on(DummyEvent).map(fn_to_invoke)

    await bridge.handle_event(Message(source="test", event=DummyEvent()))

    fn_to_invoke.assert_called_once()


@pytest.mark.asyncio
async def test_find_matching_route_aliases():
    """
    Test that _find_matching_routes correctly routes based on aliases and alias globs.
    """
    try:
        # Set up bridge and routes (note we don't need handlers to test _find_matching_routes)
        bridge = Bridge(node="agent")
        bridge.on(DummyEvent)  # Route for the specific DummyEvent class
        bridge.on("user.*")  # String pattern route
        bridge.on("*")  # Wildcard route for any event

        # String alias for the event
        EventsRegistry.register("user.message", DummyEvent)

        # Test case 1: An event with a registered alias, matches all three routes
        routes1 = bridge._find_matching_routes(DummyEvent())
        assert len(routes1) == 3, "Expected exact event to match 3 routes: DummyEvent, '*', and 'user.*'"

        # Test case 2: A subclass of a registered event, doesn't match 'user.*'
        routes2 = bridge._find_matching_routes(SubDummyEvent())
        assert len(routes2) == 2, "Expected subclass event to match 2 routes: DummyEvent and '*'"

        # Test case 3: Only matches '*'
        routes3 = bridge._find_matching_routes(AnotherEvent())
        assert len(routes3) == 1, "Expected unrelated event to match only '*'"

    finally:
        EventsRegistry.events.clear()


@pytest.mark.parametrize("source,expected_num_calls", [("denied_source", 0), ("allowed_source", 1)])
@pytest.mark.asyncio
async def test_handle_event_authorization(source: str, expected_num_calls: int):
    """Test that handle_event respects authorization."""
    auth_bridge = Bridge(node="auth_agent")
    auth_handler = Mock()
    auth_bridge.authorize("allowed_source")
    auth_bridge.on(DummyEvent).map(auth_handler)

    await auth_bridge.handle_event(Message(source=source, event=DummyEvent()))
    assert auth_handler.call_count == expected_num_calls, f"Expected {expected_num_calls} calls for {source}"


@pytest.mark.asyncio
async def test_handle_event_source_filtering():
    """Test that handle_event respects source filtering."""
    filter_bridge = Bridge(node="filter_agent")
    filter_handler = Mock()

    filter_bridge.on(DummyEvent, source="correct_source").map(filter_handler)

    # Event from a non-matching source should not fire the handler
    await filter_bridge.handle_event(Message(source="wrong_source", event=DummyEvent()))
    filter_handler.assert_not_called()

    # Event from a matching source should be handled
    await filter_bridge.handle_event(Message(source="correct_source", event=DummyEvent()))
    filter_handler.assert_called_once()


@pytest.mark.asyncio
async def test_multiple_event_handlers():
    """Test that handle_event can run multiple handlers."""
    bridge = Bridge(node="agent")
    handler1 = Mock()
    handler2 = Mock()
    bridge.on(DummyEvent).map(handler1)
    bridge.on(DummyEvent).map(handler2)

    await bridge.handle_event(Message(source="test", event=DummyEvent()))
    handler1.assert_called_once()
    handler2.assert_called_once()
