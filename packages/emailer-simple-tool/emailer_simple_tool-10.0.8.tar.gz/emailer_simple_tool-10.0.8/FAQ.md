# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is Emailer Simple Tool?
**A:** It's a simple tool that helps you send personalized emails to multiple people at once. Instead of manually typing each person's name and details, the program does it automatically.

### Q: Do I need to be technical to use this?
**A:** No! It's designed for regular computer users. If you can use Excel and email, you can use this tool.

### Q: Is it safe to use?
**A:** Yes. Your email passwords are encrypted and stored only on your computer. No information is sent to external servers except for sending your emails through your email provider.

### Q: How many emails can I send?
**A:** The tool is designed for up to 100 recipients per campaign. For larger lists, consider breaking them into smaller groups.

## Setup Questions

### Q: What email providers work with this?
**A:** Most email providers work, including:
- Gmail (most common)
- Outlook/Hotmail
- Yahoo Mail
- Corporate email systems
- Most other SMTP-enabled email services

### Q: Why can't I use my regular email password?
**A:** Many email providers (like Gmail) require "App Passwords" for security. This is a special password just for applications like this one.

### Q: How do I get an App Password for Gmail?
**A:** 
1. Go to your Google Account settings
2. Enable 2-factor authentication first
3. Go to Security → App passwords
4. Generate a new app password for "Mail"
5. Use this password instead of your regular one

### Q: What if I don't know my SMTP settings?
**A:** Common settings:
- **Gmail**: smtp.gmail.com, port 587
- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- For others, search online for "[your email provider] SMTP settings"

## File Questions

### Q: What is a CSV file?
**A:** It's a simple text file that stores data in columns, like a basic Excel spreadsheet. You can create it by saving an Excel file as "CSV" format.

### Q: Can I use Excel instead of CSV?
**A:** You need to save your Excel file as CSV format. In Excel: File → Save As → Choose "CSV" format.

### Q: What does {{name}} mean in the templates?
**A:** These are placeholders that get replaced with actual data. If your CSV has a "name" column, {{name}} will be replaced with each person's name.

### Q: Can I use different column names?
**A:** Yes! Just make sure the names in {{}} exactly match your CSV column headers. For example, if your column is "FirstName", use {{FirstName}}.

## Error Messages

### Q: "Invalid email address" - what does this mean?
**A:** Check your CSV file for:
- Typos in email addresses
- Missing @ symbols
- Incomplete addresses (like "john@" without the domain)

### Q: "Template reference not found" - what's wrong?
**A:** The name inside {{}} doesn't match any column in your CSV. Check:
- Spelling (case-sensitive)
- Exact match with column headers
- No extra spaces

### Q: "SMTP connection failed" - how do I fix this?
**A:** Try these steps:
1. Check your internet connection
2. Verify your email server settings
3. Make sure you're using an App Password (not regular password)
4. Try a different port (587 or 465)

### Q: "Duplicate email found" - what should I do?
**A:** Remove duplicate email addresses from your CSV file. Each person should appear only once in your list.

## Usage Questions

### Q: What is a "dry run"?
**A:** It creates sample emails without actually sending them. This lets you preview exactly what will be sent before sending real emails.

### Q: Can I stop sending emails once I've started?
**A:** Yes, press Ctrl+C to stop the program. Emails already sent cannot be recalled, but remaining emails won't be sent.

### Q: Can I send the same campaign multiple times?
**A:** Yes, but be careful not to spam recipients. The program doesn't track who has already received emails.

### Q: Where are my files stored?
**A:** Everything is stored in the campaign folder you created. This includes:
- Your original files (CSV, templates)
- Encrypted email settings
- Dry run results
- Log files

## Troubleshooting

### Q: The program says "command not found"
**A:** The installation might not be complete. Try:
1. Restart your command prompt/terminal
2. Check if Python is installed: `python --version`
3. Reinstall: `pip install emailer-simple-tool`

### Q: My personalized text isn't showing up
**A:** Check that:
- Column names in CSV exactly match template placeholders
- No typos in {{field}} names
- CSV file is properly formatted

### Q: Emails are going to spam folders
**A:** This is common with bulk emails. Tips:
- Use a professional email address
- Avoid spam-trigger words
- Keep email content relevant and personal
- Consider asking recipients to add you to their contacts

### Q: Can I include attachments?
**A:** Yes! Create an "attachments" folder in your campaign folder and put any files you want to attach there. All recipients will receive the same attachments.

### Q: What file types can I attach?
**A:** Most file types work, but some may be blocked by email providers:
- **Safe**: .pdf, .docx, .jpg, .png, .txt, .xlsx
- **Risky**: .exe, .zip, .bat, .scr (may be blocked)
- The program will warn you about potentially blocked files

### Q: How large can my attachments be?
**A:** Keep total attachment size under 15MB for best delivery. The program will warn you:
- **15MB+**: Warning about potential delivery issues
- **20MB+**: Strong warning about delivery failures
- Different email providers have different limits

### Q: Why are my emails going to spam folders?
**A:** 
1. Start with 2-3 test recipients (maybe your own email addresses)
2. Use the dry-run feature first
3. Send to test recipients before the full list
4. Check that personalization works correctly

### Q: What's the best way to organize my campaigns?
**A:** 
- Create separate folders for different campaigns
- Use descriptive folder names (like "Conference-2025-Invites")
- Keep backup copies of your CSV files
- Delete old campaigns when no longer needed

### Q: Any tips for writing good email templates?
**A:** 
- Keep it personal but professional
- Don't use too many personalization fields at once
- Test with different types of data
- Make sure the email makes sense even if some fields are empty
- If using attachments, mention them in your message

### Q: What's the best way to handle large files?
**A:**
- Keep attachments under 15MB total
- Compress large files when possible
- Consider using cloud storage links for very large files
- Split large campaigns into smaller batches if needed

### Q: How do I know if my attachments will be delivered?
**A:**
- Use the dry-run feature to check attachment sizes
- Test with a small group first
- Avoid file types commonly blocked by email providers
- Check with recipients if they received attachments

## Getting More Help

### Q: Where can I find examples?
**A:** Check the `examples/sample-campaign/` folder that comes with the installation.

### Q: What if I'm still having problems?
**A:** 
1. Check the [User Guide](USER_GUIDE.md) for detailed instructions
2. Try the [Quick Start Guide](QUICK_START.md) for a simple example
3. Look at the example files
4. Contact your IT support for email server issues
