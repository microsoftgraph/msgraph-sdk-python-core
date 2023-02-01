# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0a4] - 2023-02-02

### Added

### Changed

- Enabled configuring of middleware during client creation by passing custom options in call to create with default middleware.
- Fixed a bug where the transport would check for request options even after they have been removed after final middleware execution.