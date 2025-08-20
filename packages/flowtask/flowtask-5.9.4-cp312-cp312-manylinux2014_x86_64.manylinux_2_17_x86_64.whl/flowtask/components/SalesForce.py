from navconfig.logging import logging
from querysource.exceptions import DataNotFound as QSNotFound
from ..exceptions import ComponentError, DataNotFound
from .QSBase import QSBase


class SalesForce(QSBase):
    """SalesForce Connector."""

    type = "report"
    _driver = "salesforce"

    async def report(self):
        try:
            return await self._qs.report()
        except QSNotFound as err:
            raise DataNotFound(f"SalesForce: Report Not Found: {err}") from err
        except Exception as err:
            logging.exception(err)
            raise ComponentError(f"SalesForce ERROR: {err!s}") from err
