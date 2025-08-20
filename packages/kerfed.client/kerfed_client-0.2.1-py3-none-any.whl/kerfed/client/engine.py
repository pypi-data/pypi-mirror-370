"""
# kerfed.client.engine

Call the Kerfed Engine on geometry requests.
"""

import dataclasses
import hashlib
import logging
from base64 import b64encode
from typing import Optional

import httpx
from authlib.integrations.httpx_client import OAuth2Client

from .models import GeometryRequest

logger = logging.getLogger(__name__)


class EngineClient:
    """
    Client to connect to Kerfed Engine.
    """

    _api_url: str = "https://engine.kerfed.com/api"

    def __init__(self, api_key: str):
        """
        Parameters
        -----------
        api_key
          An API key used to authorize use of the remote API.
        """

        self.api_key = api_key

    @property
    def authorized(self) -> OAuth2Client:
        """
        Return a client authorized to make requests from the remote
        API server.

        Returns
        --------
        client
          Has a request-style api: i.e. `authorized.get(url, ...)`
        """
        if not hasattr(self, "_authorized"):
            # API keys should be packed (header, client_id, client_secret)
            # which can be used with the `client_credentials` oauth2 flow
            key = self.api_key.strip().split("_")
            if len(key) != 3:
                raise ValueError("invalid API key!")

            # unpack the API key into the `client_credentials` values
            _header, client_id, client_secret = key

            # this client will be authorized to make requests
            self._authorized = OAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                token_endpoint=f"{self._api_url}/auth/token",
                raise_for_status=True,
            )

            # fetch the authorization token which will be stored automatically
            fetched = self._authorized.fetch_token()
            if "access_token" not in fetched:
                # if the token is not in the response raise here to avoid
                # harder to debug errors later
                raise ValueError(f"Unable to get authorization token: `{fetched}`")

        return self._authorized

    def geometry_start(
        self, request: GeometryRequest, upload: Optional[bool] = None
    ) -> str:
        """
        Start a geometry analysis request.

        Parameters
        -----------
        request
          A populated message.
        upload
          Upload large data files automatically rather than
          transferring them as a large Base64 JSON field.

        Returns
        ------------
        task_id
          The identifier for the ongoing analysis task.
        """
        if isinstance(request, dict):
            # will validate the fields when passed a dict
            # and will fail immediately client-side
            request = GeometryRequest(**request)
        elif not isinstance(request, GeometryRequest):
            raise TypeError(f"`{type(request)}` != `GeometryRequest`!")

        if request.source is None:
            raise ValueError("request must include a source model!")

        if request.source.data is not None:
            if upload is None:
                # if the user doesn't care about upload set it
                # based on the size of the source file
                upload = len(request.source.data) > 1e6

            if upload and len(request.source.data) > 0:
                # if the request has data in-line in message upload it
                # rather than POST with a giant base64 blob
                dest = self.upload_url(file_name=request.source.name)

                logger.debug("uploading `request.source.data` to signed URL")

                # do the upload to the cloud bucket
                up = self.authorized.put(dest["upload_url"], content=request.source.data)
                up.raise_for_status()

                # replace the in-line data with a reference to the copy in a bucket
                request.source.file_id = dest["file_id"]
                # add a hash to the file request
                request.source.sha256 = hashlib.sha256(request.source.data).hexdigest()
                request.source.data = b""
            elif len(request.source.data) > 0:
                # add a hash to the file request
                request.source.sha256 = hashlib.sha256(request.source.data).hexdigest()

        # create the analysis request
        create = self.authorized.post(
            f"{self._api_url}/v2/geometry", json=serialize(request)
        )
        create.raise_for_status()

        return create.json()["task_id"]

    def geometry_result(self, task_id: str, timeout: float = 90.0) -> dict:
        """
        Get the result for a geometry analysis result.

        Parameters
        ----------
        task_id
          The task identifier to retrieve.
        timeout
          How long to wait in seconds before raising an `httpx.ReadTimeout`
          if you want to not wait if it isn't done set this to zero
          or a negative number. Note that this is only for the *read*, and
          if the analysis times out on the GPU backend you need to increase
          the value in `GeometryRequest.time_out`.

        Returns
        ----------
        response
          The analysis of the geometry response.

        Raises
        ------------
        httpx.ReadTimeout
          If the requested client-side timeout is exceeded.
        """

        # configure maximum iterations from the passed timeout
        long_poll = 5
        max_iter = int(timeout / long_poll) + 1

        # block until the request is done
        # you can also set the timeout to zero or None
        for _ in range(max_iter):
            try:
                response = self.authorized.get(
                    url=f"{self._api_url}/v2/geometry/{task_id}",
                    headers={"Request-Timeout": f"{int(timeout)}"},
                    timeout=httpx.Timeout(long_poll, read=long_poll),
                )
            except httpx.ReadTimeout:
                # long poll cycle exceeded
                continue

            if response.status_code == 200:
                # if the status code is 200 it means we have
                # been returned a GeometryResponse in JSON format
                return response.json()

            elif response.status_code == 202:
                # A response code of 202 means the request is still in
                # progress, so just log the result and continue.
                logger.debug(response.json())
            else:
                # This is an abnormal status, so print the contents.
                logger.warning(response.text)

            # if there was a failure response raise here
            response.raise_for_status()

        raise httpx.ReadTimeout("Requested timeout exceeded")

    def upload_url(self, file_name: str) -> dict:
        """
        Generate a signed URL which can be used to upload the file.
        """
        logger.debug(f"Upload call: {self._api_url}/upload")

        response = self.authorized.post(
            f"{self._api_url}/v2/upload", json={"file_name": file_name}
        )
        response.raise_for_status()

        logger.debug(response.json())
        return response.json()


def serialize(item) -> dict:
    """
    Serialize a message object to a dictionary.

    Parameters
    ----------
    item
      A dataclass model.

    Returns
    ---------
    serialized
      A JSON serializable dict.
    """

    def clean(i):
        if isinstance(i, dict):
            # convert all values filtering out null and empty
            return {
                k: v
                for k, v in {k: clean(v) for k, v in i.items()}.items()
                if v not in (None, "", b"")
            }

        elif isinstance(i, bytes):
            return b64encode(i).decode("utf-8")
        else:
            return i

    return clean(dataclasses.asdict(item))  # type: ignore


def deserialize(item: dict, model: type):
    if not dataclasses.is_dataclass(model):
        raise TypeError(model)

    lookup = {field.name: field.type for field in dataclasses.fields(model)}

    kwargs = {}
    for field_name, value in item.items():
        try:
            # recursively deserialize nested dataclasses
            kwargs[field_name] = deserialize(value, lookup[field_name])  # type: ignore
        except (TypeError, KeyError):
            # break from the recursion
            kwargs[field_name] = value

    return model(**kwargs)
