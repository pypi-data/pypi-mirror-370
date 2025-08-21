from pydantic import BaseModel, Field
from typing import Optional, TypeVar
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.service import Service


class MaleoClientConfigurationDTO(BaseModel):
    environment: Environment = Field(..., description="Client's environment")
    key: Service = Field(..., description="Client's key")
    name: str = Field(..., description="Client's name")
    url: str = Field(..., description="Client's URL")


class MaleoTelemetryClientConfigurationMixin(BaseModel):
    telemetry: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoTelemetry client's configuration"
    )


class MaleoMetadataClientConfigurationMixin(BaseModel):
    metadata: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoMetadata client's configuration"
    )


class MaleoIdentityClientConfigurationMixin(BaseModel):
    identity: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoIdentity client's configuration"
    )


class MaleoAccessClientConfigurationMixin(BaseModel):
    access: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoAccess client's configuration"
    )


class MaleoWorkshopClientConfigurationMixin(BaseModel):
    workshop: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoWorkshop client's configuration"
    )


class MaleoResearchClientConfigurationMixin(BaseModel):
    research: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoResearch client's configuration"
    )


class MaleoSOAPIEClientConfigurationMixin(BaseModel):
    soapie: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoSOAPIE client's configuration"
    )


class MaleoMedixClientConfigurationMixin(BaseModel):
    medix: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoMedix client's configuration"
    )


class MaleoDICOMClientConfigurationMixin(BaseModel):
    dicom: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoDICOM client's configuration"
    )


class MaleoScribeClientConfigurationMixin(BaseModel):
    scribe: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoScribe client's configuration"
    )


class MaleoCDSClientConfigurationMixin(BaseModel):
    cds: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoCDS client's configuration"
    )


class MaleoImagingClientConfigurationMixin(BaseModel):
    imaging: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoImaging client's configuration"
    )


class MaleoMCUClientConfigurationMixin(BaseModel):
    mcu: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoMCU client's configuration"
    )


MaleoClientsConfigurationT = TypeVar(
    "MaleoClientsConfigurationT", bound=Optional[BaseModel]
)
