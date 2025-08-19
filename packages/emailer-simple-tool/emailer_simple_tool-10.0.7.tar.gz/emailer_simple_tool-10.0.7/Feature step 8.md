# Feature Step 8: Picture Generator Tab GUI Implementation

## Description
For Feature Step 8, the target is to implement a comprehensive and user-friendly GUI for the Picture Generator Tab within the existing emailer-simple-tool interface. This step focuses on making the powerful picture generation capabilities accessible to non-technical users through an intuitive visual interface while maintaining the full functionality and flexibility of the underlying system. The implementation should provide complete project management, file handling, validation, and generation capabilities with crystal-clear guidance for users unfamiliar with technical concepts.

## Features and Guidelines

### Tab Requirements
The Picture Generator Tab should follow the same requirements as other tabs in the application:
- **Resizable Interface**: Full width and height resizing capability
- **Language Localization**: Complete French translation support as primary delivery target
- **Crystal Clear GUI**: Designed specifically for non-technical users with comprehensive guidance
- **Consistent Styling**: Maintain visual consistency with existing Campaign, Send, and SMTP tabs

### Top Section: Project Management

#### Project Selection Dropdown
The tab should provide intelligent project selection based on the number of available projects in the campaign.

##### Dropdown States
- **0 Projects**: Display "No project created yet" with dropdown disabled
- **1 Project**: Auto-select the existing project name and automatically load the project
- **Multiple Projects**: Display "Select the project to load" and require user selection to load a project

##### Project Loading Behavior
When a project is selected from the dropdown, the system should:
- Load all project files and configuration
- Validate project integrity and display status
- Update all interface elements to reflect the loaded project
- Display any validation errors or warnings immediately

#### Project Management Buttons
Three action buttons should be positioned to the right of the dropdown:

##### Create Button
- **Function**: Launch the Create Project Wizard
- **Availability**: Always enabled regardless of current project state
- **Action**: Open modal wizard dialog for step-by-step project creation

##### Duplicate Button
- **Function**: Create a copy of the currently selected project
- **Availability**: Enabled only when a project is selected in the dropdown
- **Behavior**: 
  - Open name input dialog with "Original: [project_name]" display
  - Provide text field for new project name
  - Include "Cancel" and "Validate" buttons
  - Validate that new name doesn't conflict with existing projects
  - Copy entire project folder structure to new location
  - Automatically load the newly created project

##### Delete Button
- **Function**: Remove the currently selected project
- **Availability**: Enabled only when a project is selected in the dropdown
- **Behavior**: 
  - Display confirmation dialog with project name
  - Permanently delete project folder and all contents
  - Update dropdown to reflect remaining projects
  - Reset interface if no projects remain

### Create Project Wizard

#### Wizard Structure
The wizard should follow the same design patterns as the existing Campaign Creation Wizard, providing a consistent user experience across the application.

##### Step 1: Project Basics
- **Project Name**: Text input field for unique project identifier
- **Template Image**: 
  - File browser for template.jpg selection (required)
  - Support for .jpg and .jpeg formats
  - Display selected file name and basic properties
  - Allow replacement through re-browsing
  - Show thumbnail preview of selected template
- **Fusion Configuration**:
  - File browser for existing fusion.csv (optional)
  - "Create Empty" button to generate blank fusion.csv
  - Validate CSV format if provided
  - Display basic CSV information (number of fusion operations)

##### Step 2: Additional Files
- **File Upload Interface**:
  - "Add Files" button for individual file selection
  - "Add Folder" button for bulk folder upload
  - Support for .png, .jpg, .jpeg, .docx, .txt file types
  - Recursive folder processing with OS depth limits
- **File Management**:
  - List view of all uploaded files and folders
  - Individual "Remove" buttons for mistake correction
  - Folder display with file count: "📂 qrcodes/ (25 files)"
  - File type validation and clear error messages
- **Navigation**: Previous/Next/Cancel buttons with step validation

#### Wizard Completion
Upon successful completion:
- Create project folder structure with all selected files
- Generate empty fusion.csv if not provided
- Create default attach.txt with "false" value
- Create empty data/ folder for generated images
- Automatically load the newly created project
- Display success confirmation with project location

### Main Interface Layout

