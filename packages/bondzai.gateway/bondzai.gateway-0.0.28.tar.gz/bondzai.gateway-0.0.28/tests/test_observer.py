from gateway.core.observer import Dispatcher
from unittest.mock import Mock, call


def test_add_observers():
    d = Dispatcher()

    event1 = "event1"
    event2 = "event2"

    handler = lambda : None
    handler2 = lambda : None

    # Adding observers for events
    assert d.add_observer(event1, handler)
    assert d.add_observer(event2, handler)
    assert d.add_observer(event2, handler2)

    # Checking global observers counts
    obs_list = list(d.get_observers().keys())
    assert len(obs_list) == 2
    assert event1 in obs_list
    assert event2 in obs_list

    # Checking event1 observers
    e1_obs = d.get_event_observers(event1)
    assert len(e1_obs) == 1
    assert e1_obs[0] == handler

    # Checking event2 observers
    e2_obs = d.get_event_observers(event2)
    assert len(e2_obs) == 2
    assert e2_obs[0] in [handler, handler2]
    assert e2_obs[1] in [handler, handler2]

    # Checking that dispatcher get empty observers for unknown event
    assert len(d.get_event_observers("UNKNOWN-EVENT")) == 0


def test_remove_observer():
    d = Dispatcher()

    event = "e"
    
    handler = lambda : None
    handler2 = lambda : None

    # Adding two observers
    d.add_observer(event, handler)
    remove_obs = d.add_observer(event, handler2)

    # Checking that observers count is 2
    assert len(list(d.get_event_observers(event))) == 2
    # Removing observer 2
    remove_obs()
    # Checking that observers count is 1
    assert len(list(d.get_event_observers(event))) == 1


def test_notify_event():
    d = Dispatcher()
    event = "e"
    handler = Mock()

    # Adding event observer
    remove_handler = d.add_observer(event, handler)

    # Notifying event and checking that observer as been called
    d.notify(event)
    handler.assert_has_calls([call()])

    arg1 = 12
    arg2 = "test"
    
    # Notifying event with arguments and checking that observer as been called
    # in correct order with correct arguments
    d.notify(event, arg1, arg2)
    handler.assert_has_calls([
        call(),
        call(arg1, arg2)
    ])

    # Removing handler
    remove_handler()

    # Notifying event and checking that call stack hasn't moved
    d.notify(event)
    handler.assert_has_calls([
        call(),
        call(arg1, arg2)
    ])
