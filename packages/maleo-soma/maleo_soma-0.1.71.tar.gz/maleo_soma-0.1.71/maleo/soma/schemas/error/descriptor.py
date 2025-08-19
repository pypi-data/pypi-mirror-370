from maleo.soma.enums.code import Error as ErrorCode
from maleo.soma.mixins.general import Descriptor


class ErrorDescriptorSchema(Descriptor[ErrorCode]):
    pass


class BadRequestErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.BAD_REQUEST
    message: str = "Bad Request"
    description: str = "Bad/Unexpected parameters given."


class UnauthorizedErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.UNAUTHORIZED
    message: str = "Unauthorized"
    description: str = "Authentication is required or invalid."


class ForbiddenErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.FORBIDDEN
    message: str = "Forbidden"
    description: str = "Insufficient permission found."


class NotFoundErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.NOT_FOUND
    message: str = "Not Found"
    description: str = "The requested resource could not be found."


class MethodNotAllowedErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.METHOD_NOT_ALLOWED
    message: str = "Method Not Allowed"
    description: str = "The HTTP method is not supported for this resource."


class ConflictErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.CONFLICT
    message: str = "Conflict"
    description: str = "Failed processing request due to conflicting state."


class UnprocessableEntityErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.UNPROCESSABLE_ENTITY
    message: str = "Unprocessable Entity"
    description: str = "The request was well-formed but could not be processed."


class TooManyRequestsErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.TOO_MANY_REQUESTS
    message: str = "Too Many Requests"
    description: str = "You have sent too many requests in a given time frame."


class InternalServerErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "Internal Server Error"
    description: str = "An unexpected error occurred on the server."


class DatabaseErrorDescriptorSchema(InternalServerErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.DATABASE_ERROR
    message: str = "Database Error"
    description: str = "An error occurred while accessing the database."


class NotImplementedErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.NOT_IMPLEMENTED
    message: str = "Not Implemented"
    description: str = "This functionality is not supported by the server."


class BadGatewayErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.BAD_GATEWAY
    message: str = "Bad Gateway"
    description: str = (
        "The server received an invalid response from an upstream server."
    )


class ServiceUnavailableErrorDescriptorSchema(ErrorDescriptorSchema):
    code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE
    message: str = "Service Unavailable"
    description: str = "The server is temporarily unable to handle the request."
