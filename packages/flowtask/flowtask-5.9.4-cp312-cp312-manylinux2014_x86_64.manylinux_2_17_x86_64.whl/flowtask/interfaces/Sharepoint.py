import os
from typing import List, Optional, Union
from collections.abc import Callable
from urllib.parse import quote
from pathlib import Path, PurePath
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
from tqdm import tqdm  # Progress bar library
import pandas as pd
import aiofiles
from io import BytesIO
from office365.sharepoint.client_context import ClientContext
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.files.file import File
from ..exceptions import FileError, FileNotFound
from .O365Client import O365Client
from ..conf import (
    SHAREPOINT_APP_ID,
    SHAREPOINT_APP_SECRET,
    SHAREPOINT_TENANT_ID,
    SHAREPOINT_TENANT_NAME
)

class SharepointClient(O365Client):
    """
    Sharepoint Client.

    Managing connections to MS Sharepoint Resources.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default credentials
        self._default_tenant_id = SHAREPOINT_TENANT_ID
        self._default_client_id = SHAREPOINT_APP_ID
        self._default_client_secret = SHAREPOINT_APP_SECRET
        self._default_tenant_name = SHAREPOINT_TENANT_NAME

    def get_context(self, url: str, *args) -> Callable:
        return ClientContext(url, *args)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return self

    def _start_(self, **kwargs):
        # processing URL:
        site = f"sites/{self.site}/" if self.site is not None else ""
        self.site_url = f"https://{self.tenant}.sharepoint.com"
        self.url = f"{self.site_url}/{site}".rstrip('/')  # Ensure no trailing slash
        if hasattr(self, '_srcfiles'):
            for file in self._srcfiles:
                fd = file.get('directory')
                if 'sites' in fd:
                    file['directory'] = f"{fd}"
                else:
                    file["directory"] = f"/{site}{fd}"
        return True

    def download_excel_from_sharepoint(
        self,
        file_url: str,
        destination: Path = None,
        as_pandas: bool = False
    ):
        try:
            response = self.context.web.get_file_by_server_relative_url(file_url).download().execute_query()
            content = response.content
            if as_pandas:
                bytes_buffer = BytesIO(content)
                return pd.read_excel(bytes_buffer)
            else:
                with open(destination, "wb") as local_file:
                    local_file.write(content)
                return str(destination)
        except Exception as err:
            self._logger.error(
                f"Error downloading Excel file {file_url}: {err}"
            )
            raise FileError(
                f"Error downloading Excel file {file_url}: {err}"
            ) from err

    async def file_search(self) -> List:
        destinations = []
        try:
            # Get the default document library and its drive
            drive = self.context.web.get_default_document_library().drive

            for file in self._srcfiles:
                directory = file["directory"]
                fname = file["filename"]

                # Search for the file within the drive
                items = drive.root.search(f"name:{fname}")
                self.context.load(items)
                self.context.execute_query()

                # Filter results to ensure they are within the specified directory
                paths_matched = [
                    item.serverRelativeUrl for item in items
                    if fname in item.name and directory in item.serverRelativeUrl
                ]

                if len(paths_matched) == 0:
                    self._logger.error(
                        f"Error downloading File: Pattern not match {fname}"
                    )
                    raise FileError(
                        f"Error downloading File: Pattern not match {fname}"
                    )
                else:
                    for path in paths_matched:
                        file = path[path.rfind("/") + 1: len(path)]
                        destination = "{}/{}".format(self.directory, file)
                        try:
                            with open(destination, "wb") as local_file:
                                self.context.web.get_file_by_server_relative_url(
                                    path
                                ).download(local_file).execute_query()
                                destinations.append(destination)
                        except Exception as err:
                            raise RuntimeError(
                                f"Sharepoint: Error downloading file {path}: {err}"
                            ) from err
            return destinations

        except Exception as e:
            print(e)

    async def file_download(self) -> List:
        destinations = []
        for file in self._srcfiles:
            directory = file.get('directory', self.directory)
            fname = file.get('filename', self.filename)
            if self.filename is None:
                self.filename = fname
                destination = self.directory.joinpath(fname)
            else:
                destination = self.filename or fname
            if not directory.endswith('/'):
                directory += '/'
            source = f"{directory}{fname}"
            try:
                self._logger.notice(
                    f"Sharepoint Download: {source}"
                )
                self.context.web.get_file_by_server_relative_url(
                    source
                ).get().execute_query()
                with open(destination, "wb") as local_file:
                    self.context.web.get_file_by_server_relative_url(source).download(
                        local_file
                    ).execute_query()
                destinations.append(destination)
            except Exception as err:
                if 'Not Found for url' in str(err):
                    raise FileNotFound(
                        f"File {fname} not found: {err}"
                    )
                else:
                    self._logger.error(
                        f"Error downloading file {fname}: {err}"
                    )
                    raise FileError(
                        f"Error downloading file {fname}: {err}"
                    ) from err
        return destinations

    async def download_files(self, files: List[dict], destination_dir: str) -> List:
        """
        Download a list of files from SharePoint to a specified destination directory.

        Args:
            files (List[dict]): A list of dictionaries with 'directory' and 'filename' keys.
            destination_dir (str): The local directory where files will be downloaded.

        Returns:
            List: A list of paths to the downloaded files.
        """
        destination_dir = Path(destination_dir).resolve()
        if not destination_dir.exists():
            destination_dir.mkdir(parents=True, exist_ok=True)

        destinations = []

        for file in files:
            directory = file.get('directory')
            fname = file.get('filename')

            if not directory or not fname:
                raise ValueError(
                    "Each file entry must have both 'directory' and 'filename'."
                )

            # Build the SharePoint source path (directory + filename)
            # Ensure forward slashes for SharePoint URLs
            source = f"{directory}/{fname}".replace("\\", "/")

            # Determine the destination file path
            destination = destination_dir.joinpath(fname)

            try:
                # Fetch the file from SharePoint
                self.context.web.get_file_by_server_relative_url(source).get().execute_query()

                # Download the file to the local destination
                with open(destination, "wb") as local_file:
                    self.context.web.get_file_by_server_relative_url(source).download(local_file).execute_query()

                # Append the local destination path to the results
                destinations.append(destination)
            except Exception as err:
                if 'Not Found for url' in str(err):
                    raise FileNotFound(
                        f"File {fname} not found: {err}"
                    )
                else:
                    self._logger.error(
                        f"Error downloading file {fname}: {err}"
                    )
                    raise FileError(
                        f"Error downloading file {fname}: {err}"
                    ) from err

        return destinations

    def print_upload_progress(self, offset):
        file_size = os.path.getsize(str(self._file_handler))
        print(
            "Uploaded '{0}' bytes from '{1}'...[{2}%]".format(offset, file_size, round(offset / file_size * 100, 2))
        )

    def _update_progress_bar(self, progress_bar, offset):
        """Update the progress bar based on the current offset."""
        progress_bar.n = offset  # Set the current position
        progress_bar.refresh()   # Refresh the tqdm bar to show the update

    async def _chunked_upload(
        self,
        target_folder: File,
        file_path: Union[PurePath, Path],
        file_name: str,
        chunk_size: int = 10 * 1024 * 1024
    ) -> File:
        """
        Perform a chunked upload for large files using the method from the GitHub example.

        Args:
            target_folder: SharePoint folder where the file is to be uploaded.
            file_path: Path of the local file.
            file_name: Name of the file in SharePoint.
            chunk_size: Size of each chunk in bytes (default is 10 MB).

        Returns:
            File: The uploaded file object in SharePoint.
        """
        self._file_handler = file_path
        file_size = os.path.getsize(file_path)

        # Initialize tqdm progress bar
        with tqdm(
            total=file_size, unit='B', unit_scale=True, desc=f'Uploading {file_name}'
        ) as pbar:
            with open(file_path, 'rb') as file:
                uploaded_file: File = target_folder.files.create_upload_session(
                    file,
                    chunk_size,
                    lambda offset: self._update_progress_bar(pbar, offset),
                    file_name=file_name
                ).execute_query()

        self._logger.debug(
            'File {0} has been uploaded successfully'.format(uploaded_file.serverRelativeUrl)
        )

        server_relative_url = uploaded_file.serverRelativeUrl
        encoded_path = quote(server_relative_url)

        absolute_url = f"{self.site_url}{encoded_path}"

        self._logger.debug(
            f"File {absolute_url} has been uploaded successfully"
        )

        # Return the uploaded file object
        return {
            # "filename": uploaded_file,
            "relative_url": server_relative_url,
            "absolute_url": absolute_url
        }

    async def upload_files(
        self,
        filenames: Optional[List[Union[Path, PurePath]]] = None,
        sharepoint_folder: Optional[str] = None
    ) -> List[dict]:
        """Upload files to a SharePoint folder using a resumable upload for large files."""
        files = []
        if not filenames:
            filenames = self._srcfiles

        for idx, file in enumerate(filenames):
            # Destination SharePoint folder URL
            destination_folder = self.directory if not sharepoint_folder else sharepoint_folder
            try:
                destination_file = self._destination[idx]
                if destination_file == 'None':
                    destination_file = None
            except KeyError:
                destination_file = None
            if isinstance(file, str):
                file_path = Path(file)  # Convert to Path object for compatibility
            else:
                file_path = file
            file_size = file_path.stat().st_size
            file_name = destination_file or file_path.name

            try:
                # Get the target folder
                target_folder = self.context.web.get_folder_by_server_relative_url(destination_folder)
                self.context.load(target_folder)
                self.context.execute_query()

                if file_size <= 4 * 1024 * 1024:  # 4 MB threshold
                    # Small file, upload directly
                    async with aiofiles.open(file_path, "rb") as content_file:
                        file_content = await content_file.read()
                    target_file = target_folder.upload_file(file_name, file_content).execute_query()
                else:
                    # Large file, use custom chunked upload
                    target_file = await self._chunked_upload(target_folder, file_path, file_name)

                # Append file URL after successful upload
                files.append(
                    {"filename": target_file}
                )

            except Exception as err:
                self._logger.error(
                    f"Error uploading file {file_name}: {err}"
                )
                raise FileError(
                    f"Error uploading file {file_name}: {err}"
                ) from err

        return files

    async def upload_folder(self, local_folder: PurePath):
        destinations = []
        # destination:
        destination = self.destination.get('directory', '')
        try:
            for p in local_folder.glob('**/*'):
                # Check if it's a file or directory
                if p.is_dir():
                    # Create corresponding folder in SharePoint if it doesn't exist
                    folder_path = self._get_sharepoint_folder_path(
                        p, local_folder, destination
                    )
                    self._create_sharepoint_folder(folder_path)
                elif p.is_file():
                    # Upload file to SharePoint
                    sharepoint_folder = self._get_sharepoint_folder_path(
                        p.parent, local_folder, destination
                    )
                    file_url = await self.upload_files([p], sharepoint_folder)
                    destinations.append(file_url)
            return destinations  # Return list of uploaded file URLs

        except Exception as err:
            self._logger.error(
                f"Error uploading folder {local_folder}: {err}"
            )
            raise FileError(
                f"Error uploading folder {local_folder}: {err}"
            ) from err

    # Helper method to create folder paths in SharePoint
    def _get_sharepoint_folder_path(
        self,
        path: PurePath,
        local_folder: PurePath,
        destination: str
    ) -> str:
        """Get the corresponding SharePoint folder path for a local file or folder."""
        # Strip the local folder prefix and combine with SharePoint destination folder
        relative_path = path.relative_to(local_folder)
        sharepoint_folder_path = f"{destination}/{relative_path}".replace("\\", "/")  # Convert to forward slashes
        return sharepoint_folder_path

    # Helper method to create a folder in SharePoint
    def _create_sharepoint_folder(self, folder_url: str):
        """Create a folder in SharePoint if it doesn't exist."""
        folder = self.context.web.get_folder_by_server_relative_url(folder_url)
        try:
            folder.exists
            folder.execute_query()
            if folder.properties.get("Exists"):
                self._logger.info(f"Folder already exists: {folder_url}")
                return
        except Exception:
            pass  # Folder does not exist

        parent_folder_url = "/".join(folder_url.split("/")[:-1])
        folder_name = folder_url.split("/")[-1]

        parent_folder = self.context.web.get_folder_by_server_relative_url(parent_folder_url)
        parent_folder.folders.add(folder_name)
        self.context.execute_query()

        self._logger.info(f"Created folder: {folder_url}")

    async def create_subscription(
        self,
        library_id: str,
        webhook_url: str,
        client_state: str = "secret_string",
        expiration_days: int = 1
    ) -> dict:
        """
        Create a webhook subscription to receive notifications when files are added, updated,
        or deleted in a SharePoint document library.

        Args:
            library_id (str): The ID of the SharePoint document library to subscribe to.
            webhook_url (str): The webhook URL to receive notifications.
            client_state (str): A secret string to verify notifications.
            expiration_days (int): Duration in days for the subscription to be valid (maximum is 180 days).

        Returns:
            dict: The response from Microsoft Graph API containing the subscription details.
        """
        # Set up expiration for the subscription (max 180 days)
        expiration_date = datetime.utcnow() + timedelta(days=expiration_days)
        expiration_datetime = expiration_date.isoformat() + "Z"

        # Define the subscription request body
        request_body = {
            "changeType": "created,updated,deleted",
            "notificationUrl": webhook_url,
            "resource": f"sites/{self.tenant}/lists/{library_id}",  # Resource ID for the library
            "expirationDateTime": expiration_datetime,
            "clientState": client_state
        }

        # Acquire an access token for Microsoft Graph
        access_token = self._access_token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Send the subscription request to Microsoft Graph API
        url = "https://graph.microsoft.com/v1.0/subscriptions"
        response = requests.post(url, headers=headers, json=request_body)

        # Handle the response
        if response.status_code == 201:
            subscription_info = response.json()
            print("Subscription created successfully:", subscription_info)
            return subscription_info
        else:
            error_message = response.json().get("error", {}).get("message", "Unknown error")
            print(f"Failed to create subscription: {error_message}")
            raise RuntimeError(f"Failed to create subscription: {error_message}")

    def get_library_id(self, absolute_url: str) -> str:
        """
        Extracts the Library ID of a SharePoint document library from an absolute URL.

        Args:
            absolute_url (str): The absolute URL of the SharePoint resource.

        Returns:
            str: The ID of the document library.

        Raises:
            RuntimeError: If the library ID could not be retrieved.
        """
        try:
            # Parse the absolute URL to get site and document library path
            parsed_url = urlparse(absolute_url)
            path_parts = parsed_url.path.strip("/").split("/")

            # Format the site name and library path
            site_name = path_parts[1]  # e.g., 'sites/mysite'
            library_name = "/".join(path_parts[2:])  # e.g., 'Documents'

            # Construct the Microsoft Graph API endpoint
            graph_api_url = f"https://graph.microsoft.com/v1.0/sites/{self._default_tenant_name}:/{site_name}:/lists/{library_name}"  # noqa

            # Acquire access token
            access_token = self._access_token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Make a GET request to retrieve the library details
            response = requests.get(graph_api_url, headers=headers)
            response.raise_for_status()
            library_info = response.json()

            # Extract and return the library ID
            library_id = library_info.get("id")
            if not library_id:
                raise RuntimeError("Library ID could not be found in the response.")
            print(f"Library ID for {absolute_url} is {library_id}")
            return library_id

        except Exception as err:
            raise RuntimeError(f"Failed to retrieve library ID: {err}") from err
