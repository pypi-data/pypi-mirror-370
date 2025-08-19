#!/usr/bin/env python3
"""
Find ALL remaining English text - fixed version
"""

import sys
import os
sys.path.insert(0, 'src')

from PySide6.QtWidgets import QApplication, QFormLayout
from emailer_simple_tool.gui.main_window import EmailerMainWindow
from emailer_simple_tool.gui.translation_manager import translation_manager

def find_all_english_text():
    """Find ALL English text systematically"""
    
    app = QApplication([])
    window = EmailerMainWindow()
    
    print("🔍 COMPREHENSIVE ENGLISH TEXT DETECTION")
    print("=" * 70)
    
    # Set to French
    translation_manager.set_language('fr')
    window.refresh_translations()
    
    english_found = []
    
    print("\n📸 PICTURE TAB - DETAILED SCAN:")
    picture_tab = window.picture_tab
    
    # Picture tab specific checks
    checks = [
        ("Help text content", picture_tab.help_text.text() if hasattr(picture_tab.help_text, 'text') else ""),
        ("Validation group title", picture_tab.validation_group.title() if hasattr(picture_tab.validation_group, 'title') else ""),
        ("Generation group title", picture_tab.generation_group.title() if hasattr(picture_tab.generation_group, 'title') else ""),
        ("Images group title", picture_tab.images_group.title() if hasattr(picture_tab.images_group, 'title') else ""),
        ("Generate button text", picture_tab.generate_button.text() if hasattr(picture_tab.generate_button, 'text') else ""),
        ("Validation content", picture_tab.validation_content.text() if hasattr(picture_tab.validation_content, 'text') else ""),
    ]
    
    for name, text in checks:
        if text and has_english_words(text):
            english_found.append(f"Picture Tab - {name}: {repr(text[:100])}")
            print(f"  ❌ {name}: {repr(text[:100])}...")
    
    print("\n📧 SMTP TAB - DETAILED SCAN:")
    smtp_tab = window.smtp_tab
    
    # SMTP tab specific checks
    smtp_checks = [
        ("Guidance HTML content", smtp_tab.guidance_text.toHtml() if hasattr(smtp_tab.guidance_text, 'toHtml') else ""),
        ("Form labels", ""),  # Will check separately
    ]
    
    # Check guidance HTML
    if hasattr(smtp_tab.guidance_text, 'toHtml'):
        html_content = smtp_tab.guidance_text.toHtml()
        if has_english_words(html_content):
            english_found.append(f"SMTP Tab - Guidance HTML: Contains English")
            print(f"  ❌ Guidance HTML: Contains English content")
    
    # Check form labels
    if hasattr(smtp_tab, 'config_group') and smtp_tab.config_group:
        layout = smtp_tab.config_group.layout()
        if layout and isinstance(layout, QFormLayout):
            for i in range(layout.rowCount()):
                label_item = layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget():
                    label_text = label_item.widget().text()
                    if label_text and has_english_words(label_text):
                        english_found.append(f"SMTP Tab - Form label {i}: {repr(label_text)}")
                        print(f"  ❌ Form label {i}: {repr(label_text)}")
    
    app.quit()
    
    print(f"\n📊 SUMMARY:")
    print(f"Found {len(english_found)} English text elements")
    
    return english_found

def has_english_words(text):
    """Check if text contains English words"""
    if not text or len(text.strip()) == 0:
        return False
    
    # Key English words that indicate untranslated content
    english_words = [
        'How to use', 'Editing', 'Each line', 'fusion-type', 'Use ', 'text for text',
        'graphic for images', 'Type your text', 'insert recipient', 'positioning',
        'first number moves', 'second moves down', 'Font size for text',
        'Choose ', 'left', 'center', 'right', 'Positioning Guide', 'Top-left corner',
        'Increase first number', 'move right', 'move down', 'pixels from left',
        'pixels from top', 'File References', 'Static files', 'exact names',
        'Personalized files', 'reference CSV data', 'Folder structure',
        'subfolders', 'Template Variables', 'any column from', 'recipients.csv',
        'Variables will be replaced', 'actual recipient data',
        'Validation Panel', 'Picture Generation', 'Generated Images',
        'Generate Pictures', 'No project loaded',
        'SMTP Server', 'Username', 'Password', 'Port',
        'Quick Setup', 'Manual Setup', 'Security', 'Always use',
        'secure connections', 'popular email providers', 'app password',
        'not your regular password', 'Microsoft account credentials',
        'La Poste email credentials', 'Go to Campaign tab',
        'select a folder first', 'Configuration Help',
        'Current Campaign', 'Auto-Save', 'automatically saved',
        'fill all required fields', 'server, username, password',
        'buttons on the left', 'Enter your email', 'SMTP settings manually',
        'No Campaign Loaded', 'Please select', 'campaign folder first',
        'test SMTP connections', 'settings won\'t be saved',
        'without a campaign', 'To save settings'
    ]
    
    text_lower = text.lower()
    
    for word in english_words:
        if word.lower() in text_lower:
            return True
    
    return False

if __name__ == "__main__":
    english_items = find_all_english_text()
    
    print(f"\n🔧 IDENTIFIED ISSUES TO FIX:")
    for item in english_items:
        print(f"  - {item}")
    
    if english_items:
        print(f"\n❌ TOTAL: {len(english_items)} English elements found")
        print("🔧 Creating comprehensive fix...")
    else:
        print(f"\n✅ SUCCESS: No English text found!")
