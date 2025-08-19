#!/usr/bin/env python3
"""
Find ALL remaining English text in Picture and SMTP tabs
"""

import sys
import os
sys.path.insert(0, 'src')

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QCheckBox, QLineEdit, QTextEdit, QGroupBox
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
    
    print("\n📸 PICTURE TAB - SCANNING ALL ELEMENTS:")
    picture_tab = window.picture_tab
    
    # Scan all widgets recursively
    def scan_widget(widget, path=""):
        if hasattr(widget, 'text') and callable(widget.text):
            text = widget.text()
            if text and has_english_words(text):
                english_found.append(f"Picture Tab - {path}: {repr(text)}")
                print(f"  ❌ {path}: {repr(text)}")
        
        if hasattr(widget, 'title') and callable(widget.title):
            title = widget.title()
            if title and has_english_words(title):
                english_found.append(f"Picture Tab - {path} (title): {repr(title)}")
                print(f"  ❌ {path} (title): {repr(title)}")
        
        if hasattr(widget, 'placeholderText') and callable(widget.placeholderText):
            placeholder = widget.placeholderText()
            if placeholder and has_english_words(placeholder):
                english_found.append(f"Picture Tab - {path} (placeholder): {repr(placeholder)}")
                print(f"  ❌ {path} (placeholder): {repr(placeholder)}")
        
        if hasattr(widget, 'toHtml') and callable(widget.toHtml):
            html = widget.toHtml()
            if html and has_english_words(html):
                english_found.append(f"Picture Tab - {path} (HTML): {repr(html[:100])}...")
                print(f"  ❌ {path} (HTML): {repr(html[:100])}...")
        
        # Recursively scan children
        if hasattr(widget, 'children'):
            for i, child in enumerate(widget.children()):
                if hasattr(child, 'text') or hasattr(child, 'title'):
                    scan_widget(child, f"{path}.child[{i}]")
    
    # Scan specific Picture tab elements
    elements_to_check = [
        ("fusion_open_btn", picture_tab.fusion_open_btn),
        ("template_open_btn", picture_tab.template_open_btn),
        ("open_additional_file_btn", picture_tab.open_additional_file_btn),
        ("open_selected_btn", picture_tab.open_selected_btn),
        ("attachment_label", picture_tab.attachment_label),
        ("attachment_checkbox", picture_tab.attachment_checkbox),
        ("help_group", picture_tab.help_group),
        ("validation_group", picture_tab.validation_group),
        ("generation_group", picture_tab.generation_group),
        ("images_group", picture_tab.images_group),
        ("help_text", picture_tab.help_text),
        ("validation_content", picture_tab.validation_content),
        ("generation_status", picture_tab.generation_status),
    ]
    
    for name, widget in elements_to_check:
        if widget:
            scan_widget(widget, name)
    
    print("\n📧 SMTP TAB - SCANNING ALL ELEMENTS:")
    smtp_tab = window.smtp_tab
    
    # Scan specific SMTP tab elements
    smtp_elements = [
        ("test_button", smtp_tab.test_button),
        ("save_button", smtp_tab.save_button),
        ("gmail_btn", smtp_tab.gmail_btn),
        ("outlook_btn", smtp_tab.outlook_btn),
        ("laposte_btn", smtp_tab.laposte_btn),
        ("config_group", smtp_tab.config_group),
        ("presets_group", smtp_tab.presets_group),
        ("test_group", smtp_tab.test_group),
        ("guidance_group", smtp_tab.guidance_group),
        ("smtp_server", smtp_tab.smtp_server),
        ("smtp_username", smtp_tab.smtp_username),
        ("smtp_password", smtp_tab.smtp_password),
        ("use_tls", smtp_tab.use_tls),
        ("guidance_text", smtp_tab.guidance_text),
        ("test_result", smtp_tab.test_result),
    ]
    
    for name, widget in smtp_elements:
        if widget:
            scan_widget(widget, name)
    
    # Also check form labels in SMTP
    if hasattr(smtp_tab, 'config_group') and smtp_tab.config_group:
        layout = smtp_tab.config_group.layout()
        if layout and hasattr(layout, 'rowCount'):
            for i in range(layout.rowCount()):
                label_item = layout.itemAt(i, layout.LabelRole)
                if label_item and label_item.widget():
                    label_text = label_item.widget().text()
                    if label_text and has_english_words(label_text):
                        english_found.append(f"SMTP Tab - form_label[{i}]: {repr(label_text)}")
                        print(f"  ❌ form_label[{i}]: {repr(label_text)}")
    
    app.quit()
    
    print(f"\n📊 SUMMARY:")
    print(f"Found {len(english_found)} English text elements")
    
    if english_found:
        print(f"\n❌ ENGLISH TEXT STILL PRESENT:")
        for item in english_found:
            print(f"  - {item}")
    else:
        print(f"\n✅ NO ENGLISH TEXT FOUND!")
    
    return english_found

def has_english_words(text):
    """Check if text contains English words"""
    if not text or len(text.strip()) == 0:
        return False
    
    # Common English words that shouldn't appear in French UI
    english_indicators = [
        'Click', 'Test', 'Save', 'Open', 'Browse', 'Create', 'Delete', 'Duplicate',
        'Configuration', 'Connection', 'Settings', 'Help', 'Guidance', 'Setup',
        'Quick', 'Manual', 'Security', 'Password', 'Username', 'Server', 'Port',
        'Email', 'Attachment', 'Generate', 'Pictures', 'Images', 'Files', 'Folder',
        'Project', 'Campaign', 'Validation', 'Error', 'Success', 'Failed',
        'How to use', 'Editing', 'Positioning', 'Template', 'Variables',
        'Gmail', 'Outlook', 'requires', 'credentials', 'automatically', 'saved',
        'providers', 'connections', 'folder', 'first', 'select', 'load'
    ]
    
    text_lower = text.lower()
    
    # Check for English indicators
    for indicator in english_indicators:
        if indicator.lower() in text_lower:
            return True
    
    # Check for common English patterns
    english_patterns = [
        'use ', 'the ', 'and ', 'for ', 'with ', 'your ', 'you ', 'are ', 'is ',
        'to ', 'of ', 'in ', 'on ', 'at ', 'by ', 'from ', 'up ', 'about ',
        'into ', 'through ', 'during ', 'before ', 'after ', 'above ', 'below ',
        'between ', 'among ', 'under ', 'over ', 'inside ', 'outside ', 'without '
    ]
    
    for pattern in english_patterns:
        if pattern in text_lower:
            return True
    
    return False

if __name__ == "__main__":
    english_items = find_all_english_text()
    
    if english_items:
        print(f"\n🔧 NEXT STEP: Fix all {len(english_items)} English text elements")
    else:
        print(f"\n🎉 SUCCESS: No English text found!")