#### UI Layout Structure
```
┌─────────────────────────────────────────────────────────────────┐
│ Picture Generator Tab                                           │
├─────────────────────────────────────────────────────────────────┤
│ [Project Dropdown ▼           ] [Create] [Duplicate] [Delete]   │
├─────────────────────────────────┬───────────────────────────────┤
│ LEFT PANEL                      │ RIGHT PANEL                   │
│ Project Properties              │ Picture Generation            │
│                                 │                               │
│ 📄 fusion.csv    [Browse][Open] │ [🎨 Generate Pictures]       │
│ 🖼️ template.jpg  [Browse][Open] │                               │
│                                 │ ┌─────────────────────────────┐ │
│ Additional Files:               │ │ ⏳ Generating... 15/47     │ │
│ ┌─────────────────────────────┐ │ │ [████████░░] 68%           │ │
│ │ 📄 logo.png        [Open]  │ │ └─────────────────────────────┘ │
│ │ 📂 qrcodes/ (25)   [Open]  │ │                               │
│ │ 📄 header.docx     [Open]  │ │ Generated Images:             │
│ └─────────────────────────────┘ │ ┌─────────────────────────────┐ │
│                                 │ │ ☑️ john_doe.jpg            │ │
│ Email Attachment: ○ Yes ● No    │ │ ☑️ jane_smith.jpg          │ │
│                                 │ │ ☑️ bob_wilson.jpg          │ │
│ ═══════════════════════════════ │ │ ... (44 more files)        │ │
│                                 │ └─────────────────────────────┘ │
│ 📚 User Help & Guidance         │                               │
│ • How to edit fusion.csv        │ [Open Selected Images]        │
│ • Positioning guide (pixels)    │                               │
│ • File reference examples       │ ✅ Generated 47 images        │
│ • Template variables: {{name}}  │    successfully in 12.3s     │
│                                 │                               │
│ 🔍 Validation Panel             │                               │
│ ✅ Template: Valid (640x480)    │                               │
│ ⚠️ fusion.csv: 2 warnings       │                               │
│ │  • Text may extend beyond     │                               │
│ │    template at row 3          │                               │
│ ❌ Missing file: logo2.png      │                               │
│ │  Referenced in fusion row 5   │                               │
└─────────────────────────────────┴───────────────────────────────┘
```

#### Two-Panel Design
The main project editing interface should use a split-panel layout for optimal organization:

##### Left Panel: Project Properties and Guidance
- **Project Properties Section**: File management and configuration
- **User Help Section**: Comprehensive guidance for non-technical users
- **Validation Panel**: Real-time error and warning display

##### Right Panel: Picture Generation
- **Generation Controls**: Trigger and progress display
- **Results Management**: Generated image access and preview

### Left Panel Implementation

#### Project Properties Section

##### Core Project Files
Each core file should have browse and open functionality:

**fusion.csv Management**:
- Display current file name and basic properties
- "Browse" button to replace with new fusion.csv file
- "Open" button to launch file with system default application (Excel, LibreOffice, text editor)
- Real-time validation when file is modified externally
- File system monitoring for automatic reload

**template.jpg Management**:
- Display current template file name and dimensions
- "Browse" button to replace template image
- "Open" button to launch with default image viewer/editor
- Automatic validation of image format and properties
- Boundary validation integration for fusion element checking

##### Additional Files Management
Display comprehensive list of all additional project files:

**File List Display**:
- Individual files: "📄 logo.png [Open]"
- Folders with counts: "📂 qrcodes/ (25 files) [Open]"
- Folder opening launches OS file explorer for bulk management
- File opening uses system default application based on file type

**File Operations**:
- Add new files through browse dialog
- Remove files with confirmation
- Validate file types and accessibility
- Update project validation when files change

##### Email Attachment Control
**attach.txt Widget**:
- Radio button or toggle: "Email Attachment: ○ Yes ● No"
- Automatically updates attach.txt file content
- Clear visual indication of current state
- Integration with campaign sending logic
- Tooltip explanation of functionality

#### User Help Section
Provide comprehensive guidance specifically designed for non-technical users:

##### fusion.csv Editing Guide
- **Purpose Explanation**: "Each row adds one element to your personalized images"
- **Column Descriptions**:
  - fusion-type: "Use 'text' for words, 'graphic' for images, 'formatted-text' for styled documents"
  - data: "Type your text or use {{name}} to insert recipient information"
  - positioning: "Use 'x:y' format - first number moves right, second moves down"
  - size: "Font size for text, 'width:height' for images"
  - alignment: "Choose 'left', 'center', or 'right'"
