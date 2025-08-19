"""
Campaign Tab - Campaign management and overview
"""

import os
import csv
import shutil
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, 
    QFileDialog, QMessageBox, QGroupBox, QSplitter, QDialog,
    QWizard, QWizardPage, QListWidget, QProgressBar, QCheckBox,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QFileSystemWatcher, Signal, QCoreApplication
from PySide6.QtGui import QFont


class CampaignTab(QWidget):
    """Campaign management and overview tab"""
    
    # Signal emitted when campaign is loaded or changed
    campaign_changed = Signal(str)  # Emits campaign path
    campaign_cleared = Signal()     # Emitted when no campaign is loaded
    
    def __init__(self, campaign_manager):
        super().__init__()
        self.campaign_manager = campaign_manager
        self.current_campaign_path = None
        
        # File system watcher for external editor integration
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        
        # Track current files being watched
        self.watched_files = set()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize campaign tab UI"""
        layout = QVBoxLayout()
        
        # Campaign folder selection
        folder_group = QGroupBox(self.tr("📁 Campaign Folder"))
        self.folder_group = folder_group  # Store reference for translation updates
        folder_layout = QVBoxLayout()
        
        # Folder selection row
        folder_row = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText(self.tr("Select your campaign folder..."))
        self.folder_path.setReadOnly(True)
        
        browse_button = QPushButton(self.tr("Browse..."))
        browse_button.clicked.connect(self.browse_folder)
        browse_button.setStyleSheet("QPushButton { background-color: #6c757d; }")
        self.browse_button = browse_button  # Store reference for translation updates
        
        # Campaign management buttons
        save_as_button = QPushButton(self.tr("Save As..."))
        save_as_button.clicked.connect(self.save_campaign_as)
        save_as_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        save_as_button.setEnabled(False)  # Disabled until campaign loaded
        self.save_as_button = save_as_button
        
        create_new_button = QPushButton(self.tr("Create New..."))
        create_new_button.clicked.connect(self.create_new_campaign)
        create_new_button.setStyleSheet("QPushButton { background-color: #007bff; }")
        self.create_new_button = create_new_button  # Store reference for translation updates
        
        folder_row.addWidget(self.folder_path)
        folder_row.addWidget(browse_button)
        folder_row.addWidget(save_as_button)
        folder_row.addWidget(create_new_button)
        
        folder_layout.addLayout(folder_row)
        folder_group.setLayout(folder_layout)
        
        # Campaign status and validation overview (side by side)
        status_validation_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Campaign status overview
        status_group = QGroupBox(self.tr("📊 Campaign Status"))
        self.status_group = status_group  # Store reference for translation updates
        status_layout = QVBoxLayout()
        
        # Add scroll area for status content
        status_scroll = QScrollArea()
        status_scroll.setWidgetResizable(True)
        status_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        status_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create widget for status content
        status_content_widget = QWidget()
        status_content_layout = QVBoxLayout()
        
        self.status_overview = QLabel(self.tr("No campaign loaded"))
        self.status_overview.setStyleSheet("color: #6c757d; font-size: 14px; padding: 10px;")
        self.status_overview.setWordWrap(True)
        
        status_content_layout.addWidget(self.status_overview)
        status_content_widget.setLayout(status_content_layout)
        status_scroll.setWidget(status_content_widget)
        
        status_layout.addWidget(status_scroll)
        status_group.setLayout(status_layout)
        
        # Right side - Validation issues panel (initially hidden)
        self.validation_panel = self.create_validation_panel()
        
        # Add to splitter
        status_validation_splitter.addWidget(status_group)
        status_validation_splitter.addWidget(self.validation_panel)
        # Set more reasonable sizes - validation panel needs more space to be visible
        status_validation_splitter.setSizes([500, 400])  # Increased validation panel size
        status_validation_splitter.setStretchFactor(0, 1)  # Status can stretch
        status_validation_splitter.setStretchFactor(1, 0)  # Validation panel fixed size
        
        # Create splitter for side-by-side content
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Recipients preview
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        recipients_group = QGroupBox(self.tr("👥 Recipients Preview"))
        self.recipients_group = recipients_group  # Store reference for translation updates
        recipients_layout = QVBoxLayout()
        
        # Recipients edit button
        recipients_button_layout = QHBoxLayout()
        edit_recipients_button = QPushButton(self.tr("Edit Recipients"))
        self.edit_recipients_button = edit_recipients_button  # Store reference for translation updates
        edit_recipients_button.clicked.connect(self.edit_recipients)
        edit_recipients_button.setStyleSheet("QPushButton { background-color: #17a2b8; }")
        edit_recipients_button.setEnabled(False)
        self.edit_recipients_button = edit_recipients_button
        
        browse_recipients_button = QPushButton(self.tr("Browse..."))
        browse_recipients_button.clicked.connect(self.browse_recipients)
        browse_recipients_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        browse_recipients_button.setEnabled(False)
        self.browse_recipients_button = browse_recipients_button
        
        recipients_button_layout.addWidget(edit_recipients_button)
        recipients_button_layout.addWidget(browse_recipients_button)
        recipients_button_layout.addStretch()
        
        self.recipients_table = QTableWidget()
        # Remove fixed height restrictions to allow table to resize with parent panel
        # self.recipients_table.setMinimumHeight(400)  # Removed to allow flexible sizing
        self.recipients_table.setAlternatingRowColors(True)
        
        # Configure scroll behavior - scrollbars appear when needed
        self.recipients_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recipients_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recipients_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.recipients_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        
        # Allow table to resize with parent
        from PySide6.QtWidgets import QSizePolicy
        self.recipients_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # Horizontal expansion
            QSizePolicy.Policy.Expanding   # Vertical expansion
        )
        
        # Initialize with placeholder content
        self.init_empty_recipients_table()
        
        recipients_layout.addLayout(recipients_button_layout)
        recipients_layout.addWidget(self.recipients_table, 1)  # Add stretch factor of 1 to make table expand
        recipients_group.setLayout(recipients_layout)
        
        left_layout.addWidget(recipients_group, 1)  # Add stretch factor to make recipients group expand
        # Removed validation panel from left side - it's now in the top section
        left_widget.setLayout(left_layout)
        
        # Right side - Message, subject, and attachments preview
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Create scroll area for right side content
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget for right side
        right_content_widget = QWidget()
        right_content_layout = QVBoxLayout()
        
        # Subject line editor (external editor pattern)
        subject_group = QGroupBox(self.tr("📄 Subject Line"))
        self.subject_group = subject_group  # Store reference for translation updates
        subject_layout = QVBoxLayout()
        
        # Subject edit button
        subject_button_layout = QHBoxLayout()
        edit_subject_button = QPushButton(self.tr("Edit Subject"))
        edit_subject_button.clicked.connect(self.edit_subject)
        edit_subject_button.setStyleSheet("QPushButton { background-color: #17a2b8; }")
        edit_subject_button.setEnabled(False)
        self.edit_subject_button = edit_subject_button
        
        browse_subject_button = QPushButton(self.tr("Browse..."))
        browse_subject_button.clicked.connect(self.browse_subject)
        browse_subject_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        browse_subject_button.setEnabled(False)
        self.browse_subject_button = browse_subject_button
        
        subject_button_layout.addWidget(edit_subject_button)
        subject_button_layout.addWidget(browse_subject_button)
        subject_button_layout.addStretch()
        
        # Subject preview display
        self.subject_preview = QLabel()
        self.subject_preview.setStyleSheet("QLabel { padding: 8px; border: 1px solid #ccc; background-color: #f8f9fa; }")
        self.subject_preview.setWordWrap(True)
        self.subject_preview.setText(self.tr("No subject loaded"))
        
        subject_layout.addLayout(subject_button_layout)
        subject_layout.addWidget(self.subject_preview)
        subject_group.setLayout(subject_layout)
        
        # Message preview
        message_group = QGroupBox(self.tr("📝 Message Template"))
        self.message_group = message_group  # Store reference for translation updates
        message_layout = QVBoxLayout()
        
        # Message edit button
        message_button_layout = QHBoxLayout()
        edit_message_button = QPushButton(self.tr("Edit Message"))
        edit_message_button.clicked.connect(self.edit_message)
        edit_message_button.setStyleSheet("QPushButton { background-color: #17a2b8; }")
        edit_message_button.setEnabled(False)
        self.edit_message_button = edit_message_button
        
        browse_message_button = QPushButton(self.tr("Browse..."))
        browse_message_button.clicked.connect(self.browse_message)
        browse_message_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        browse_message_button.setEnabled(False)
        self.browse_message_button = browse_message_button
        
        message_button_layout.addWidget(edit_message_button)
        message_button_layout.addWidget(browse_message_button)
        message_button_layout.addStretch()
        
        self.message_preview = QTextEdit()
        self.message_preview.setMinimumHeight(100)  # Minimum height for readability
        self.message_preview.setMaximumHeight(250)  # Increased from 150 to 250 for better vertical resizing
        self.message_preview.setPlaceholderText(self.tr("Message template will appear here..."))
        self.message_preview.setReadOnly(True)
        
        message_layout.addLayout(message_button_layout)
        message_layout.addWidget(self.message_preview)
        message_group.setLayout(message_layout)
        
        # Attachments preview
        attachments_group = QGroupBox(self.tr("📎 Attachments"))
        self.attachments_group = attachments_group  # Store reference for translation updates
        attachments_layout = QVBoxLayout()
        
        # Attachment management buttons
        attachment_button_layout = QHBoxLayout()
        
        add_attachment_button = QPushButton(self.tr("Add"))
        add_attachment_button.clicked.connect(self.add_attachments)
        add_attachment_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        add_attachment_button.setEnabled(False)
        self.add_attachment_button = add_attachment_button
        
        open_attachment_button = QPushButton(self.tr("Open"))
        open_attachment_button.clicked.connect(self.open_attachment)
        open_attachment_button.setStyleSheet("QPushButton { background-color: #17a2b8; }")
        open_attachment_button.setEnabled(False)
        self.open_attachment_button = open_attachment_button
        
        delete_attachment_button = QPushButton(self.tr("Delete"))
        delete_attachment_button.clicked.connect(self.delete_attachment)
        delete_attachment_button.setStyleSheet("QPushButton { background-color: #dc3545; }")
        delete_attachment_button.setEnabled(False)
        self.delete_attachment_button = delete_attachment_button
        
        attachment_button_layout.addWidget(add_attachment_button)
        attachment_button_layout.addWidget(open_attachment_button)
        attachment_button_layout.addWidget(delete_attachment_button)
        attachment_button_layout.addStretch()
        
        self.attachments_list = QListWidget()
        self.attachments_list.setMinimumHeight(80)   # Minimum height for usability
        self.attachments_list.setMaximumHeight(150)  # Increased from 100 to 150 for better vertical resizing
        self.attachments_list.itemSelectionChanged.connect(self.on_attachment_selection_changed)
        
        attachments_layout.addLayout(attachment_button_layout)
        attachments_layout.addWidget(self.attachments_list)
        attachments_group.setLayout(attachments_layout)
        
        right_content_layout.addWidget(subject_group)
        right_content_layout.addWidget(message_group)
        right_content_layout.addWidget(attachments_group)
        right_content_widget.setLayout(right_content_layout)
        
        # Add content widget to scroll area
        right_scroll.setWidget(right_content_widget)
        
        # Add scroll area to main right layout
        right_layout.addWidget(right_scroll)
        right_widget.setLayout(right_layout)
        
        # Add widgets to splitter
        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([500, 500])
        
        # Set stretch factors to allow proper resizing
        content_splitter.setStretchFactor(0, 1)  # Left side (recipients) can stretch
        content_splitter.setStretchFactor(1, 1)  # Right side can also stretch
        
        # Add all components to main layout
        layout.addWidget(folder_group)
        layout.addWidget(status_validation_splitter)  # New combined status and validation section
        layout.addWidget(content_splitter)
        
        self.setLayout(layout)
    
    def create_validation_panel(self):
        """Create an improved validation panel for displaying errors and warnings"""
        # Main validation group (always visible, shows status)
        validation_group = QGroupBox(self.tr("🔍 Validation Issues"))
        self.validation_group = validation_group  # Store reference for translation updates
        validation_group.setVisible(True)  # Always visible to prevent splitter issues
        validation_group.setMinimumWidth(300)  # Ensure minimum width for visibility
        validation_layout = QVBoxLayout()
        
        # Add scroll area wrapper for the entire validation content (like Campaign Status)
        validation_scroll_wrapper = QScrollArea()
        validation_scroll_wrapper.setWidgetResizable(True)
        validation_scroll_wrapper.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        validation_scroll_wrapper.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create widget for validation content
        validation_wrapper_widget = QWidget()
        validation_wrapper_layout = QVBoxLayout()
        
        # Summary label
        self.validation_summary = QLabel()
        self.validation_summary.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 8px;
            }
        """)
        
        # Create inner scroll area for validation details (existing functionality)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(150)  # Minimum height for readability
        scroll_area.setMaximumHeight(400)  # Increased from 300 to 400 for better vertical resizing
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # Content widget for inner scroll area
        self.validation_content = QWidget()
        self.validation_content_layout = QVBoxLayout()
        self.validation_content.setLayout(self.validation_content_layout)
        scroll_area.setWidget(self.validation_content)
        
        # Add components to wrapper layout
        validation_wrapper_layout.addWidget(self.validation_summary)
        validation_wrapper_layout.addWidget(scroll_area)
        validation_wrapper_widget.setLayout(validation_wrapper_layout)
        
        # Add wrapper widget to scroll wrapper
        validation_scroll_wrapper.setWidget(validation_wrapper_widget)
        
        # Add scroll wrapper to main layout
        validation_layout.addWidget(validation_scroll_wrapper)
        validation_group.setLayout(validation_layout)
        
        # Initialize with default "no issues" message
        self.init_validation_panel_default()
        
        # Store reference to the group for show/hide
        self.validation_group = validation_group
        
        return validation_group
    
    def translate_validation_message(self, message: str) -> str:
        """Translate validation error/warning messages"""
        # Create translation mappings for common validation messages
        translations = {
            # File missing errors
            "Required file missing: recipients.csv": self.tr("Required file missing: recipients.csv"),
            "Required file missing: subject.txt": self.tr("Required file missing: subject.txt"),
            "Message file missing: either msg.txt or msg.docx is required": self.tr("Message file missing: either msg.txt or msg.docx is required"),
            "Multiple message files found: only one of msg.txt or msg.docx should exist. Please remove one.": self.tr("Multiple message files found: only one of msg.txt or msg.docx should exist. Please remove one."),
            
            # File type errors
            "'recipients.csv' exists but is not a file": self.tr("'recipients.csv' exists but is not a file"),
            "'subject.txt' exists but is not a file": self.tr("'subject.txt' exists but is not a file"),
            "'attachments' exists but is not a folder": self.tr("'attachments' exists but is not a folder"),
            
            # CSV content errors
            "recipients.csv is empty": self.tr("recipients.csv is empty"),
            "recipients.csv must contain an 'email' column": self.tr("recipients.csv must contain an 'email' column"),
            "CSV must have at least one column when picture generator projects exist": self.tr("CSV must have at least one column when picture generator projects exist"),
            "Primary key (first column) cannot be 'email' when picture generator projects exist. Please use an ID column as the first column.": self.tr("Primary key (first column) cannot be 'email' when picture generator projects exist. Please use an ID column as the first column."),
            "No valid recipients found in CSV file": self.tr("No valid recipients found in CSV file"),
            
            # Subject file errors
            "Subject file (subject.txt) is empty": self.tr("Subject file (subject.txt) is empty"),
            "Subject file (subject.txt) must contain only one line. Email subjects cannot be multi-line.": self.tr("Subject file (subject.txt) must contain only one line. Email subjects cannot be multi-line."),
            "Subject file (subject.txt) contains line breaks. Only the first non-empty line will be used as the email subject.": self.tr("Subject file (subject.txt) contains line breaks. Only the first non-empty line will be used as the email subject."),
        }
        
        # Check for exact matches first
        if message in translations:
            return translations[message]
        
        # Handle dynamic messages with patterns
        import re
        
        # Pattern for "Required file missing: filename"
        match = re.match(r"Required file missing: (.+)", message)
        if match:
            filename = match.group(1)
            return self.tr("Required file missing: {filename}").format(filename=filename)
        
        # Pattern for "'filename' exists but is not a file"
        match = re.match(r"'(.+)' exists but is not a file", message)
        if match:
            filename = match.group(1)
            return self.tr("'{filename}' exists but is not a file").format(filename=filename)
        
        # Pattern for "Attachment file not found: filename"
        match = re.match(r"Attachment file not found: (.+)", message)
        if match:
            filename = match.group(1)
            return self.tr("Attachment file not found: {filename}").format(filename=filename)
        
        # Pattern for "Cannot read attachment file: filename"
        match = re.match(r"Cannot read attachment file: (.+)", message)
        if match:
            filename = match.group(1)
            return self.tr("Cannot read attachment file: {filename}").format(filename=filename)
        
        # Pattern for "Potentially blocked file type: filename (ext)"
        match = re.match(r"Potentially blocked file type: (.+) \((.+)\)", message)
        if match:
            filename, ext = match.groups()
            return self.tr("Potentially blocked file type: {filename} ({ext})").format(filename=filename, ext=ext)
        
        # Pattern for "Empty email in data row X"
        match = re.match(r"Empty email in data row (\d+)", message)
        if match:
            row_num = match.group(1)
            return self.tr("Empty email in data row {row}").format(row=row_num)
        
        # Pattern for "Invalid email 'email' in data row X"
        match = re.match(r"Invalid email '(.+)' in data row (\d+)", message)
        if match:
            email, row_num = match.groups()
            return self.tr("Invalid email '{email}' in data row {row}").format(email=email, row=row_num)
        
        # Pattern for "Duplicate email 'email' found in data rows X and Y"
        match = re.match(r"Duplicate email '(.+)' found in data rows (\d+) and (\d+)", message)
        if match:
            email, row1, row2 = match.groups()
            return self.tr("Duplicate email '{email}' found in data rows {row1} and {row2}").format(email=email, row1=row1, row2=row2)
        
        # Pattern for template reference errors
        match = re.match(r"Template reference '(.+)' in (.+) not found in CSV columns", message)
        if match:
            ref, filename = match.groups()
            return self.tr("Template reference '{ref}' in {filename} not found in CSV columns").format(ref=ref, filename=filename)
        
        # If no pattern matches, return the original message
        return message
    
    def create_error_item(self, error_text: str, error_type: str = "error"):
        """Create a styled error item widget"""
        item_frame = QFrame()
        item_frame.setStyleSheet(f"""
            QFrame {{
                border-left: 4px solid {'#dc3545' if error_type == 'error' else '#ffc107'};
                background-color: {'#f8d7da' if error_type == 'error' else '#fff3cd'};
                border-radius: 4px;
                margin: 2px 0px;
                padding: 8px;
            }}
        """)
        
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(8, 4, 8, 4)
        
        # Icon
        icon_label = QLabel("❌" if error_type == "error" else "⚠️")
        icon_label.setStyleSheet("font-size: 16px;")
        
        # Error text
        error_label = QLabel(error_text)
        error_label.setWordWrap(True)
        error_label.setStyleSheet(f"""
            QLabel {{
                color: {'#721c24' if error_type == 'error' else '#856404'};
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)
        
        item_layout.addWidget(icon_label)
        item_layout.addWidget(error_label, 1)
        
        # Add action button for specific error types
        action_button = self.create_action_button(error_text, error_type)
        if action_button:
            item_layout.addWidget(action_button)
        
        item_frame.setLayout(item_layout)
        return item_frame
    
    def create_action_button(self, error_text: str, error_type: str):
        """Create action button for specific error types"""
        button = None
        
        if "Template reference" in error_text and "not found in CSV columns" in error_text:
            button = QPushButton("📝 Edit")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 4px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            
            # Determine which file to edit based on error text
            if "subject.txt" in error_text:
                button.clicked.connect(self.edit_subject)
            elif "msg.txt" in error_text or "msg.docx" in error_text:
                button.clicked.connect(self.edit_message)
                
        elif "Duplicate email" in error_text:
            button = QPushButton("👥 Fix")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 4px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            button.clicked.connect(self.edit_recipients)
            
        elif "must contain only one line" in error_text:
            button = QPushButton("📄 Fix")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #fd7e14;
                    color: white;
                    border: none;
                    padding: 4px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #e96b00;
                }
            """)
            button.clicked.connect(self.edit_subject)
        
        return button
    
    def update_validation_panel(self, validation_result):
        """Update the validation panel with current errors and warnings"""
        # Clear existing content
        for i in reversed(range(self.validation_content_layout.count())):
            child = self.validation_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Count total issues
        error_count = len(validation_result.errors)
        warning_count = len(validation_result.warnings)
        total_issues = error_count + warning_count
        
        # Always keep validation panel visible to prevent splitter issues
        self.validation_group.setVisible(True)
        
        if total_issues == 0:
            # Show "no issues" message
            self.validation_summary.setText(self.tr("✅ No validation issues found"))
            self.validation_summary.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #d4edda;
                    color: #155724;
                    margin-bottom: 8px;
                }
            """)
            # Clear the content area
            self.clear_validation_content()
            return
        
        # Update summary
        if error_count > 0 and warning_count > 0:
            summary_text = self.tr("Found {error_count} error(s) and {warning_count} warning(s)").format(error_count=error_count, warning_count=warning_count)
        elif error_count > 0:
            summary_text = self.tr("Found {error_count} error(s)").format(error_count=error_count)
        else:
            summary_text = self.tr("Found {warning_count} warning(s)").format(warning_count=warning_count)
            
        if error_count > 0:
            self.validation_summary.setText(f"🚨 {summary_text}")
            self.validation_summary.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 8px;
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
            """)
        else:
            self.validation_summary.setText(f"⚠️ {summary_text}")
            self.validation_summary.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 8px;
                    background-color: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeaa7;
                }
            """)
        
        # Add error items
        for error in validation_result.errors:
            translated_error = self.translate_validation_message(error)
            error_item = self.create_error_item(translated_error, "error")
            self.validation_content_layout.addWidget(error_item)
        
        # Add warning items
        for warning in validation_result.warnings:
            translated_warning = self.translate_validation_message(warning)
            warning_item = self.create_error_item(translated_warning, "warning")
            self.validation_content_layout.addWidget(warning_item)
        
        # Add stretch to push items to top
        self.validation_content_layout.addStretch()
        
        # Force update the layout
        self.validation_group.updateGeometry()
        self.validation_group.update()
    
    def init_empty_recipients_table(self):
        """Initialize recipients table with placeholder content when no campaign is loaded"""
        self.recipients_table.setRowCount(1)
        self.recipients_table.setColumnCount(1)
        self.recipients_table.setHorizontalHeaderLabels(["Recipients"])
        
        placeholder_item = QTableWidgetItem(self.tr("No campaign loaded\nSelect a campaign folder to view recipients"))
        placeholder_font = QFont("Arial", 10)
        placeholder_font.setItalic(True)
        placeholder_item.setFont(placeholder_font)
        self.recipients_table.setItem(0, 0, placeholder_item)
        
        # Make sure the column expands to show full text
        self.recipients_table.resizeColumnsToContents()
        self.recipients_table.horizontalHeader().setStretchLastSection(True)
    
    def init_validation_panel_default(self):
        """Initialize validation panel with default 'no issues' message"""
        self.validation_summary.setText(self.tr("✅ No validation issues found"))
        self.validation_summary.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
                background-color: #d4edda;
                color: #155724;
                margin-bottom: 8px;
            }
        """)
        # Clear any existing content
        self.clear_validation_content()
    
    def clear_validation_content(self):
        """Clear all validation content items"""
        # Remove all items from the validation content layout
        while self.validation_content_layout.count():
            child = self.validation_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def browse_folder(self):
        """Browse for campaign folder"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Campaign Folder",
            str(Path.home())
        )
        
        if folder:
            self.folder_path.setText(folder)
            self.current_campaign_path = folder
            
            # Actually load the campaign into campaign_manager
            result = self.campaign_manager.create_or_load_campaign(folder, gui_mode=True)
            if result == 0:  # Success
                self.load_campaign_preview(folder)
                # Enable Save As button when campaign is loaded
                self.save_as_button.setEnabled(True)
                # Emit signal that campaign has changed
                self.campaign_changed.emit(folder)
                # Enable edit buttons
                self.enable_edit_buttons()
            else:
                # Failed to load campaign
                QMessageBox.critical(self, "Campaign Load Error", 
                                   f"Failed to load campaign from '{folder}'. Please check the campaign structure.")
                self.folder_path.clear()
                self.current_campaign_path = None
    
    def enable_edit_buttons(self):
        """Enable edit buttons when campaign is loaded"""
        if self.current_campaign_path:
            campaign_path = Path(self.current_campaign_path)
            
            # Enable recipients edit if CSV exists
            if (campaign_path / "recipients.csv").exists():
                self.edit_recipients_button.setEnabled(True)
            
            # Always enable recipients browse (can replace even if doesn't exist)
            self.browse_recipients_button.setEnabled(True)
            
            # Enable message edit if message file exists
            if (campaign_path / "msg.txt").exists() or (campaign_path / "msg.docx").exists():
                self.edit_message_button.setEnabled(True)
            
            # Always enable message browse (can replace even if doesn't exist)
            self.browse_message_button.setEnabled(True)
            
            # Enable subject edit if subject file exists
            if (campaign_path / "subject.txt").exists():
                self.edit_subject_button.setEnabled(True)
            
            # Always enable subject browse (can replace even if doesn't exist)
            self.browse_subject_button.setEnabled(True)
            
            # Enable attachment buttons
            self.add_attachment_button.setEnabled(True)
            if (campaign_path / "attachments").exists():
                self.open_attachment_button.setEnabled(True)
                self.delete_attachment_button.setEnabled(True)
    
    def setup_file_watching(self):
        """Set up file system watching for current campaign"""
        if not self.current_campaign_path:
            return
        
        # Clear existing watches
        if self.watched_files:
            self.file_watcher.removePaths(list(self.watched_files))
            self.watched_files.clear()
        
        campaign_path = Path(self.current_campaign_path)
        
        # Watch key files
        files_to_watch = [
            campaign_path / "recipients.csv",
            campaign_path / "msg.txt",
            campaign_path / "msg.docx",
            campaign_path / "subject.txt"
        ]
        
        for file_path in files_to_watch:
            if file_path.exists():
                self.file_watcher.addPath(str(file_path))
                self.watched_files.add(str(file_path))
    
    def on_file_changed(self, file_path):
        """Handle file changes from external editors"""
        if not self.current_campaign_path:
            return
        
        file_path = Path(file_path)
        
        # Reload the appropriate preview
        if file_path.name == "recipients.csv":
            self.load_recipients_preview(file_path)
        elif file_path.name in ["msg.txt", "msg.docx"]:
            self.load_message_preview(file_path, file_path.suffix == ".docx")
        elif file_path.name == "subject.txt":
            self.load_subject_from_file()
        
        # Update campaign status
        self.load_campaign_preview(self.current_campaign_path)
    
    def edit_recipients(self):
        """Open recipients CSV in external editor"""
        if not self.current_campaign_path:
            return
        
        csv_path = Path(self.current_campaign_path) / "recipients.csv"
        if csv_path.exists():
            self.open_file_externally(csv_path)
    
    def edit_message(self):
        """Open message template in external editor"""
        if not self.current_campaign_path:
            return
        
        campaign_path = Path(self.current_campaign_path)
        msg_docx = campaign_path / "msg.docx"
        msg_txt = campaign_path / "msg.txt"
        
        if msg_docx.exists():
            self.open_file_externally(msg_docx)
        elif msg_txt.exists():
            self.open_file_externally(msg_txt)
    
    def edit_subject(self):
        """Open subject.txt in external editor"""
        if not self.current_campaign_path:
            return
        
        subject_path = Path(self.current_campaign_path) / "subject.txt"
        if subject_path.exists():
            self.open_file_externally(subject_path)
    
    def browse_recipients(self):
        """Browse for a new recipients CSV file to replace the current one"""
        if not self.current_campaign_path:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select New Recipients CSV File",
            str(Path.home()),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                # Copy the new file to replace recipients.csv
                dest_path = Path(self.current_campaign_path) / "recipients.csv"
                shutil.copy2(file_path, dest_path)
                
                # Reload the campaign preview to show changes
                self.load_campaign_preview(self.current_campaign_path)
                
                QMessageBox.information(
                    self,
                    self.tr("Recipients Updated"),
                    self.tr("Recipients file successfully replaced with:\n{filename}").format(
                        filename=Path(file_path).name
                    )
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Replace Error"),
                    self.tr("Failed to replace recipients file:\n{error}").format(error=str(e))
                )
    
    def browse_subject(self):
        """Browse for a new subject file to replace the current one"""
        if not self.current_campaign_path:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select New Subject File",
            str(Path.home()),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                # Copy the new file to replace subject.txt
                dest_path = Path(self.current_campaign_path) / "subject.txt"
                shutil.copy2(file_path, dest_path)
                
                # Reload the campaign preview to show changes
                self.load_campaign_preview(self.current_campaign_path)
                
                QMessageBox.information(
                    self,
                    self.tr("Subject Updated"),
                    self.tr("Subject file successfully replaced with:\n{filename}").format(
                        filename=Path(file_path).name
                    )
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Replace Error"),
                    self.tr("Failed to replace subject file:\n{error}").format(error=str(e))
                )
    
    def browse_message(self):
        """Browse for a new message file to replace the current one"""
        if not self.current_campaign_path:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select New Message File",
            str(Path.home()),
            "All Message Files (*.txt *.docx);;Text Files (*.txt);;Word Documents (*.docx);;All Files (*)"
        )
        
        if file_path:
            try:
                campaign_path = Path(self.current_campaign_path)
                source_path = Path(file_path)
                
                # Remove existing message files
                old_txt = campaign_path / "msg.txt"
                old_docx = campaign_path / "msg.docx"
                if old_txt.exists():
                    old_txt.unlink()
                if old_docx.exists():
                    old_docx.unlink()
                
                # Copy new file with appropriate name
                if source_path.suffix.lower() == '.docx':
                    dest_path = campaign_path / "msg.docx"
                else:
                    dest_path = campaign_path / "msg.txt"
                
                shutil.copy2(file_path, dest_path)
                
                # Reload the campaign preview to show changes
                self.load_campaign_preview(self.current_campaign_path)
                
                QMessageBox.information(
                    self,
                    self.tr("Message Updated"),
                    self.tr("Message file successfully replaced with:\n{source}\nSaved as: {dest}").format(
                        source=source_path.name,
                        dest=dest_path.name
                    )
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Replace Error"),
                    self.tr("Failed to replace message file:\n{error}").format(error=str(e))
                )
    
    def open_file_externally(self, file_path):
        """Open file with system default application"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            elif system == "Windows":
                subprocess.run(["start", str(file_path)], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path)])
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Open Error",
                f"Could not open file with external application:\n{str(e)}"
            )
    
    def load_subject_from_file(self):
        """Load subject from subject.txt file and display in preview"""
        if not self.current_campaign_path:
            return
        
        subject_path = Path(self.current_campaign_path) / "subject.txt"
        if subject_path.exists():
            try:
                with open(subject_path, 'r', encoding='utf-8') as f:
                    subject_text = f.read().strip()
                    if subject_text:
                        self.subject_preview.setText(subject_text)
                        self.subject_preview.setStyleSheet("QLabel { padding: 8px; border: 1px solid #28a745; background-color: #f8f9fa; color: #000; }")
                    else:
                        self.subject_preview.setText("Subject file is empty")
                        self.subject_preview.setStyleSheet("QLabel { padding: 8px; border: 1px solid #ffc107; background-color: #fff3cd; color: #856404; }")
            except Exception as e:
                self.subject_preview.setText(f"Error loading subject: {str(e)}")
                self.subject_preview.setStyleSheet("QLabel { padding: 8px; border: 1px solid #dc3545; background-color: #f8d7da; color: #721c24; }")
        else:
            self.subject_preview.setText(self.tr("No subject.txt file found"))
            self.subject_preview.setStyleSheet("QLabel { padding: 8px; border: 1px solid #6c757d; background-color: #e9ecef; color: #495057; }")
    
    def add_attachments(self):
        """Add new attachment files"""
        if not self.current_campaign_path:
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Attachment Files",
            str(Path.home()),
            "All Files (*)"
        )
        
        if files:
            campaign_path = Path(self.current_campaign_path)
            attachments_dir = campaign_path / "attachments"
            attachments_dir.mkdir(exist_ok=True)
            
            try:
                for file_path in files:
                    file_name = Path(file_path).name
                    dest_path = attachments_dir / file_name
                    
                    # Handle duplicate names
                    counter = 1
                    original_name = dest_path.stem
                    extension = dest_path.suffix
                    
                    while dest_path.exists():
                        dest_path = attachments_dir / f"{original_name}_{counter}{extension}"
                        counter += 1
                    
                    shutil.copy2(file_path, dest_path)
                
                # Refresh attachments display
                self.load_attachments_preview(attachments_dir)
                self.load_campaign_preview(self.current_campaign_path)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Add Attachments Error",
                    f"Failed to add attachments:\n{str(e)}"
                )
    
    def open_attachment(self):
        """Open selected attachment in external application"""
        selected_items = self.attachments_list.selectedItems()
        if not selected_items or not self.current_campaign_path:
            return
        
        attachments_dir = Path(self.current_campaign_path) / "attachments"
        for item in selected_items:
            file_name = item.text().split(" (")[0].replace("📄 ", "")  # Remove icon and size info
            file_path = attachments_dir / file_name
            if file_path.exists():
                self.open_file_externally(file_path)
    
    def delete_attachment(self):
        """Delete selected attachments"""
        selected_items = self.attachments_list.selectedItems()
        if not selected_items or not self.current_campaign_path:
            return
        
        # Filter out non-file items (only process items that start with 📄)
        file_items = [item for item in selected_items if item.text().startswith("📄 ")]
        
        if not file_items:
            return  # No actual files selected
        
        # Confirm deletion
        file_names = [item.text().split(" (")[0].replace("📄 ", "") for item in file_items]
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("Delete Attachments"))
        msg_box.setText(self.tr("Are you sure you want to delete {count} attachment(s)?\n\n{files}").format(
            count=len(file_names),
            files="\n".join(file_names)
        ))
        msg_box.setIcon(QMessageBox.Question)
        
        # Add custom translated buttons
        yes_button = msg_box.addButton(self.tr("Yes"), QMessageBox.YesRole)
        no_button = msg_box.addButton(self.tr("No"), QMessageBox.NoRole)
        msg_box.setDefaultButton(no_button)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
            attachments_dir = Path(self.current_campaign_path) / "attachments"
            try:
                for file_name in file_names:
                    file_path = attachments_dir / file_name
                    if file_path.exists():
                        file_path.unlink()
                
                # Refresh attachments display
                self.load_attachments_preview(attachments_dir)
                self.load_campaign_preview(self.current_campaign_path)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Delete Error"),
                    self.tr("Failed to delete attachments:\n{error}").format(error=str(e))
                )
    
    def on_attachment_selection_changed(self):
        """Handle attachment selection changes"""
        has_selection = bool(self.attachments_list.selectedItems())
        self.open_attachment_button.setEnabled(has_selection and bool(self.current_campaign_path))
        self.delete_attachment_button.setEnabled(has_selection and bool(self.current_campaign_path))
    
    def save_campaign_as(self):
        """Save current campaign to a new location"""
        if not self.current_campaign_path:
            QMessageBox.warning(self, "No Campaign", "Please load a campaign first.")
            return
        
        # Select destination folder
        destination = QFileDialog.getExistingDirectory(
            self,
            "Save Campaign As - Select Destination Folder",
            str(Path.home())
        )
        
        if not destination:
            return
        
        try:
            source_path = Path(self.current_campaign_path)
            dest_path = Path(destination)
            
            # Create destination if it doesn't exist
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all files except dryrun and picture-generator data folders
            for item in source_path.iterdir():
                if item.name == "dryrun":
                    continue  # Skip dryrun folder
                elif item.name == "picture-generator":
                    # Copy picture-generator but skip data folders
                    dest_pg = dest_path / "picture-generator"
                    dest_pg.mkdir(exist_ok=True)
                    for pg_item in item.iterdir():
                        if pg_item.is_dir():
                            pg_dest = dest_pg / pg_item.name
                            pg_dest.mkdir(exist_ok=True)
                            for pg_file in pg_item.iterdir():
                                if pg_file.name != "data":
                                    if pg_file.is_dir():
                                        shutil.copytree(pg_file, pg_dest / pg_file.name, dirs_exist_ok=True)
                                    else:
                                        shutil.copy2(pg_file, pg_dest)
                        else:
                            shutil.copy2(pg_item, dest_pg)
                elif item.is_dir():
                    shutil.copytree(item, dest_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_path)
            
            # Load the new campaign into campaign_manager
            self.folder_path.setText(str(dest_path))
            self.current_campaign_path = str(dest_path)
            
            # Actually load the campaign into campaign_manager
            result = self.campaign_manager.create_or_load_campaign(str(dest_path), gui_mode=True)
            if result == 0:  # Success
                self.load_campaign_preview(str(dest_path))
                # Enable buttons when campaign is loaded
                self.save_as_button.setEnabled(True)
                # Emit signal that campaign has changed
                self.campaign_changed.emit(str(dest_path))
                
                QMessageBox.information(
                    self, 
                    "Campaign Saved", 
                    f"Campaign successfully saved to:\n{dest_path}"
                )
            else:
                QMessageBox.critical(self, "Campaign Load Error", 
                                   f"Campaign saved but failed to load from '{dest_path}'.")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save campaign:\n{str(e)}"
            )
    
    def create_new_campaign(self):
        """Launch Create New Campaign Wizard"""
        wizard = CreateCampaignWizard(self)
        if wizard.exec() == QDialog.Accepted:
            # Load the newly created campaign
            campaign_path = wizard.get_campaign_path()
            if campaign_path:
                self.folder_path.setText(campaign_path)
                self.current_campaign_path = campaign_path
                
                # Actually load the campaign into campaign_manager
                result = self.campaign_manager.create_or_load_campaign(campaign_path, gui_mode=True)
                if result == 0:  # Success
                    self.load_campaign_preview(campaign_path)
                    self.save_as_button.setEnabled(True)
                    # Emit signal that campaign has changed
                    self.campaign_changed.emit(campaign_path)
                else:
                    QMessageBox.critical(self, "Campaign Load Error", 
                                       f"Campaign created but failed to load from '{campaign_path}'.")

    def load_campaign_preview(self, folder_path: str):
        """Load and display campaign preview with full validation"""
        try:
            from ...utils.validators import validate_campaign_folder
            
            folder_name = Path(folder_path).name
            
            # Perform full campaign validation
            validation_result = validate_campaign_folder(folder_path)
            
            # Check required files for preview loading
            recipients_csv = Path(folder_path) / "recipients.csv"
            subject_txt = Path(folder_path) / "subject.txt"
            msg_txt = Path(folder_path) / "msg.txt"
            msg_docx = Path(folder_path) / "msg.docx"
            attachments_dir = Path(folder_path) / "attachments"
            picture_gen_dir = Path(folder_path) / "picture-generator"
            
            # Build status overview starting with campaign name
            status_parts = []
            
            # Show validation status first
            if validation_result.is_valid:
                status_parts.append(self.tr("✅ Campaign: {folder_name}").format(folder_name=folder_name))
            else:
                status_parts.append(self.tr("❌ Campaign: {folder_name} (Has Issues)").format(folder_name=folder_name))
            
            # Add file existence info
            if recipients_csv.exists():
                recipient_count = self.count_csv_rows(recipients_csv)
                status_parts.append(self.tr("👥 Recipients: {count}").format(count=recipient_count))
                self.load_recipients_preview(recipients_csv)
            else:
                status_parts.append(self.tr("❌ No recipients.csv found"))
                self.recipients_table.clear()
            
            if subject_txt.exists():
                status_parts.append(self.tr("✅ Subject template found"))
            else:
                status_parts.append(self.tr("❌ No subject.txt found"))
            
            if msg_docx.exists():
                status_parts.append(self.tr("✅ Message template: .docx (formatted)"))
                self.load_message_preview(msg_docx, is_docx=True)
            elif msg_txt.exists():
                status_parts.append(self.tr("✅ Message template: .txt (plain)"))
                self.load_message_preview(msg_txt, is_docx=False)
            else:
                status_parts.append(self.tr("❌ No message template found"))
                self.message_preview.clear()
            
            if attachments_dir.exists():
                attachment_count = len([f for f in attachments_dir.iterdir() if f.is_file()])
                status_parts.append(self.tr("📎 Attachments: {count} files").format(count=attachment_count))
                self.load_attachments_preview(attachments_dir)
            else:
                status_parts.append(self.tr("📎 No attachments folder"))
                self.attachments_list.clear()
                self.attachments_list.addItem(self.tr("No attachments folder found"))
            
            if picture_gen_dir.exists():
                project_count = len([d for d in picture_gen_dir.iterdir() if d.is_dir()])
                status_parts.append(self.tr("🖼️ Picture projects: {count}").format(count=project_count))
            else:
                status_parts.append(self.tr("🖼️ No picture generator"))
            
            # Add validation errors and warnings to the new panel
            self.update_validation_panel(validation_result)
            
            # Set status text and color based on validation result (simplified)
            status_text = "\n".join(status_parts)
            self.status_overview.setText(status_text)
            
            if validation_result.errors:
                # Red for errors
                self.status_overview.setStyleSheet("color: #dc3545; font-size: 14px; padding: 10px;")
            elif validation_result.warnings:
                # Orange for warnings
                self.status_overview.setStyleSheet("color: #fd7e14; font-size: 14px; padding: 10px;")
            else:
                # Green for success
                self.status_overview.setStyleSheet("color: #28a745; font-size: 14px; padding: 10px;")
            
            # Set up file watching and load subject
            self.setup_file_watching()
            self.load_subject_from_file()
            
            # Enable edit buttons
            self.enable_edit_buttons()
            
        except Exception as e:
            self.status_overview.setText(f"❌ Error loading campaign: {str(e)}")
            self.status_overview.setStyleSheet("color: #dc3545; font-size: 14px; padding: 10px;")
    
    def count_csv_rows(self, csv_path: Path) -> int:
        """Count rows in CSV file"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in csv.reader(f)) - 1  # Subtract header
        except:
            return 0
    
    def load_recipients_preview(self, csv_path: Path):
        """Load recipients CSV preview"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if not rows:
                    return
                
                # Set up table
                headers = rows[0]
                data_rows = rows[1:16]  # Show first 15 rows (increased from 5)
                
                self.recipients_table.setRowCount(len(data_rows))
                self.recipients_table.setColumnCount(len(headers))
                self.recipients_table.setHorizontalHeaderLabels(headers)
                
                # Populate data
                for row_idx, row_data in enumerate(data_rows):
                    for col_idx, cell_data in enumerate(row_data):
                        if col_idx < len(headers):
                            item = QTableWidgetItem(str(cell_data))
                            self.recipients_table.setItem(row_idx, col_idx, item)
                
                # Auto-resize columns
                self.recipients_table.resizeColumnsToContents()
                
                # Add note if there are more rows
                if len(rows) > 16:  # Updated threshold (16 = header + 15 data rows)
                    remaining = len(rows) - 16
                    note = f"... and {remaining} more recipients"
                    self.recipients_table.setRowCount(len(data_rows) + 1)
                    note_item = QTableWidgetItem(note)
                    note_font = QFont("Arial", 9)
                    note_font.setItalic(True)
                    note_item.setFont(note_font)
                    self.recipients_table.setItem(len(data_rows), 0, note_item)
                    self.recipients_table.setSpan(len(data_rows), 0, 1, len(headers))
                
        except Exception as e:
            self.recipients_table.clear()
            self.recipients_table.setRowCount(1)
            self.recipients_table.setColumnCount(1)
            self.recipients_table.setItem(0, 0, QTableWidgetItem(f"Error loading CSV: {str(e)}"))
    
    def load_message_preview(self, msg_path: Path, is_docx: bool):
        """Load message template preview"""
        try:
            if is_docx:
                self.message_preview.setPlainText(
                    self.tr("📄 DOCX Template Detected\n\n"
                    "This is a formatted document template (.docx) that contains:\n"
                    "• Rich text formatting (bold, italic, colors)\n"
                    "• Tables and structured content\n"
                    "• Template variables like {{name}}, {{email}}\n\n"
                    "The actual formatted content would be processed when sending emails.")
                )
            else:
                with open(msg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:500] + "..." if len(content) > 500 else content
                    self.message_preview.setPlainText(preview)
        except Exception as e:
            self.message_preview.setPlainText(f"Error loading message template: {str(e)}")
    
    def load_attachments_preview(self, attachments_dir: Path):
        """Load attachments preview"""
        try:
            from PySide6.QtWidgets import QListWidgetItem
            from PySide6.QtCore import Qt
            
            self.attachments_list.clear()
            files = [f for f in attachments_dir.iterdir() if f.is_file()]
            
            if not files:
                no_files_item = QListWidgetItem("No attachments found")
                no_files_item.setFlags(no_files_item.flags() & ~Qt.ItemIsSelectable)
                self.attachments_list.addItem(no_files_item)
                return
            
            total_size = 0
            
            for file_path in files[:20]:  # Show first 20 files
                size = file_path.stat().st_size
                total_size += size
                size_str = self.format_file_size(size)
                # Regular file items remain selectable (default behavior)
                self.attachments_list.addItem(f"📄 {file_path.name} ({size_str})")
            
            if len(files) > 20:
                more_files_item = QListWidgetItem(f"... and {len(files) - 20} more files")
                more_files_item.setFlags(more_files_item.flags() & ~Qt.ItemIsSelectable)
                self.attachments_list.addItem(more_files_item)
            
            # Add total size info as non-selectable item
            total_item = QListWidgetItem(f"Total: {self.format_file_size(total_size)}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsSelectable)
            self.attachments_list.addItem(total_item)
            
        except Exception as e:
            self.attachments_list.clear()
            error_item = QListWidgetItem(f"Error loading attachments: {str(e)}")
            error_item.setFlags(error_item.flags() & ~Qt.ItemIsSelectable)
            self.attachments_list.addItem(error_item)
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def tr(self, text: str) -> str:
        """Translate text using translation manager"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "CampaignTab")
    
    def refresh_translations(self):
        """Refresh all translatable UI elements when language changes"""
        # Update placeholder text
        if hasattr(self, 'folder_path'):
            self.folder_path.setPlaceholderText(self.tr("Select your campaign folder..."))
        
        # Update status text if no campaign loaded
        if hasattr(self, 'status_overview'):
            current_text = self.status_overview.text()
            if current_text in ["No campaign loaded", "Aucune campagne chargée"]:
                self.status_overview.setText(self.tr("No campaign loaded"))
        
        # Update recipients table placeholder if showing default text
        if hasattr(self, 'recipients_table') and self.recipients_table.rowCount() == 1:
            item = self.recipients_table.item(0, 0)
            if item and ("No campaign loaded" in item.text() or "Aucune campagne chargée" in item.text()):
                item.setText(self.tr("No campaign loaded\nSelect a campaign folder to view recipients"))
        
        # Update subject preview if showing default text
        if hasattr(self, 'subject_preview'):
            current_text = self.subject_preview.text()
            if current_text in ["No subject loaded", "Aucun objet chargé", "No subject.txt file found", "Fichier subject.txt introuvable"]:
                if "file found" in current_text or "introuvable" in current_text:
                    self.subject_preview.setText(self.tr("No subject.txt file found"))
                else:
                    self.subject_preview.setText(self.tr("No subject loaded"))
        
        # Update group box titles (need to store references during creation)
        if hasattr(self, 'folder_group'):
            self.folder_group.setTitle(self.tr("📁 Campaign Folder"))
        if hasattr(self, 'status_group'):
            self.status_group.setTitle(self.tr("📊 Campaign Status"))
        if hasattr(self, 'recipients_group'):
            self.recipients_group.setTitle(self.tr("👥 Recipients Preview"))
        
        # Update validation summary if it shows "no issues"
        if hasattr(self, 'validation_summary'):
            current_text = self.validation_summary.text()
            if "No validation issues found" in current_text or "Aucun problème de validation trouvé" in current_text:
                self.validation_summary.setText(self.tr("✅ No validation issues found"))
        if hasattr(self, 'subject_group'):
            self.subject_group.setTitle(self.tr("📄 Subject Line"))
        if hasattr(self, 'message_group'):
            self.message_group.setTitle(self.tr("📝 Message Template"))
        if hasattr(self, 'attachments_group'):
            self.attachments_group.setTitle(self.tr("📎 Attachments"))
        if hasattr(self, 'validation_group'):
            self.validation_group.setTitle(self.tr("🔍 Validation Issues"))
        
        # Update button texts (need to store references during creation)
        if hasattr(self, 'browse_button'):
            self.browse_button.setText(self.tr("Browse..."))
        if hasattr(self, 'save_as_button'):
            self.save_as_button.setText(self.tr("Save As..."))
        if hasattr(self, 'create_new_button'):
            self.create_new_button.setText(self.tr("Create New..."))
        if hasattr(self, 'edit_recipients_button'):
            self.edit_recipients_button.setText(self.tr("Edit Recipients"))
        if hasattr(self, 'edit_subject_button'):
            self.edit_subject_button.setText(self.tr("Edit Subject"))
        if hasattr(self, 'edit_message_button'):
            self.edit_message_button.setText(self.tr("Edit Message"))
        if hasattr(self, 'browse_recipients_button'):
            self.browse_recipients_button.setText(self.tr("Browse..."))
        if hasattr(self, 'browse_subject_button'):
            self.browse_subject_button.setText(self.tr("Browse..."))
        if hasattr(self, 'browse_message_button'):
            self.browse_message_button.setText(self.tr("Browse..."))
        if hasattr(self, 'add_attachment_button'):
            self.add_attachment_button.setText(self.tr("Add"))
        if hasattr(self, 'open_attachment_button'):
            self.open_attachment_button.setText(self.tr("Open"))
        if hasattr(self, 'delete_attachment_button'):
            self.delete_attachment_button.setText(self.tr("Delete"))
        
        # Update placeholder texts
        if hasattr(self, 'subject_line_input'):
            self.subject_line_input.setPlaceholderText(self.tr("Enter email subject line..."))
        if hasattr(self, 'message_preview'):
            self.message_preview.setPlaceholderText(self.tr("Message template will appear here..."))
        
        # Update validation summary if it shows default text
        if hasattr(self, 'validation_summary'):
            current_text = self.validation_summary.text()
            if "No validation issues found" in current_text or "Aucun problème de validation trouvé" in current_text:
                self.validation_summary.setText(self.tr("✅ No validation issues found"))
        
        # Refresh campaign status and validation if a campaign is loaded
        if hasattr(self, 'current_campaign_path') and self.current_campaign_path:
            campaign_path = Path(self.current_campaign_path)
            msg_docx = campaign_path / "msg.docx"
            msg_txt = campaign_path / "msg.txt"
            
            # Reload message preview to get updated translations
            if msg_docx.exists():
                self.load_message_preview(msg_docx, is_docx=True)
            elif msg_txt.exists():
                self.load_message_preview(msg_txt, is_docx=False)
            
            # Reload campaign status to get updated translations
            self.load_campaign_preview(self.current_campaign_path)


class CreateCampaignWizard(QWizard):
    """Wizard for creating new campaigns from scratch"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Create New Campaign"))
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(600, 500)
        
        self.campaign_path = None
        
        # Set custom button texts for translation
        self.setButtonText(QWizard.BackButton, self.tr("< Back"))
        self.setButtonText(QWizard.NextButton, self.tr("Next >"))
        self.setButtonText(QWizard.FinishButton, self.tr("Create Campaign"))
        self.setButtonText(QWizard.CancelButton, self.tr("Cancel"))
        
        # Add wizard pages with parent for translation context
        self.addPage(DestinationPage(self))
        self.addPage(RecipientsPage(self))
        self.addPage(MessagePage(self))
        self.addPage(AttachmentsPage(self))
        
        # Connect finish button
        self.finished.connect(self.on_finished)
    
    def showEvent(self, event):
        """Override showEvent to refresh translations when wizard is shown"""
        super().showEvent(event)
        self.refresh_translations()
    
    def refresh_translations(self):
        """Refresh all translations in the wizard"""
        # Refresh wizard window title using CampaignTab context
        self.setWindowTitle(QCoreApplication.translate("CampaignTab", "Create New Campaign"))
        
        # Refresh button texts
        self.setButtonText(QWizard.BackButton, QCoreApplication.translate("CampaignTab", "< Back"))
        self.setButtonText(QWizard.NextButton, QCoreApplication.translate("CampaignTab", "Next >"))
        self.setButtonText(QWizard.FinishButton, QCoreApplication.translate("CampaignTab", "Create Campaign"))
        self.setButtonText(QWizard.CancelButton, QCoreApplication.translate("CampaignTab", "Cancel"))
        
        # Refresh all page translations
        for i in range(self.pageIds().__len__()):
            page = self.page(self.pageIds()[i])
            if hasattr(page, 'refresh_translations'):
                page.refresh_translations()
    
    def get_campaign_path(self):
        """Get the created campaign path"""
        return self.campaign_path
    
    def on_finished(self, result):
        """Handle wizard completion"""
        if result == QDialog.Accepted:
            try:
                self.create_campaign_files()
            except Exception as e:
                QMessageBox.critical(self, "Creation Error", f"Failed to create campaign:\n{str(e)}")
    
    def create_campaign_files(self):
        """Create the actual campaign files"""
        # Get data from wizard pages
        dest_page = self.page(0)
        recipients_page = self.page(1)
        message_page = self.page(2)
        attachments_page = self.page(3)
        
        destination = dest_page.get_destination()
        recipients_file = recipients_page.get_recipients_file()
        message_file = message_page.get_message_file()
        subject_text = message_page.get_subject_text()
        attachment_files = attachments_page.get_attachment_files()
        
        if not destination:
            raise Exception("No destination folder selected")
        
        campaign_path = Path(destination)
        campaign_path.mkdir(parents=True, exist_ok=True)
        
        # Copy recipients CSV
        if recipients_file:
            shutil.copy2(recipients_file, campaign_path / "recipients.csv")
        
        # Copy message file
        if message_file:
            message_path = Path(message_file)
            if message_path.suffix.lower() == '.docx':
                shutil.copy2(message_file, campaign_path / "msg.docx")
            else:
                shutil.copy2(message_file, campaign_path / "msg.txt")
        
        # Create subject.txt
        if subject_text:
            with open(campaign_path / "subject.txt", 'w', encoding='utf-8') as f:
                f.write(subject_text)
        
        # Copy attachments
        if attachment_files:
            attachments_dir = campaign_path / "attachments"
            attachments_dir.mkdir(exist_ok=True)
            for attachment_file in attachment_files:
                shutil.copy2(attachment_file, attachments_dir)
        
        self.campaign_path = str(campaign_path)


