# Emailer Simple Tool

**Send personalized emails to multiple people easily and securely**

Emailer Simple Tool is a simple application that enables users to send personalized emails to a list of recipients through both command-line and graphical interfaces.

## 🚀 Quick Start

### **With Graphical Interface (Recommended for most users)**
```bash
# Install with GUI support
pip install emailer-simple-tool[gui]

# Launch graphical interface
emailer-simple-tool gui
```

### **Command Line Interface (For automation & advanced users)**
```bash
# Install CLI only
pip install emailer-simple-tool

# Create campaign
emailer-simple-tool config create /path/to/campaign

# Configure email
emailer-simple-tool config smtp

# Test first
emailer-simple-tool send --dry-run

# Send emails
emailer-simple-tool send
```

### **From Source Code**
```bash
# Clone/download source code, then:
cd emailer-simple-tool
pip install -e ".[gui]"

# Launch GUI
emailer-simple-tool gui
```

## 📚 Complete Documentation

**Choose your language:**

- 🇺🇸 **[English Documentation](DOCUMENTATION_EN.md)** - Complete user guide in English
- 🇫🇷 **[Documentation Française](DOCUMENTATION_FR.md)** - Guide utilisateur complet en français
- 📋 **[Documentation Index](DOCUMENTATION.md)** - Language selection and quick reference

## ✨ Key Features

- **Dual Interface**: Choose between graphical (GUI) or command-line (CLI) interface
- **🎨 Picture Generator Tab**: Complete GUI for creating personalized images with wizard-guided project creation
- **Email Personalization**: Use CSV data to customize emails with `{{variables}}`
- **Rich Text Support**: Create formatted emails with .docx files
- **Picture Generation**: Generate personalized images with text and graphics through intuitive GUI
- **Attachments**: Add files to all emails in a campaign
- **Dry Run Testing**: Preview emails as .eml files before sending
- **Campaign Management**: Organize campaigns in folders with comprehensive GUI tools
- **Cross-Platform**: Works on Windows, Mac, and Linux

## 🎯 Perfect For

- Event invitations with personal details
- Newsletters with recipient names  
- Business communications to multiple clients
- Marketing campaigns with personalized images
- Any email requiring personal information for each recipient

## 🖥️ Interface Options

### **🎨 Graphical Interface (GUI)**
- **Perfect for**: Non-technical users, visual workflow
- **Features**: Point-and-click interface, visual previews, progress bars
- **Install**: `pip install emailer-simple-tool[gui]`
- **Launch**: `emailer-simple-tool gui`

### **⌨️ Command Line Interface (CLI)**
- **Perfect for**: Automation, scripting, advanced users
- **Features**: Fast execution, scriptable, server-friendly
- **Install**: `pip install emailer-simple-tool`
- **Usage**: `emailer-simple-tool config create /path/to/campaign`

## 📁 Campaign Structure

```
My Campaign/
├── recipients.csv          # Email list with data
├── subject.txt            # Email subject line
├── msg.txt or msg.docx    # Email message (plain or formatted)
├── attachments/           # Files to attach (optional)
└── picture-generator/     # Personalized images (optional)
```

## 🔧 System Requirements

- Python 3.8 or higher
- Internet connection for sending emails
- 512MB available RAM
- 100MB storage space

## 📖 Documentation

For complete installation instructions, user guides, troubleshooting, and advanced features, please refer to the documentation in your preferred language:

- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide for all platforms
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Start here for language selection
- **[DOCUMENTATION_EN.md](DOCUMENTATION_EN.md)** - Complete English guide
- **[DOCUMENTATION_FR.md](DOCUMENTATION_FR.md)** - Guide complet en français

## 🆘 Quick Help

```bash
emailer-simple-tool --help           # General help
emailer-simple-tool config --help    # Campaign management help
emailer-simple-tool send --help      # Email sending help
emailer-simple-tool picture --help   # Picture generation help
emailer-simple-tool gui              # Launch graphical interface
```

## ⚡ Performance

- **Picture Generation**: 180 images/second
- **Email Processing**: 478 emails/second  
- **Recommended**: Up to 100 recipients per campaign

## 🛡️ Security

- Email passwords encrypted and stored locally only
- No data sent to external servers except for email delivery
- All processing happens on your computer

---

**Get started now**: Read the [complete documentation](DOCUMENTATION.md) in your language!

*Emailer Simple Tool - Making personalized email campaigns simple and accessible.*
