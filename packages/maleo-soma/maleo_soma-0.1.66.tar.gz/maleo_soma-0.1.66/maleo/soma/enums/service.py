from enum import StrEnum


class ServiceType(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"


class Category(StrEnum):
    CORE = "core"
    AI = "ai"


class ShortService(StrEnum):
    STUDIO = "studio"
    NEXUS = "nexus"
    TELEMETRY = "telemetry"
    METADATA = "metadata"
    IDENTITY = "identity"
    ACCESS = "access"
    WORKSHOP = "workshop"
    SOAPIE = "soapie"
    MEDIX = "medix"
    DICOM = "dicom"
    SCRIBE = "scribe"
    CDS = "cds"
    IMAGING = "imaging"
    MCU = "mcu"


class Service(StrEnum):
    MALEO_STUDIO = "maleo-studio"
    MALEO_NEXUS = "maleo-nexus"
    MALEO_TELEMETRY = "maleo-telemetry"
    MALEO_METADATA = "maleo-metadata"
    MALEO_IDENTITY = "maleo-identity"
    MALEO_ACCESS = "maleo-access"
    MALEO_WORKSHOP = "maleo-workshop"
    MALEO_SOAPIE = "maleo-soapie"
    MALEO_MEDIX = "maleo-medix"
    MALEO_DICOM = "maleo-dicom"
    MALEO_SCRIBE = "maleo-scribe"
    MALEO_CDS = "maleo-cds"
    MALEO_IMAGING = "maleo-imaging"
    MALEO_MCU = "maleo-mcu"
