# Changelog

All notable changes to Emailer Simple Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [10.0.8] - 2025-08-18

### 🔧 Windows Text Rotation Fix
- **Fixed Top-Edge Clipping**: Resolved Windows-specific issue where rotated text near the top edge was clipped at the bottom
  - Smart detection of text positioned near top edge (y < 100 pixels)
  - Intelligent padding calculation based on font size and rotation angle
  - Moves text DOWN when near top edge to prevent clipping, UP elsewhere for standard adjustment
- **Improved Rotation Logic**: Enhanced Windows compatibility for rotated text positioning
  - Base padding: 15% of font size (minimum 10px) for adequate spacing
  - Angle-aware adjustment: Scales padding based on rotation angle (normalized to 45°)
  - Preserves existing behavior for text positioned away from edges
- **Real-World Testing**: Fix specifically addresses issues with large rotated text (e.g., "2025" at 102px, 8° rotation)
  - Prevents bottom character clipping on Windows systems
  - Maintains cross-platform consistency with macOS and Linux
  - No impact on non-rotated text or text positioned away from edges

## [10.0.7] - 2025-08-18

### 🎨 Enhanced Text Rotation with PIL
- **Professional Text Rotation**: Completely redesigned text rotation using PIL's native capabilities
  - Replaced manual mathematical calculations with PIL's `rotate(angle, expand=True)`
  - PIL automatically calculates perfect bounding boxes for any rotation angle
  - Eliminates positioning errors and ensures accurate text placement
- **Fixed Character Clipping**: Resolved missing pixels at bottom of rotated characters
  - Added dynamic padding based on font size: `max(20, int(font_size * 0.3))`
  - Proper handling of font descenders (g, j, p, q, y) and ascenders
  - Scales automatically with font size for consistent results
- **Cross-Platform Compatibility**: Maintains Windows-specific adjustments while using PIL
  - Windows Y-position adjustment preserved for consistency
  - Works identically on macOS, Windows, and Linux

### 🎯 Negative Positioning Support
- **Full Negative Coordinate Support**: All fusion types now support negative x and y positioning
  - **Text fusion**: Regular and rotated text can be positioned with negative coordinates
  - **Graphic fusion**: Images and QR codes support negative positioning
  - **Formatted-text fusion**: Rendered .docx documents support negative positioning
- **Natural Boundary Clipping**: PIL automatically clips content extending beyond image bounds
  - No artificial coordinate restrictions - use any integer values
  - Perfect for artistic layouts and large rotated text near edges
  - Enables professional design flexibility
- **Fixed CSV Validation**: Updated positioning validation regex
  - Changed from `^\d+:\d+$` to `^-?\d+:-?\d+$` to allow negative values
  - Supports formats like `-50:100`, `100:-20`, `-30:-10`
  - Maintains validation for invalid formats while enabling negative coordinates

### 🔧 Technical Improvements
- **PIL-Native Implementation**: Leverages PIL's built-in rotation and positioning capabilities
- **Mathematical Accuracy**: Positioning calculations now mathematically correct for all alignments
- **Debug Output**: Enhanced debug logging for rotation and positioning troubleshooting
- **Validation Enhancement**: Comprehensive support for negative positioning across all fusion types

### 🎯 Use Cases Enabled
- **Large Rotated Text**: Text like "2025" with center alignment at x=20 correctly positions at x=-78
- **Artistic Layouts**: Elements can extend beyond image boundaries for creative effects  
- **Professional Typography**: Perfect text rotation without character clipping
- **Flexible Positioning**: No coordinate restrictions for advanced layout control

## [10.0.6] - 2025-08-18

### 🐛 Rotated Text Padding Adjustment
- **Fixed Bottom Cutoff**: Increased rotated text padding to prevent text being cut off at the bottom
  - Changed padding calculation from `max(20, font_size * 0.3)` to `max(25, font_size * 0.4)`
  - For 102px font: increased padding from 30px to 40px to ensure full text visibility
  - Balances positioning control with complete text rendering

