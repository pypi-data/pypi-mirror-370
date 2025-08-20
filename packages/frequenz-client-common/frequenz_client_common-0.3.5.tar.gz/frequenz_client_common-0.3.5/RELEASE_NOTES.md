# Frequenz Client Common Library Release Notes

## Summary


## Upgrading

- The `pagination.Params` class is deprecated; use the protobuf message directly.
- The `pagination.Info` class is deprecated in favor of the new `pagination.PaginationInfo` class.

## New Features

- Mapping for the new `Event` message has been added.
- Add new common API enums for `ElectricalComponent` (previously `Components`).

- Added `v1alpha8` variants of the pagination data structures.

## Bug Fixes

- Updated display of protobuf version warnings
