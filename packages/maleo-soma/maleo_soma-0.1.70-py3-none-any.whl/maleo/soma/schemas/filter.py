from maleo.soma.mixins.general import Name
from maleo.soma.mixins.timestamp import OptionalFromTimestamp, OptionalToTimestamp


class DateFilter(
    OptionalToTimestamp,
    OptionalFromTimestamp,
    Name,
):
    pass
