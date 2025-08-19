from datetime import date, datetime
from typing import Any, Dict, Literal, List, Mapping, Optional, Sequence, Union
from uuid import UUID
from maleo.soma.enums.pagination import Limit
from maleo.soma.enums.status import DataStatus


# Any-related types
ListOfAny = List[Any]
SequenceOfAny = Sequence[Any]
OptionalAny = Optional[Any]

# Boolean-related types
LiteralFalse = Literal[False]
LiteralTrue = Literal[True]
ListOfBools = List[bool]
SequenceOfBools = Sequence[bool]
OptionalBoolean = Optional[bool]

# Float-related types
ListOfFloats = List[float]
SequenceOfFloats = Sequence[float]
OptionalFloat = Optional[float]
OptionalListOfFloats = Optional[List[float]]
OptionalSequenceOfFloats = Optional[Sequence[float]]

# Integer-related types
ListOfIntegers = List[int]
SequenceOfIntegers = Sequence[int]
OptionalInteger = Optional[int]
OptionalListOfIntegers = Optional[List[int]]
OptionalSequenceOfIntegers = Optional[Sequence[int]]


# Bytes-related types
OptionalBytes = Optional[bytes]

# String-related types
ListOfStrings = List[str]
SequenceOfStrings = Sequence[str]
OptionalString = Optional[str]
OptionalListOfStrings = Optional[List[str]]
OptionalSequenceOfStrings = Optional[Sequence[str]]

# Date-related types
OptionalDate = Optional[date]

# Datetime-related types
OptionalDatetime = Optional[datetime]

# Any Dict-related types
StringToAnyDict = Dict[str, Any]
OptionalStringToAnyDict = Optional[Dict[str, Any]]
ListOfStringToAnyDict = List[Dict[str, Any]]
SequenceOfStringToAnyDict = Sequence[Dict[str, Any]]
OptionalListOfStringToAnyDict = Optional[List[Dict[str, Any]]]
OptionalSequenceOfStringToAnyDict = Optional[Sequence[Dict[str, Any]]]
StringToObjectDict = Dict[str, object]
OptionalStringToObjectDict = Optional[Dict[str, object]]
ListOfStringToObjectDict = List[Dict[str, object]]
SequenceOfStringToObjectDict = Sequence[Dict[str, object]]
OptionalListOfStringToObjectDict = Optional[List[Dict[str, object]]]
OptionalSequenceOfStringToObjectDict = Optional[Sequence[Dict[str, object]]]
IntToAnyDict = Dict[int, Any]
OptionalIntToAnyDict = Optional[Dict[int, Any]]
ListOfIntToAnyDict = List[Dict[int, Any]]
SequenceOfIntToAnyDict = Sequence[Dict[int, Any]]
OptionalListOfIntToAnyDict = Optional[List[Dict[int, Any]]]
OptionalSequenceOfIntToAnyDict = Optional[Sequence[Dict[int, Any]]]

# Any Mapping-related types
StringToAnyMapping = Mapping[str, Any]
OptionalStringToAnyMapping = Optional[Mapping[str, Any]]
ListOfStringToAnyMapping = List[Mapping[str, Any]]
SequenceOfStringToAnyMapping = Sequence[Mapping[str, Any]]
OptionalListOfStringToAnyMapping = Optional[List[Mapping[str, Any]]]
OptionalSequenceOfStringToAnyMapping = Optional[Sequence[Mapping[str, Any]]]
StringToObjectMapping = Mapping[str, object]
OptionalStringToObjectMapping = Optional[Mapping[str, object]]
ListOfStringToObjectMapping = List[Mapping[str, object]]
SequenceOfStringToObjectMapping = Sequence[Mapping[str, object]]
OptionalListOfStringToObjectMapping = Optional[List[Mapping[str, object]]]
OptionalSequenceOfStringToObjectMapping = Optional[Sequence[Mapping[str, object]]]
IntToAnyMapping = Mapping[int, Any]
OptionalIntToAnyMapping = Optional[Mapping[int, Any]]
ListOfIntToAnyMapping = List[Mapping[int, Any]]
SequenceOfIntToAnyMapping = Sequence[Mapping[int, Any]]
OptionalListOfIntToAnyMapping = Optional[List[Mapping[int, Any]]]
OptionalSequenceOfIntToAnyMapping = Optional[Sequence[Mapping[int, Any]]]

