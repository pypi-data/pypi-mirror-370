# Emailer Simple Tool - Complete User Documentation

**Send personalized emails to multiple people easily and securely**

---

## Table of Contents

1. [What is Emailer Simple Tool?](#what-is-emailer-simple-tool)
2. [Installation](#installation)
3. [Quick Start (5 minutes)](#quick-start-5-minutes)
4. [Complete User Guide](#complete-user-guide)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting & FAQ](#troubleshooting--faq)
7. [Performance & Limits](#performance--limits)

---

## What is Emailer Simple Tool?

Emailer Simple Tool is a simple application that enables users to send personalized emails to a list of recipients through an intuitive command-line interface.

### Core Features
- **Email Personalization**: Customize email subject and message body using recipient data from CSV files
- **Rich Text Support**: Use formatted .docx files with fonts, colors, and styles
- **Picture Generation**: Create personalized images with text and graphics
- **Static Attachments**: Attach documents to all emails in a campaign
- **Campaign Management**: Save, reopen, and manage email campaigns using a folder-based structure
- **Data Validation**: Comprehensive validation of recipient data and email templates
- **Dry Run Testing**: Preview generated emails as .eml files before sending
- **SMTP Troubleshooting**: Built-in guidance for email delivery issues

### Perfect For
- Event invitations with personal details
- Newsletters with recipient names
- Business communications to multiple clients
- Marketing campaigns with personalized images
- Any email where you want to include personal information for each recipient

---

## Installation

### For Windows Users

#### Method 1: Simple Installation (Recommended)

1. **Download Python** (if not already installed):
   - Go to https://python.org/downloads
   - Click "Download Python" (latest version)
   - Run the installer
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

2. **Install Emailer Simple Tool**:
   - Press `Windows Key + R`
   - Type `cmd` and press Enter
   - In the black window that opens, type:
     ```
     pip install emailer-simple-tool
     ```
   - Press Enter and wait for installation to complete

3. **Verify Installation**:
   ```
   emailer-simple-tool --version
   ```

### For Mac Users

1. **Install Python** (if not already installed):
   - Download from https://python.org/downloads
   - Or use Homebrew: `brew install python`

2. **Install Emailer Simple Tool**:
   ```bash
   pip3 install emailer-simple-tool
   ```

3. **Verify Installation**:
   ```bash
   emailer-simple-tool --version
   ```

### For Linux Users

1. **Install Python** (usually pre-installed):
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Install Emailer Simple Tool**:
   ```bash
   pip3 install emailer-simple-tool
   ```

3. **Verify Installation**:
   ```bash
   emailer-simple-tool --version
   ```

---

## Quick Start (5 minutes)

### What You Need
- A folder on your computer
- A list of email addresses (can be from Excel)
- Your email account information

### Step 1: Create Your Files (2 minutes)

**Create a folder** called "My Email Campaign" on your desktop.

**Inside this folder, create 3 files:**

**File 1: `recipients.csv`** (your email list)
```csv
email,name,company
john@example.com,John Smith,ACME Corp
jane@example.com,Jane Doe,Tech Inc
bob@example.com,Bob Johnson,Design Co
```

**File 2: `subject.txt`** (your email subject)
```
Welcome {{name}} to our event!
```

**File 3: `msg.txt`** (your email message)
```
Dear {{name}},

We're excited to invite you from {{company}} to our special event.

Best regards,
The Event Team
```

### Step 2: Set Up Your Campaign (1 minute)

Open your command prompt/terminal and navigate to your folder:
```bash
cd "Desktop/My Email Campaign"
emailer-simple-tool config create .
```

### Step 3: Configure Email Settings (1 minute)

```bash
emailer-simple-tool config smtp
```

Follow the prompts to enter your email settings:
- **Gmail**: smtp.gmail.com, port 587, use app password
- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587

### Step 4: Test and Send (1 minute)

**Test first** (creates preview files):
```bash
emailer-simple-tool send --dry-run
```

**Send for real**:
```bash
emailer-simple-tool send
```

🎉 **Done!** Your personalized emails are sent!

---

## Complete User Guide

### Campaign Structure

Every email campaign is organized in a folder with these files:

```
My Campaign/
├── recipients.csv          # Required: List of recipients
├── subject.txt            # Required: Email subject line
├── msg.txt or msg.docx    # Required: Email message
├── attachments/           # Optional: Files to attach
│   ├── document.pdf
│   └── image.jpg
└── picture-generator/     # Optional: Personalized images
    └── my-project/
        ├── template.jpg
        ├── fusion.csv
        └── data/
```

### Recipients File (recipients.csv)

This CSV file contains your recipient list. The first row defines column names, which you can use as variables in your messages.

**Basic Example:**
```csv
email,name,company
john@example.com,John Smith,ACME Corp
jane@example.com,Jane Doe,Tech Inc
```

**Advanced Example:**
```csv
email,name,company,event_date,ticket_type
john@example.com,John Smith,ACME Corp,2024-03-15,VIP
jane@example.com,Jane Doe,Tech Inc,2024-03-15,Standard
```

**Rules:**
- First column must be `email`
- Column names become variables: `{{name}}`, `{{company}}`
- No spaces in column names (use underscores: `event_date`)
- Save as CSV format from Excel

### Message Files

#### Simple Text Messages (msg.txt)
```
Dear {{name}},

Welcome to our event on {{event_date}}.
Your {{ticket_type}} ticket is confirmed.

Best regards,
Event Team
```

#### Rich Formatted Messages (msg.docx)
Create a Word document with:
- **Fonts**: Different fonts, sizes, colors
- **Formatting**: Bold, italic, underline
- **Tables**: Structured data
- **Images**: Static images (logos, etc.)
- **Variables**: Use `{{name}}` anywhere in the document

**Example formatted message:**
- Title in large, bold, blue text: "Welcome {{name}}!"
- Body in regular text with company name in red: "From {{company}}"
- Footer with italic contact information

### Subject Line (subject.txt)
```
Event Invitation for {{name}} - {{event_date}}
```

### Attachments
Place any files you want to attach in the `attachments/` folder:
- PDFs, Word documents, images
- All files will be attached to every email
- Keep total size under 25MB per email

### Command Reference

#### Campaign Management
```bash
# Create/load a campaign
emailer-simple-tool config create /path/to/campaign

# Show current campaign status
emailer-simple-tool config show

# Switch to different campaign
emailer-simple-tool config create /path/to/other/campaign
```

#### SMTP Configuration
```bash
# Configure email settings
emailer-simple-tool config smtp

# Test email connection
emailer-simple-tool config smtp --test
```

#### Sending Emails
```bash
# Preview emails (creates .eml files)
emailer-simple-tool send --dry-run

# Send emails for real
emailer-simple-tool send

# Send with custom delay between emails
emailer-simple-tool send --delay 2
```

#### Picture Generation
```bash
# List picture projects
emailer-simple-tool picture list

# Generate pictures for a project
emailer-simple-tool picture generate project-name

# Generate all picture projects
emailer-simple-tool picture generate-all
```

---

## Advanced Features

### Picture Generation

Create personalized images for each recipient with text, graphics, and formatting.

#### Setting Up Picture Projects

1. **Create project folder:**
   ```
   picture-generator/
   └── my-invitation/
       ├── template.jpg      # Background image
       ├── fusion.csv        # Instructions
       └── data/            # Generated images appear here
   ```

2. **Create template image** (`template.jpg`):
   - Background image (JPG, PNG)
   - Any size, recommended 800x600 or larger

3. **Create fusion instructions** (`fusion.csv`):
   ```csv
   fusion-type,data,positioning,size,alignment,orientation,policy,shape,color
   text,{{name}},100:50,24,center,0,Arial,bold,red
   text,{{company}},100:100,16,center,0,Helvetica,italic,blue
   formatted-text,invitation.docx,50:200,400:200,left,0,,,
   ```

#### Fusion Types

**Text Fusion:**
- `fusion-type`: `text`
- `data`: Text to display (can use `{{variables}}`)
- `positioning`: `x:y` coordinates
- `size`: Font size in points
- `alignment`: `left`, `center`, `right`
- `font`: Font family (`Arial`, `Helvetica`, `Courier`, `Monaco`)
- `shape`: Font style (`bold`, `italic`, `bold italic`)
- `color`: Text color (`red`, `blue`, `green`, `black`, etc.)

**Formatted Text Fusion:**
- `fusion-type`: `formatted-text`
- `data`: Path to .docx file with rich formatting
- `positioning`: `x:y` coordinates for top-left corner
- `size`: `width:height` of rendered area
- `alignment`: `left`, `center`, `right`

**Graphic Fusion:**
- `fusion-type`: `graphic`
- `data`: Path to image file (can use `{{variables}}` for personalized images)
- `positioning`: `x:y` coordinates
- `size`: `width:height` or single value for proportional scaling

#### Example: Event Invitation

**Template:** Background image with event theme
**Fusion instructions:**
```csv
fusion-type,data,positioning,size,alignment,orientation,font,shape,color
text,Welcome {{name}}!,400:100,32,center,0,Arial,bold,white
text,{{company}},400:150,18,center,0,Arial,,white
text,Event Date: March 15 2024,400:300,16,center,0,Courier,,yellow
formatted-text,event-details.docx,50:400,700:200,left,0,,,
```

### Rich Text Messages (.docx)

Use Microsoft Word to create formatted email messages:

1. **Create Word document** with formatting:
   - Fonts, colors, sizes
   - Bold, italic, underline
   - Tables and lists
   - Static images

2. **Add variables** anywhere: `{{name}}`, `{{company}}`

3. **Save as .docx** in campaign folder as `msg.docx`

4. **Preview with dry run** - creates .eml files you can open in email client

### Email Preview (.eml files)

When you run `--dry-run`, the system creates .eml files that you can:
- Double-click to open in your email client
- Preview exactly how emails will look
- Check formatting, images, and personalization
- Verify before sending

---

## Troubleshooting & FAQ

### General Questions

**Q: Do I need to be technical to use this?**
A: No! If you can use Excel and email, you can use this tool.

**Q: Is it safe to use?**
A: Yes. Your email passwords are encrypted and stored only on your computer.

**Q: How many emails can I send?**
A: Designed for up to 100 recipients per campaign. For larger lists, break into smaller groups.

### Email Provider Settings

**Gmail:**
- Server: `smtp.gmail.com`
- Port: `587`
- Security: Use App Password (not regular password)
- Enable 2-factor authentication first

**Outlook/Hotmail:**
- Server: `smtp-mail.outlook.com`
- Port: `587`
- Use regular password

**Yahoo:**
- Server: `smtp.mail.yahoo.com`
- Port: `587`
- Use App Password

**Corporate Email:**
- Contact your IT department for SMTP settings

### Common Issues

**"Authentication failed"**
- Check username/password
- For Gmail: Use App Password
- Enable "Less secure apps" if needed

**"Connection refused"**
- Check server address and port
- Verify internet connection
- Try different port (25, 465, 587)

**"File not found"**
- Check file paths in fusion.csv
- Ensure all referenced files exist
- Use forward slashes in paths

**"Template variables not replaced"**
- Check spelling: `{{name}}` not `{name}`
- Ensure column exists in recipients.csv
- No spaces in column names

**Pictures not generating**
- Check template image exists
- Verify fusion.csv format
- Ensure positioning coordinates are within image bounds

### Performance Tips

- Keep recipient lists under 100 for best performance
- Use `--delay` option for large lists
- Optimize image sizes (under 1MB recommended)
- Test with small groups first

---

## Performance & Limits

### Tested Performance
- **Picture Generation**: 180 images/second
- **Email Processing**: 478 emails/second
- **Concurrent Operations**: 976 emails/second

### Recommended Limits
- **Recipients**: Up to 100 per campaign
- **Attachments**: Total size under 25MB
- **Images**: Under 1MB each for best performance
- **Email Rate**: Use delays for large lists to avoid provider limits

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 512MB available RAM
- **Storage**: 100MB for installation + campaign data
- **Network**: Internet connection for sending emails

---

## Support

For issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Test with small recipient lists first
4. Verify all file paths and formats

**Remember**: Always test with `--dry-run` before sending real emails!

---

*Emailer Simple Tool - Making personalized email campaigns simple and accessible.*
