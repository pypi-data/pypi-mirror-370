# Changelog

All notable changes to the Mindzie API Python Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of the Mindzie API Python Client
- Complete coverage of all Mindzie Studio API endpoints
- Support for multiple authentication methods (API Key, Bearer Token, Azure AD)
- Comprehensive type hints and Pydantic models for all API responses
- Automatic retry logic with exponential backoff
- File upload support for CSV, package, and binary datasets
- Pagination handling for large result sets
- Rate limiting support
- Comprehensive test suite with >90% code coverage
- Detailed documentation and usage examples
- Support for Python 3.8 through 3.12

### Controllers Implemented
- **Project Controller**: List, get, and search projects
- **Dataset Controller**: Create and update datasets from various file formats
- **Investigation Controller**: Full CRUD operations for investigations
- **Notebook Controller**: Manage and execute notebooks
- **Block Controller**: Create and manage different block types
- **Execution Controller**: Monitor and manage execution queue
- **Enrichment Controller**: Handle data enrichment pipelines
- **Dashboard Controller**: Access dashboards and panels
- **Action Controller**: Execute actions
- **Action Execution Controller**: Track action executions
- **Ping Controller**: Connectivity testing

### Features
- Automatic environment variable configuration
- Context manager support for proper resource cleanup
- Comprehensive error handling with custom exception types
- Optional async/await support (with additional dependencies)
- Proxy configuration support
- SSL verification control
- Request timeout configuration
- Custom headers support

## [Unreleased]

### Planned
- WebSocket support for real-time updates
- Batch operations for improved performance
- Caching layer for frequently accessed data
- CLI tool for command-line operations
- GraphQL support (if API adds GraphQL endpoint)
- Additional authentication methods
- Improved async/await implementation
- Data export utilities
- Local data validation before upload