# String Dict-related types
StringToStringDict = Dict[str, str]
OptionalStringToStringDict = Optional[Dict[str, str]]
ListOfStringToStringDict = List[Dict[str, str]]
SequenceOfStringToStringDict = Sequence[Dict[str, str]]
OptionalListOfStringToStringDict = Optional[List[Dict[str, str]]]
OptionalSequenceOfStringToStringDict = Optional[Sequence[Dict[str, str]]]
IntToStringDict = Dict[int, str]
OptionalIntToStringDict = Optional[Dict[int, str]]
ListOfIntToStringDict = List[Dict[int, str]]
SequenceOfIntToStringDict = Sequence[Dict[int, str]]
OptionalListOfIntToStringDict = Optional[List[Dict[int, str]]]
OptionalSequenceOfIntToStringDict = Optional[Sequence[Dict[int, str]]]

# String Mapping-related types
StringToStringMapping = Mapping[str, str]
OptionalStringToStringMapping = Optional[Mapping[str, str]]
ListOfStringToStringMapping = List[Mapping[str, str]]
SequenceOfStringToStringMapping = Sequence[Mapping[str, str]]
OptionalListOfStringToStringMapping = Optional[List[Mapping[str, str]]]
OptionalSequenceOfStringToStringMapping = Optional[Sequence[Mapping[str, str]]]
IntToStringMapping = Mapping[int, str]
OptionalIntToStringMapping = Optional[Mapping[int, str]]
ListOfIntToStringMapping = List[Mapping[int, str]]
SequenceOfIntToStringMapping = Sequence[Mapping[int, str]]
OptionalListOfIntToStringMapping = Optional[List[Mapping[int, str]]]
OptionalSequenceOfIntToStringMapping = Optional[Sequence[Mapping[int, str]]]

# List Dict-related types
StringToListOfStringDict = Dict[str, List[str]]
StringToSequenceOfStringDict = Dict[str, Sequence[str]]
OptionalStringToListOfStringDict = Optional[Dict[str, List[str]]]
OptionalStringToSequenceOfStringDict = Optional[Dict[str, Sequence[str]]]

# List Mapping-related types
StringToListOfStringMapping = Mapping[str, List[str]]
StringToSequenceOfStringMapping = Mapping[str, Sequence[str]]
OptionalStringToListOfStringMapping = Optional[Mapping[str, List[str]]]
OptionalStringToSequenceOfStringMapping = Optional[Mapping[str, Sequence[str]]]

# UUID-related types
ListOfUUIDs = List[UUID]
SequenceOfUUIDs = Sequence[UUID]
OptionalUUID = Optional[UUID]
OptionalListOfUUIDs = Optional[List[UUID]]
OptionalSequenceOfUUIDs = Optional[Sequence[UUID]]

# DataStatuses-related types
ListOfDataStatuses = List[DataStatus]
SequenceOfDataStatuses = Sequence[DataStatus]
OptionalListOfDataStatuses = Optional[List[DataStatus]]
OptionalSequenceOfDataStatuses = Optional[Sequence[DataStatus]]

# Limit-related types
OptionalLimit = Limit

# Miscellanous types
BytesOrString = Union[bytes, str]
OptionalBytesOrString = Optional[BytesOrString]
IdentifierValue = Union[int, UUID, str]
ListOrDictOfAny = Union[List[Any], Dict[str, Any]]
SequenceOrDictOfAny = Union[Sequence[Any], Dict[str, Any]]
ListOrMappingOfAny = Union[List[Any], Mapping[str, Any]]
SequenceOrMappingOfAny = Union[Sequence[Any], Mapping[str, Any]]
OptionalListOrDictOfAny = Optional[Union[List[Any], Dict[str, Any]]]
OptionalSequenceOrDictOfAny = Optional[Union[Sequence[Any], Dict[str, Any]]]
OptionalListOrMappingOfAny = Optional[Union[List[Any], Mapping[str, Any]]]
OptionalSequenceOrMappingOfAny = Optional[Union[Sequence[Any], Mapping[str, Any]]]
