import asyncio
from collections.abc import Callable
from navconfig.logging import logging
from ..exceptions import FileNotFound, FileError
from .DownloadFrom import DownloadFromBase
from ..interfaces.Sharepoint import SharepointClient


class DownloadFromSharepoint(SharepointClient, DownloadFromBase):
    """
    DownloadFromSharepoint.

    **Overview**

        This Sharepoint component downloads a file or uploads it to the Microsoft Sharepoint service

    **Properties** (inherited from DownloadFromBase and Sharepoint)

    .. table:: Properties
        :widths: auto

        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | Name               | Required | Summary                                                                          |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | credentials        |   Yes    | Credentials to establish connection with SharePoint site (username and password) |
        |                    |          | get credentials from environment if null.                                        |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | site               |   Yes    | The URL of the SharePoint site.                                                  |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | verify             |   No     | Whether to verify the SSL certificate of the SharePoint site (default: True).    |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | timeout            |   No     | The timeout value for SharePoint operations (default: 30 seconds).               |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | create_destination |   No     | Boolean flag indicating whether to create the destination directory if it        |
        |                    |          | doesn't exist (default: True).                                                   |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | tenant             |   Yes    | Is the set of site collections of SharePoint                                     |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | file_id            |   Yes    | Identificador del archivo en sharepoint                                          |
        +--------------------+----------+-----------+----------------------------------------------------------------------+

    Save the downloaded files on the new destination.
    

        Example:

        ```yaml
        DownloadFromSharepoint:
          credentials:
            username: SHAREPOINT_TROCADV_USERNAME
            password: SHAREPOINT_TROCADV_PASSWORD
            tenant: symbits
            site: FlexRoc
          file:
            filename: Bose Schedule.xlsx
            directory: Shared Documents/General/Monthly Schedule & Reporting
          destination:
            directory: /home/ubuntu/symbits/bose/stores/
            filename: Bose Schedule - {today}.xlsx
          masks:
            '{today}':
            - today
            - mask: '%Y-%m-%d'
        ```

    """  # noqa
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        self.url: str = None
        self.folder = None
        self.rename: str = None
        self.context = None
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        # Call the start method from the base classes
        await super(DownloadFromSharepoint, self).start(**kwargs)
        self._started = True
        return True

    async def close(self):
        pass

    async def run(self):
        async with self.connection():
            if not self.context:
                self.context = self.get_context(self.url)
            try:
                if hasattr(self, 'file') and "pattern" in self.file:  # search-like context
                    filenames = await self.file_search()
                else:
                    filenames = await self.file_download()
                self._result = filenames
                self.add_metric(
                    "SHAREPOINT_FILES",
                    self._result
                )
                return self._result
            except (FileError, FileNotFound):
                raise
            except Exception as err:
                logging.error(f"Error downloading File: {err}")
                raise FileError(
                    f"Error downloading File: {err}"
                ) from err
