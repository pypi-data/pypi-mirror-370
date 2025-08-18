import requests
from sempy.fabric.exceptions import FabricHTTPException
import typing as t


class TaggedValue:
    """
    A value along with its ETag, used to support optimistic concurrency control.

    Attributes
    ----------
    value : dict
        The data associated with this TaggedValue.
    etag : str
        The ETag associated with this value.
    """

    value: t.Dict[str, t.Any]
    etag: str

    def __init__(self, value: t.Dict[str, t.Any], etag: str):
        """
        Initialize a TaggedValue instance.

        Parameters
        ----------
        value : dict
            The data to be stored.
        etag : str
            The ETag associated with the value.
        """
        self.value = value
        self.etag = etag

    def __str__(self):
        """
        Return a string representation of the TaggedValue.

        Returns
        -------
        str
            The string representation including the value and ETag.
        """
        return f"{self.value} (ETag: {self.etag})"

    def __repr__(self):
        """
        Return the official string representation of the TaggedValue.

        Returns
        -------
        str
            The string representation suitable for debugging.
        """
        return f"TaggedValue(value={self.value}, etag={self.etag})"

    @staticmethod
    def from_response(response: requests.Response) -> "TaggedValue":
        """
        Create a TaggedValue instance from an HTTP response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response containing the data and ETag.

        Returns
        -------
        TaggedValue
            An instance of TaggedValue with data and ETag extracted from the response.

        Raises
        ------
        FabricHTTPException
            If the response status code is not 200.
        """
        if response.status_code != 200:
            raise FabricHTTPException(response)

        return TaggedValue(response.json(), response.headers.get("ETag", ""))
