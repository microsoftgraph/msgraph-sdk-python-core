# Changelog

All notable changes to this project will be documented in this file.

## [1.1.5](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.1.4...v1.1.5) (2024-10-02)


### Bug Fixes

* release please initial configuration ([e781cd8](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/e781cd81156622b59a5b3c48fdf70995379d08a0))

## [1.1.4](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.1.3...v1.1.4) (2024-09-24)


### Bug Fixes

* Use abstractions request adapter in tasks ([6d390a2](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/6d390a2a5dea74d137f907cabf8b520100c5b1a8))

## [1.1.3](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.1.2...v1.1.3) (2024-09-03)


### Bug Fixes

* remove print statements from upload code. ([353d72d](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/353d72da513e0c5b809d31a8d921de0a0bde10be))

## [1.1.2](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.1.1...v1.1.2) (2024-07-12)


### Bug Fixes

* adds missing whitespace for suppressions ([7ad013e](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/7ad013e52190ab607dfe82c86ae68c87e7abe4cc))
* fixes exception configuration in pylint ([857ad99](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/857ad9950a0200dbe69d4b96052725624fbe8833))
* linting fix import ordering ([b56cc8d](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/b56cc8d11221166fbd4c8002dfdf9eb027968b5e))
* linting missing line ([f39f0b9](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/f39f0b9b68f94b91c6b179f5f65db960922ecc77))
* moves attributes suppression to class definition ([b6c1d29](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/b6c1d29777829aedf50cadf994e9b8ea68d8ed4a))
* suppressed linting error message that fails dependencies ([d7c0e1b](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/d7c0e1b901ffb0970eb6b94dd623dda41995a772))

## [1.1.1](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.1.0...v1.1.1) (2024-07-10)


### Bug Fixes

* avoid using default mutable parameters ([9fa773a](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/9fa773a7ca92f916a6eb593f033322d5a1918a10))
* fixes constants path for release please config ([2ff4440](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/2ff4440a18347feb173a40010ab4d9910717c6b6))

## [1.1.0](https://github.com/microsoftgraph/msgraph-sdk-python-core/compare/v1.0.1...v1.1.0) (2024-06-19)


### Features

* adds support for python 3.12 ([991a5e0](https://github.com/microsoftgraph/msgraph-sdk-python-core/commit/991a5e0bc2ea4db108a127a1d079967b97ae1280))


### Bug Fixes

* removes unecessary printout in large file upload task.
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
