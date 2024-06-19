# Changelog

All notable changes to this project will be documented in this file.

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
