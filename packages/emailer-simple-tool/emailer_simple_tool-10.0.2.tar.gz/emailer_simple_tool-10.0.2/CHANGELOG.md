# Changelog

All notable changes to Emailer Simple Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [10.0.1] - 2025-08-16

### 🐛 Critical Bug Fix
- **Text Orientation Support**: Fixed missing orientation parameter support for regular text fusion type
  - Text fusion type (`fusion-type='text'`) now properly supports the `orientation` parameter
  - Previously only `formatted-text` fusion type supported text rotation
  - Users can now rotate text using orientation values (e.g., `-90` for vertical text)
  - Implemented proper alignment handling for rotated text (left, center, right)
  - Added graceful fallback to normal text rendering if orientation value is invalid

### 🔧 Technical Implementation
- **Enhanced Text Rendering**: Added temporary image technique for text rotation
  - Creates temporary RGBA image for text, applies rotation, then pastes to main image
  - Maintains transparency and proper positioning after rotation
  - Consistent with existing formatted-text rotation implementation
- **Error Handling**: Added warning logging for invalid orientation values with fallback
- **Backward Compatibility**: All existing text without orientation continues to work normally

### 📊 Impact
- **Fixed User Issue**: Resolves reported problem where orientation parameter was ignored
- **Feature Parity**: Text and formatted-text fusion types now have consistent rotation support
- **Enhanced Functionality**: Enables vertical text, angled labels, and rotated text elements

## [10.0.0] - 2025-08-15

### 🌍 Complete French Localization
- **100% Translation Coverage**: Achieved complete French localization across entire application
  - Picture Creation Wizard: All wizard pages, buttons, and content fully translated
  - SMTP Configuration Storage Panel: Complete HTML content translation with proper XML escaping
  - Final Confirmation Dialogs: All wizard success/error dialogs now in French
  - Bidirectional Language Switching: Perfect English ↔ French functionality without application restart

### 🐛 Critical Bug Fixes
- **Send Report Parsing**: Fixed incorrect "0 sent" display when emails were successfully sent
  - Enhanced message parsing with multiple regex patterns for various success message formats
  - Now correctly displays actual sent counts (e.g., "2 sent" instead of "0 sent")
- **Attachment Size Display**: Fixed "0,0MB" display for small files
  - Implemented adaptive precision formatting (2 decimals for <0.1MB, 1 decimal for larger files)
  - Now shows proper sizes like "0.02 MB" instead of "0,0 MB"
- **Picture Project Information**: Enhanced display with comprehensive attachment details
  - Shows number of attached picture projects and average image size
  - Displays estimated total attachment size per recipient
  - Format: "X project(s), avg YKB/image (~ZMB/recipient)"

### 🚀 UI/UX Enhancements
- **Delete Functionality**: Added delete buttons for dry run results and sent reports
  - Side-by-side layout with Open and Delete buttons on same line
  - Comprehensive safety features with confirmation dialogs
  - Automatic list refresh after successful deletion
- **Button Styling**: Implemented standard delete button design
  - Red background with white text following UI conventions
  - Hover effects for better user interaction feedback
  - Clear visual distinction for destructive actions

### 🔧 Technical Improvements
- **Translation System Architecture**: Enhanced translation handling with proper XML escaping
- **Dynamic Content Refresh**: All UI elements update immediately during language changes
- **Error Handling**: Comprehensive error handling for all new delete functionality
- **Code Quality**: Maintained consistent UI patterns and improved maintainability

### 📊 Quality Assurance
- **Translation Quality**: Consistent terminology and accurate French technical terms
- **Functional Testing**: Verified all bug fixes and new features work correctly
- **User Experience**: Enhanced interface provides professional, fully localized experience

## [9.0.0] - 2025-08-13

### 🚀 Major Features
- **CLI Report Generation**: Added comprehensive JSON report generation to CLI for consistency with GUI
  - New `--generate-report` flag (enabled by default) and `--no-report` flag for CLI control
  - CLI and GUI now generate identical JSON reports with campaign details, statistics, and audit trails
  - Reports include execution timestamp, success status, recipient results, and configuration snapshot

### 🏗️ Architecture Improvements
- **Code Deduplication**: Eliminated duplicate report generation code between GUI and CLI
  - GUI now uses core `EmailSender.generate_sent_report()` method instead of duplicate implementation
  - Single source of truth for all report generation logic in core module
  - Reduced technical debt and improved maintainability

