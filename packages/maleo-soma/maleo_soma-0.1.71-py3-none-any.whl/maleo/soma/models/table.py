from sqlalchemy.orm import declared_attr
from maleo.soma.utils.formatter.case import to_snake_case
from .columns.identifier import DataIdentifier
from .columns.status import DataStatus
from .columns.timestamp import DataTimestamp


class BaseTable:
    __abstract__ = True

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return to_snake_case(cls.__name__)  # type: ignore


class DataTable(DataStatus, DataTimestamp, DataIdentifier):
    pass
