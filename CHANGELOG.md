# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.0.1...v1.1.0) (2024-06-19)


### Features

* adds support for python 3.12 ([991a5e0](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/991a5e0bc2ea4db108a127a1d079967b97ae1280))


### Bug Fixes

* replaces older contributing rst by md version ([70f6fb2](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/70f6fb25e612b7d01abba27c6c43ca43f166dcbf))

## [1.0.1] - 2024-04-22

### Added

### Changed

 -Enabled Large File Upload and Page iterator support

## [1.0.0] - 2023-10-31

### Added

### Changed

- GA release.

## [1.0.0a6] - 2023-10-12

### Added

### Changed

- Replaced default transport with graph transport when using custom client with proxy.

## [1.0.0a5] - 2023-06-20

### Added

- Added `AzureIdentityAuthenticationProvider` that sets the default scopes and allowed hosts.

### Changed

- Changed the documentation in the README to show how to use `AzureIdentityAuthenticationProvider` from the core SDK.

## [1.0.0a4] - 2023-02-02

### Added

### Changed

- Enabled configuring of middleware during client creation by passing custom options in call to create with default middleware.
- Fixed a bug where the transport would check for request options even after they have been removed after final middleware execution.
