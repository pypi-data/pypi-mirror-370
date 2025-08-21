# Frequenz Client Common Library Release Notes

## Summary

This is the same release as v0.3.5 but with prefixes in `Event` enum values removed. The v0.3.5 release will be yanked from PyPI and it should not be used.

## Upgrading

- The `pagination.Params` class is deprecated; use the protobuf message directly.
- The `pagination.Info` class is deprecated in favor of the new `pagination.PaginationInfo` class.

## New Features

- Mapping for the new `Event` message has been added.
- Add new common API enums for `ElectricalComponent` (previously `Components`).

- Added `v1alpha8` variants of the pagination data structures.

## Bug Fixes

- Updated display of protobuf version warnings
