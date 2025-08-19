# from pydantic import BaseModel, Field
# from typing import Generic, TypeVar
# from maleo_soma.enums.error import Error
# from maleo_soma.mixins.general import CodeT, Code, Message, Description
# from maleo_soma.types.base import OptionalAny, OptionalFloat


# # class Duration(BaseModel):
# #     duration: float = Field(..., description="Duration")


# # class OptionalDuration(BaseModel):
# #     duration: OptionalFloat = Field(None, description="Duration. (Optional)")


# # class KeyString(BaseModel):
# #     key: str = Field(..., description="Key string")


# # class Message(BaseModel):
# #     message: str = Field(..., description="Message")


# # class Description(BaseModel):
# #     description: str = Field(..., description="Description")


# # class OptionalOther(BaseModel):
# #     other: OptionalAny = Field(None, description="Other. (Optional)")


# # SuccessT = TypeVar("SuccessT", bound=bool)


# # class GenericSuccess(BaseModel, Generic[SuccessT]):
# #     success: SuccessT = Field(..., description="Success")


# # class Success(BaseModel):
# #     success: bool = Field(..., description="Success")


# class Descriptor(Description, Message, Code[CodeT], Generic[CodeT]):
#     pass


# # class ErrorType(BaseModel):
# #     type: Error = Field(..., description="Error type")


# # class StatusCode(BaseModel):
# #     status_code: int = Field(..., description="Status code")