### 🔧 Technical Implementation
- **Optimal Padding**: Fine-tuned padding formula based on Windows Server 2022 testing feedback
- **Complete Text Rendering**: Ensures rotated text like "2025" displays fully without cutoff
- **Positioning Control**: Maintains improved positioning control from v10.0.5 while preventing cutoff

### 📚 Compatibility
- **Maintains All Previous Fixes**: Non-rotated text alignment fix and GUI improvements
- **Windows Server 2022**: Optimized specifically for Windows text rendering behavior
- **Cross-platform**: Consistent behavior across Windows, macOS, and Linux

## [10.0.5] - 2025-08-18

### 🐛 Windows Text Positioning Improvements
- **Rotated Text Padding**: Reduced excessive top padding for rotated text positioning
  - Changed padding calculation from `max(40, font_size * 0.8)` to `max(20, font_size * 0.3)`
  - For 102px font: reduced padding from 81px to 30px for better positioning control
  - Allows rotated text like "2025" to be positioned higher as needed

- **Non-Rotated Text Alignment**: Fixed 13-pixel vertical offset between Windows and Mac
  - Added Windows-specific Y-position adjustment for regular text
  - Adjustment formula: `y - max(3, font_size * 0.12)` (upward by ~12% of font size)
  - Ensures consistent text positioning across platforms for text like "le 8 ou 9 nov."

### 🔧 Technical Implementation
- **Platform Detection**: Enhanced Windows-specific adjustments for both rotated and non-rotated text
- **Font Size Scaling**: Dynamic adjustments based on actual font size for better precision
- **Cross-platform Consistency**: Maintains identical visual output between Windows, macOS, and Linux

### 📚 Compatibility
- **Maintains All Previous Fixes**: GUI indentation fix (v10.0.4) and original Windows rotation fix (v10.0.2)
- **Improved Positioning Control**: Better fine-tuning capabilities for text placement on Windows
- **Production Ready**: Tested on Windows Server 2022 with various font sizes and orientations

## [10.0.4] - 2025-08-18

### 🐛 Critical Bug Fix
- **GUI Indentation Error**: Fixed Python indentation error in send_tab.py that prevented GUI from launching
  - Resolved "unindent does not match any outer indentation level" error on line 19
  - Cleaned up corrupted dual PySide compatibility code that was introduced during troubleshooting
  - Restored clean PySide6-only implementation throughout the codebase

### 🔧 Technical Implementation
- **Code Cleanup**: Removed all remnants of dual PySide2/PySide6 compatibility layer
- **Distribution Fix**: Rebuilt package with clean source code to ensure PyPI distribution is error-free
- **Quality Assurance**: Verified all Python files compile correctly before distribution

### 📚 Compatibility
- **Windows Text Rotation**: Maintains the Windows text rotation fix from v10.0.2
- **PySide6 Only**: Clean, simplified codebase with PySide6 as the sole GUI framework
- **Cross-platform**: Full compatibility with Windows Server 2022, macOS, and Linux

## [10.0.2] - 2025-08-18

### 🐛 Windows Compatibility Fix
- **Windows Text Rotation**: Fixed rotated text being cut off at the bottom on Windows systems
  - Implemented dynamic padding calculation based on font size for rotated text
  - Added Windows-specific Y-position adjustment for rotated text rendering  
  - Maintains cross-platform compatibility (macOS, Linux, Windows)
  - Resolves issue where large fonts (e.g., 102px) with rotation were truncated on Windows

### 🔧 Technical Implementation
- **Enhanced Padding Logic**: Dynamic padding calculation `max(40, font_size * 0.8)` for better text boundary handling
- **Platform Detection**: Automatic Windows detection for platform-specific adjustments
- **Cross-platform Consistency**: Maintains identical behavior on macOS and Linux
- **Improved Text Rendering**: Better bounding box calculation for rotated text on Windows

### 📚 Documentation
- Added `WINDOWS_TEXT_ROTATION_FIX.md` with installation and testing instructions
- Detailed technical explanation of the Windows font rendering differences

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
