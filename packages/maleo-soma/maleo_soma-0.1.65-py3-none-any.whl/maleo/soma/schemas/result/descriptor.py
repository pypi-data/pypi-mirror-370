from maleo.soma.enums.code import Result as ResultCode
from maleo.soma.mixins.general import Descriptor


class ResultDescriptorSchema(Descriptor[ResultCode]):
    pass


class AnyDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.ANY_DATA
    message: str = "Any data result"
    description: str = "Result with Any Data"


class NoDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.NO_DATA
    message: str = "No data result"
    description: str = "Result with No Data"


class SingleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.SINGLE_DATA
    message: str = "Single data result"
    description: str = "Result with Single Data"


class CreateSingleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.CREATE_SINGLE_DATA
    message: str = "Create single data result"
    description: str = "Create result with Single Data"


class UpdateSingleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.UPDATE_SINGLE_DATA
    message: str = "Update single data result"
    description: str = "Update result with Single Data"


class OptionalSingleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.OPTIONAL_SINGLE_DATA
    message: str = "Optional single data result"
    description: str = "Result with Optional Single Data"


class ReadSingleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.READ_SINGLE_DATA
    message: str = "Read single data result"
    description: str = "Read result with Single Data"


class DeleteSingleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.DELETE_SINGLE_DATA
    message: str = "Delete single data result"
    description: str = "Delete result with Single Data"


class MultipleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.MULTIPLE_DATA
    message: str = "Multiple data result"
    description: str = "Result with Multiple Data"


class CreateMultipleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.CREATE_MULTIPLE_DATA
    message: str = "Create multiple data result"
    description: str = "Create result with Multiple Data"


class UpdateMultipleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.UPDATE_MULTIPLE_DATA
    message: str = "Update multiple data result"
    description: str = "Update result with Multiple Data"


class OptionalMultipleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.OPTIONAL_MULTIPLE_DATA
    message: str = "Optional multiple data result"
    description: str = "Result with Optional Multiple Data"


class ReadMultipleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.READ_MULTIPLE_DATA
    message: str = "Read multiple data result"
    description: str = "Read result with Multiple Data"


class DeleteMultipleDataResultDescriptorSchema(ResultDescriptorSchema):
    code: ResultCode = ResultCode.DELETE_MULTIPLE_DATA
    message: str = "Delete multiple data result"
    description: str = "Delete result with Multiple Data"
