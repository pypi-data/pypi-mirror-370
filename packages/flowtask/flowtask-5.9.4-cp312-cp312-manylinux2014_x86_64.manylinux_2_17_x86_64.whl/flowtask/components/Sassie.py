import asyncio
from collections.abc import Callable
from ..utils import is_empty
from ..exceptions import ComponentError, DataNotFound
from ..interfaces.sassie import SassieClient
from .flow import FlowComponent

class Sassie(SassieClient, FlowComponent):
    """
    Sassie

    Overview

        Get Data from Sassie API.

    Properties (inherited from Sassie)

    .. table:: Properties
        :widths: auto

        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | Name               | Required | Summary                                                                          |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | domain             |   Yes    | Domain of Sassie API                                                             |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | credentials        |   Yes    | Credentials to establish connection with Polestar site (user and password)       |
        |                    |          | get credentials from environment if null.                                        |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | data               |   No     | Type of data to retrieve (surveys, questions, jobs, waves, locations, clients)   |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | filter             |   No     | List of filters to apply to the results. Each filter must have:                  |
        |                    |          | - column: The column name to filter on                                           |
        |                    |          | - operator: One of: eq (equals), lt (less than), gt (greater than),              |
        |                    |          |   lte (less than or equal), gte (greater than or equal), btw (between)           |
        |                    |          | - value: The value to compare against                                            |
        +--------------------+----------+-----------+----------------------------------------------------------------------+
        | masks              |   No     | A dictionary mapping mask strings to replacement strings used for                |
        |                    |          | replacing values in filters.                                                     |
        +--------------------+----------+-----------+----------------------------------------------------------------------+

        Save the downloaded files on the new destination.

    

        Example:

        ```yaml
        Sassie:
          domain: SASSIE_PROD_URL
          data: locations
          credentials:
            client_id: SASSIE_CLIENT_ID
            client_secret: SASSIE_CLIENT_SECRET
          filter:
            - column: updated
              operator: eq
              value: '{today}'
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
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        self.data = kwargs.get('data')
        # Apply masks to filter values if present
        if hasattr(self, 'filters') and hasattr(self, 'masks'):
            for filter_item in self.filters:
                filter_item['value'] = self.mask_replacement(filter_item['value'])

        self.processing_credentials()
        self.client_id: str = self.credentials.get('username', None)
        self.client_secret: str = self.credentials.get('password', None)
        await self.get_bearer_token()
        await super(Sassie, self).start(**kwargs)
        return True

    async def close(self):
        pass

    async def run(self):
        # Map data types to their corresponding methods
        data_methods = {
            'surveys': self.get_surveys,
            'questions': self.get_questions,
            'jobs': self.get_jobs,
            'waves': self.get_waves,
            'locations': self.get_locations,
            'clients': self.get_clients,
            'responses': self.get_responses,
            'question_sections': self.get_question_sections,
            'question_properties': self.get_question_properties,
            'custom': self.get_custom,
        }

        if self.data not in data_methods:
            raise ComponentError(f"{self.__name__}: Unsupported data type '{self.data}'. Supported types are: {', '.join(data_methods.keys())}")

        try:
            self._result = await self.create_dataframe(await data_methods[self.data]())
            if is_empty(self._result):
                raise DataNotFound(f"{self.__name__}: Data Not Found")
        except Exception as e:
            raise ComponentError(f"{self.__name__}: Error retrieving {self.data} data: {str(e)}")

        if self._debug:
            print(self._result)
            columns = list(self._result.columns)
            print(f"Debugging: {self.__name__} ===")
            for column in columns:
                t = self._result[column].dtype
                print(column, "->", t, "->", self._result[column].iloc[0])
        return self._result