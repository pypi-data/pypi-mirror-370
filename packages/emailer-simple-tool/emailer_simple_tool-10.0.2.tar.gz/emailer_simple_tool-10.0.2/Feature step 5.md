# Description
For the feature step 5, the target is to provide a graphical user interface (GUI) to the end user as an alternative to the command line interface. This GUI should provide the same functionality as the CLI but through an intuitive, visual interface that is accessible to non-technical users. The GUI should work cross-platform (Windows, Mac, Linux) and integrate seamlessly with the existing CLI infrastructure without duplicating business logic.

# Features details and guidances

## Graphical User Interface Implementation
The program should provide a modern, professional graphical interface using PySide6 (Qt for Python) as the GUI framework. The interface should be organized as a tabbed application with clear separation of functionality areas.

### GUI Framework Selection
I suggest using PySide6 for the following reasons:
- Cross-platform compatibility (Windows, Mac, Linux)
- Professional, native-looking appearance
- Free license (LGPL) suitable for commercial use
- Rich widget set appropriate for data-heavy applications
- Mature ecosystem with excellent documentation
- Future-proof with active development by Qt Company

### Main Window Structure
The GUI should be organized as a main window with a tabbed interface containing four primary tabs:
- **Campaign Tab**: Campaign folder management and overview
- **SMTP Tab**: Email server configuration and testing
- **Pictures Tab**: Picture generator project management
- **Send Tab**: Email sending and dry run operations

## Campaign Management Tab
### Description
This tab should provide visual campaign folder management with real-time preview of campaign components.

### Guidances
- **Folder Selection**: Provide a "Browse" button for campaign folder selection with visual feedback
- **Campaign Status Overview**: Display a comprehensive status summary showing:
  - Campaign name and folder path
  - Number of recipients found in CSV
  - Message template type (txt/docx) and status
  - Attachments count and total size
  - Picture generator projects count
- **Recipients Preview**: Show a table preview of the first 5-10 recipients from the CSV file with:
  - All columns visible with proper headers
  - Indication if more recipients exist beyond the preview
  - Error display if CSV cannot be loaded
- **Message Template Preview**: Display message content with:
  - Plain text preview for .txt files
  - Formatted document indication for .docx files
  - Template variable highlighting where possible
- **Attachments Overview**: List attachment files with:
  - File names and sizes
  - Total attachment size calculation
  - Warning indicators for large files or potentially blocked types
- **Real-time Validation**: Automatically validate campaign components when folder is selected and provide visual feedback (green checkmarks, red X marks, warning triangles)

## SMTP Configuration Tab
### Description
This tab should provide visual SMTP server configuration with guided setup and connection testing.

### Guidances
- **Configuration Form**: Provide form fields for:
  - SMTP server hostname
  - Port number (with spinner control)
  - Username/email address
  - Password (with masked input)
  - TLS/STARTTLS checkbox (enabled by default)
- **Quick Setup Presets**: Provide buttons for common email providers:
  - Gmail (smtp.gmail.com:587)
  - Outlook (smtp-mail.outlook.com:587)
  - Yahoo (smtp.mail.yahoo.com:587)
  - Each button should auto-fill appropriate settings
- **Connection Testing**: Provide "Test Connection" button with:
  - Real-time feedback during testing
  - Clear success/failure messages
  - Specific error guidance for common issues
  - Progress indication during test
- **Provider-Specific Help**: Display contextual help for selected providers including:
  - App password requirements (Gmail)
  - Security settings guidance
  - Links to provider documentation
  - Troubleshooting common connection issues

## Picture Generator Management Tab
### Description
This tab should provide visual management of picture generator projects with status tracking and generation controls.

### Guidances
- **Project List View**: Display picture generator projects in a tree/list view showing:
  - Project names
  - Status indicators (Ready, Needs Generation, In Progress)
  - Generated image counts
  - Last generation timestamp
- **Project Details Panel**: When a project is selected, show:
  - Template file information
  - Fusion configuration table with columns for type, data, positioning, size
  - Generated images list and preview
  - Project validation status
- **Generation Controls**: Provide:
  - "Generate Pictures" button for selected project
  - Progress bar during generation
  - Real-time status updates
  - Success/failure feedback with specific error messages
- **Project Management**: Allow:
  - Refresh projects list
  - View project configuration
  - Access to generated images folder
  - Validation of project consistency

## Email Sending and Dry Run Tab
### Description
This tab should provide email sending operations with comprehensive progress tracking and dry run capabilities.

### Guidances
- **Pre-Send Validation**: Provide "Validate Campaign" button that checks:
  - All campaign components are present and valid
  - SMTP configuration is working
  - Picture projects are ready (if used)
  - Attachment sizes and types
  - Display comprehensive validation results with actionable feedback
