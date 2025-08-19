# Changelog

## [0.1.4] - 2025-08-18

### Changed

- Updated dependencies to latest versions.

## [0.1.3] - 2025-04-22

### Changed

- Added and used `pyserde[toml]` as a dependency for easier I/O of TOML formatting options.
  - `pyserde` wraps around regular dataclasses, to no further action is required to make use of
    this.
  - It might put more stringent requirements on your input to the classes in some edge cases.

## [0.1.2] - 2025-03-07

### Changed

- Moved `typst` dependency to `test` group as it's not required at runtime.

## [0.1.1] - 2025-03-06

### Changed

- Bumped `typst` dependency to 0.13.1.

## [0.1.0] - 2025-01-13

### Added

- Initial version!
