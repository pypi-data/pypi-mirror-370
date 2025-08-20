# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Module to define the pagination used with the common client."""

from __future__ import annotations  # required for constructor type hinting

from dataclasses import dataclass
from typing import Self

# pylint: disable=no-name-in-module
from frequenz.api.common.v1.pagination.pagination_info_pb2 import (
    PaginationInfo as PBPaginationInfo,
)
from frequenz.api.common.v1.pagination.pagination_params_pb2 import (
    PaginationParams as PBPaginationParams,
)
from frequenz.api.common.v1alpha8.pagination.pagination_info_pb2 import (
    PaginationInfo as PBPaginationInfoAlpha8,
)
from typing_extensions import deprecated

# pylint: enable=no-name-in-module


@deprecated(
    "Params is deprecated, use "
    "frequenz.api.common.v1.pagination.pagination_params_pb2.PaginationParams"
    " from the API directly instead.",
)
@dataclass(frozen=True, kw_only=True)
class Params:
    """Parameters for paginating list requests."""

    page_size: int
    """The maximum number of results to be returned per request."""

    page_token: str
    """The token identifying a specific page of the list results."""

    @classmethod
    def from_proto(cls, pagination_params: PBPaginationParams) -> Self:
        """Convert a protobuf Params to PaginationParams object.

        Args:
            pagination_params: Params to convert.
        Returns:
            Params object corresponding to the protobuf message.
        """
        return cls(
            page_size=pagination_params.page_size,
            page_token=pagination_params.page_token,
        )

    def to_proto(self) -> PBPaginationParams:
        """Convert a Params object to protobuf PaginationParams.

        Returns:
            Protobuf message corresponding to the Params object.
        """
        return PBPaginationParams(
            page_size=self.page_size,
            page_token=self.page_token,
        )


@deprecated(
    "Info is deprecated, use PaginationInfo instead.",
)
@dataclass(frozen=True, kw_only=True)
class Info:
    """Information about the pagination of a list request."""

    total_items: int
    """The total number of items that match the request."""

    next_page_token: str | None = None
    """The token identifying the next page of results."""

    @classmethod
    def from_proto(cls, pagination_info: PBPaginationInfo) -> Self:
        """Convert a protobuf PBPaginationInfo to Info object.

        Args:
            pagination_info: Info to convert.
        Returns:
            Info object corresponding to the protobuf message.
        """
        return cls(
            total_items=pagination_info.total_items,
            next_page_token=pagination_info.next_page_token,
        )

    def to_proto(self) -> PBPaginationInfo:
        """Convert a Info object to protobuf PBPaginationInfo.

        Returns:
            Protobuf message corresponding to the Info object.
        """
        return PBPaginationInfo(
            total_items=self.total_items,
            next_page_token=self.next_page_token,
        )


@dataclass(frozen=True, kw_only=True)
class PaginationInfo:
    """Information about the pagination of a list request."""

    total_items: int
    """The total number of items that match the request."""

    next_page_token: str | None = None
    """The token identifying the next page of results."""

    @classmethod
    def from_proto(
        cls, pagination_info: PBPaginationInfoAlpha8 | PBPaginationInfo
    ) -> Self:
        """Convert a protobuf PBPaginationInfo to Info object.

        Args:
            pagination_info: Info to convert.
        Returns:
            Info object corresponding to the protobuf message.
        """
        # We check for truthiness here to handle both cases where the token is
        # not set (defaults to "") or is explicitly set to "". In both
        # situations, we want to return `None`. Using `HasField("next_page_token")`
        # would not handle the case where the token is explicitly set to "".
        return cls(
            total_items=pagination_info.total_items,
            next_page_token=(
                pagination_info.next_page_token
                if pagination_info.next_page_token
                else None
            ),
        )

    def to_proto_v1alpha8(self) -> PBPaginationInfoAlpha8:
        """Convert a Info object to protobuf PBPaginationInfo.

        Returns:
            Protobuf message corresponding to the Info object.
        """
        return PBPaginationInfoAlpha8(
            total_items=self.total_items,
            next_page_token=self.next_page_token,
        )

    def to_proto(self) -> PBPaginationInfo:
        """Convert a Info object to protobuf PBPaginationInfo.

        Returns:
            Protobuf message corresponding to the Info object.
        """
        return PBPaginationInfo(
            total_items=self.total_items,
            next_page_token=self.next_page_token,
        )
