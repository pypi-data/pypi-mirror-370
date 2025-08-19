from typing import List, Dict
from datetime import datetime, timedelta
from .O365Client import O365Client
from ..exceptions import ComponentError


class OutlookCalendarClient(O365Client):
    """
    Outlook Calendar Client for managing calendar events through Microsoft Graph API.
    """

    async def get_client(self):
        """Ensure that the Graph client is initialized and ready to use."""
        if not self._graph_client:
            self.connection()  # Ensures that `_graph_client` is created during connection setup
        return self._graph_client

    async def create_event(self, calendar_id: str, event: Dict) -> Dict:
        """
        Create an event in the specified Outlook calendar.

        Args:
            calendar_id (str): The ID of the calendar.
            event (dict): The event details.

        Returns:
            dict: Details of the created event.
        """
        client = await self.get_client()
        event = await self.run_in_executor(
            client.me.calendars[calendar_id].events.add,
            **event
        )
        return event

    async def list_events(
        self, 
        calendar_id: str, 
        start_datetime: datetime, 
        end_datetime: datetime,
        max_results: int = 10
    ) -> List[Dict]:
        """
        List events in a specified time range in the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar.
            start_datetime (datetime): Start time for retrieving events.
            end_datetime (datetime): End time for retrieving events.
            max_results (int): Maximum number of events to retrieve (default: 10).

        Returns:
            list: List of events in the specified time range.
        """
        client = await self.get_client()
        events = await self.run_in_executor(
            client.me.calendars[calendar_id].calendar_view,
            start_datetime.isoformat(),
            end_datetime.isoformat(),
            max_results=max_results
        )
        return [event.to_dict() for event in events]

    async def get_event(self, calendar_id: str, event_id: str) -> Dict:
        """
        Retrieve details of a specific event.

        Args:
            calendar_id (str): The ID of the calendar.
            event_id (str): The ID of the event.

        Returns:
            dict: Details of the retrieved event.
        """
        client = await self.get_client()
        event = await self.run_in_executor(
            client.me.calendars[calendar_id].events.get,
            event_id=event_id
        )
        return event.to_dict()

    async def update_event(self, calendar_id: str, event_id: str, updated_event: Dict) -> Dict:
        """
        Update an existing event in the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar.
            event_id (str): The ID of the event.
            updated_event (dict): Updated event details.

        Returns:
            dict: Details of the updated event.
        """
        client = await self.get_client()
        updated = await self.run_in_executor(
            client.me.calendars[calendar_id].events[event_id].update,
            **updated_event
        )
        return updated.to_dict()

    async def delete_event(self, calendar_id: str, event_id: str):
        """
        Delete an event from the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar.
            event_id (str): The ID of the event to delete.
        """
        client = await self.get_client()
        await self.run_in_executor(
            client.me.calendars[calendar_id].events[event_id].delete
        )
        print(f"Event {event_id} deleted.")