- **Examples**: Practical examples with real values
- **Common Mistakes**: Frequent errors and how to avoid them

##### Positioning Guide
- **Coordinate System**: "Top-left corner is 0:0"
- **Movement Logic**: "Increase first number to move right, second to move down"
- **Practical Examples**: "100:50 means 100 pixels from left, 50 pixels from top"
- **Boundary Warnings**: Explanation of template size limits

##### File Reference Guide
- **Static Files**: "Use exact file names like 'logo.png'"
- **Personalized Files**: "Use {{column_name}} to reference CSV data"
- **Folder Structure**: "Files can be in subfolders using 'folder/file.png'"

#### Validation Panel
Implement real-time validation with the same behavior as the Campaign Tab:

##### Validation Categories
- **Errors**: Critical issues preventing generation (missing files, invalid CSV format)
- **Warnings**: Potential issues that may affect results (boundary violations, large files)
- **Success**: Confirmation when all validations pass

##### Validation Display
- **Visual Indicators**: Green checkmarks, yellow warning triangles, red error icons
- **Detailed Messages**: Specific, actionable error descriptions
- **Action Buttons**: Direct links to resolve issues where possible
- **Real-time Updates**: Immediate validation when files or configuration change

##### Boundary Validation
Implement the innovative boundary checking system:
- **Template Analysis**: Read template.jpg dimensions automatically
- **Fusion Element Checking**: Validate positioning + size against template boundaries
- **Warning Messages**: "Text 'Welcome {{name}}' may extend beyond image edge at position 500:400"
- **Guidance**: "Reduce font size, adjust position, or use smaller template"

### Right Panel Implementation

#### Picture Generation Controls

##### Generate Pictures Button
- **Primary Action**: Large, prominent button to trigger generation process
- **State Management**: Disabled during generation, enabled when ready
- **Visual Design**: Clear call-to-action styling consistent with application theme

##### Progress Indication
During generation process:
- **Progress Bar**: Visual progress indicator showing completion percentage
- **Status Text**: "Generating images... 15/47 completed"
- **Time Estimation**: Approximate remaining time when possible
- **Cancellation**: Option to abort generation if needed

##### Generation Status Display
**Success Scenario**:
- **Confirmation Message**: "✅ Successfully generated 47 images"
- **Statistics**: Total count, processing time, file size information
- **Next Steps**: Guidance on previewing results or proceeding to email sending

**Failure Scenario**:
- **Error Summary**: "❌ Generation failed: 3 errors found"
- **Detailed Information**: Specific error descriptions with file names and line numbers
- **Resolution Guidance**: Step-by-step instructions to resolve each issue
- **Examples**: 
  - "Missing file 'logo.png' - Add to additional files or update fusion.csv row 2"
  - "Text extends beyond template - Reduce font size in fusion.csv row 5 or adjust position"
  - "Invalid positioning format in row 3 - Use 'x:y' format like '100:200'"

#### Generated Images Management

##### Image List Display
- **Checkbox Selection**: Multi-select capability for batch operations
- **File Information**: Image name, file size, generation timestamp
- **Visual Indicators**: Success/failure status for each image
- **Sorting Options**: By name, date, or recipient order

##### Image Preview Controls
- **Open Selected Images**: Launch selected images in default image viewer
- **Selection Management**: Select all, select none, invert selection options
- **Keyboard Shortcuts**: Standard selection shortcuts (Ctrl+A, Ctrl+click, Shift+click)

##### Data Folder Protection
- **No Direct Access**: Users cannot open the data folder directly
- **Automatic Management**: System handles all file operations
- **Clean Generation**: Each generation flushes previous images automatically
- **Integrity Maintenance**: System ensures file naming consistency with recipients

### Technical Implementation Guidelines

#### File System Integration
- **File Monitoring**: Use Qt's QFileSystemWatcher for external file change detection
- **Process Management**: QProcess for launching external applications
- **Path Handling**: Cross-platform path management for Windows, Mac, Linux
- **File Operations**: Robust copying, validation, and error handling

#### Validation System
- **Real-time Processing**: Immediate validation on file changes
- **Boundary Checking**: Template dimension analysis and fusion element validation
- **CSV Parsing**: Comprehensive fusion.csv format validation
- **File Accessibility**: Verify all referenced files exist and are readable

