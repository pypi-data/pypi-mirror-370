from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from typing import Any, Dict, Optional, Set
from typing_extensions import Self

from istari_digital_client.models.comment import Comment
from istari_digital_client.models.pageable import Pageable
from istari_digital_client.models.client_having import ClientHaving


class PageComment(Pageable[Comment], ClientHaving):
    """
    A paginated response object for listing comments.

    This class represents a single page of :class:`Comment` results returned from the API.
    It includes pagination metadata such as page size, page number, and total result count,
    along with the list of comments retrieved in the current page.
    """
    def to_str(self) -> str:
        """
        Return the string representation of the model using field aliases.

        This method serializes the model to a JSON-formatted string, respecting any defined aliases
        for fields instead of their original attribute names.
        """
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """
        Return the JSON string representation of the model using field aliases.

        This method serializes the model into a JSON-formatted string, using aliases for field names
        where defined instead of their raw attribute names.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """
        Create an instance of the model from a JSON string.

        This method deserializes the given JSON string into a model instance. It expects the
        string to match the model's schema, using field aliases where applicable.

        :param json_str: JSON string representing the model.
        :type json_str: str
        """
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """
        Return the dictionary representation of the model using field aliases.

        This method differs from calling `self.model_dump(by_alias=True)` in the following way:

        - Fields with a value of `None` are included in the output only if they are nullable and
          were explicitly set during model initialization. All other `None` fields are omitted.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in items (list)
        _items = []
        if self.items:
            for _item_items in self.items:
                if _item_items:
                    _items.append(_item_items.to_dict())
            _dict['items'] = _items
        # set to None if total (nullable) is None
        # and model_fields_set contains the field
        if self.total is None and "total" in self.model_fields_set:
            _dict['total'] = None

        # set to None if page (nullable) is None
        # and model_fields_set contains the field
        if self.page is None and "page" in self.model_fields_set:
            _dict['page'] = None

        # set to None if size (nullable) is None
        # and model_fields_set contains the field
        if self.size is None and "size" in self.model_fields_set:
            _dict['size'] = None

        # set to None if pages (nullable) is None
        # and model_fields_set contains the field
        if self.pages is None and "pages" in self.model_fields_set:
            _dict['pages'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """
        Create an instance of the model from a dictionary.

        This method deserializes a dictionary into a model instance. The input should use
        field aliases where applicable.

        :param obj: Dictionary representing the model.
        :type obj: Optional[Dict[str, Any]]
        """
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "items": [Comment.from_dict(_item) for _item in obj["items"]] if obj.get("items") is not None else None,
            "total": obj.get("total"),
            "page": obj.get("page"),
            "size": obj.get("size"),
            "pages": obj.get("pages")
        })
        return _obj