- **Dry Run Operations**: Provide:
  - "Dry Run" button with optional custom naming
  - Progress bar showing dry run generation progress
  - Results log showing each email generated
  - Success message with location of .eml files
  - Guidance on how to preview .eml files
- **Email Sending**: Provide:
  - "Send Campaign" button with confirmation checkbox
  - Confirmation dialog before actual sending
  - Real-time progress tracking with:
    - Progress bar showing completion percentage
    - Statistics: Sent count, Failed count, Remaining count
    - Live results log with per-recipient status
  - Final summary with success/failure counts
- **Results Management**: Provide:
  - Clear log button
  - Save log to file functionality
  - Export results for record keeping

## Technical Implementation Guidelines

### Project Structure
The GUI should be implemented as a proper Python module within the existing project structure:
```
src/emailer_simple_tool/
├── gui/                    # GUI module
│   ├── __init__.py        # GUI entry point with dependency checking
│   ├── main_window.py     # Main application window
│   ├── tabs/              # Individual tab components
│   │   ├── __init__.py
│   │   ├── campaign_tab.py
│   │   ├── smtp_tab.py
│   │   ├── picture_tab.py
│   │   └── send_tab.py
│   ├── widgets/           # Custom GUI widgets
│   └── resources/         # GUI assets (icons, styles)
```

### Integration with Existing CLI
- The GUI should reuse existing core modules (campaign_manager, email_sender, picture_generator, validators)
- No duplication of business logic - GUI provides interface only
- CLI should be enhanced with `emailer-simple-tool gui` command
- GUI dependencies should be optional extras in setup configuration

### Installation and Distribution
- GUI dependencies should be installable via `pip install emailer-simple-tool[gui]`
- CLI-only installation should remain available via `pip install emailer-simple-tool`
- Graceful fallback when GUI dependencies are not available
- Clear installation instructions for GUI support

### Cross-Platform Considerations
- Use PySide6's native styling to match operating system appearance
- Handle file path separators correctly across platforms
- Ensure proper window sizing and DPI scaling
- Test on Windows, macOS, and Linux

### Error Handling and User Experience
- Comprehensive error handling with user-friendly messages
- Progress indicators for all long-running operations
- Confirmation dialogs for destructive actions
- Contextual help and tooltips where appropriate
- Keyboard shortcuts for common operations

### Styling and Appearance
- Modern, professional appearance with consistent color scheme
- Proper spacing and alignment following UI design principles
- Clear visual hierarchy with appropriate fonts and sizes
- Responsive layout that works on different screen sizes
- Accessibility considerations (contrast, font sizes, keyboard navigation)

## CLI Integration
The existing command line interface should be enhanced to support GUI launch:
- Add `gui` subcommand to the argument parser
- Implement `handle_gui_command()` function with proper error handling
- Check for GUI dependencies and provide helpful installation messages if missing
- Update help text and documentation to include GUI option

## Installation Configuration
Update the project's setup configuration to support optional GUI installation:
- Add `gui` extras_require section with PySide6 dependency
- Add `all` extras_require combining GUI and development dependencies
- Update project classifiers to include GUI-related categories
- Ensure proper dependency version constraints

# Documentation
Update all project documentation to reflect the dual-interface approach:
- Update README.md with GUI installation and usage instructions
- Update INSTALLATION.md with GUI-specific installation steps
- Update QUICK_START.md with both CLI and GUI quick start guides
- Create GUI-specific user documentation
- Update FAQ with GUI-related questions
- Add troubleshooting section for GUI issues

The documentation should clearly explain:
- When to use GUI vs CLI interface
- Installation options for different user needs
- GUI-specific features and workflows
- Integration between GUI and existing CLI functionality

# Testing
Provide comprehensive testing for GUI components:
- Unit tests for individual GUI components and tabs
- Integration tests for GUI-CLI interaction
- Mock testing for GUI operations that interact with external services
- Cross-platform testing on Windows, macOS, and Linux
- User acceptance testing with non-technical users
- Performance testing for GUI responsiveness

Testing should cover:
- GUI component initialization and layout
- User interaction handling (button clicks, form submission)
- Data validation and error display
- Progress tracking and status updates
- Integration with existing core modules
- Graceful handling of missing dependencies

==%%*Note for Q Dev CLI: The GUI implementation should prioritize user experience for non-technical users while maintaining the power and flexibility of the CLI for advanced users and automation. The interface should feel intuitive and provide clear guidance at each step of the email campaign process. Consider conducting user testing with the target audience to validate the interface design and workflow.*%%==
