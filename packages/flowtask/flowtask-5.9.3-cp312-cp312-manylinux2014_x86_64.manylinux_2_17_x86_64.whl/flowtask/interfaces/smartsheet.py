"""
SmartSheet.

Making operations over an Smartsheet Service.

"""
import random
from functools import partial
from pathlib import Path
import ssl
import aiofiles
import aiohttp
from ..exceptions import (
    ComponentError,
    ConfigError,
    FileNotFound
)
from .credentials import CredentialsInterface
from ..interfaces.http import ua


class SmartSheetClient(CredentialsInterface):
    _credentials: dict = {"token": str, "scheme": str}

    def __init__(self, *args, **kwargs):
        self.file_format: str = "application/vnd.ms-excel"
        self.url: str = "https://api.smartsheet.com/2.0/sheets/"
        self.create_destination: bool = True  # by default
        self.file_id: str = kwargs.pop('file_id', None)
        api_key = self.get_env_value("SMARTSHEET_API_KEY")
        self.api_key: str = kwargs.pop('api_key', api_key)
        kwargs['no_host'] = True
        super().__init__(*args, **kwargs)
        if not self.api_key:
            raise ComponentError(
                f"SmartSheet: Invalid API Key name {self.api_key}"
            )
        self.ssl_certs = kwargs.get('ssl_certs', [])
        self.ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.ssl_ctx.options &= ~ssl.OP_NO_SSLv3
        self.ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE
        if self.ssl_certs:
            self.ssl_ctx.load_cert_chain(*self.ssl_certs)

    async def http_get(
        self,
        url: str = None,
        credentials: dict = None,
        headers: dict = {},
        accept: str = 'application/vnd.ms-excel',
        destination: Path = None
    ):
        """
        session.
            connect to an http source using aiohttp
        """
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        if url is None:
            url = self.url
        # TODO: Auth, Data, etc
        auth = {}
        params = {}
        headers = {
            "Accept": accept,
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(ua),
            **headers,
        }
        if credentials:
            if "username" in credentials:  # basic Authentication
                auth = aiohttp.BasicAuth(
                    credentials["username"], credentials["password"]
                )
                params = {"auth": auth}
            elif "token" in credentials:
                headers["Authorization"] = "{scheme} {token}".format(
                    scheme=credentials["scheme"], token=credentials["token"]
                )
        async with aiohttp.ClientSession(**params) as session:
            meth = getattr(session, 'get')
            ssl = {"ssl": self.ssl_ctx, "verify_ssl": True}
            fn = partial(
                meth,
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                **ssl,
            )
            try:
                async with fn() as response:
                    if response.status in (200, 201, 202):
                        return await self.http_response(response, destination)
                    else:
                        print("ERROR RESPONSE >> ", response)
                        raise ComponentError(
                            f"Smartsheet: Error getting data from URL {response}"
                        )
            except Exception as err:
                raise ComponentError(
                    f"Smartsheet: Error Making an SSL Connection to ({self.url}): {err}"
                ) from err
            except aiohttp.exceptions.HTTPError as err:
                raise ComponentError(
                    f"Smartsheet: SSL Certificate Error: {err}"
                ) from err

    async def http_response(self, response, destination: str):
        # getting aiohttp response:
        if response.status == 200:
            try:
                async with aiofiles.open(str(destination), mode="wb") as fp:
                    await fp.write(await response.read())
                if destination.exists():
                    return response
                else:
                    raise FileNotFound(
                        f"Error saving File {destination!s}"
                    )
            except FileNotFound:
                raise
            except Exception as err:
                raise FileNotFound(
                    f"Error saving File {err!s}"
                )
        else:
            raise ComponentError(
                f"DownloadFromSmartSheet: Wrong response from Smartsheet: {response!s}"
            )

    async def download_file(self, file_id: str = None, destination: Path = None):
        if isinstance(destination, str):
            destination = Path(destination)
        if not file_id:
            file_id = self.file_id
        if not file_id:
            raise ConfigError(
                "SmartSheet: Unable to Download without FileId."
            )
        credentials = {"token": self.api_key, "scheme": "Bearer"}
        url = f"{self.url}{file_id}"
        if not destination:
            destination = self.filename
        if await self.http_get(
            url=url,
            credentials=credentials,
            destination=destination
        ):
            return True
