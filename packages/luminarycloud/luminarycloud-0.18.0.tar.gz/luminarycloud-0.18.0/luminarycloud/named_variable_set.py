# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from datetime import datetime

from ._client import get_default_client
from ._helpers._timestamp_to_datetime import timestamp_to_datetime
from ._helpers.named_variables import _named_variables_from_proto, _named_variables_to_proto
from ._proto.api.v0.luminarycloud.named_variable_set import (
    named_variable_set_pb2 as namedvariablepb,
)
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .types import ProjectID, NamedVariableSetID, LcFloat


@ProtoWrapper(namedvariablepb.NamedVariableSet)
class NamedVariableSet(ProtoWrapperBase):
    """
    Represents a named variable set object.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Attributes
    ----------
    id : NamedVariableSetID
        Named variable set ID.
    project_id : ProjectID
        ID of the project containing this named variable set.
    name : str
        Name of the named variable set.
    create_time : datetime
        Time the named variable set was created.
    update_time : datetime
        Time the named variable set was last updated.
    version_id : str
        ID of the current (latest) version of the named variable set.

    Examples
    --------
    >>> named_variable_set = lc.get_named_variable_set(NamedVariableSetID("123"))
    >>> named_variable_set.name = "My Named Variable Set"
    >>> named_variable_set["x"] = 1.0
    >>> named_variable_set["custom_expression"] = "x + 1"
    >>> named_variable_set.save()
    """

    id: NamedVariableSetID
    "Named variable set ID."
    project_id: ProjectID
    "ID of the project containing this named variable set."

    _proto: namedvariablepb.NamedVariableSet
    _named_variables: dict[str, LcFloat] | None

    @property
    def name(self) -> str:
        """Name of the named variable set."""
        return self._proto.name

    @name.setter
    def name(self, value: str) -> None:
        self._proto.name = value

    @property
    def create_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.create_time)

    @property
    def update_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.update_time)

    @property
    def _version_id(self) -> str:
        return self._proto.version_id

    def save(self) -> None:
        """Save the named variable set."""
        req = namedvariablepb.UpdateNamedVariableSetRequest(
            id=self.id,
            name=self._proto.name,
            named_variables=_named_variables_to_proto(self._get_named_variables()),
        )
        res: namedvariablepb.UpdateNamedVariableSetResponse = (
            get_default_client().UpdateNamedVariableSet(req)
        )
        self._proto = res.named_variable_set
        self._named_variables = None

    def refresh(self) -> None:
        """Refresh the named variable set."""
        self._proto = get_named_variable_set(self.id)._proto
        self._named_variables = None

    def delete(self) -> None:
        """Delete the named variable set. This is irreversible."""
        req = namedvariablepb.DeleteNamedVariableSetRequest(id=self.id)
        get_default_client().DeleteNamedVariableSet(req)

    def __getitem__(self, key: str) -> LcFloat:
        return self._get_named_variables()[key]

    def __setitem__(self, key: str, value: LcFloat) -> None:
        self._get_named_variables()[key] = value

    def __delitem__(self, key: str) -> None:
        del self._get_named_variables()[key]

    def __contains__(self, key: str) -> bool:
        return key in self._get_named_variables()

    def __len__(self) -> int:
        return len(self._get_named_variables())

    def _get_named_variables(self) -> dict[str, LcFloat]:
        if getattr(self, "_named_variables", None) is None:
            named_variables_dict = dict(self._proto.named_variables)
            self._named_variables = _named_variables_from_proto(named_variables_dict)
        assert self._named_variables is not None
        return self._named_variables


def get_named_variable_set(id: NamedVariableSetID) -> NamedVariableSet:
    """
    Retrieve a specific named variable set by ID.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Parameters
    ----------
    id : str
        Named variable set ID.
    """
    req = namedvariablepb.GetNamedVariableSetRequest(id=id)
    res: namedvariablepb.GetNamedVariableSetResponse = get_default_client().GetNamedVariableSet(req)
    return NamedVariableSet(res.named_variable_set)
