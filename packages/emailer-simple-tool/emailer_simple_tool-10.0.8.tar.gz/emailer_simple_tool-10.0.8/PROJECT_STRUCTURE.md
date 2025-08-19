# Emailer Simple Tool Project Structure

This document describes the comprehensive file structure of the emailer-simple-tool application.

## Directory Structure

```
emailer-simple-tool/
├── src/                          # Source code
│   └── emailer_simple_tool/     # Main package
│       ├── __init__.py          # Package initialization (v5.0.0)
│       ├── cli.py               # CLI entry point (RClone-inspired)
│       ├── core/                # Core functionality
│       │   ├── __init__.py
│       │   ├── campaign_manager.py  # Campaign management
│       │   ├── email_sender.py      # Email sending logic
│       │   └── picture_generator.py # Picture generation (Step 3)
│       ├── utils/               # Utility modules
│       │   ├── __init__.py
│       │   ├── credential_manager.py  # Secure SMTP credentials
│       │   ├── validators.py         # Data validation
│       │   ├── template_processor.py # Email template processing
│       │   ├── smtp_helper.py        # SMTP operations
│       │   ├── logger.py            # Logging utilities
│       │   ├── document_processor.py # .docx processing (Step 4)
│       │   ├── email_formatter.py   # Email formatting (Step 4)
│       │   └── global_config.py     # Global configuration
│       └── gui/                 # 🆕 Graphical User Interface (Step 5)
│           ├── __init__.py      # GUI module entry point
│           ├── main_window.py   # Main GUI application window
│           └── tabs/            # Individual GUI tab components
│               ├── __init__.py
│               ├── campaign_tab.py   # Campaign management tab
│               ├── smtp_tab.py       # SMTP configuration tab
│               ├── picture_tab.py    # Picture generator management tab
│               └── send_tab.py       # Email sending and dry run tab
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_campaign_manager.py
│   ├── test_validators.py
│   ├── test_email_sender.py
│   ├── test_picture_generator.py
│   ├── test_document_processor.py
│   ├── test_email_formatter.py
│   ├── test_feature_step4.py
│   ├── test_attachment_validation.py
│   ├── test_formatted_text_rendering.py
│   ├── test_font_policies.py
│   └── test_campaign_manager_docx.py
├── prototypes/                  # Development prototypes
│   └── gui_initial/            # Initial GUI prototypes
├── QChat/                      # Development session logs
├── .samples/                   # Sample campaigns
│   ├── sample-campaign/
│   ├── inao-2025/
│   ├── test-campaign-step4/
│   ├── test-performance-25/
│   ├── test-performance-50/
│   └── test-performance-100/
│       ├── recipients.csv
│       ├── msg.txt
│       └── subject.txt
├── docs/                        # Documentation (future)
├── setup.py                     # Package setup
├── requirements.txt             # Core dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                  # Test configuration
├── Makefile                     # Development commands
├── .gitignore                   # Git ignore rules
├── Readme.md                    # Main documentation
├── Feature step 1.md           # Feature specification
├── Feature step 2.md           # Feature specification
└── PROJECT_STRUCTURE.md        # This file
```

## Core Components

### CLI Interface (`cli.py`)
- RClone-inspired command structure
- Subcommands: `config`, `send`
- Entry point for all user interactions

### Campaign Manager (`core/campaign_manager.py`)
- Campaign creation and loading
- SMTP configuration management
- Campaign validation orchestration

### Email Sender (`core/email_sender.py`)
- Email composition and sending
- Dry run functionality
- Template processing integration

### Utilities (`utils/`)
- **credential_manager.py**: Secure SMTP credential storage using encryption
- **validators.py**: Comprehensive validation for CSV, templates, and campaign structure
- **template_processor.py**: Email template processing with {{field}} substitution
- **smtp_helper.py**: SMTP connection testing and email sending
- **logger.py**: Logging configuration and utilities

## Campaign Folder Structure

When users create a campaign, the following structure is expected/created:

```
user-campaign-folder/
├── recipients.csv               # Required: Recipient data
├── msg.txt                     # Required: Email message template
├── subject.txt                 # Required: Email subject template
├── smtp-credentials.enc        # Created: Encrypted SMTP settings
├── .smtp-key                   # Created: Encryption key (hidden)
├── .emailer-config.json        # Created: Campaign configuration
├── logs/                       # Created: Application logs
│   └── emailer-YYYY-MM-DD.log
└── dryrun/                     # Created: Dry run outputs
    ├── YYYY-MM-DD_HH-MM-SS/    # Timestamped dry runs
    └── custom-name/            # Named dry runs
```

## Development Workflow

### Installation
```bash
make install-dev    # Install with development dependencies
```

### Testing
```bash
make test          # Run tests
make test-cov      # Run tests with coverage
```

### Code Quality
```bash
make lint          # Run linting
make format        # Format code
```

### Building
```bash
make build         # Build distribution packages
```

## Key Design Principles

1. **OS Agnostic**: Works on Windows, macOS, and Linux
2. **User-Friendly**: Designed for non-technical users
3. **Secure**: Encrypted credential storage
4. **Modular**: Clear separation of concerns
5. **Testable**: Comprehensive test coverage
6. **Extensible**: Easy to add new features (Step 2, 3, etc.)

## Template System

Uses `{{field}}` syntax for template substitution:
- Easy for non-technical users
- Clear visual distinction
- Allows literal `{` and `}` in text
- Validates against CSV columns

## Error Handling

- Comprehensive validation with clear error messages
- User-friendly troubleshooting guidance
- Graceful handling of network issues
- Detailed logging for debugging

## Future Extensions

The structure is designed to easily accommodate:
- Static attachments (Feature Step 2)
- Personalized PDF generation (Feature Step 3+)
- Additional template formats
- Enhanced SMTP provider support
- GUI interface (potential future enhancement)
