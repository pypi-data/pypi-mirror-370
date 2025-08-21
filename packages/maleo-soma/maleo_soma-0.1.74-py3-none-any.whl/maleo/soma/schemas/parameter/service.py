from datetime import datetime
from pydantic import model_validator
from typing import Self
from maleo.soma.enums.sort import SortOrder
from maleo.soma.mixins.parameter import (
    DateFilters,
    Filters,
    ListOfDataStatuses,
    SortColumns,
    Sorts,
    Search,
    UseCache,
)
from maleo.soma.schemas.filter import DateFilter
from maleo.soma.schemas.pagination import BaseFlexiblePagination, BaseStrictPagination
from maleo.soma.schemas.sort import SortColumn


class ReadUnpaginatedMultipleQueryParameterSchema(
    UseCache,
    BaseFlexiblePagination,
    Sorts,
    Search,
    ListOfDataStatuses,
    Filters,
):
    pass


class ReadUnpaginatedMultipleParameterSchema(
    SortColumns,
    DateFilters,
    ReadUnpaginatedMultipleQueryParameterSchema,
):
    @model_validator(mode="after")
    def set_sort_columns(self) -> Self:
        # * Process sort parameters
        sort_columns = []
        for item in self.sorts:
            parts = item.split(".")
            if len(parts) == 2 and parts[1].lower() in SortOrder:
                try:
                    sort_columns.append(
                        SortColumn(
                            name=parts[0],
                            order=SortOrder(parts[1].lower()),
                        )
                    )
                except ValueError:
                    continue

        # * Only update if we have valid sort columns, otherwise keep the default
        if sort_columns:
            self.sort_columns = sort_columns
        return self

    @model_validator(mode="after")
    def set_date_filters(self) -> Self:
        # * Process filter parameters
        date_filters = []
        for filter_item in self.filters:
            parts = filter_item.split("|")
            if len(parts) >= 2 and parts[0]:
                name = parts[0]
                from_date = None
                to_date = None

                # * Process each part to extract from and to dates
                for part in parts[1:]:
                    if part.startswith("from::"):
                        try:
                            from_date_str = part.replace("from::", "")
                            from_date = datetime.fromisoformat(from_date_str)
                        except ValueError:
                            continue
                    elif part.startswith("to::"):
                        try:
                            to_date_str = part.replace("to::", "")
                            to_date = datetime.fromisoformat(to_date_str)
                        except ValueError:
                            continue

                # * Only add filter if at least one date is specified
                if from_date or to_date:
                    date_filters.append(
                        DateFilter(name=name, from_date=from_date, to_date=to_date)
                    )

        # * Update date_filters
        self.date_filters = date_filters
        return self


class ReadPaginatedMultipleQueryParameterSchema(
    UseCache,
    BaseStrictPagination,
    Sorts,
    Search,
    ListOfDataStatuses,
    Filters,
):
    pass


class ReadPaginatedMultipleParameterSchema(
    SortColumns,
    DateFilters,
    ReadPaginatedMultipleQueryParameterSchema,
):
    @model_validator(mode="after")
    def set_sort_columns(self) -> Self:
        # * Process sort parameters
        sort_columns = []
        for item in self.sorts:
            parts = item.split(".")
            if len(parts) == 2 and parts[1].lower() in SortOrder:
                try:
                    sort_columns.append(
                        SortColumn(
                            name=parts[0],
                            order=SortOrder(parts[1].lower()),
                        )
                    )
                except ValueError:
                    continue

        # * Only update if we have valid sort columns, otherwise keep the default
        if sort_columns:
            self.sort_columns = sort_columns
        return self

    @model_validator(mode="after")
    def set_date_filters(self) -> Self:
        # * Process filter parameters
        date_filters = []
        for filter_item in self.filters:
            parts = filter_item.split("|")
            if len(parts) >= 2 and parts[0]:
                name = parts[0]
                from_date = None
                to_date = None

                # * Process each part to extract from and to dates
                for part in parts[1:]:
                    if part.startswith("from::"):
                        try:
                            from_date_str = part.replace("from::", "")
                            from_date = datetime.fromisoformat(from_date_str)
                        except ValueError:
                            continue
                    elif part.startswith("to::"):
                        try:
                            to_date_str = part.replace("to::", "")
                            to_date = datetime.fromisoformat(to_date_str)
                        except ValueError:
                            continue

                # * Only add filter if at least one date is specified
                if from_date or to_date:
                    date_filters.append(
                        DateFilter(name=name, from_date=from_date, to_date=to_date)
                    )

        # * Update date_filters
        self.date_filters = date_filters
        return self
