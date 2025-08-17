from sqlalchemy import Column, Integer, UUID
from uuid import uuid4


class DataIdentifier:
    id = Column(name="id", type_=Integer, primary_key=True)
    uuid = Column(name="uuid", type_=UUID, default=uuid4, unique=True, nullable=False)


class OperationIdentifier:
    id = Column(
        name="id",
        type_=UUID,
        default=uuid4,
        unique=True,
        nullable=False,
        primary_key=True,
    )
