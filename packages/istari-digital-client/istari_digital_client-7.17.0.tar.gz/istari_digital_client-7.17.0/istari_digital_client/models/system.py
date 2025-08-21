from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Set, Union
from typing_extensions import Self

from istari_digital_client.models.system_configuration import SystemConfiguration
from istari_digital_client.models.page_snapshot_revision_search_item import PageSnapshotRevisionSearchItem
from istari_digital_client.models.snapshot import Snapshot
from istari_digital_client.models.snapshot_tag import SnapshotTag
from istari_digital_client.models.shareable import Shareable
from istari_digital_client.models.archivable import Archivable
from istari_digital_client.models.client_having import ClientHaving
from istari_digital_client.log_utils import log_method


class System(BaseModel, ClientHaving, Shareable, Archivable):
    """
    Represents a System object that aggregates configuration, versioning, and file content
    across Snapshots. Systems can be shared, archived, and queried for associated files
    or metadata based on Snapshots or SnapshotTags.

    This model includes methods to fetch file revisions, resolve configuration baselines,
    and load structured file contents (e.g., JSON files) associated with snapshots.
    """
    id: StrictStr
    created: datetime
    created_by_id: StrictStr
    name: StrictStr
    description: StrictStr
    archive_status: StrictStr
    configurations: Optional[List[SystemConfiguration]] = None
    baseline_tagged_snapshot_id: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["id", "created", "created_by_id", "name", "description", "archive_status", "configurations", "baseline_tagged_snapshot_id"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @log_method
    def list_file_revisions_by_snapshot(
            self,
            snapshot: Optional[Union[Snapshot | str]] = None,
            page: Optional[int] = None,
            size: Optional[int] = None,
            name: Optional[List[str]] = None,
            extension: Optional[List[str]] = None,
            sort: Optional[str] = None,
    ) -> PageSnapshotRevisionSearchItem:
        """
        Retrieve a paginated list of file revisions associated with a given snapshot.

        If no snapshot is specified, the system's baseline snapshot will be used.

        :param snapshot: Snapshot object or ID string to fetch revisions for.
        :param page: Page number for pagination.
        :param size: Page size for pagination.
        :param name: Optional list of file names to filter the results.
        :param extension: Optional list of file extensions to filter results (e.g., [".json"]).
        :param sort: Optional sort order, e.g., "name", "created", etc.

        :raises ValueError: If no snapshot is provided and a baseline snapshot cannot be resolved.
        """

        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        if snapshot is None:
            snapshot_id = self.baseline_tagged_snapshot_id or self.client.get_system_baseline(system_id=self.id).snapshot_id
            if snapshot_id is None:
                raise ValueError("No snapshot provided and no baseline snapshot exists.")
        elif isinstance(snapshot, Snapshot):
            snapshot_id = snapshot.id
        elif isinstance(snapshot, str):
            snapshot_id = snapshot
        else:
            raise ValueError("Invalid type for snapshot. Must be Snapshot, str, or None.")

        return self.client.list_snapshot_revisions(
            snapshot_id=snapshot_id,
            page=page,
            size=size,
            name=name,
            extension=extension,
            sort=sort,
        )

    @log_method
    def list_file_revisions_by_snapshot_tag(
        self,
        snapshot_tag: SnapshotTag,
        page: Optional[int] = None,
        size: Optional[int] = None,
        name: Optional[List[str]] = None,
        extension: Optional[List[str]] = None,
        sort: Optional[str] = None,
    ) -> PageSnapshotRevisionSearchItem:
        """
        Retrieve a paginated list of file revisions using a SnapshotTag.

        This uses the tag to resolve a snapshot ID and delegates to
        ``list_file_revisions_by_snapshot``.

        :param snapshot_tag: A snapshot tag containing a valid snapshot ID.
        :param page: Page number for pagination.
        :param size: Page size for pagination.
        :param name: Optional list of file names to filter the results.
        :param extension: Optional list of file extensions to filter results.
        :param sort: Optional sorting criteria.
        """
        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        return self.list_file_revisions_by_snapshot(
            snapshot=snapshot_tag.snapshot_id,
            page=page,
            size=size,
            name=name,
            extension=extension,
            sort=sort
        )

    @log_method
    def get_json_file_contents_by_snapshot(self, snapshot: Optional[Union[Snapshot]] = None) -> Dict[str, Any]:
        """
        Load contents of all JSON files for a given snapshot.

        If no snapshot is specified, the baseline-tagged snapshot will be resolved and used.

        This returns a dictionary keyed by file name, with the parsed JSON as values.
        Metadata about the system and snapshot is included under the "metadata" key.

        :param snapshot: Optional Snapshot object. If None, resolves the system baseline.
        :raises ValueError: If no snapshot can be resolved or the client is not set.
        """
        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        if snapshot is None:
            baseline_snapshot_id = self.baseline_tagged_snapshot_id or self.client.get_system_baseline(system_id=self.id).snapshot_id
            if baseline_snapshot_id is None:
                raise ValueError("No snapshot provided and no baseline snapshot exists.")
            snapshot = self.client.get_snapshot(snapshot_id=baseline_snapshot_id)

        result: Dict[str, Any] = {"metadata": {
            "system_name": self.name,
            "system_id": self.id,
            "system_snapshot_id": snapshot.id,
            "system_snapshot_created": snapshot.created.isoformat(),
        }}

        snapshot_revision_items = self.list_file_revisions_by_snapshot(
            snapshot=snapshot,
            size=100,
            extension=[".json"]
        )

        for revision_item in snapshot_revision_items:
            if revision_item.name:
                result[revision_item.name] = revision_item.read_json()

        return result

    @log_method
    def get_json_file_contents_by_snapshot_tag(self, snapshot_tag: SnapshotTag) -> Dict[str, Any]:
        """
        Load contents of all JSON files using a snapshot tag reference.

        Internally resolves the snapshot from the tag and delegates to
        ``get_json_file_contents_by_snapshot``.

        :param snapshot_tag: A snapshot tag referencing the desired snapshot.
        :raises ValueError: If the client is not set.
        """

        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        snapshot = self.client.get_snapshot(snapshot_id=snapshot_tag.snapshot_id)

        return self.get_json_file_contents_by_snapshot(snapshot=snapshot)

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
        # override the default output from pydantic by calling `to_dict()` of each item in configurations (list)
        _items = []
        if self.configurations:
            for _item_configurations in self.configurations:
                if _item_configurations:
                    _items.append(_item_configurations.to_dict())
            _dict['configurations'] = _items
        # set to None if baseline_tagged_snapshot_id (nullable) is None
        # and model_fields_set contains the field
        if self.baseline_tagged_snapshot_id is None and "baseline_tagged_snapshot_id" in self.model_fields_set:
            _dict['baseline_tagged_snapshot_id'] = None

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
            "id": obj.get("id"),
            "created": obj.get("created"),
            "created_by_id": obj.get("created_by_id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "archive_status": obj.get("archive_status"),
            "configurations": [SystemConfiguration.from_dict(_item) for _item in obj["configurations"]] if obj.get("configurations") is not None else None,
            "baseline_tagged_snapshot_id": obj.get("baseline_tagged_snapshot_id")
        })
        return _obj
