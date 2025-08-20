import asyncio
from typing import Dict
from collections.abc import Callable
from pathlib import Path
import csv
import numpy as np
import pandas as pd
from ..exceptions import ComponentError, DataNotFound
from .flow import FlowComponent
from ..utils.constants import excel_based


class PandasToFile(FlowComponent):
    """
    PandasToFile

        Overview

            This component exports a pandas DataFrame to a file in CSV, Excel, or JSON format.

        .. table:: Properties
        :widths: auto


        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | Name                   | Required | Summary                                                                     |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | filename               |   Yes    | The name of the file to save the DataFrame to.                              |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | directory              |   No     | The directory where the file will be saved. If not specified,               |
        |                        |          | it will be derived from the filename.                                       |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | mime                   |   No     | The MIME type of the file. Supported types are "text/csv",                  |
        |                        |          | "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",        |
        |                        |          | "application/vnd.ms-excel", "application/json". Default is "text/csv".      |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | zerofill               |   No     | If True, fills NaN values with "0" in string columns. Default is False.     |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | quoting                |   No     | Specifies the quoting behavior for CSV files. Options are "all" (QUOTE_ALL),|
        |                        |          | "string" (QUOTE_NONNUMERIC), and None (QUOTE_NONE). Default is None.        |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        | pd_args                |   No     | Additional arguments for pandas' to_csv, to_excel, or to_json methods.      |
        |                        |          | Default is an empty dictionary.                                             |
        +------------------------+----------+-----------+-----------------------------------------------------------------+
        |  sep                   |   Yes    | Make a separation of the file name with this sign                           |
        +------------------------+----------+-----------+-----------------------------------------------------------------+

        Returns

        This component returns the filename of the saved file.

    

        Example:

        ```yaml
        PandasToFile:
          filename: /home/ubuntu/symbits/bose/files/report/troc_open_tickets_{today}.csv
          masks:
            '{today}':
            - today
            - mask: '%Y-%m-%d'
          mime: text/csv
          quoting: string
          pd_args:
            sep: ','
        ```

    """  # noqa
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        """Init Method."""
        self.zerofill: bool = False
        self.quoting = None
        self.params: Dict = {}
        self.args: Dict = {}
        self.filename: str = None
        self.directory: str = None
        self.mime: str = "text/csv"
        super(PandasToFile, self).__init__(
            loop=loop,
            job=job,
            stat=stat,
            **kwargs
        )
        if hasattr(self, "pd_args"):
            self.args = getattr(self, "pd_args", {})

    async def start(self, **kwargs):
        # Si lo que llega no es un DataFrame de Pandas se cancela la tarea
        if self.previous:
            self.data = self.input
        else:
            raise ComponentError("Data Not Found")
        if not isinstance(self.data, pd.DataFrame):
            raise ComponentError(
                'Incompatible Pandas Dataframe: hint> add "export_dataframe"\
                :true to tMap component'
            )
        if hasattr(self, "masks"):
            self.filename = self.mask_replacement(self.filename)
        # Create directory if not exists
        try:
            if not self.directory:
                self.directory = Path(self.filename).parents[0]
            self.directory.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            self._logger.error(
                f"Error creating directory {self.directory}: {err}"
            )
            raise ComponentError(
                f"Error creating directory {self.directory}: {err}"
            ) from err

    async def close(self):
        pass

    async def run(self):
        self._result = {}
        if self.zerofill:
            cols = self.data.select_dtypes(include=["object", "string"])
            self.data[cols.columns] = cols.fillna("0")
            # self.data.fillna('0', inplace=True)
            self.data.replace(np.nan, 0)
            intcols = self.data.select_dtypes(include=["Int64"])
            self.data[intcols.columns] = intcols.fillna(0)
        try:
            # filename, file_extension = os.path.splitext(self.filename)
            if self.mime == "text/csv" or self.mime == "text/plain":
                if self.quoting == "all":
                    quoting = csv.QUOTE_ALL
                elif self.quoting == "string":
                    quoting = csv.QUOTE_NONNUMERIC
                else:
                    quoting = csv.QUOTE_NONE
                #  if file_extension == '.csv':
                # Los parametros se deben colocar en un diccionario en el JSON
                # donde las llaves van a ser el nombre de los parametros que se
                # muestran en la siguiente dirección
                # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html
                if self.data.empty:
                    raise DataNotFound("PandasToFile: Cannot save an Empty Dataframe.")
                self._logger.debug(
                    f"PandasToFile: Export to CSV: {self.filename}"
                )
                self.data.to_csv(
                    self.filename,
                    index=False,
                    quoting=quoting,
                    quotechar='"',
                    escapechar="\\",
                    **self.args,
                )
            elif self.mime in excel_based:
                # elif file_extension == '.xlsx':
                # Los parametros se deben colocar en un diccionario en el JSON
                # donde las llaves van a ser el nombre de los parametros que se
                # muestran en la siguiente dirección
                # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html
                self._logger.debug(
                    f"PandasToFile: Export to EXCEL: {self.filename}"
                )
                self.data.to_excel(self.filename, index=False, **self.args)
            elif self.mime == "application/json":
                # elif file_extension == '.json':
                # Los parametros se deben colocar en un diccionario en el JSON
                # donde las llaves van a ser el nombre de los parametros que se
                # muestran en la siguiente dirección
                # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
                self._logger.debug(
                    f"PandasToFile: Export to JSON: {self.filename}"
                )
                self.data.to_json(self.filename, index=False, **self.args)
            else:
                raise ComponentError(
                    "Error: Only extension supported: csv, xlsx and json are supported"
                )
            # getting filename:
            self._result[self.filename] = True
            self.setTaskVar("FILENAME", self.filename)
            self.add_metric("FILENAME", self.filename)
            return self._result
        except Exception as err:
            raise ComponentError(f"Error in PandasToFile: {err}") from err