class DestinationPage(QWizardPage):
    """Wizard page for selecting destination folder"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Select Destination"))
        self.setSubTitle(self.tr("Choose where to create your new campaign"))
        
        layout = QVBoxLayout()
        
        # Guidance text
        guidance = QLabel(
            self.tr("Select or create a folder where your campaign files will be stored. "
            "This folder will contain all your campaign data including recipients, "
            "message templates, and attachments.")
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet("color: #6c757d; margin-bottom: 20px;")
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText(self.tr("Select destination folder..."))
        self.folder_path.setReadOnly(True)
        
        browse_button = QPushButton(self.tr("Browse..."))
        browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(browse_button)
        
        layout.addWidget(guidance)
        layout.addLayout(folder_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register field for validation
        self.registerField("destination*", self.folder_path)
    
    def browse_folder(self):
        """Browse for destination folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Campaign Destination Folder"),
            str(Path.home())
        )
        if folder:
            self.folder_path.setText(folder)
    
    def get_destination(self):
        """Get selected destination"""
        return self.folder_path.text()
    
    def refresh_translations(self):
        """Refresh translations for this page"""
        self.setTitle(QCoreApplication.translate("CampaignTab", "Step 1: Select Destination"))
        self.setSubTitle(QCoreApplication.translate("CampaignTab", "Choose where to create your new campaign"))


