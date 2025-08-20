from typing import Generic
from maleo.soma.mixins.parameter import (
    IdentifierTypeT,
    IdentifierValueT,
    IdentifierTypeValue,
    ListOfDataStatuses,
    StatusUpdateAction,
    UseCache,
)


class ReadSingleQueryParameterSchema(
    UseCache,
    ListOfDataStatuses,
):
    pass


class ReadSingleParameterSchema(
    ReadSingleQueryParameterSchema,
    IdentifierTypeValue[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class StatusUpdateQueryParameterSchema(StatusUpdateAction):
    pass
