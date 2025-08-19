from typing import List

import yaml
from pydantic import BaseModel

from ingenious.files.files_repository import FileStorage


class Event(BaseModel):
    identifier: str
    event_type: str
    file_name: str
    conversation_flow: str
    response_content: str
    identifier_group: str = "default"


class Events(BaseModel):
    _events: List[Event] = []
    _fs: FileStorage | None = None

    def __init__(self, fs: FileStorage):
        super().__init__()
        self._fs = fs
        print("loaded events")

    def add_event(self, event: Event) -> None:
        self._events.append(event)

    def get_events(self) -> list[Event]:
        return self._events

    def get_event_by_identifier(self, identifier: str) -> Event:
        for event in self._events:
            if event.identifier == identifier:
                return event
        raise ValueError(f"Event with identifier {identifier} not found")

    def get_events_by_identifier(self, identifier: str) -> List[Event]:
        events = []
        for event in self._events:
            if event.identifier == identifier:
                events.append(event)
        return events

    async def load_events_from_file(self, file_path: str) -> None:
        try:
            self._events = []
            if self._fs and await self._fs.check_if_file_exists(
                file_name="events.yml", file_path=file_path
            ):
                events_raw = yaml.safe_load(
                    await self._fs.read_file(
                        file_name="events.yml", file_path=file_path
                    )
                )
                # use pydantic to validate the data
                for event_raw in events_raw:
                    try:
                        event = Event(**event_raw)
                        self.add_event(event)

                    except Exception as e:
                        print(f"Unexpected error during validation: {e}")
                        raise e

            else:
                print(f"No events.yml found at {file_path}")

        except ValueError as e:
            print(f"No events.yml found at {file_path} and error is {e}")
