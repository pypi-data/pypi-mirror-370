from pydantic import BaseModel, Field
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.service import Service


class MaleoClientConfigurationDTO(BaseModel):
    environment: Environment = Field(..., description="Client's environment")
    key: Service = Field(..., description="Client's key")
    name: str = Field(..., description="Client's name")
    url: str = Field(..., description="Client's URL")


class MaleoClientsConfigurationDTO(BaseModel):
    telemetry: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoTelemetry client's configuration"
    )
    metadata: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoMetadata client's configuration"
    )
    identity: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoIdentity client's configuration"
    )
    access: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoAccess client's configuration"
    )
    workshop: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoWorkshop client's configuration"
    )
    soapie: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoSOAPIE client's configuration"
    )
    medix: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoMedix client's configuration"
    )
    dicom: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoDICOM client's configuration"
    )
    scribe: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoScribe client's configuration"
    )
    cds: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoCDS client's configuration"
    )
    imaging: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoImaging client's configuration"
    )
    mcu: MaleoClientConfigurationDTO = Field(
        ..., description="MaleoMCU client's configuration"
    )
