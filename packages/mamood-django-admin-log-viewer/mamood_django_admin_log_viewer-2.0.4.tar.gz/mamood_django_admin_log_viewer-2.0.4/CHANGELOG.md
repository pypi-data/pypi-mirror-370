# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.4] - 2025-08-17

### Fixed

- **CSS Conflicts**: Fixed CSS class conflicts with Django admin's built-in `.module` class
- Renamed conflicting CSS classes to more unique names to prevent styling issues

### Changed

- `.module` class renamed to `.log-module`
- `.module-name` class renamed to `.log-module-name`
- `.no-module` class renamed to `.no-log-module`
- Updated CSS, HTML templates, and JavaScript files with new class names
- Improved CSS specificity to avoid conflicts with Django admin styling

### Technical Improvements

- Enhanced CSS class naming convention for better compatibility with Django admin
- Maintained all existing functionality while resolving styling conflicts
- Updated both light and dark theme styles with new class names

## [2.0.3] - 2025-01-16

### Fixed

- **CRITICAL**: Fixed admin site replacement issue that was hiding all other Django models from admin interface
- Changed admin integration to extend existing admin site instead of replacing it entirely

### Technical Details

- Replaced `admin.site = admin_site` with dynamic class extension approach
- Now uses `DefaultAdminSiteWithLogViewer` mixin to add log viewer functionality without disrupting existing admin registrations
- Ensures compatibility with other Django apps and their admin registrations

## [2.0.2] - 2025-01-16

### Fixed

- Fixed dropdown styling issues where text was not fully visible due to improper height settings
- Fixed log message parsing to display only the message content without timestamp, level, and module metadata
- Fixed JavaScript errors in multiline log modal display by implementing data attribute approach instead of inline onclick
- Fixed pagination issues by implementing proper multiline-aware pagination using entries instead of lines
- Fixed "Next" button not appearing in pagination due to incorrect pagination calculation

### Changed

- Updated views to use multiline-aware log reading functions for proper pagination
- Improved JavaScript security by replacing inline onclick handlers with data attributes
- Enhanced CSS styling for all select elements with consistent height and text visibility

### Technical Improvements

- Refactored `format_multiline_log_entry` function to properly separate message content from metadata
- Updated view pagination logic to work with log entries rather than raw lines
- Added comprehensive dropdown styling with dark theme support
- Implemented safer JavaScript modal handling to prevent syntax errors from special characters

## [2.0.1] - Previous Release

- Previous features and fixes...
