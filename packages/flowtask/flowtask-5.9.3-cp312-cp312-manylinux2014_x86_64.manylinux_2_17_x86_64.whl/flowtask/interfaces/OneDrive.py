import os
from typing import List
from collections.abc import Callable
from pathlib import Path
import pandas as pd
from io import BytesIO
from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.drives.drive import Drive
from ..exceptions import FileError, FileNotFound
from .O365Client import O365Client


class OneDriveClient(O365Client):
    """
    OneDrive Client.

    Interface for Managing connections to OneDrive resources.

    Methods:
        file_list: Lists files in a specified OneDrive folder.
        file_search: Searches for files matching a query.
        file_download: Downloads a single file by its item ID.
        download_files: Downloads multiple files provided as a list of dictionaries containing file info.
        folder_download: Downloads a folder and its contents recursively.
        file_delete: Deletes a file or folder by its item ID.
        upload_files: Uploads multiple files to a specified OneDrive folder.
        upload_file: Uploads a single file to OneDrive.
        upload_folder: Uploads a local folder and its contents to OneDrive recursively.

    """

    def get_context(self, url: str, *args) -> Callable:
        # For OneDrive, we primarily use GraphClient
        if not self._graph_client:
            self._graph_client = GraphClient(acquire_token=lambda: self.access_token)
        return self._graph_client

    def _start_(self, **kwargs):
        return True

    async def download_excel_file(
        self,
        item_id: str,
        destination: Path = None,
        as_pandas: bool = False
    ):
        """
        Download an Excel file from OneDrive by item ID.
        If `as_pandas` is True, return as a pandas DataFrame.
        If `as_pandas` is False, save to the destination path.
        """
        try:
            drive = self._graph_client.me.drive
            file_item = drive.items[item_id]

            if as_pandas:
                bytes_buffer = BytesIO()
                file_item.download(bytes_buffer).execute_query()
                bytes_buffer.seek(0)
                df = pd.read_excel(bytes_buffer)
                return df
            else:
                if not destination:
                    raise ValueError("Destination path must be provided when `as_pandas` is False.")
                with open(destination, "wb") as local_file:
                    file_item.download(local_file).execute_query()
                return str(destination)
        except Exception as err:
            self._logger.error(f"Error downloading Excel file {item_id}: {err}")
            raise FileError(f"Error downloading Excel file {item_id}: {err}") from err

    async def upload_dataframe_as_excel(
        self,
        df: pd.DataFrame,
        file_name: str,
        destination_folder: str = None
    ):
        """
        Upload a pandas DataFrame as an Excel file to OneDrive.
        """
        try:
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            drive = self._graph_client.me.drive
            if destination_folder:
                item_path = f"{destination_folder}/{file_name}"
            else:
                item_path = file_name
            target_item = drive.root.item_with_path(item_path)
            target_item.upload(output).execute_query()
            return {
                "name": file_name,
                "webUrl": target_item.web_url
            }
        except Exception as err:
            self._logger.error(f"Error uploading DataFrame as Excel file {file_name}: {err}")
            raise FileError(f"Error uploading DataFrame as Excel file {file_name}: {err}") from err

    async def file_list(self, folder_path: str = None) -> List[dict]:
        """
        List files in a given OneDrive folder.
        """
        try:
            drive = self._graph_client.me.drive
            if folder_path:
                folder_item = drive.root.get_by_path(folder_path)
            else:
                folder_item = drive.root

            items = folder_item.children.get().execute_query()
            file_list = []
            for item in items:
                file_info = {
                    "name": item.name,
                    "id": item.id,
                    "webUrl": item.web_url,
                    "isFolder": item.folder is not None
                }
                file_list.append(file_info)
            return file_list
        except Exception as err:
            self._logger.error(f"Error listing files: {err}")
            raise FileError(f"Error listing files: {err}") from err

    async def file_search(self, search_query: str) -> List[dict]:
        """
        Search for files in OneDrive matching the search query.
        """
        try:
            drive = self._graph_client.me.drive
            items = drive.root.search(search_query).get().execute_query()
            search_results = []
            for item in items:
                file_info = {
                    "name": item.name,
                    "id": item.id,
                    "webUrl": item.web_url,
                    "path": item.parent_reference.path,
                    "isFolder": item.folder is not None
                }
                search_results.append(file_info)
            return search_results
        except Exception as err:
            self._logger.error(f"Error searching files: {err}")
            raise FileError(f"Error searching files: {err}") from err

    async def file_download(self, item_id: str, destination: Path):
        """
        Download a file from OneDrive by item ID.
        """
        try:
            drive = self._graph_client.me.drive
            file_item = drive.items[item_id]
            with open(destination, "wb") as local_file:
                file_item.download(local_file).execute_query()
            return str(destination)
        except Exception as err:
            self._logger.error(f"Error downloading file {item_id}: {err}")
            raise FileError(f"Error downloading file {item_id}: {err}") from err

    async def download_files(self, items: List[dict], destination_folder: Path):
        """
        Download multiple files from OneDrive.
        """
        downloaded_files = []
        for item in items:
            item_id = item.get("id")
            file_name = item.get("name")
            destination = destination_folder / file_name
            await self.file_download(item_id, destination)
            downloaded_files.append(str(destination))
        return downloaded_files

    async def folder_download(self, folder_id: str, destination_folder: Path):
        """
        Download a folder and its contents from OneDrive.
        """
        try:
            drive = self._graph_client.me.drive
            folder_item = drive.items[folder_id]
            await self._download_folder_recursive(folder_item, destination_folder)
            return True
        except Exception as err:
            self._logger.error(f"Error downloading folder {folder_id}: {err}")
            raise FileError(f"Error downloading folder {folder_id}: {err}") from err

    async def _download_folder_recursive(self, folder_item: DriveItem, local_path: Path):
        """
        Recursively download a folder's contents.
        """
        if not local_path.exists():
            local_path.mkdir(parents=True)
        items = folder_item.children.get().execute_query()
        for item in items:
            item_path = local_path / item.name
            if item.folder:
                await self._download_folder_recursive(item, item_path)
            else:
                await self.file_download(item.id, item_path)

    async def file_delete(self, item_id: str):
        """
        Delete a file or folder in OneDrive by item ID.
        """
        try:
            drive = self._graph_client.me.drive
            item = drive.items[item_id]
            item.delete_object().execute_query()
            return True
        except Exception as err:
            self._logger.error(f"Error deleting item {item_id}: {err}")
            raise FileError(f"Error deleting item {item_id}: {err}") from err

    async def upload_files(self, files: List[Path], destination_folder: str = None):
        """
        Upload multiple files to OneDrive.
        """
        uploaded_files = []
        for file_path in files:
            file_name = file_path.name
            uploaded_item = await self.upload_file(file_path, destination_folder)
            uploaded_files.append(uploaded_item)
        return uploaded_files

    async def upload_file(self, file_path: Path, destination_folder: str = None):
        """
        Upload a single file to OneDrive.
        """
        try:
            drive = self._graph_client.me.drive
            if destination_folder:
                target_folder = drive.root.get_by_path(destination_folder)
            else:
                target_folder = drive.root
            with open(file_path, "rb") as content_file:
                file_content = content_file.read()
                uploaded_item = target_folder.children[file_path.name].upload(file_content).execute_query()
            return {
                "name": uploaded_item.name,
                "id": uploaded_item.id,
                "webUrl": uploaded_item.web_url
            }
        except Exception as err:
            self._logger.error(f"Error uploading file {file_path}: {err}")
            raise FileError(f"Error uploading file {file_path}: {err}") from err

    async def upload_folder(self, local_folder: Path, destination_folder: str = None):
        """
        Upload a local folder and its contents to OneDrive.
        """
        uploaded_items = []
        for root, dirs, files in os.walk(local_folder):
            relative_path = Path(root).relative_to(local_folder)
            one_drive_path = f"{destination_folder}/{relative_path}".strip("/") if destination_folder else str(relative_path)  # noqa
            # Create folder in OneDrive if it doesn't exist
            await self._create_onedrive_folder(one_drive_path)
            for file_name in files:
                file_path = Path(root) / file_name
                destination_path = f"{one_drive_path}/{file_name}".strip("/")
                uploaded_item = await self.upload_file(file_path, destination_path)
                uploaded_items.append(uploaded_item)
        return uploaded_items

    async def _create_onedrive_folder(self, folder_path: str):
        """
        Create a folder in OneDrive if it doesn't exist.
        """
        try:
            drive = self._graph_client.me.drive
            # Try to get the folder; if it doesn't exist, create it
            folder_item = drive.root.get_by_path(folder_path)
            folder_item.get().execute_query()
        except Exception:
            # Folder does not exist; create it
            parent_path = "/".join(folder_path.split("/")[:-1])
            folder_name = folder_path.split("/")[-1]
            if parent_path:
                parent_folder = drive.root.get_by_path(parent_path)
            else:
                parent_folder = drive.root
            new_folder = parent_folder.children.add_folder(folder_name).execute_query()
            self._logger.info(f"Created folder: {new_folder.web_url}")
