# Emailer Simple Tool User Guide

**Send personalized emails to multiple people easily and securely**

## What is Emailer Simple Tool?

Emailer Simple Tool helps you send personalized emails to many people at once. Instead of copying and pasting each person's name and details manually, this tool does it automatically for you.

**Perfect for:**
- Event invitations with personal details
- Newsletter with recipient names
- Business communications to multiple clients
- Any email where you want to include personal information for each recipient

## How It Works (Simple Overview)

1. **Prepare your data**: Create a simple Excel file (saved as CSV) with your recipients' information
2. **Write your email**: Create your email message with placeholders for personal information
3. **Set up email**: Tell the program how to send emails through your email account
4. **Send**: The program creates personalized emails for each person and sends them

## Getting Started

### Step 1: Prepare Your Recipient List

Create a file called `recipients.csv` using Excel or any spreadsheet program:

1. Open Excel (or similar program)
2. Create columns for the information you want to personalize:
   - **email** (required) - the person's email address
   - **name** - the person's name
   - **company** - their company name
   - Add any other columns you need

**Example:**
```
email,name,company,position
john.doe@example.com,John Doe,ACME Corporation,Manager
jane.smith@company.com,Jane Smith,Tech Solutions,Director
```

3. Save the file as "CSV" format (not Excel format)
4. Name it exactly: `recipients.csv`

### Step 2: Write Your Email Message

Create a text file called `msg.txt` with your email content:

1. Open Notepad (Windows) or TextEdit (Mac)
2. Write your email message
3. Use `{{column_name}}` to insert personal information

**Example:**
```
Dear {{name}},

We are pleased to invite you to our annual conference.

As a {{position}} at {{company}}, we believe you would find great value in attending.

Best regards,
Conference Team
```

4. Save as `msg.txt`

### Step 3: Write Your Email Subject

Create a text file called `subject.txt`:

**Example:**
```
Personal invitation for {{name}} - Annual Conference 2025
```

Save as `subject.txt`

### Step 4: Add Attachments (Optional)

If you want to include files with your emails:

1. Create a folder called `attachments` inside your campaign folder
2. Put any files you want to attach in this folder
3. All recipients will receive the same attachments

**Example folder structure:**
```
My Email Campaign/
├── recipients.csv
├── msg.txt
├── subject.txt
└── attachments/
    ├── conference-agenda.pdf
    ├── venue-map.jpg
    └── speaker-bios.docx
```

**Important notes about attachments:**
- Keep total size under 15MB for best delivery
- Avoid file types that might be blocked (.exe, .zip, .bat, etc.)
- Common safe file types: .pdf, .jpg, .png, .docx, .txt

### Step 5: Create Personalized Pictures (Optional)

If you want to create personalized images (like badges, tickets, or certificates) for each recipient:

1. Create a folder called `picture-generator` inside your campaign folder
2. Inside that, create a project folder (e.g., `conference-badge`)
3. Add the required files to your project folder

**Picture Generator Project Structure:**
```
My Email Campaign/
├── recipients.csv          (must use ID as first column, not email)
├── msg.txt
├── subject.txt
└── picture-generator/
    └── conference-badge/   (your project name)
        ├── template.jpg    (base image template)
        ├── fusion.csv      (instructions for personalization)
        ├── attach.txt      (true/false to attach to emails)
        ├── logo.png        (static graphics)
        ├── qr_001.png      (personalized graphics)
        └── data/           (generated pictures appear here)
```

**Important:** Your `recipients.csv` must use an ID (not email) as the first column:
```csv
id,email,name,company
001,john@example.com,John Doe,ACME Corp
002,jane@example.com,Jane Smith,Tech Inc
```

**Creating fusion.csv:**
This file tells the program where to place text and graphics on your template:

```csv
fusion-type,data,positioning,size,alignment
text,"Conference 2025",200:50,32,center
text,"{{name}}",200:120,28,center
text,"{{company}}",200:160,20,center
graphic,logo.png,50:30,80:,left
graphic,{{qr_code_file}},320:250,100:100,center
```

**Column explanations:**
- **fusion-type**: `text` or `graphic`
- **data**: Text to display or graphic filename (use `{{field}}` for personalization)
- **positioning**: `x:y` pixel coordinates (top-left is 0:0)
- **size**: Font size for text, or `width:height` for graphics (use `width:` or `:height` to maintain proportions)
- **alignment**: `left`, `center`, or `right`

**Creating attach.txt:**
Simple file containing either:
- `true` - attach generated pictures to emails
- `false` - don't attach (just generate for other use)

### Step 6: Organize Your Files

Create a folder on your computer and put these files inside:
- `recipients.csv`
- `msg.txt`
- `subject.txt`
- `attachments/` (optional folder for files to attach)

**Example folder structure:**
```
My Email Campaign/
├── recipients.csv
├── msg.txt
├── subject.txt
└── attachments/          (optional)
    ├── document1.pdf
    └── image.jpg
```

