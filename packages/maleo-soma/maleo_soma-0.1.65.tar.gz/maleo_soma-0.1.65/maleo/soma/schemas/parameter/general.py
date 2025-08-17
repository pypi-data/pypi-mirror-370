from typing import Generic
from maleo.soma.mixins.parameter import (
    IdentifierTypeT,
    IdentifierValueT,
    IdentifierTypeValue,
    OptionalListOfDataStatuses,
    UseCache,
)


class ReadSingleQueryParameterSchema(
    UseCache,
    OptionalListOfDataStatuses,
):
    pass


class ReadSingleParameterSchema(
    ReadSingleQueryParameterSchema,
    IdentifierTypeValue[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass
