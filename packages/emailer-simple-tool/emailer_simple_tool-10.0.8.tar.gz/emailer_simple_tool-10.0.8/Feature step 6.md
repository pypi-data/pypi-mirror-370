# Description
For the feature step 6, the target is to enhance the existing GUI interface by focusing specifically on the Campaign Tab functionality. This step introduces comprehensive campaign management capabilities including campaign creation wizard, external file editing integration, and live validation systems. The enhancement also establishes the foundation for internationalization support, starting with English and French localization.

# Features details and guidances

## Internationalization Foundation
The GUI should be enhanced to support multiple languages, starting with English and French, with architecture ready for future expansion to 4-5 additional Latin alphabet languages (Spanish, German, Italian, Portuguese).

### Implementation Approach
I suggest implementing Qt's standard internationalization system using:
- **Base Language**: English as the source language for all development
- **Translation System**: Qt's `.ts` and `.qm` file system with `QTranslator`
- **String Management**: All user-visible strings wrapped with `tr()` function
- **Localization Process**: French translation added at the end of development
- **Future Ready**: Architecture supports easy addition of Spanish, German, Italian, Portuguese

### Technical Guidelines
- Use `self.tr("Text")` instead of hardcoded strings throughout the GUI
- Organize translation files in `src/emailer_simple_tool/gui/translations/`
- Implement language selection mechanism in GUI settings
- Ensure proper text layout for different language lengths
- Test UI layout with longer text strings (German/French tend to be longer than English)

## Campaign Tab Enhancements

### UI Layout Structure
```
┌─────────────────────────────────────────────────────────────────┐
│ Campaign Tab                                                    │
├─────────────────────────────────────────────────────────────────┤
│ 📁 Campaign Folder                                              │
│ [Campaign Path________________] [Browse] [Save As] [Create New] │
├─────────────────────────────────┬───────────────────────────────┤
│ 📊 Campaign Status              │ 🔍 Validation Issues          │
│                                 │                               │
│ ❌ Campaign: my_campaign        │ 🚨 Found 2 error(s), 1 warn  │
│    (Has Issues)                 │                               │
│ 👥 Recipients: 47               │ ┌─────────────────────────────┐ │
│ ✅ Subject template found       │ │ ❌ Missing template var     │ │
│ ✅ Message: .docx (formatted)   │ │    {{invalid}} in msg.docx │ │
│ ⚠️ Attachments: 3 files (18MB) │ │                    [📝 Fix] │ │
│ ✅ Picture projects: 1 ready    │ ├─────────────────────────────┤ │
│                                 │ │ ❌ Duplicate email found   │ │
│                                 │ │    in recipients row 23     │ │
│                                 │ │                    [👥 Fix] │ │
│                                 │ ├─────────────────────────────┤ │
│                                 │ │ ⚠️ Large attachment size   │ │
│                                 │ │    report.pdf (15.2MB)     │ │
│                                 │ │                    [📎 Fix] │ │
│                                 │ └─────────────────────────────┘ │
├─────────────────────────────────┼───────────────────────────────┤
│ 👥 Recipients Preview           │ 📄 Subject Line               │
│                                 │                               │
│ [Edit Recipients] [Browse...]   │ [Edit Subject] [Browse...]    │
│                                 │                               │
│ ┌─────────────────────────────┐ │ Subject: Welcome {{name}}!   │
│ │ Name     │ Email    │ City  │ │                               │
│ │ John Doe │ j@ex.com │ NYC   │ │ ═══════════════════════════   │
│ │ Jane S.  │ jane@... │ LA    │ │                               │
│ │ Bob W.   │ bob@...  │ CHI   │ │ 📝 Message Template           │
│ │ ... (44 more recipients)    │ │                               │
│ └─────────────────────────────┘ │ [Edit Message] [Browse...]    │
│                                 │                               │
│                                 │ ┌─────────────────────────────┐ │
│                                 │ │ Dear {{name}},              │ │
│                                 │ │                             │ │
│                                 │ │ Welcome to our event in     │ │
│                                 │ │ {{city}}! Your ticket is    │ │
│                                 │ │ attached.                   │ │
│                                 │ │                             │ │
│                                 │ │ Best regards,               │ │
│                                 │ │ Event Team                  │ │
│                                 │ └─────────────────────────────┘ │
│                                 │                               │
│                                 │ 📎 Attachments                │
│                                 │                               │
│                                 │ [Add] [Open] [Delete]         │
│                                 │                               │
│                                 │ ┌─────────────────────────────┐ │
│                                 │ │ 📄 ticket_template.pdf      │ │
│                                 │ │ 📄 event_info.docx          │ │
│                                 │ │ 📄 venue_map.png            │ │
│                                 │ │                             │ │
│                                 │ │ Total: 3 files (18.2 MB)   │ │
│                                 │ └─────────────────────────────┘ │
└─────────────────────────────────┴───────────────────────────────┘
```

### Enhanced Campaign Management Operations

#### Save As Functionality
The Campaign Tab should provide the ability to save the current loaded campaign to a new location.

##### Description
Users should be able to duplicate an existing campaign to create variations or backups while preserving most configuration and excluding temporary data.

##### Guidances
- **File Copying**: Copy all campaign files and folders EXCEPT:
  - `dryrun/` folder and all its contents
  - `picture-generator/*/data/` folders (generated images)
- **SMTP Preservation**: Preserve encrypted SMTP credentials in the new campaign location
- **User Interface**: Simple "Save As..." button that opens folder selection dialog
- **Destination Selection**: Allow user to select destination folder through standard file dialog
- **Automatic Loading**: After successful save, automatically load the new campaign location
- **Error Handling**: Provide clear error messages for insufficient permissions, disk space, or file conflicts
- **Confirmation**: Show success message with new campaign location path

#### Create New Campaign Wizard
The Campaign Tab should provide a guided wizard for creating campaigns from scratch.

##### Description
A step-by-step wizard that guides users through creating a complete email campaign without requiring knowledge of the folder structure or file naming conventions.

##### Wizard Steps
The wizard should consist of 4 sequential steps with clear navigation and guidance:

**Step 1: Destination Selection**
- **Purpose**: Select where to create the new campaign
- **Interface**: Folder browser dialog with "Create New Folder" option
- **Validation**: Ensure write permissions and sufficient disk space
- **Guidance**: "Select or create a folder where your campaign files will be stored. This folder will contain all your campaign data including recipients, message templates, and attachments."

**Step 2: Recipients Configuration**
- **Purpose**: Import recipient data
- **Interface**: File browser for CSV file selection
- **Processing**: Copy selected CSV file and save as `recipients.csv`
- **Validation**: Basic CSV format validation (headers, email column detection)
- **Guidance**: "Select a CSV file containing your recipients. The file should include an 'email' column and any other data you want to personalize your messages with."

**Step 3: Message and Subject Configuration**
- **Purpose**: Set up email content
- **Message Interface**: File browser for .txt or .docx file selection
- **Subject Interface**: Single-line text input field
- **Processing**: Copy message file as `msg.txt` or `msg.docx`, create `subject.txt` with entered text
- **Validation**: File format validation, template variable checking
- **Guidance**: "Select your message template file and enter the email subject line. You can use {{variable}} syntax to personalize content with recipient data."

**Step 4: Attachments Configuration**
- **Purpose**: Add static attachments
- **Interface**: Multiple file selection browser with file list display
- **Processing**: Copy selected files to `attachments/` folder
- **Validation**: File size warnings, blocked file type warnings
- **Guidance**: "Select any files you want to attach to all emails. These will be the same for every recipient. You can add, remove, or modify attachments later."

##### Wizard Features
- **Navigation**: Next/Previous/Cancel buttons with step validation
- **Progress Indicator**: Visual progress bar or step indicator
- **Validation**: Real-time validation at each step with clear error messages
- **Flexibility Notice**: Inform users at each step that all files and content can be modified after campaign creation
- **Scope Limitation**: Wizard does not include picture generator project setup (reserved for future enhancement)
- **Completion**: Automatic loading of newly created campaign with success confirmation

### External File Editor Integration

#### Recipients CSV Editor Integration
The recipients preview section should provide direct editing capabilities for the CSV file.

##### Description
Users should be able to edit the recipients CSV file using their preferred external application while maintaining live synchronization with the GUI.

##### Guidances
- **Edit Button**: "Edit Recipients" button prominently displayed in recipients preview section
- **External Editor**: Open `recipients.csv` with system default application (Excel, LibreOffice, text editor)
- **File Monitoring**: Implement file system watching to detect when CSV file is saved
- **Auto-Reload**: Automatically refresh recipients preview table when file changes detected
- **Live Validation**: Re-run CSV validation and update campaign status immediately after reload
- **Error Display**: Show specific validation errors in campaign status if CSV becomes invalid
- **User Feedback**: Provide visual indication when file is being edited externally
- **Conflict Handling**: Handle cases where file is locked by external editor during reload attempts

#### Message Template Editor Integration
The message preview section should provide direct editing capabilities for the message template file.

##### Description
Users should be able to edit message templates using their preferred external application with live preview updates.

##### Guidances
- **Edit Button**: "Edit Message" button in message template preview section
- **File Type Support**: Handle both `msg.txt` and `msg.docx` files appropriately
- **External Editor**: Open with system default application for the file type
- **File Monitoring**: Detect changes to message template file
- **Auto-Reload**: Refresh message preview when file is saved externally
- **Live Validation**: Re-validate template variables and format after reload
- **Preview Updates**: Update message preview display to reflect changes
- **Format Handling**: Properly display plain text vs. formatted document indicators

#### Attachment Management Integration
The attachments section should provide comprehensive file management capabilities.

##### Description
Users should be able to manage attachment files directly from the GUI with immediate feedback and validation.

##### Guidances
- **Open Attachment**: Button to open individual attachment files with default system application
- **Add Attachments**: Button to browse and add new attachment files to the campaign
- **Delete Attachments**: Button to remove selected attachments from the campaign
- **File Operations**: 
  - **Add**: Copy selected files to `attachments/` folder with duplicate handling
  - **Delete**: Remove files from `attachments/` folder with confirmation dialog
  - **Open**: Launch files with system default application for editing
- **Live Updates**: Automatically refresh attachment list, file sizes, and total size after any operation
- **Validation Updates**: Re-run attachment validation (size limits, file types) after changes
- **Error Handling**: Display warnings for large files, blocked file types, or operation failures
- **User Feedback**: Show progress indicators for file operations and clear success/error messages

### Subject Line Management

#### Inline Subject Editor
The Campaign Tab should provide direct inline editing of the email subject line to ensure single-line constraint and immediate user feedback.

##### Description
Since email subjects must be single-line text, provide an inline editing experience that prevents multi-line content while offering immediate validation and template support.

##### Guidances
- **Interface**: Single-line text input field integrated into the campaign overview
- **Live Editing**: Changes save automatically to `subject.txt` file
- **Single-Line Enforcement**: Text input prevents line breaks and multi-line content
- **Template Support**: Support {{variable}} syntax with live validation
- **Validation**: Real-time validation of template variables against CSV columns
- **Error Display**: Inline error indicators for invalid template variables
- **Positioning**: Integrate with message template section for logical grouping
- **Auto-Save**: Implement debounced auto-save to prevent excessive file writes
- **Placeholder Text**: Show helpful placeholder when subject is empty
- **Character Limit**: Optional character count display for email subject best practices

### Live Validation and Status Updates

#### Real-Time Campaign Validation
All file editing operations should trigger immediate campaign validation with user feedback.

##### Description
Provide users with immediate feedback about campaign health and validity as they make changes to campaign components.

##### Guidances
- **Validation Triggers**: Run validation after any file modification (CSV, message, subject, attachments)
- **Status Indicators**: Visual indicators (green checkmarks, red X marks, warning triangles) for each campaign component
- **Error Messages**: Specific, actionable error messages for validation failures
- **Warning Messages**: Clear warnings for potential issues (large attachments, missing variables)
- **Performance**: Efficient validation that doesn't block the UI
- **Debouncing**: Prevent excessive validation during rapid file changes
- **Recovery Guidance**: Provide specific steps to resolve validation errors

## Technical Implementation Guidelines

### File System Integration
- **File Monitoring**: Use Qt's `QFileSystemWatcher` for detecting external file changes
- **Process Management**: Use `QProcess` or system calls for launching external editors
- **File Operations**: Implement robust file copying, moving, and deletion with error handling
- **Path Handling**: Ensure cross-platform path handling for Windows, Mac, Linux

### User Interface Design
- **Consistent Styling**: Maintain consistent button styles, spacing, and visual hierarchy
- **Progress Indicators**: Show progress for long-running operations (file copying, validation)
- **Error Presentation**: Use consistent error/warning/success message styling
- **Accessibility**: Ensure keyboard navigation and screen reader compatibility

### Integration with Existing CLI
- **Core Module Reuse**: Leverage existing validation, file processing, and campaign management modules
- **No Code Duplication**: GUI enhancements should use existing business logic
- **CLI Compatibility**: Ensure GUI changes don't affect CLI functionality
- **Shared Configuration**: Use same configuration files and formats as CLI

### Cross-Platform Considerations
- **File Associations**: Respect system file associations for external editor launching
- **Path Separators**: Handle Windows/Unix path differences correctly
- **Permissions**: Handle file permission differences across operating systems
- **File Locking**: Manage file locking behavior differences between platforms

## Installation and Distribution

### GUI Dependencies
The enhanced GUI maintains the existing optional installation approach:
- **CLI Only**: `pip install emailer-simple-tool` (no GUI dependencies)
- **With GUI**: `pip install emailer-simple-tool[gui]` (includes PySide6)
- **Development**: `pip install emailer-simple-tool[all]` (includes all dependencies)

### Translation Files
- **File Organization**: Translation files in `src/emailer_simple_tool/gui/translations/`
- **Build Process**: Include compiled `.qm` files in distribution package
- **Runtime Loading**: Automatic language detection and loading based on system locale
- **Fallback**: Graceful fallback to English if translation files missing

# Documentation
Update all project documentation to reflect the Campaign Tab enhancements:

## User Documentation Updates
- **README.md**: Update with new Campaign Tab features and internationalization support
- **QUICK_START.md**: Include Create New Wizard workflow in quick start guide
- **USER_GUIDE.md**: Add comprehensive section on Campaign Tab enhancements
- **FAQ.md**: Add frequently asked questions about external editor integration and file management

## Technical Documentation
- **PROJECT_STRUCTURE.md**: Document translation file organization and GUI enhancement architecture
- **INSTALLATION.md**: Update with any new dependencies or installation considerations
- **CHANGELOG.md**: Comprehensive changelog entry for Feature Step 6

## Internationalization Documentation
- **Translation Guide**: Instructions for adding new languages and maintaining translations
- **Developer Guide**: Guidelines for adding new translatable strings and UI elements
- **Localization Testing**: Procedures for testing different language layouts and text lengths

The documentation should clearly explain:
- How to use the new Campaign Tab features
- External editor integration workflow
- Create New Wizard step-by-step process
- File management capabilities and limitations
- Troubleshooting common issues with external editors and file operations

# Testing
Provide comprehensive testing for all Campaign Tab enhancements:

## Unit Testing
- **File Operations**: Test file copying, moving, deletion with various scenarios
- **Validation Logic**: Test campaign validation with different file states and contents
- **External Editor Integration**: Mock external process launching and file monitoring
- **Wizard Logic**: Test wizard step validation and campaign creation process

## Integration Testing
- **File System Monitoring**: Test file change detection and auto-reload functionality
- **External Process Management**: Test launching and monitoring external editors
- **Cross-Platform**: Test file operations and editor launching on Windows, Mac, Linux
- **Error Scenarios**: Test handling of locked files, permission errors, disk space issues

## User Interface Testing
- **Wizard Navigation**: Test all wizard steps, validation, and error handling
- **Live Updates**: Test real-time updates of previews and validation status
- **Button Functionality**: Test all new buttons and their associated operations
- **Error Display**: Test error message display and user guidance

## Internationalization Testing
- **Translation Loading**: Test language switching and translation file loading
- **UI Layout**: Test interface layout with different language text lengths
- **Text Encoding**: Test proper handling of accented characters and special symbols
- **Fallback Behavior**: Test graceful fallback when translation files are missing

## Performance Testing
- **File Monitoring**: Test performance impact of file system watching
- **Large Files**: Test handling of large CSV files and attachments
- **Validation Speed**: Test validation performance with complex campaigns
- **Memory Usage**: Monitor memory usage during file operations and external editor integration

Testing should cover:
- All new Campaign Tab functionality
- Integration with existing CLI components
- Cross-platform compatibility
- Error handling and recovery scenarios
- User experience with various file types and sizes
- Internationalization and localization features

==%%*Note for Q Dev CLI: The Campaign Tab enhancements represent a significant improvement in user experience by providing comprehensive campaign management capabilities directly within the GUI. The external editor integration bridges the gap between GUI convenience and power-user flexibility, while the Create New Wizard makes the tool accessible to users who are unfamiliar with the underlying file structure. The internationalization foundation ensures the tool can serve a global user base while maintaining the high-quality user experience established in previous feature steps.*%%==
