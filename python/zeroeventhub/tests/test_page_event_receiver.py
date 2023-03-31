import pytest

from zeroeventhub import (
    Cursor,
    EventReceiver,
    PageEventReceiver,
    Event,
)


@pytest.fixture
def page_event_receiver():
    return PageEventReceiver()


def receive_page_1_events(page_event_receiver: EventReceiver) -> None:
    page_event_receiver.event(1, {"header1": "abc"}, "event 1 partition 1")
    page_event_receiver.event(1, {}, "event 2 partition 1")
    page_event_receiver.checkpoint(1, "0xf01dab1e")
    page_event_receiver.event(2, {"header1": "abc"}, "event 1 partition 2")
    page_event_receiver.event(1, {"header1": "def"}, "event 3 partition 1")
    page_event_receiver.checkpoint(1, "0xFOO")
    page_event_receiver.event(2, {"header1": "blah"}, "event 2 partition 2")
    page_event_receiver.checkpoint(2, "0xBA5EBA11")


def test_page_contains_all_received_events_and_checkpoints(page_event_receiver):
    """
    Test that the page contains all received events and checkpoints in order.
    """

    # act
    receive_page_1_events(page_event_receiver)

    # assert
    assert page_event_receiver.events == [
        Event(1, {"header1": "abc"}, "event 1 partition 1"),
        Event(1, {}, "event 2 partition 1"),
        Event(2, {"header1": "abc"}, "event 1 partition 2"),
        Event(1, {"header1": "def"}, "event 3 partition 1"),
        Event(2, {"header1": "blah"}, "event 2 partition 2"),
    ]

    assert page_event_receiver.checkpoints == [
        Cursor(1, "0xf01dab1e"),
        Cursor(1, "0xFOO"),
        Cursor(2, "0xBA5EBA11"),
    ]

    assert page_event_receiver.latest_checkpoints == [
        Cursor(1, "0xFOO"),
        Cursor(2, "0xBA5EBA11"),
    ]


def test_page_is_empty_after_clearing(page_event_receiver):
    """
    Test that the page contains no events or checkpoints after being cleared.
    """
    # arrange
    receive_page_1_events(page_event_receiver)

    # act
    page_event_receiver.clear()

    # assert
    assert not page_event_receiver.events
    assert not page_event_receiver.checkpoints
    assert not page_event_receiver.latest_checkpoints


def test_page_contains_all_received_events_and_checkpoints_when_receiving_after_being_cleared(
    page_event_receiver,
):
    """
    Test that the page contains all received events and checkpoints in order
    from the second page only after the first page was cleared.
    """
    # arrange
    receive_page_1_events(page_event_receiver)

    # act
    page_event_receiver.clear()
    page_event_receiver.event(1, None, "event 4 partition 1")
    page_event_receiver.checkpoint(1, "0x5ca1ab1e")

    # assert
    assert page_event_receiver.events == [
        Event(1, None, "event 4 partition 1"),
    ]

    assert page_event_receiver.checkpoints == [
        Cursor(1, "0x5ca1ab1e"),
    ]
    assert page_event_receiver.latest_checkpoints == page_event_receiver.checkpoints
