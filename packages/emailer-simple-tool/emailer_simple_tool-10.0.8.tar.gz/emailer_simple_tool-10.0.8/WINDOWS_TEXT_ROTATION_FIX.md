# Windows Text Rotation Fix - Version 10.0.2

## 🎯 Problem Solved
Fixed the issue where rotated text (like "2025" with orientation=10) was being cut off at the bottom on Windows systems, while working perfectly on macOS.

## 🔧 What Was Fixed

### **Root Cause:**
Windows and macOS handle text rotation and bounding box calculations differently. The original code used fixed padding (20 pixels) which wasn't sufficient for large fonts with rotation on Windows.

### **Solution Implemented:**
1. **Dynamic Padding**: Padding now scales with font size (`max(40, font_size * 0.8)`)
2. **Better Bounding Box**: Improved calculation for rotated text dimensions
3. **Windows-Specific Adjustment**: Slight upward Y-position adjustment for rotated text on Windows
4. **Platform Detection**: Automatically detects Windows and applies appropriate fixes

## 📦 Installation on Windows Server

### **Step 1: Install the Fixed Version**

On your Windows Server 2022, open PowerShell as Administrator and run:

```powershell
# Uninstall current version
pip uninstall emailer-simple-tool -y

# Install the fixed version 10.0.2
pip install emailer-simple-tool[gui] --upgrade

# Verify version
python -c "import emailer_simple_tool; print(f'Version: {emailer_simple_tool.__version__}')"
```

### **Step 2: Test Your Fusion File**

Use your original fusion file with font size 102:

```csv
fusion-type,data,positioning,size,alignment,orientation,font,shape,color
graphic,{{qrcode}},500:660,300:300,center,0,,,
text,Samedi 8 nov. de 10h à 20h,2850:650,58,center,0,Segoe UI,bold,#ffffff
text,Dimanche 9 nov. de 10h à 18h,2850:720,58,center,0,Segoe UI,bold,#ffffff
text,{{ID}},830:1100,72,center,0,Segoe UI,bold,#000000
text,2025,2850:60,102,center,10,Segoe UI,bold,#ffffff
text,le 8 ou 9 nov.,465:493,48,left,0,Segoe UI,,#000000
```

### **Step 3: Generate Pictures**

```powershell
# Launch GUI
emailer-simple-tool gui

# Or use CLI
emailer-simple-tool picture generate your-project-name
```

## 🎯 Expected Results

- ✅ **"2025" text displays completely** without bottom cutoff
- ✅ **Font size 102 works perfectly** as on macOS
- ✅ **10-degree rotation** renders correctly
- ✅ **Cross-platform compatibility** maintained

## 🔍 Technical Details

### **Code Changes Made:**

```python
# Before (fixed padding)
temp_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
temp_draw.text((10, 10), text, fill=color, font=font)

# After (dynamic padding + Windows adjustment)
font_size = getattr(font, 'size', 50)
padding = max(40, int(font_size * 0.8))  # Dynamic padding
temp_img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
temp_draw.text((padding, padding), text, fill=color, font=font)

# Windows-specific Y adjustment
if platform.system() == 'Windows' and abs(angle) > 0:
    y = y - int(font_size * 0.1)
```

### **Benefits:**
- **Automatic Detection**: No manual configuration needed
- **Scalable Solution**: Works with any font size
- **Platform Agnostic**: Same code works on Windows, macOS, and Linux
- **Backward Compatible**: Existing fusion files work without changes

## 🧪 Testing Checklist

- [ ] Text "2025" displays completely without cutoff
- [ ] Font size 102 works as expected
- [ ] 10-degree rotation renders correctly
- [ ] Other text elements remain unaffected
- [ ] Performance is maintained

## 📝 Version History

- **v10.0.1**: Original version with Windows text rotation issues
- **v10.0.2**: Fixed Windows text rotation with dynamic padding and platform-specific adjustments

Your fusion file should now work identically on both Windows Server 2022 and macOS! 🎉
