from sqlalchemy import Column, Enum
from maleo.soma.enums.status import DataStatus as DataStatusEnum


class DataStatus:
    status = Column(
        name="status",
        type_=Enum(DataStatusEnum, name="statustype", create_constraints=True),
        default=DataStatusEnum.ACTIVE,
        nullable=False,
    )
