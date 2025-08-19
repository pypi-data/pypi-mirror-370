# Installation Guide

**How to install Emailer Simple Tool on your computer**

## 🎯 Installation Options

### **CLI Only (Minimal)**
For command-line use only, smaller download:
```bash
pip install emailer-simple-tool
```

### **With GUI Support (Recommended)**
For both command-line and graphical interface:
```bash
pip install emailer-simple-tool[gui]
```

### **From Source Code**
If you have the source code folder:
```bash
cd /path/to/emailer-simple-tool
pip install -e ".[gui]"
```

**Note for macOS/zsh users**: Use quotes around `".[gui]"` to avoid shell globbing issues.

## For Windows Users

### Method 1: Simple Installation (Recommended)

1. **Download Python** (if not already installed):
   - Go to https://python.org/downloads
   - Click "Download Python" (latest version)
   - Run the installer
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

2. **Install Emailer Simple Tool**:
   - Press `Windows Key + R`
   - Type `cmd` and press Enter
   - In the black window that opens, choose your installation:
   
   **For GUI support (recommended):**
   ```
   pip install emailer-simple-tool[gui]
   ```
   
   **For CLI only:**
   ```
   pip install emailer-simple-tool
   ```

3. **Test Installation**:
   - Type: `emailer-simple-tool --version`
   - You should see the version number
   - For GUI: `emailer-simple-tool gui`

### Method 2: From Source Code

If you have the source code folder:

1. Open Command Prompt
2. Navigate to the emailer-simple-tool folder:
   ```
   cd C:\path\to\emailer-simple-tool
   ```
3. Install with GUI support:
   ```
   pip install -e .[gui]
   ```

## For Mac Users

### Method 1: Simple Installation (Recommended)

1. **Install Python** (if not already installed):
   - Download from https://python.org/downloads
   - Run the installer
   - Python is usually pre-installed on Mac, but you might need a newer version

2. **Open Terminal**:
   - Press `Cmd + Space`
   - Type "Terminal" and press Enter

3. **Install Emailer Simple Tool**:
   
   **For GUI support (recommended):**
   ```bash
   pip install emailer-simple-tool[gui]
   ```
   
   **For CLI only:**
   ```bash
   pip install emailer-simple-tool
   ```

4. **Test Installation**:
   ```bash
   emailer-simple-tool --version
   emailer-simple-tool gui  # If you installed GUI support
   ```

### Method 2: From Source Code

1. Open Terminal
2. Navigate to the source folder:
   ```bash
   cd /path/to/emailer-simple-tool
   ```
3. Install with GUI support:
   ```bash
   pip install -e .[gui]
   ```

## For Linux Users

### Method 1: Simple Installation

1. **Open Terminal** (usually Ctrl+Alt+T)

2. **Install Python and pip** (if not already installed):
   ```bash
   # Ubuntu/Debian:
   sudo apt update
   sudo apt install python3 python3-pip
   
   # CentOS/RHEL:
   sudo yum install python3 python3-pip
   
   # Fedora:
   sudo dnf install python3 python3-pip
   ```

3. **Install Emailer Simple Tool**:
   
   **For GUI support (recommended):**
   ```bash
   pip install emailer-simple-tool[gui]
   ```
   
   **For CLI only:**
   ```bash
   pip install emailer-simple-tool
   ```

4. **Test Installation**:
   ```bash
   emailer-simple-tool --version
   emailer-simple-tool gui  # If you installed GUI support
   ```

### Method 2: From Source Code

1. Open Terminal
2. Navigate to the source folder:
   ```bash
   cd /path/to/emailer-simple-tool
   ```
3. Install with GUI support:
   ```bash
   pip install -e .[gui]
   ```

## 🎨 GUI vs CLI

### **Command Line Interface (CLI)**
- Perfect for automation and scripting
- Smaller installation size
- Works on servers without display
- Commands like: `emailer-simple-tool config create /path/to/campaign`

### **Graphical User Interface (GUI)**
- User-friendly visual interface
- No command line knowledge required
- Perfect for non-technical users
- Launch with: `emailer-simple-tool gui`

## 🔧 Development Installation

For developers who want to modify the code:

```bash
# Clone or download the source code
cd /path/to/emailer-simple-tool

# Install in development mode with all dependencies
pip install -e .[all]

# This includes:
# - GUI support (PySide6)
# - Development tools (pytest, black, flake8, mypy)
# - Editable installation (changes are immediately available)
```

## ⚠️ Troubleshooting

### **zsh Shell Issues (macOS)**
If you get `zsh: no matches found: .[gui]`:
```bash
# Use quotes to fix zsh globbing:
pip install -e ".[gui]"

# Or escape the brackets:
pip install -e .\[gui\]
```

### **"Command not found" Error**
- Make sure Python is in your PATH
- Try `python -m emailer_simple_tool.cli` instead
- Restart your terminal/command prompt

### **GUI Won't Launch**
- Make sure you installed with `[gui]`: `pip install emailer-simple-tool[gui]`
- Check if PySide6 is installed: `pip list | grep PySide6`
- Try: `pip install PySide6` manually

### **Permission Errors**
- On Mac/Linux, try: `pip install --user emailer-simple-tool[gui]`
- On Windows, run Command Prompt as Administrator

### **Python Version Issues**
- Emailer Simple Tool requires Python 3.8 or higher
- Check your version: `python --version`
- Update Python if needed

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space
- **Internet**: Required for email sending and initial installation

## 🎉 Verification

After installation, verify everything works:

```bash
# Check version
emailer-simple-tool --version

# See available commands
emailer-simple-tool --help

# Launch GUI (if installed with GUI support)
emailer-simple-tool gui

# Test with a sample campaign
emailer-simple-tool config create /path/to/test/campaign
```

## 📚 Next Steps

After installation:
1. Read the [User Guide](USER_GUIDE.md) for detailed usage instructions
2. Check out [Quick Start](QUICK_START.md) for a fast introduction
3. Browse the [FAQ](FAQ.md) for common questions

---

**Need help?** Check the [FAQ](FAQ.md) or create an issue on GitHub.
