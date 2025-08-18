# Quick Start Guide

**Get up and running with Emailer Simple Tool in 5 minutes**

## 🎯 Choose Your Interface

### **🎨 Graphical Interface (Recommended for beginners)**
Perfect if you prefer point-and-click over typing commands.

### **⌨️ Command Line Interface (For advanced users)**
Perfect for automation, scripting, or if you're comfortable with terminals.

---

## 🎨 Quick Start - Graphical Interface

### **Step 1: Install with GUI Support**
```bash
pip install emailer-simple-tool[gui]
```

### **Step 2: Launch GUI**
```bash
emailer-simple-tool gui
```

### **Step 3: Use the Visual Interface**
1. **📁 Campaign Tab**: Click "Browse" to select your campaign folder
2. **📧 SMTP Tab**: Fill in your email settings (Gmail, Outlook, etc.)
3. **🖼️ Pictures Tab**: Generate personalized images (if needed)
4. **🚀 Send Tab**: Test with dry run, then send your campaign

**That's it!** The GUI guides you through each step visually.

---

## ⌨️ Quick Start - Command Line Interface

### **Step 1: Install**
```bash
pip install emailer-simple-tool
```

### **Step 2: Create Campaign**
```bash
emailer-simple-tool config create /path/to/your/campaign
```

### **Step 3: Configure Email**
```bash
emailer-simple-tool config smtp
```

### **Step 4: Test First**
```bash
emailer-simple-tool send --dry-run
```

### **Step 5: Send Emails**
```bash
emailer-simple-tool send
```

---

## 📁 Campaign Folder Setup

Create a folder with these files:

### **Required Files**
- **`recipients.csv`** - Your email list
  ```csv
  id,email,name
  001,john@example.com,John Doe
  002,jane@example.com,Jane Smith
  ```

- **`subject.txt`** - Email subject
  ```
  Hello {{name}}, your invitation is ready!
  ```

- **`msg.txt`** - Email message
  ```
  Dear {{name}},
  
  Your personalized invitation is attached.
  
  Best regards,
  The Team
  ```

### **Optional Folders**
- **`attachments/`** - Files to attach to all emails
- **`picture-generator/`** - For personalized image generation

---

## 📧 Email Provider Setup

### **Gmail**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password (not your regular password)

### **Outlook/Hotmail**
1. Use your regular email password
2. May need to enable "Less secure app access"

### **Yahoo**
1. Generate App Password in Account Security
2. Use App Password for authentication

---

## 🎨 GUI vs CLI Comparison

| Feature | GUI | CLI |
|---------|-----|-----|
| **Ease of Use** | ✅ Point and click | ⚠️ Requires commands |
| **Visual Preview** | ✅ See data/templates | ❌ Text only |
| **Progress Tracking** | ✅ Progress bars | ✅ Text output |
| **Automation** | ❌ Manual operation | ✅ Scriptable |
| **Server Use** | ❌ Needs display | ✅ Headless friendly |
| **Learning Curve** | ✅ Intuitive | ⚠️ Commands to learn |

---

## 🚀 Next Steps

### **For GUI Users**
1. Launch: `emailer-simple-tool gui`
2. Follow the visual workflow through each tab
3. Use dry run to test before sending

### **For CLI Users**
1. Read the [User Guide](USER_GUIDE.md) for detailed commands
2. Check [FAQ](FAQ.md) for common questions
3. Explore advanced features in the documentation

### **For Developers**
```bash
# Install with all development tools
pip install -e .[all]

# Run tests
pytest

# Launch GUI for testing
emailer-simple-tool gui
```

---

## 🆘 Need Help?

- **GUI Issues**: Make sure you installed with `[gui]`: `pip install emailer-simple-tool[gui]`
- **Command Not Found**: Check Python is in PATH, restart terminal
- **Email Problems**: Verify SMTP settings, check provider documentation
- **More Help**: Check [FAQ](FAQ.md) or [Documentation](DOCUMENTATION.md)

---

**🎉 You're ready to send personalized emails!**

Choose your preferred interface and start creating professional email campaigns.