#### Progress and Status Management
- **Threading**: Background processing for image generation
- **Progress Tracking**: Accurate progress reporting with cancellation support
- **Error Collection**: Comprehensive error logging and user-friendly reporting
- **Memory Management**: Efficient handling of large image processing operations

#### User Interface Design
- **Responsive Layout**: Proper resizing behavior for all screen sizes
- **Accessibility**: Keyboard navigation and screen reader compatibility
- **Visual Hierarchy**: Clear information organization and visual flow
- **Consistent Styling**: Maintain application-wide design standards

### Integration with Existing System

#### CLI Compatibility
- **Shared Core Logic**: Reuse existing picture generation modules
- **Configuration Consistency**: Same file formats and validation rules
- **No Code Duplication**: GUI provides interface layer only

#### Campaign Integration
- **Project Discovery**: Automatic detection of picture generator projects in campaigns
- **Validation Integration**: Picture project validation within campaign validation
- **Email Integration**: Seamless attachment handling based on attach.txt settings

#### Internationalization
- **French Translation**: Complete translation of all user-visible text
- **Help Content**: Translated user guidance and error messages
- **Cultural Adaptation**: French-appropriate examples and explanations
- **Future Expansion**: Architecture ready for additional languages

## Documentation
Update all project documentation to reflect the Picture Generator Tab implementation:

### User Documentation Updates
- **README.md**: Add Picture Generator Tab overview and key features
- **QUICK_START.md**: Include picture generation workflow in quick start guide
- **USER_GUIDE.md**: Comprehensive Picture Generator Tab user guide
- **FAQ.md**: Common questions about picture generation and troubleshooting

### Technical Documentation
- **PROJECT_STRUCTURE.md**: Document Picture Generator Tab architecture
- **INSTALLATION.md**: Any new dependencies or requirements
- **CHANGELOG.md**: Detailed changelog entry for Feature Step 8

### User Guidance Documentation
- **Picture Generation Guide**: Step-by-step tutorial for creating picture projects
- **fusion.csv Reference**: Complete reference guide for fusion configuration
- **Troubleshooting Guide**: Common issues and solutions for picture generation
- **Best Practices**: Recommendations for optimal picture generation workflows

The documentation should clearly explain:
- How to create and manage picture generator projects
- Step-by-step fusion.csv editing instructions
- File management and organization best practices
- Troubleshooting common generation issues
- Integration with email campaign workflows

## Testing
Provide comprehensive testing for all Picture Generator Tab functionality:

### Unit Testing
- **Project Management**: Test creation, duplication, deletion workflows
- **File Operations**: Test browse, open, validation, and monitoring functionality
- **Validation Logic**: Test boundary checking, CSV parsing, and error reporting
- **Generation Process**: Test image generation with various configurations

### Integration Testing
- **External Applications**: Test launching and integration with system applications
- **File System Monitoring**: Test automatic reload when files change externally
- **Campaign Integration**: Test picture project integration with campaign workflows
- **Cross-Platform**: Test functionality on Windows, macOS, and Linux

### User Interface Testing
- **Wizard Functionality**: Test all wizard steps, validation, and error handling
- **Panel Resizing**: Test responsive behavior and layout adaptation
- **Progress Tracking**: Test generation progress display and cancellation
- **Error Display**: Test validation panel and error message presentation

### User Experience Testing
- **Non-Technical Users**: Test interface with target user demographic
- **Workflow Efficiency**: Test complete picture generation workflows
- **Error Recovery**: Test user ability to resolve common issues
- **Help System**: Test effectiveness of built-in user guidance

### Performance Testing
- **Large Projects**: Test with many additional files and complex fusion configurations
- **Batch Generation**: Test generation of large numbers of personalized images
- **Memory Usage**: Monitor resource usage during intensive operations
- **Responsiveness**: Ensure UI remains responsive during background operations

Testing should cover:
- All Picture Generator Tab functionality and user interactions
- Integration with existing CLI and core modules
- Cross-platform compatibility and file system integration
- Error handling and user guidance effectiveness
- Performance with realistic project sizes and complexity

==%%*Note for Q Dev CLI: The Picture Generator Tab represents the culmination of making advanced image personalization accessible to non-technical users. The interface should feel intuitive and provide comprehensive guidance while maintaining the full power and flexibility of the underlying picture generation system. Special attention should be paid to the user help system and validation feedback, as these are critical for user success with this complex feature. The boundary validation system is particularly innovative and should be implemented as a key differentiator that prevents user frustration and improves success rates.*%%==
