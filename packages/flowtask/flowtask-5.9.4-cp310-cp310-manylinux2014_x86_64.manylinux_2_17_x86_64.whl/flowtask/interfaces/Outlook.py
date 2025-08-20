import asyncio
from typing import List, Optional
from office365.graph_client import GraphClient
from office365.outlook.mail.attachments.attachment import Attachment
from office365.outlook.mail.folders.folder import MailFolder
from office365.outlook.user import OutlookUser
from pathlib import Path
from ..exceptions import FileError
from .O365Client import O365Client


class OutlookClient(O365Client):
    """
    Outlook Client.

    Managing connections to Outlook Mail API.
    """

    def get_context(self, url: str = None, *args) -> GraphClient:
        # For Outlook, we primarily use GraphClient
        if not self._graph_client:
            self._graph_client = GraphClient(acquire_token=lambda: self.access_token)
        return self._graph_client

    def _start_(self, **kwargs):
        return True

    async def list_messages(
        self,
        folder: str = "Inbox",
        top: int = 10,
        filter_query: str = None,
        select_fields: List[str] = None,
    ) -> List[dict]:
        """
        List messages in a specified folder.
        """
        try:
            messages = []
            mail_folder = self._graph_client.me.mail_folders[folder]
            query = mail_folder.messages.top(top)
            if filter_query:
                query = query.filter(filter_query)
            if select_fields:
                query = query.select(select_fields)
            msg_pages = query.get_paged()
            while True:
                for message in msg_pages:
                    messages.append({
                        "id": message.id,
                        "subject": message.subject,
                        "sender": message.sender.email_address.address,
                        "receivedDateTime": message.received_date_time,
                    })
                if not msg_pages.has_next:
                    break
                msg_pages = msg_pages.get_next()
            return messages
        except Exception as err:
            self._logger.error(f"Error listing messages: {err}")
            raise FileError(f"Error listing messages: {err}") from err

    async def download_message(self, message_id: str, destination: Path):
        """
        Download a message by its ID.
        """
        try:
            message = self._graph_client.me.messages[message_id].get().execute_query()
            eml_content = message.mime_content
            with open(destination, "wb") as file:
                file.write(eml_content)
            return str(destination)
        except Exception as err:
            self._logger.error(f"Error downloading message {message_id}: {err}")
            raise FileError(f"Error downloading message {message_id}: {err}") from err

    async def move_message(self, message_id: str, destination_folder_id: str):
        """
        Move a message to a different folder.
        """
        try:
            message = self._graph_client.me.messages[message_id]
            moved_message = message.move(destination_folder_id).execute_query()
            return {
                "id": moved_message.id,
                "subject": moved_message.subject,
                "folderId": destination_folder_id,
            }
        except Exception as err:
            self._logger.error(f"Error moving message {message_id}: {err}")
            raise FileError(f"Error moving message {message_id}: {err}") from err

    async def search_messages(self, search_query: str, top: int = 10) -> List[dict]:
        """
        Search for messages matching the search query.
        """
        try:
            messages = []
            query = self._graph_client.me.messages.search(search_query).top(top)
            msg_pages = query.get_paged()
            while True:
                for message in msg_pages:
                    messages.append({
                        "id": message.id,
                        "subject": message.subject,
                        "sender": message.sender.email_address.address,
                        "receivedDateTime": message.received_date_time,
                    })
                if not msg_pages.has_next:
                    break
                msg_pages = msg_pages.get_next()
            return messages
        except Exception as err:
            self._logger.error(f"Error searching messages: {err}")
            raise FileError(f"Error searching messages: {err}") from err

    async def send_message(
        self,
        subject: str,
        body: str,
        to_recipients: List[str],
        cc_recipients: Optional[List[str]] = None,
        bcc_recipients: Optional[List[str]] = None,
        attachments: Optional[List[Path]] = None,
        from_address: Optional[str] = None,
    ):
        """
        Send a message with optional attachments and optional 'on behalf of' another user.
        """
        try:
            message = self._graph_client.me.messages.new()
            message.subject = subject
            message.body = {
                "contentType": "HTML",
                "content": body
            }
            message.to_recipients = [{"emailAddress": {"address": addr}} for addr in to_recipients]
            if cc_recipients:
                message.cc_recipients = [{"emailAddress": {"address": addr}} for addr in cc_recipients]
            if bcc_recipients:
                message.bcc_recipients = [{"emailAddress": {"address": addr}} for addr in bcc_recipients]
            if attachments:
                for attachment_path in attachments:
                    attachment = message.attachments.add_file_attachment(attachment_path.name)
                    with open(attachment_path, "rb") as file:
                        attachment.content_bytes = file.read()
            if from_address:
                # Set the 'from' address
                message.from_ = {"emailAddress": {"address": from_address}}
            # Send the message
            message.send().execute_query()
            return True
        except Exception as err:
            self._logger.error(f"Error sending message: {err}")
            raise FileError(f"Error sending message: {err}") from err