## Using the Program

### Setting Up Your Campaign

1. Open Command Prompt (Windows) or Terminal (Mac)
2. Type: `emailer-simple-tool config create "C:\path\to\your\folder"`
   - Replace the path with your actual folder location
3. The program will check your files and tell you if anything needs to be fixed

### Setting Up Your Email Account

1. Type: `emailer-simple-tool config smtp`
2. Enter your email settings:
   - **SMTP Server**: Usually provided by your email provider
   - **Port**: Usually 587 or 465
   - **Username**: Your email address
   - **Password**: Your email password (or app password)

**Common Email Settings:**

**Gmail:**
- Server: `smtp.gmail.com`
- Port: `587`
- Security: TLS
- Note: You need to use an "App Password" instead of your regular password

**Outlook/Hotmail:**
- Server: `smtp-mail.outlook.com`
- Port: `587`
- Security: TLS

**Yahoo:**
- Server: `smtp.mail.yahoo.com`
- Port: `587`
- Security: TLS

### Generating Personalized Pictures

If you created picture generator projects:

1. Type: `emailer-simple-tool picture generate`
2. Select your project if you have multiple
3. The program creates personalized images for each recipient
4. Generated pictures are saved in the `data/` folder

### Testing Before Sending (Recommended)

Before sending real emails, test your setup:

1. Type: `emailer-simple-tool send --dry-run`
2. The program creates sample emails in a "dryrun" folder
3. Open these files to see exactly what will be sent
4. Check that names and information are correctly inserted

### Sending Your Emails

When you're ready to send:

1. Type: `emailer-simple-tool send`
2. The program will ask for confirmation
3. Type `y` and press Enter to send
4. Watch as emails are sent to each recipient

## Troubleshooting Common Issues

### "Invalid email address"
- Check your CSV file for typos in email addresses
- Make sure all email addresses have @ symbol and domain (like .com)

### "SMTP connection failed"
- Check your internet connection
- Verify your email server settings
- For Gmail: Make sure you're using an App Password, not your regular password
- Contact your email provider if problems persist

### "Template reference not found"
- Make sure the names in `{{}}` exactly match your CSV column headers
- Check for typos (case-sensitive)
- Example: If your CSV has "Name" but template uses "{{name}}", it won't work

### "Email size too large"
- Check total size of attachments (should be under 15MB)
- Remove or compress large files
- Consider sending multiple smaller emails instead

### "Potentially blocked file type"
- Some email providers block certain file types (.exe, .zip, etc.)
- Try renaming the file extension or compressing differently
- Use cloud storage links instead of direct attachments for risky files

### "Primary key cannot be 'email'"
- Change your CSV so the first column is an ID, not email address
- Example: Use `id,email,name` instead of `email,name,id`
- IDs should be simple (001, 002, etc.) for filename compatibility

### "Template file is not a valid JPEG"
- Make sure your template.jpg is actually a JPEG image file
- Try opening it in an image viewer to verify it's not corrupted
- Re-save from an image editor if needed

### "Fusion file missing" or CSV errors
- Check that fusion.csv exists in your project folder
- Verify all required columns are present
- Check for typos in column names and data formats

### "Graphic file not found"
- Make sure PNG files referenced in fusion.csv exist in the project folder
- Check filename spelling and case sensitivity
- For personalized graphics, ensure files exist for all recipients

## Security Notes

- Your email password is stored securely and encrypted
- Only you can access your campaign folder and credentials
- Delete the campaign folder when done to remove stored passwords

## Tips for Success

1. **Start Small**: Test with 2-3 recipients first
2. **Check Spelling**: Double-check names and email addresses
3. **Preview First**: Always use dry-run before sending
4. **Keep It Simple**: Don't use too many personalization fields at first
5. **Backup Your Data**: Keep a copy of your recipient list

## Getting Help

If you encounter problems:

1. Check this guide first
2. Look at the example files in the `examples` folder
3. Use the dry-run feature to test your setup
4. Contact your IT support if email server issues persist

## Example: Complete Setup

Here's a complete example for a conference invitation with attachments:

**Folder structure:**
```
Conference Invitation/
├── recipients.csv
├── subject.txt
├── msg.txt
└── attachments/
    ├── conference-agenda.pdf
    └── venue-info.txt
```

**recipients.csv:**
```
email,name,company,position
john@company.com,John Smith,ABC Corp,Manager
mary@business.com,Mary Johnson,XYZ Ltd,Director
```

**subject.txt:**
```
Conference Invitation for {{name}}
```

**msg.txt:**
```
Dear {{name}},

We are excited to invite you to our Technology Conference 2025.

As a {{position}} at {{company}}, we believe this event will provide valuable insights for your work.

Please find the conference agenda and venue information attached.

Please reply by March 15th to confirm your attendance.

Best regards,
Conference Organizing Committee
```

This setup will send personalized emails to John and Mary with their specific names, companies, and positions automatically inserted, plus the agenda and venue information attached to each email.