class RecipientsPage(QWizardPage):
    """Wizard page for selecting recipients CSV"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Recipients"))
        self.setSubTitle(self.tr("Import your recipient data"))
        
        layout = QVBoxLayout()
        
        # Guidance text
        guidance = QLabel(
            self.tr("Select a CSV file containing your recipients. The file should include "
            "an 'email' column and any other data you want to personalize your "
            "messages with (like name, company, etc.).")
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet("color: #6c757d; margin-bottom: 20px;")
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText(self.tr("Select recipients CSV file..."))
        self.file_path.setReadOnly(True)
        
        browse_button = QPushButton(self.tr("Browse..."))
        browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_button)
        
        # Preview area
        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(150)  # Minimum height for readability
        self.preview_table.setMaximumHeight(300)  # Increased from 200 to 300 for better vertical resizing
        self.preview_table.setAlternatingRowColors(True)
        
        layout.addWidget(guidance)
        layout.addLayout(file_layout)
        layout.addWidget(QLabel("Preview:"))
        layout.addWidget(self.preview_table)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register field for validation
        self.registerField("recipients*", self.file_path)
    
    def browse_file(self):
        """Browse for recipients CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Recipients CSV File"),
            str(Path.home()),
            self.tr("CSV Files (*.csv);;All Files (*)")
        )
        if file_path:
            self.file_path.setText(file_path)
            self.load_preview(file_path)
    
    def load_preview(self, csv_path):
        """Load CSV preview"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if not rows:
                    return
                
                # Set up table
                headers = rows[0]
                data_rows = rows[1:4]  # Show first 3 rows
                
                self.preview_table.setRowCount(len(data_rows))
                self.preview_table.setColumnCount(len(headers))
                self.preview_table.setHorizontalHeaderLabels(headers)
                
                # Populate data
                for row_idx, row_data in enumerate(data_rows):
                    for col_idx, cell_data in enumerate(row_data):
                        if col_idx < len(headers):
                            item = QTableWidgetItem(str(cell_data))
                            self.preview_table.setItem(row_idx, col_idx, item)
                
                self.preview_table.resizeColumnsToContents()
                
        except Exception as e:
            self.preview_table.clear()
            self.preview_table.setRowCount(1)
            self.preview_table.setColumnCount(1)
            self.preview_table.setItem(0, 0, QTableWidgetItem(f"Error: {str(e)}"))
    
    def get_recipients_file(self):
        """Get selected recipients file"""
        return self.file_path.text()

    def refresh_translations(self):
        """Refresh translations for this page"""
        self.setTitle(QCoreApplication.translate("CampaignTab", "Step 2: Recipients"))
        self.setSubTitle(QCoreApplication.translate("CampaignTab", "Import your recipient data"))


class MessagePage(QWizardPage):
    """Wizard page for message template and subject"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Message and Subject"))
        self.setSubTitle(self.tr("Set up your email content"))
        
        layout = QVBoxLayout()
        
        # Guidance text
        guidance = QLabel(
            self.tr("Select your message template file and enter the email subject line. "
            "You can use {{variable}} syntax to personalize content with recipient data.")
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet("color: #6c757d; margin-bottom: 20px;")
        
        # Message file selection
        message_group = QGroupBox(self.tr("Message Template"))
        message_layout = QVBoxLayout()
        
        file_layout = QHBoxLayout()
        self.message_file_path = QLineEdit()
        self.message_file_path.setPlaceholderText(self.tr("Select message template (.txt or .docx)..."))
        self.message_file_path.setReadOnly(True)
        
        browse_message_button = QPushButton(self.tr("Browse..."))
        browse_message_button.clicked.connect(self.browse_message_file)
        
        file_layout.addWidget(self.message_file_path)
        file_layout.addWidget(browse_message_button)
        message_layout.addLayout(file_layout)
        message_group.setLayout(message_layout)
        
        # Subject line
        subject_group = QGroupBox(self.tr("Subject Line"))
        subject_layout = QVBoxLayout()
        
        self.subject_text = QLineEdit()
        self.subject_text.setPlaceholderText(self.tr("Enter email subject line..."))
        
        subject_layout.addWidget(self.subject_text)
        subject_group.setLayout(subject_layout)
        
        layout.addWidget(guidance)
        layout.addWidget(message_group)
        layout.addWidget(subject_group)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register fields for validation
        self.registerField("message*", self.message_file_path)
        self.registerField("subject*", self.subject_text)
    
    def browse_message_file(self):
        """Browse for message template file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Message Template File"),
            str(Path.home()),
            self.tr("All Message Files (*.txt *.docx);;Text Files (*.txt);;Word Documents (*.docx);;All Files (*)")
        )
        if file_path:
            self.message_file_path.setText(file_path)
    
    def get_message_file(self):
        """Get selected message file"""
        return self.message_file_path.text()
    
    def get_subject_text(self):
        """Get subject text"""
        return self.subject_text.text()

    def refresh_translations(self):
        """Refresh translations for this page"""
        self.setTitle(QCoreApplication.translate("CampaignTab", "Step 3: Message and Subject"))
        self.setSubTitle(QCoreApplication.translate("CampaignTab", "Create your email content"))


class AttachmentsPage(QWizardPage):
    """Wizard page for selecting attachments"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 4: Attachments"))
        self.setSubTitle(self.tr("Add static attachments (optional)"))
        
        layout = QVBoxLayout()
        
        # Guidance text
        guidance = QLabel(
            self.tr("Select any files you want to attach to all emails. These will be "
            "the same for every recipient. You can add, remove, or modify "
            "attachments later.")
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet("color: #6c757d; margin-bottom: 20px;")
        
        # File selection buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton(self.tr("Add Files..."))
        add_button.clicked.connect(self.add_files)
        
        remove_button = QPushButton(self.tr("Remove Selected"))
        remove_button.clicked.connect(self.remove_selected)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        
        layout.addWidget(guidance)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel(self.tr("Selected attachments:")))
        layout.addWidget(self.file_list)
        
        self.setLayout(layout)
        
        self.attachment_files = []
    
    def add_files(self):
        """Add attachment files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Select Attachment Files"),
            str(Path.home()),
            self.tr("All Files (*)")
        )
        
        for file_path in files:
            if file_path not in self.attachment_files:
                self.attachment_files.append(file_path)
                self.file_list.addItem(Path(file_path).name)
    
    def remove_selected(self):
        """Remove selected files"""
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            if row < len(self.attachment_files):
                self.attachment_files.pop(row)
    
    def get_attachment_files(self):
        """Get selected attachment files"""
        return self.attachment_files
    
    def refresh_translations(self):
        """Refresh translations for this page"""
        self.setTitle(QCoreApplication.translate("CampaignTab", "Step 4: Attachments"))
        self.setSubTitle(QCoreApplication.translate("CampaignTab", "Add files to include with your emails (optional)"))
