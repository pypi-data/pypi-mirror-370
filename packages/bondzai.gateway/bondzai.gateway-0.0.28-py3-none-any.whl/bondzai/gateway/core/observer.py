import traceback
from typing import Any, Callable
from uuid import UUID, uuid4
from .logger import log


Event = str
EventCallbackFunction = Callable[[Any], None]
EventCallbackRemovalFunction = Callable[[None], None]
EventObserverList = dict[Event, dict[UUID, EventCallbackFunction]]


# Dispatcher Class
# Used to dispatch events in the application runtime
# Observers can listen to events and register a callback handler
# Called each time the event is triggered
class Dispatcher(object):
    def __init__(self) -> None:
        # Observers list
        self._observers: EventObserverList = {}
        
    def get_observers(self) -> EventObserverList:
        return self._observers

    def get_event_observers(self, event: Event) -> list[EventCallbackFunction]:
        # Return the event's observers callback list if event exists
        if event not in self._observers.keys():
            return []
        return list(self._observers[event].values())
    
    def add_observer(self, event: Event, handler: EventCallbackFunction) -> EventCallbackRemovalFunction:
        # If event is not present in observer list, we create an empty list
        if event not in self._observers:
            self._observers[event] = {}

        # Generate an uuid for the observer callback
        # Adding it to the list
        e_id = uuid4()
        self._observers[event][e_id] = handler

        # Returning a lambda function used to unregister obsrever
        return lambda : self.event_remove_observer(event, e_id)

    def event_remove_observer(self, event: Event, event_id: UUID) -> None:
        # If observer is present for this event with this id
        # We remove it from the list
        if event in self._observers:
            if event_id in self._observers[event]:
                del self._observers[event][event_id]

    def notify(self, event: Event, *args: Any, **kargs: Any) -> None:
        # We iterate the event's observers list
        # and run handler callcack for each
        if event in self._observers:
            for handler in self._observers[event].values():
                try:
                    if callable(handler):
                        handler(*args, **kargs)
                except:
                    # If an error occurs, we log it
                    # and continue the execution with the other handlers
                    log(f"Error while dispatching event {event}, trying the other handlers")
                    traceback.format_exc()                        

# Default dispatch for the application
# Users can create their own if needed
# Used in the UT for exemple
dispatcher: Dispatcher = Dispatcher()
