import abc
from typing import TYPE_CHECKING, Optional, ClassVar, List

if TYPE_CHECKING:
    from istari_digital_client.api.client_api import ClientApi


class ClientHaving(abc.ABC):
    """
    Mixin for models that require access to a `ClientApi` instance.

    This class provides a `client` property and ensures that the same client is
    propagated to any nested attributes listed in ``__client_fields__``. It is
    typically used in combination with other mixins that perform API operations.
    """

    _client: Optional["ClientApi"] = None
    __client_fields__: ClassVar[List[str]] = []

    @property
    def client(self) -> Optional["ClientApi"]:
        """
        Get the client instance associated with this object.

        The client is typically used to make SDK API calls.
        """

        return self._client

    @client.setter
    def client(self, value: "ClientApi"):
        """
        Set the client instance for this object and propagate it to any nested fields.

        Fields listed in ``__client_fields__`` will also have their ``client`` attribute
        set if applicable (e.g., for nested models or lists of models).

        :param value: The `ClientApi` instance to assign.
        :type value: ClientApi
        """

        self._client = value

        for name in self.__client_fields__:
            attr = getattr(self, name, None)

            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, 'client'):
                        item.client = value
            elif attr is not None and hasattr(attr, 'client'):
                attr.client = value