### 🔧 Fixed
- **GUI Send Tab Issues**: Resolved multiple critical bugs in send functionality
  - Fixed `progress_callback` parameter error that prevented email sending
  - Fixed "Open Selected" button for both dry run results and sent reports with single-line display format
  - Fixed sent reports list not updating after campaign completion
  - Proper filename extraction from formatted display text for file operations

### 📊 Enhanced
- **Report Consistency**: Both CLI and GUI generate identical structured reports
  - Consistent JSON format with campaign info, execution details, statistics, recipients, and configuration
  - Standardized file naming: `YYYY-MM-DD_HH-MM-SS.json` in `sentreport/` folder
  - Enhanced timing tracking and performance metrics in reports

### 🎯 Technical Details
- **Clean Architecture**: Implemented proper separation of concerns
  - Core business logic in `EmailSender` class
  - GUI wrapper methods that delegate to core implementation
  - Zero code duplication between interfaces
- **Improved Error Handling**: Better error reporting and graceful fallbacks
- **Enhanced CLI**: More robust argument parsing and user feedback

## [8.0.1] - 2025-08-12

### 🎨 Enhanced
- **Picture Generator Tab Layout**: Completely redesigned Project Properties panel with optimized two-column layout
  - Left column (400px): Core files, attachment control, and file management buttons on same line
  - Right column: Additional files list with maximized height and proper scroll bars
  - User Help section increased from 200px to 300px height for better readability

### 🔧 Fixed
- **Attachment Checkbox Issue**: Fixed critical bug where checkbox would automatically uncheck itself
  - Root cause: Incorrect Qt enum vs integer state comparison (`state == Qt.Checked` vs `state == 2`)
  - Solution: Proper state comparison ensuring checkbox stays checked when user clicks it
  - File synchronization now works correctly between GUI and `attach.txt` file
- **Version Display**: Fixed hardcoded version display in GUI
  - GUI now dynamically imports version from `__init__.py`
  - Window title correctly shows current version (8.0.1)
  - Single source of truth for version information

### 🎯 Improved
- **Button Text Visibility**: Increased left column width from 300px to 400px for full button text visibility
- **Scroll Bar Functionality**: Added proper horizontal and vertical scroll bars to additional files list
  - Horizontal scrolling for long filenames
  - Vertical scrolling for many files
  - Smart scroll bars appear only when needed
- **Space Optimization**: Better balance between left and right columns for optimal space usage
- **User Experience**: Enhanced readability and professional appearance throughout Picture Generator Tab

### 📋 Technical Details
- Enhanced file system watcher integration with flag-based prevention of unnecessary reloads
- Improved signal handling with proper blocking during programmatic checkbox changes
- Optimized layout management with responsive design principles
- Clean code architecture with removed duplicate code and improved method organization

## [8.0.0] - Previous Release
- Initial major release with comprehensive GUI interface
- Picture Generator functionality
- Campaign management system
- SMTP configuration
- Multi-language support

---

## Release Notes

### Version 8.0.1 - "Enhanced User Experience"

This release focuses on significant user interface improvements and critical bug fixes for the Picture Generator Tab, making it more professional, user-friendly, and reliable.

#### 🌟 Highlights

**Enhanced Picture Generator Interface**
- Complete redesign of the Project Properties panel with optimal space utilization
- Professional two-column layout with logical grouping of controls
- Improved readability with 50% larger help section (300px vs 200px)

**Critical Bug Fixes**
- Resolved frustrating checkbox auto-uncheck behavior
- Fixed version display inconsistency in GUI
- Improved button text visibility and scroll bar functionality

**Better User Experience**
- More files visible without scrolling
- Easier help text reading for non-technical users
- Cleaner, more professional interface
- Responsive design that adapts to window resizing

#### 🎯 Perfect For
- Users managing picture generator projects with many additional files
- Non-technical users who rely on comprehensive help text
- Anyone seeking a professional, polished email campaign tool

#### 🔄 Upgrade Notes
- No breaking changes - all existing functionality preserved
- Existing projects and campaigns remain fully compatible
- GUI improvements are immediately visible upon upgrade

This release represents a significant step forward in user experience quality while maintaining the robust functionality that makes Emailer Simple Tool reliable for email campaign management.
