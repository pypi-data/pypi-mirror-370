# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2025-08-19

### Fixed
- **PowerShell Syntax Issues**: Fixed all GitHub Actions workflow syntax errors in Windows workflows
- **Quote Escaping**: Resolved PowerShell quote escaping issues in Python commands
- **Command Simplification**: Simplified complex Python one-liners to prevent syntax errors
- **Workflow Compatibility**: All Windows workflows now use proper PowerShell syntax
- **Test Commands**: Fixed Python test commands to work correctly in PowerShell environment

### Changed
- **Workflow Commands**: Updated all `python -c` commands to use proper quote escaping
- **PowerShell Integration**: Improved Windows workflow compatibility and reliability
- **Error Prevention**: Eliminated syntax errors that were causing workflow failures

### Technical Details
- Fixed quote escaping in `.github/workflows/test.yml`
- Fixed PowerShell commands in `.github/workflows/build-exe.yml`
- Fixed syntax issues in `.github/workflows/publish.yml`
- All commands now tested locally and validated for PowerShell compatibility

## [1.0.5] - 2025-08-19

### Changed
- **Configuration File Renamed**: All documentation and references updated from `app_config.ini` to `log_config.ini`
- **Documentation Updates**: Wiki files and API references updated with new configuration file name
- **Package Rebuild**: Clean build with all configuration file references updated

### Fixed
- **Documentation Consistency**: All wiki files now consistently reference `log_config.ini`
- **API Reference**: Updated function parameter defaults and examples
- **Configuration Examples**: All configuration examples use the new file name

## [1.0.4] - 2025-08-18

### Changed
- **Configuration File Renamed**: Changed default configuration file from `app_config.ini` to `log_config.ini`
- **Emoji Removal**: Removed all emoji characters from Python code for better compatibility
- **Package Structure**: Cleaned up package structure and improved organization
- **Documentation**: Updated package descriptions and metadata for clarity

### Fixed
- **Import Issues**: Resolved circular import problems in package initialization
- **Configuration Loading**: Improved error handling in configuration file loading
- **File Rotation**: Enhanced log file truncation logic for better reliability

### Technical
- **Python Support**: Maintained Python 3.11+ compatibility
- **Dependencies**: Updated development dependencies to latest stable versions
- **Build System**: Streamlined build configuration and package metadata

## [1.0.3] - 2025-08-17

### Changed
- **Author Information**: Updated author name to "Pandiyaraj Karuppasamy" and GitHub username to "Pandiyarajk"
- **Repository Links**: Updated all GitHub repository references throughout the project
- **Documentation**: Enhanced README and wiki documentation with comprehensive guides

### Added
- **GitHub Actions**: Implemented Windows-only CI/CD workflows for automated testing and publishing
- **Wiki Documentation**: Created comprehensive wiki pages covering installation, API, and troubleshooting
- **Debug Workflows**: Added specialized workflows for dependency and file location debugging

### Fixed
- **PyPI Links**: Resolved 404 errors by converting relative links to absolute GitHub URLs
- **Workflow Issues**: Fixed PowerShell syntax errors and emoji-related parsing issues
- **File Discovery**: Improved dependency file detection in GitHub Actions workflows

## [1.0.2] - 2025-08-18

### Fixed
- **PyPI Link Issues**: Converted all relative links in markdown files to absolute GitHub URLs to prevent 404 errors
- **Documentation**: Updated README.md, CHANGELOG.md, and PUBLISHING_GUIDE.md with working links
- **Project Links**: Fixed Homepage, Bug Tracker, Changelog, Documentation, and Repository links on PyPI

### Changed
- **Link Format**: All internal and external links now use absolute GitHub URLs for better PyPI compatibility
- **Documentation**: Enhanced documentation with proper linking structure

## [1.0.1] - 2025-08-17

### Changed
- **Documentation**: Updated package documentation and version consistency
- **Configuration**: Improved configuration file handling and defaults
- **Build System**: Enhanced package building and distribution process

### Fixed
- **Version Management**: Resolved version numbering inconsistencies
- **Package Metadata**: Updated package information and descriptions

## [1.0.0] - 2025-08-17

### Added
- **Core Logging**: Rich console output with beautiful formatting and colors
- **File Logging**: Automatic log file creation with configurable paths
- **Log Rotation**: Size-based log file rotation with truncation strategy (no backup files)
- **Thread Safety**: Queue-based asynchronous logging for multi-threaded applications
- **Windows Optimization**: Windows-safe file handling with proper encoding support
- **Configuration Management**: INI-based configuration with sensible defaults
- **UTF-8 Support**: Full Unicode support for international character logging

### Features
- **Rich Console Output**: Beautiful, colored console logging using the Rich library
- **File Rotation**: Automatic log file size management with configurable limits
- **Queue Processing**: Thread-safe logging with configurable queue sizes and flush intervals
- **Multiple Logger Types**: Console-only, file-only, and combined logging options
- **Configuration Files**: Easy customization via `log_config.ini` files
- **Error Handling**: Robust error handling with fallback configurations
- **Cleanup Functions**: Proper resource cleanup for file handlers and threads

### Technical Specifications
- **Python Version**: Requires Python 3.11 or higher
- **Dependencies**: Rich library for console formatting
- **File Size Limit**: Configurable log file size limits (default: 10MB)
- **Queue Size**: Configurable queue sizes for thread-safe logging
- **Flush Interval**: Configurable flush intervals for queue processing
- **Encoding**: UTF-8 encoding for all file operations
- **Platform**: Windows-optimized with cross-platform compatibility

### Configuration Options
- **Log Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output Mode**: Console, file, or both
- **File Rotation**: Configurable maximum file sizes
- **Queue Settings**: Enable/disable queue-based logging with size and interval controls
- **Formatting**: Customizable log message formats
- **Directory Management**: Automatic logs directory creation

### Use Cases
- **Application Logging**: Comprehensive logging for desktop and web applications
- **Development**: Enhanced debugging and development logging
- **Production**: Reliable file-based logging for production environments
- **Multi-threaded Apps**: Thread-safe logging for concurrent applications
- **Windows Applications**: Optimized logging for Windows environments
