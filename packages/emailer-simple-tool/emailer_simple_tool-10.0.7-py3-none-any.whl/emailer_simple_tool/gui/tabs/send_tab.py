"""
Send Tab - Professional email sending and dry run management
Feature Step 9 Implementation
"""

import os
import csv
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QGroupBox, QProgressBar, QCheckBox, QLineEdit,
    QListWidget, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont


class SendWorker(QThread):
    """Worker thread for email sending operations"""
    
    progress_updated = Signal(int, int, str)  # current, total, message
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error_message
    
    def __init__(self, campaign_folder):
        super().__init__()
        self.campaign_folder = campaign_folder
    
    def run(self):
        """Run the email sending in background thread"""
        try:
            from ...core.email_sender import EmailSender
            
            # Create email sender
            sender = EmailSender(self.campaign_folder)
            
            # Emit initial progress
            self.progress_updated.emit(0, 100, self.tr("Initializing email sending..."))
            
            # Perform email sending
            # Define progress callback
            def progress_callback(current, total, message):
                self.progress_updated.emit(current, total, message)
            
            result = sender.send_campaign(gui_mode=True, progress_callback=progress_callback)
            
            if result == 0:  # Success
                # Get recipient count for success message
                import csv
                recipients_file = os.path.join(self.campaign_folder, 'recipients.csv')
                try:
                    with open(recipients_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        count = len(list(reader))
                    self.finished.emit(True, self.tr("Sent {count} emails successfully").format(count=count))
                except:
                    self.finished.emit(True, self.tr("Email campaign completed"))
            else:
                self.finished.emit(False, self.tr("Email sending failed - check validation"))
                
        except Exception as e:
            self.error.emit(str(e))
    """Worker thread for dry run operations"""
    
    progress_updated = Signal(int, int, str)  # current, total, message
    finished = Signal(bool, str, str)  # success, message, custom_name
    error = Signal(str)  # error_message
    
    def __init__(self, campaign_folder, custom_name):
        super().__init__()
        self.campaign_folder = campaign_folder
        self.custom_name = custom_name
    
    def run(self):
        """Run the dry run in background thread"""
        try:
            from ...core.email_sender import EmailSender
            
            # Create email sender
            sender = EmailSender(self.campaign_folder)
            
            # Emit initial progress
            self.progress_updated.emit(0, 100, self.tr("Initializing dry run..."))
            
            # Perform dry run with custom name
            result = sender.dry_run(custom_name=self.custom_name, gui_mode=True)
            
            if result == 0:  # Success
                # Count generated emails for progress
                dry_run_folder = os.path.join(self.campaign_folder, 'dryrun', self.custom_name)
                if os.path.exists(dry_run_folder):
                    eml_files = [f for f in os.listdir(dry_run_folder) if f.endswith('.eml')]
                    count = len(eml_files)
                    self.finished.emit(True, self.tr("Generated {count} email previews").format(count=count), self.custom_name)
                else:
                    self.finished.emit(True, self.tr("Dry run completed"), self.custom_name)
            else:
                self.finished.emit(False, self.tr("Dry run validation failed"), self.custom_name)
                
        except Exception as e:
            self.error.emit(str(e))


class SendTab(QWidget):
    """Professional Send Tab with two-panel layout and safety features"""
    
    # Signals for communication with main window
    campaign_status_changed = Signal(str)
    
    def __init__(self, campaign_manager):
        super().__init__()
        self.campaign_manager = campaign_manager
        self.last_dry_run_timestamp = None
        self.campaign_last_modified = None
        
        # Import translation manager (removed direct assignment that was overriding tr() method)
        from ..translation_manager import translation_manager
        
        self.init_ui()
        self.setup_connections()
        
        # Initialize with "no campaign" state - don't auto-load campaign data
        # Wait for explicit campaign signals from Campaign Tab
        self._show_no_campaign_status()
        
        # Clear lists (they should be empty anyway)
        self.dry_run_list.clear()
        self.reports_list.clear()
    
    def refresh_translations(self):
        """Refresh all translatable UI elements when language changes"""
        # Update group box titles using original English keys
        from PySide6.QtWidgets import QGroupBox, QPushButton
        
        group_boxes = self.findChildren(QGroupBox)
        
        # Map group boxes to their original English titles
        group_box_titles = {
            0: "📁 Dry Run Results",
            1: "📊 Sent Reports", 
            2: "📊 Campaign Status",
            3: "🚀 Send Controls",
            4: "🔍 Validation Results"
        }
        
        for i, gb in enumerate(group_boxes):
            if i in group_box_titles:
                original_title = group_box_titles[i]
                translated_title = self.tr(original_title)
                gb.setTitle(translated_title)
        
        # Update button texts using original English keys
        buttons = self.findChildren(QPushButton)
        
        for btn in buttons:
            btn_text = btn.text()
            # Handle specific button types by their text content
            if "Open" in btn_text or "Ouvrir" in btn_text:
                btn.setText(self.tr("📂 Open Selected"))
            elif "Delete" in btn_text or "Supprimer" in btn_text:
                btn.setText(self.tr("🗑️ Delete Selected"))
            elif "Dry Run" in btn_text or "Test à Blanc" in btn_text:
                btn.setText(self.tr("🧪 Dry Run"))
            elif "Send Campaign" in btn_text or "Envoyer la Campagne" in btn_text:
                btn.setText(self.tr("🚀 Send Campaign"))
        
        # Update labels that might have hardcoded text
        from PySide6.QtWidgets import QLabel
        labels = self.findChildren(QLabel)
        for label in labels:
            label_text = label.text()
            if "Ready to send" in label_text or "Prêt à envoyer" in label_text:
                label.setText(self.tr("Ready to send"))
            elif "Dry Run Name:" in label_text or "Nom du Test :" in label_text:
                label.setText(self.tr("Dry Run Name:"))
        
        # Update placeholder texts
        if hasattr(self, 'dry_run_name'):
            self.dry_run_name.setPlaceholderText(self.tr("custom-name-here"))
        if hasattr(self, 'validation_list'):
            self.validation_list.setPlaceholderText(self.tr("Validation results will appear here..."))
        
        # Update status labels based on current state
        current_status = self.campaign_status_label.text()
        
        if "No Campaign Loaded" in current_status or "Aucune Campagne Chargée" in current_status:
            # Currently showing "no campaign" state - refresh with translated text
            self._show_no_campaign_status()
        else:
            # Currently showing campaign data - refresh the campaign status
            # But preserve button states during language switching
            dry_run_enabled = self.dry_run_btn.isEnabled()
            send_enabled = self.send_btn.isEnabled()
            
            self.update_campaign_status()
            
            # Restore button states if they were enabled before language switch
            if dry_run_enabled:
                self.dry_run_btn.setEnabled(True)
            if send_enabled:
                self.send_btn.setEnabled(True)
    
    def tr(self, text: str) -> str:
        """Translate text using translation manager"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "SendTab")
    
    def init_ui(self):
        """Initialize the Send Tab UI with two-panel layout"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create horizontal splitter for two-panel layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: Campaign Status & Controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right Panel: Dry Run & Sent Reports
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (left panel smaller)
        splitter.setSizes([400, 600])  # Left: 400px, Right: 600px
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Full-width progress system at bottom
        progress_section = self.create_progress_section()
        main_layout.addWidget(progress_section)
        
        self.setLayout(main_layout)
    
    def create_left_panel(self):
        """Create left panel with campaign status and controls"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        
        # Campaign Status Section
        status_group = QGroupBox(self.tr("📊 Campaign Status"))
        status_layout = QVBoxLayout()
        
        self.campaign_status_label = QLabel(self.tr("⚠️ No Campaign Loaded"))
        self.recipients_label = QLabel(self.tr("👥 Recipients: No campaign"))
        self.message_label = QLabel(self.tr("📄 Message: No campaign"))
        self.attachments_label = QLabel(self.tr("📎 Attachments: No campaign"))
        self.pictures_label = QLabel(self.tr("📎 Pictures: No campaign"))
        
        status_layout.addWidget(self.campaign_status_label)
        status_layout.addWidget(self.recipients_label)
        status_layout.addWidget(self.message_label)
        status_layout.addWidget(self.attachments_label)
        status_layout.addWidget(self.pictures_label)
        status_group.setLayout(status_layout)
        
        # Send Controls Section
        controls_group = QGroupBox(self.tr("🚀 Send Controls"))
        controls_layout = QVBoxLayout()
        
        # Dry run name input
        dry_run_layout = QHBoxLayout()
        dry_run_layout.addWidget(QLabel(self.tr("Dry Run Name:")))
        self.dry_run_name = QLineEdit()
        self.dry_run_name.setPlaceholderText(self.tr("custom-name-here"))
        dry_run_layout.addWidget(self.dry_run_name)
        controls_layout.addLayout(dry_run_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.dry_run_btn = QPushButton(self.tr("🧪 Dry Run"))
        self.send_btn = QPushButton(self.tr("🚀 Send Campaign"))
        
        # Style buttons
        self.dry_run_btn.setStyleSheet("QPushButton { background-color: #ffc107; color: #212529; font-weight: bold; }")
        self.send_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; }")
        
        buttons_layout.addWidget(self.dry_run_btn)
        buttons_layout.addWidget(self.send_btn)
        controls_layout.addLayout(buttons_layout)
        
        controls_group.setLayout(controls_layout)
        
        # Validation Results Section
        validation_group = QGroupBox(self.tr("🔍 Validation Results"))
        validation_layout = QVBoxLayout()
        
        self.validation_list = QTextEdit()
        self.validation_list.setMaximumHeight(150)
        self.validation_list.setReadOnly(True)
        self.validation_list.setPlaceholderText(self.tr("Validation results will appear here..."))
        
        validation_layout.addWidget(self.validation_list)
        validation_group.setLayout(validation_layout)
        
        # Add all sections to left panel
        layout.addWidget(status_group)
        layout.addWidget(controls_group)
        layout.addWidget(validation_group)
        layout.addStretch()  # Push everything to top
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Create right panel with dry run and sent reports"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        
        # Dry Run Results Section
        dry_run_group = QGroupBox(self.tr("📁 Dry Run Results"))
        dry_run_layout = QVBoxLayout()
        
        self.dry_run_list = QListWidget()
        # Remove height restriction for better readability
        self.dry_run_list.setMinimumHeight(150)  # Minimum height instead of maximum
        # Enable horizontal scrolling if needed
        self.dry_run_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.dry_run_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Ensure items don't wrap text
        self.dry_run_list.setWordWrap(False)
        dry_run_layout.addWidget(self.dry_run_list)
        
        # Buttons for dry run (Open and Delete on same line)
        dry_run_buttons_layout = QHBoxLayout()
        self.open_dry_run_btn = QPushButton(self.tr("📂 Open Selected"))
        self.delete_dry_run_btn = QPushButton(self.tr("🗑️ Delete Selected"))
        self.delete_dry_run_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: 1px solid #dc3545; } QPushButton:hover { background-color: #c82333; border-color: #bd2130; }")  # Red background, white text
        
        dry_run_buttons_layout.addWidget(self.open_dry_run_btn)
        dry_run_buttons_layout.addWidget(self.delete_dry_run_btn)
        dry_run_layout.addLayout(dry_run_buttons_layout)
        
        dry_run_group.setLayout(dry_run_layout)
        
        # Sent Reports Section
        reports_group = QGroupBox(self.tr("📊 Sent Reports"))
        reports_layout = QVBoxLayout()
        
        self.reports_list = QListWidget()
        # Remove height restriction for better readability
        self.reports_list.setMinimumHeight(150)  # Minimum height instead of maximum
        # Enable horizontal scrolling if needed
        self.reports_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.reports_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Ensure items don't wrap text
        self.reports_list.setWordWrap(False)
        reports_layout.addWidget(self.reports_list)
        
        # Buttons for reports (Open and Delete on same line)
        reports_buttons_layout = QHBoxLayout()
        self.open_report_btn = QPushButton(self.tr("📂 Open Selected"))
        self.delete_report_btn = QPushButton(self.tr("🗑️ Delete Selected"))
        self.delete_report_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: 1px solid #dc3545; } QPushButton:hover { background-color: #c82333; border-color: #bd2130; }")  # Red background, white text
        
        reports_buttons_layout.addWidget(self.open_report_btn)
        reports_buttons_layout.addWidget(self.delete_report_btn)
        reports_layout.addLayout(reports_buttons_layout)
        
        reports_group.setLayout(reports_layout)
        
        # Add sections to right panel
        layout.addWidget(dry_run_group)
        layout.addWidget(reports_group)
        layout.addStretch()  # Push everything to top
        
        panel.setLayout(layout)
        return panel
    
    def create_progress_section(self):
        """Create full-width progress section at bottom"""
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Hidden by default
        layout.addWidget(self.progress_bar)
        
        # Statistics line
        self.stats_label = QLabel(self.tr("Ready to send"))
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        
        progress_frame.setLayout(layout)
        return progress_frame
    
    def setup_connections(self):
        """Setup signal connections"""
        # Button connections (placeholder for now)
        self.dry_run_btn.clicked.connect(self.on_dry_run_clicked)
        self.send_btn.clicked.connect(self.on_send_clicked)
        self.open_dry_run_btn.clicked.connect(self.on_open_dry_run_clicked)
        self.delete_dry_run_btn.clicked.connect(self.on_delete_dry_run_clicked)
        self.open_report_btn.clicked.connect(self.on_open_report_clicked)
        self.delete_report_btn.clicked.connect(self.on_delete_report_clicked)
    
    # Placeholder methods for button actions
    def on_dry_run_clicked(self):
        """Handle dry run button click"""
        if not self.campaign_manager.active_campaign_folder:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.tr(self.tr("No Campaign")), self.tr(self.tr("Please load a campaign first.")))
            return
        
        # Get custom dry run name
        custom_name = self.dry_run_name.text().strip()
        if not custom_name:
            # Generate default name with timestamp
            from datetime import datetime
            custom_name = f"dryrun-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        
        # Validate dry run name (basic validation)
        if not self._validate_dry_run_name(custom_name):
            return
        
        # Start dry run process
        self._start_dry_run(custom_name)
    
    def _extract_folder_name_from_display(self, display_text):
        """Extract actual folder name from formatted display text"""
        # Format: "📁 folder-name - 📅 2025-08-13 07:20 (1 emails)"
        if display_text.startswith('📁 '):
            # Remove the folder icon
            text_without_icon = display_text[2:].strip()  # Remove "📁 "
            
            # Find the separator " - 📅"
            separator_index = text_without_icon.find(' - 📅')
            if separator_index > 0:
                folder_name = text_without_icon[:separator_index].strip()
            else:
                # Fallback: use everything after the icon
                folder_name = text_without_icon
            
            return folder_name
        return display_text
    
    def _extract_report_filename_from_display(self, display_text):
        """Extract actual report filename from formatted display text"""
        # Format: "📊 filename.json - ✅ 2 sent, 0 failed (45s)"
        if display_text.startswith('📊 '):
            # Remove the report icon
            text_without_icon = display_text[2:].strip()  # Remove "📊 "
            
            # Find the separator " - "
            separator_index = text_without_icon.find(' - ')
            if separator_index > 0:
                filename = text_without_icon[:separator_index].strip()
            else:
                # Fallback: use everything after the icon
                filename = text_without_icon
            
            return filename
        return display_text
    
    def _validate_dry_run_name(self, name):
        """Validate dry run folder name"""
        from PySide6.QtWidgets import QMessageBox
        import re
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            QMessageBox.warning(self, self.tr("Invalid Name"), 
                              self.tr("Dry run name can only contain letters, numbers, hyphens, and underscores."))
            return False
        
        # Check length
        if len(name) > 50:
            QMessageBox.warning(self, self.tr("Name Too Long"), 
                              self.tr("Dry run name must be 50 characters or less."))
            return False
        
        # Check if folder already exists
        dry_run_folder = os.path.join(self.campaign_manager.active_campaign_folder, 'dryrun', name)
        if os.path.exists(dry_run_folder):
            reply = QMessageBox.question(self, self.tr("Folder Exists"), 
                                       self.tr("Dry run folder '{name}' already exists. Overwrite?").format(name=name))
            if reply != QMessageBox.Yes:
                return False
        
        return True
    
    def _start_dry_run(self, custom_name):
        """Start the dry run process"""
        try:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.stats_label.setText(self.tr("🧪 Starting dry run..."))
            
            # Disable buttons during operation
            self.dry_run_btn.setEnabled(False)
            self.send_btn.setEnabled(False)
            
            # Import and create email sender
            from ...core.email_sender import EmailSender
            from PySide6.QtCore import QThread, Signal
            
            # Create worker thread for dry run
            self.dry_run_worker = DryRunWorker(self.campaign_manager.active_campaign_folder, custom_name)
            self.dry_run_worker.progress_updated.connect(self._update_dry_run_progress)
            self.dry_run_worker.finished.connect(self._dry_run_finished)
            self.dry_run_worker.error.connect(self._dry_run_error)
            
            # Start the worker
            self.dry_run_worker.start()
            
        except Exception as e:
            self._dry_run_error(f"Failed to start dry run: {str(e)}")
    
    def _update_dry_run_progress(self, current, total, message):
        """Update dry run progress with enhanced display"""
        # Show progress bar
        self.progress_bar.setVisible(True)
        
        # Update progress bar
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
        else:
            # Indeterminate progress for initialization
            self.progress_bar.setRange(0, 0)
        
        # Update statistics display
        self._update_progress_statistics("dry_run", current, total, message)
    
    def _dry_run_finished(self, success, message, custom_name):
        """Handle dry run completion"""
        # Reset progress system
        self._reset_progress_system()
        
        if success:
            self.stats_label.setText(self.tr("✅ Dry run completed: {message}").format(message=message))
            
            # Update dry run timestamp
            from datetime import datetime
            self.last_dry_run_timestamp = datetime.now()
            
            # Refresh dry run list
            self.refresh_dry_run_list()
            
            # Update button states - now send can be enabled
            self.check_fresh_dry_run_status()
            
            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("Dry Run Complete"), 
                                  self.tr("Dry run '{custom_name}' completed successfully!\n\n{message}").format(custom_name=custom_name, message=message))
        else:
            self.stats_label.setText(self.tr("❌ Dry run failed: {message}").format(message=message))
            
            # Show error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Dry Run Failed"), self.tr("Dry run failed:\n\n{message}").format(message=message))
        
        # Re-enable buttons
        self._update_button_states_after_operation()
    
    def _dry_run_error(self, error_message):
        """Handle dry run error"""
        self._reset_progress_system()
        self.stats_label.setText(self.tr("❌ Dry run error: {error_message}").format(error_message=error_message))
        
        # Show error message
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, self.tr("Dry Run Error"), self.tr("An error occurred during dry run:\n\n{error_message}").format(error_message=error_message))
        
        # Re-enable buttons
        self._update_button_states_after_operation()
    
    def _update_button_states_after_operation(self):
        """Update button states after dry run or send operation"""
        if not self.campaign_manager.active_campaign_folder:
            self.dry_run_btn.setEnabled(False)
            self.send_btn.setEnabled(False)
            return
        
        # Check campaign validation
        from ...utils.validators import validate_campaign_folder
        validation_result = validate_campaign_folder(self.campaign_manager.active_campaign_folder)
        
        # Enable dry run if campaign is valid
        self.dry_run_btn.setEnabled(validation_result.is_valid)
        
        # Enable send only if campaign is valid AND fresh dry run exists
        has_fresh_dry_run = self._has_fresh_dry_run()
        self.send_btn.setEnabled(validation_result.is_valid and has_fresh_dry_run)
    
    def _add_dry_run_status_to_validation(self):
        """Add dry run status to validation with enhanced messaging"""
        has_fresh = self._has_fresh_dry_run()
        
        if has_fresh:
            self.validation_list.append(self.tr("\n✅ Fresh dry run completed - Ready to send"))
            if hasattr(self, 'last_dry_run_timestamp'):
                from datetime import datetime
                time_ago = datetime.now() - self.last_dry_run_timestamp
                if time_ago.total_seconds() < 300:  # Less than 5 minutes
                    self.validation_list.append(self.tr("   📅 Dry run completed moments ago"))
                else:
                    minutes_ago = int(time_ago.total_seconds() / 60)
                    self.validation_list.append(self.tr("   📅 Dry run completed {minutes_ago} minutes ago").format(minutes_ago=minutes_ago))
        else:
            self.validation_list.append(self.tr("\n⚠️ Fresh dry run required before sending"))
            self.validation_list.append(self.tr("   → Click 'Dry Run' to test your campaign first"))
            self.validation_list.append(self.tr("   → This ensures your emails look correct before sending"))
    
    def check_fresh_dry_run_status(self):
        """Check if we have a fresh dry run with enhanced status updates"""
        if not self.campaign_manager.active_campaign_folder:
            return
        
        # Update the entire campaign status including validation display
        self.update_campaign_status()
        
        # Update button states
        self._update_button_states_after_operation()
    
    def _has_fresh_dry_run(self):
        """Check if we have a fresh dry run (campaign not modified since last dry run)"""
        campaign_folder = self.campaign_manager.active_campaign_folder
        if not campaign_folder:
            return False
        
        try:
            # First, try to find the most recent dry run folder
            dryrun_folder = os.path.join(campaign_folder, 'dryrun')
            if not os.path.exists(dryrun_folder):
                return False
            
            # Find the most recent dry run folder
            dry_run_folders = [d for d in os.listdir(dryrun_folder) 
                             if os.path.isdir(os.path.join(dryrun_folder, d))]
            
            if not dry_run_folders:
                return False
            
            # Get the most recent dry run folder by modification time
            most_recent_folder = None
            most_recent_time = 0
            
            for folder in dry_run_folders:
                folder_path = os.path.join(dryrun_folder, folder)
                folder_mtime = os.path.getmtime(folder_path)
                if folder_mtime > most_recent_time:
                    most_recent_time = folder_mtime
                    most_recent_folder = folder_path
            
            if not most_recent_folder:
                return False
            
            # Check if the dry run folder has .eml files
            eml_files = [f for f in os.listdir(most_recent_folder) if f.endswith('.eml')]
            if not eml_files:
                return False
            
            # Use the dry run timestamp if we don't have one set
            from datetime import datetime
            dry_run_timestamp = datetime.fromtimestamp(most_recent_time)
            
            if not self.last_dry_run_timestamp:
                # Set the timestamp based on the most recent dry run folder
                self.last_dry_run_timestamp = dry_run_timestamp
            else:
                # Use the more recent of the two timestamps
                if dry_run_timestamp > self.last_dry_run_timestamp:
                    self.last_dry_run_timestamp = dry_run_timestamp
            
            # Check if any campaign files have been modified since the dry run
            key_files = ['recipients.csv', 'subject.txt', 'msg.txt', 'msg.docx']
            
            for filename in key_files:
                file_path = os.path.join(campaign_folder, filename)
                if os.path.exists(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime > self.last_dry_run_timestamp.timestamp():
                        return False
            
            # Check attachments folder
            attachments_folder = os.path.join(campaign_folder, 'attachments')
            if os.path.exists(attachments_folder):
                for root, dirs, files in os.walk(attachments_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_mtime = os.path.getmtime(file_path)
                        if file_mtime > self.last_dry_run_timestamp.timestamp():
                            return False
            
            # Check picture generator projects that are attached
            picture_folder = os.path.join(campaign_folder, 'picture-generator')
            if os.path.exists(picture_folder):
                for project_name in os.listdir(picture_folder):
                    project_path = os.path.join(picture_folder, project_name)
                    if not os.path.isdir(project_path):
                        continue
                    
                    # Check if project is attached
                    attach_file = os.path.join(project_path, 'attach.txt')
                    if os.path.exists(attach_file):
                        try:
                            with open(attach_file, 'r', encoding='utf-8') as f:
                                if f.read().strip().lower() == 'true':
                                    # This project is attached, check its modification time
                                    for root, dirs, files in os.walk(project_path):
                                        for file in files:
                                            if file != 'attach.txt':  # Don't check attach.txt itself
                                                file_path = os.path.join(root, file)
                                                file_mtime = os.path.getmtime(file_path)
                                                if file_mtime > self.last_dry_run_timestamp.timestamp():
                                                    return False
                        except:
                            pass
            
            return True
            
        except Exception:
            # If we can't check, assume not fresh
            return False
    
    def on_send_clicked(self):
        """Handle send button click with safety confirmation"""
        if not self.campaign_manager.active_campaign_folder:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.tr("No Campaign"), self.tr("Please load a campaign first."))
            return
        
        # Check if campaign is valid
        from ...utils.validators import validate_campaign_folder
        validation_result = validate_campaign_folder(self.campaign_manager.active_campaign_folder)
        
        if not validation_result.is_valid:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Campaign Invalid"), 
                               self.tr("Cannot send campaign. Please fix validation errors first."))
            return
        
        # Check if fresh dry run exists
        if not self._has_fresh_dry_run():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.tr("Dry Run Required"), 
                              self.tr("A fresh dry run is required before sending. Please run a dry run first."))
            return
        
        # Show confirmation dialog
        self._show_send_confirmation_dialog()
    
    def _show_send_confirmation_dialog(self):
        """Show the enhanced campaign name confirmation dialog"""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                     QPushButton, QLineEdit, QCheckBox, QFrame)
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        
        # Get campaign info
        campaign_folder = self.campaign_manager.active_campaign_folder
        campaign_name = os.path.basename(campaign_folder)
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("⚠️ Confirm Email Campaign Send"))
        dialog.setModal(True)
        dialog.resize(550, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #212529;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0d6efd;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton#cancel_btn {
                background-color: #6c757d;
                color: white;
                border: none;
            }
            QPushButton#cancel_btn:hover {
                background-color: #5a6268;
            }
            QPushButton#send_btn:enabled {
                background-color: #dc3545;
                color: white;
                border: none;
            }
            QPushButton#send_btn:enabled:hover {
                background-color: #c82333;
            }
            QPushButton#send_btn:disabled {
                background-color: #e9ecef;
                color: #6c757d;
                border: 1px solid #dee2e6;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Warning header with icon
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px;")
        header_layout = QVBoxLayout()
        
        warning_label = QLabel(self.tr("⚠️  CONFIRM EMAIL CAMPAIGN SEND"))
        warning_font = QFont()
        warning_font.setPointSize(16)
        warning_font.setBold(True)
        warning_label.setFont(warning_font)
        warning_label.setStyleSheet("color: #856404; background: transparent; border: none; padding: 0;")
        warning_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(warning_label)
        
        subtitle_label = QLabel(self.tr("This action will send real emails to all recipients"))
        subtitle_label.setStyleSheet("color: #856404; background: transparent; border: none; padding: 0; font-style: italic;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Campaign name verification
        verify_frame = QFrame()
        verify_frame.setStyleSheet("background-color: #e7f3ff; border: 1px solid #b3d9ff; border-radius: 4px; padding: 15px;")
        verify_layout = QVBoxLayout()
        
        verify_label = QLabel(self.tr("🔐 Security Verification"))
        verify_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px; background: transparent; border: none;")
        verify_layout.addWidget(verify_label)
        
        instruction_label = QLabel(self.tr("To confirm, please type the campaign name below:"))
        instruction_label.setStyleSheet("margin-bottom: 5px; background: transparent; border: none;")
        verify_layout.addWidget(instruction_label)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText(campaign_name)
        name_input.setStyleSheet("background-color: white;")
        verify_layout.addWidget(name_input)
        
        verify_frame.setLayout(verify_layout)
        layout.addWidget(verify_frame)
        
        # Confirmation checkboxes
        checkbox_frame = QFrame()
        checkbox_frame.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 4px; padding: 15px;")
        checkbox_layout = QVBoxLayout()
        
        checkbox_title = QLabel(self.tr("✅ Final Confirmations"))
        checkbox_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        checkbox_layout.addWidget(checkbox_title)
        
        checkbox1 = QCheckBox(self.tr("I have reviewed the campaign and recipients"))
        checkbox2 = QCheckBox(self.tr("I understand this will send real emails"))
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        
        checkbox_frame.setLayout(checkbox_layout)
        layout.addWidget(checkbox_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.setObjectName("cancel_btn")
        send_btn = QPushButton(self.tr("🚀 Send Campaign"))
        send_btn.setObjectName("send_btn")
        send_btn.setEnabled(False)  # Disabled until conditions met
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(send_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Enhanced validation function
        def validate_form():
            name_matches = name_input.text().strip() == campaign_name
            both_checked = checkbox1.isChecked() and checkbox2.isChecked()
            
            # Update visual feedback
            if name_input.text().strip() and not name_matches:
                name_input.setStyleSheet("background-color: #f8d7da; border-color: #dc3545;")
            elif name_matches:
                name_input.setStyleSheet("background-color: #d4edda; border-color: #28a745;")
            else:
                name_input.setStyleSheet("background-color: white; border-color: #dee2e6;")
            
            send_btn.setEnabled(name_matches and both_checked)
        
        # Connect validation
        name_input.textChanged.connect(validate_form)
        checkbox1.toggled.connect(validate_form)
        checkbox2.toggled.connect(validate_form)
        
        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        send_btn.clicked.connect(dialog.accept)
        
        # Focus on name input
        name_input.setFocus()
        
        # Show dialog and handle result
        if dialog.exec() == QDialog.Accepted:
            self._start_send_campaign()
    
    def _start_send_campaign(self):
        """Start the actual email sending process"""
        try:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.stats_label.setText(self.tr("📧 Starting email campaign..."))
            
            # Disable buttons during operation
            self.dry_run_btn.setEnabled(False)
            self.send_btn.setEnabled(False)
            
            # Create worker thread for sending
            self.send_worker = SendWorker(self.campaign_manager.active_campaign_folder)
            self.send_worker.progress_updated.connect(self._update_send_progress)
            self.send_worker.finished.connect(self._send_finished)
            self.send_worker.error.connect(self._send_error)
            
            # Start the worker
            self.send_worker.start()
            
        except Exception as e:
            self._send_error(f"Failed to start sending: {str(e)}")
    
    def _update_send_progress(self, current, total, message):
        """Update send progress with enhanced display"""
        # Show progress bar
        self.progress_bar.setVisible(True)
        
        # Update progress bar
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
        else:
            # Indeterminate progress for initialization
            self.progress_bar.setRange(0, 0)
        
        # Update statistics display
        self._update_progress_statistics("send", current, total, message)
    
    def _update_progress_statistics(self, operation_type, current, total, message):
        """Update progress statistics display"""
        from datetime import datetime
        
        # Initialize operation start time if not set
        if not hasattr(self, 'operation_start_time'):
            self.operation_start_time = datetime.now()
        
        # Calculate elapsed time
        elapsed = datetime.now() - self.operation_start_time
        elapsed_seconds = elapsed.total_seconds()
        elapsed_str = self._format_duration(elapsed_seconds)
        
        # Calculate estimated time remaining
        eta_str = self.tr("Unknown")
        if current > 0 and total > 0 and elapsed_seconds > 0:
            rate = current / elapsed_seconds
            if rate > 0:
                remaining_items = total - current
                eta_seconds = remaining_items / rate
                eta_str = self._format_duration(eta_seconds)
        
        # Format operation-specific message
        if operation_type == "dry_run":
            icon = "🧪"
            operation_name = self.tr("Dry run")
            if current == total and total > 0:
                stats_text = f"✅ Generated: {current} | ⏱️ Completed in: {elapsed_str}"
            else:
                stats_text = f"📧 Generated: {current}/{total} | ⏱️ Elapsed: {elapsed_str} | 🕐 ETA: {eta_str}"
        else:  # send
            icon = "📧"
            operation_name = self.tr("Sending")
            if current == total and total > 0:
                stats_text = f"✅ Sent: {current} | ⏱️ Completed in: {elapsed_str}"
            else:
                stats_text = f"📧 Sent: {current}/{total} | ⏱️ Elapsed: {elapsed_str} | 🕐 ETA: {eta_str}"
        
        # Update display
        if total > 0:
            percentage = int((current / total) * 100)
            main_text = f"{icon} {operation_name}... {current}/{total} ({percentage}%)"
        else:
            main_text = f"{icon} {message}"
        
        # Set the statistics label with both main text and stats
        full_text = f"{main_text}\n{stats_text}"
        self.stats_label.setText(full_text)
    
    def _format_duration(self, seconds):
        """Format duration in human-readable format"""
        if seconds < 1:
            return "< 1s"
        elif seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = int(seconds % 60)
            if remaining_seconds == 0:
                return f"{minutes}m"
            return f"{minutes}m{remaining_seconds}s"
        else:
            hours = int(seconds / 3600)
            remaining_minutes = int((seconds % 3600) / 60)
            if remaining_minutes == 0:
                return f"{hours}h"
            return f"{hours}h{remaining_minutes}m"
    
    def _reset_progress_system(self):
        """Reset progress system to initial state"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)  # Reset to determinate mode
        self.progress_bar.setValue(0)
        self.stats_label.setText(self.tr("Ready to send"))
        
    def refresh_all_data(self):
        """Refresh all Send Tab data - called when campaign changes"""
        # Update campaign status
        self.update_campaign_status()
        
        # Check fresh dry run status
        self.check_fresh_dry_run_status()
        
        # Refresh lists
        self.refresh_dry_run_list()
        self.refresh_reports_list()
        
        # Reset progress system
        self._reset_progress_system()
    
    def on_campaign_changed(self):
        """Handle campaign change from other tabs"""
        # Mark that campaign has changed (invalidates dry run)
        if hasattr(self, 'last_dry_run_timestamp'):
            delattr(self, 'last_dry_run_timestamp')
        
        # Refresh all data
        self.refresh_all_data()
    
    def on_smtp_changed(self):
        """Handle SMTP configuration change from SMTP tab"""
        # Update campaign status to reflect SMTP changes
        self.update_campaign_status()

    def on_picture_settings_changed(self):
        """Handle picture settings change from Picture tab"""
        # Update campaign status to reflect picture changes
        self.update_campaign_status()

    def set_campaign_path(self, campaign_path: str):
        """Handle campaign change from main window"""
        # Ensure the campaign is loaded in campaign_manager
        # (Campaign Tab should have already loaded it, but let's be safe)
        if self.campaign_manager.active_campaign_folder != campaign_path:
            result = self.campaign_manager.create_or_load_campaign(campaign_path)
            if result != 0:
                # Failed to load campaign
                self._show_no_campaign_status()
                return
        
        # Now refresh our data with the loaded campaign
        self.refresh_all_data()
        
    def clear_campaign(self):
        """Handle campaign cleared from main window"""
        # Reset to no campaign state
        self._show_no_campaign_status()
        
        # Clear lists
        self.dry_run_list.clear()
        self.reports_list.clear()
        
        # Reset progress system
        self._reset_progress_system()
        
        # Clear dry run name input
        self.dry_run_name.clear()

    def on_open_dry_run_clicked(self):
        """Handle open dry run button click"""
        current_item = self.dry_run_list.currentItem()
        if not current_item:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("No Selection"), self.tr("Please select a dry run folder to open."))
            return
        
        # Extract folder name from single-line display text
        display_text = current_item.text()
        folder_name = self._extract_folder_name_from_display(display_text)
        
        # Build full path
        dry_run_folder = os.path.join(
            self.campaign_manager.active_campaign_folder, 
            'dryrun', 
            folder_name
        )
        
        if os.path.exists(dry_run_folder):
            self._open_folder_in_explorer(dry_run_folder)
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.tr("Folder Not Found"), self.tr("Dry run folder '{folder_name}' not found.").format(folder_name=folder_name))

    def on_delete_dry_run_clicked(self):
        """Handle delete dry run button click"""
        current_item = self.dry_run_list.currentItem()
        if not current_item:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("No Selection"), self.tr("Please select a dry run folder to delete."))
            return
        
        # Extract folder name from display text
        display_text = current_item.text()
        folder_name = self._extract_folder_name_from_display(display_text)
        
        # Confirm deletion
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            self.tr("Confirm Deletion"), 
            self.tr("Are you sure you want to delete the dry run '{folder_name}'?\n\nThis action cannot be undone.").format(folder_name=folder_name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Build full path
            dry_run_folder = os.path.join(
                self.campaign_manager.active_campaign_folder, 
                'dryrun', 
                folder_name
            )
            
            try:
                import shutil
                if os.path.exists(dry_run_folder):
                    shutil.rmtree(dry_run_folder)
                    # Refresh the list
                    self.refresh_dry_run_list()
                    QMessageBox.information(self, self.tr("Deleted"), self.tr("Dry run '{folder_name}' deleted successfully.").format(folder_name=folder_name))
                else:
                    QMessageBox.warning(self, self.tr("Folder Not Found"), self.tr("Dry run folder '{folder_name}' not found.").format(folder_name=folder_name))
            except Exception as e:
                QMessageBox.critical(self, self.tr("Delete Error"), self.tr("Could not delete dry run folder:\n\n{error}").format(error=str(e)))

    def _open_folder_in_explorer(self, folder_path):
        """Open folder in system file explorer"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif system == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", folder_path])
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Error Opening Folder"), 
                               self.tr("Could not open folder in file explorer:\n\n{error}").format(error=str(e)))

    def on_open_report_clicked(self):
        """Handle open report button click"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("No Selection"), self.tr("Please select a sent report to open."))
            return
        
        # Extract report filename from single-line display text
        display_text = current_item.text()
        report_filename = self._extract_report_filename_from_display(display_text)
        
        # Build full path
        report_file = os.path.join(
            self.campaign_manager.active_campaign_folder, 
            'sentreport', 
            report_filename
        )
        
        if os.path.exists(report_file):
            self._open_file_with_default_app(report_file)
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.tr("File Not Found"), self.tr("Report file '{report_filename}' not found.").format(report_filename=report_filename))

    def _open_file_with_default_app(self, file_path):
        """Open file with system default application"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            elif system == "Windows":
                subprocess.run(["start", file_path], shell=True)
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path])
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Error Opening File"), 
                               self.tr("Could not open file with default application:\n\n{error}").format(error=str(e)))

    def on_delete_report_clicked(self):
        """Handle delete report button click"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("No Selection"), self.tr("Please select a sent report to delete."))
            return
        
        # Extract report filename from display text
        display_text = current_item.text()
        report_filename = self._extract_report_filename_from_display(display_text)
        
        # Confirm deletion
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            self.tr("Confirm Deletion"), 
            self.tr("Are you sure you want to delete the report '{report_filename}'?\n\nThis action cannot be undone.").format(report_filename=report_filename),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Build full path
            report_file = os.path.join(
                self.campaign_manager.active_campaign_folder, 
                'sentreport', 
                report_filename
            )
            
            try:
                if os.path.exists(report_file):
                    os.remove(report_file)
                    # Refresh the list
                    self.refresh_reports_list()
                    QMessageBox.information(self, self.tr("Deleted"), self.tr("Report '{report_filename}' deleted successfully.").format(report_filename=report_filename))
                else:
                    QMessageBox.warning(self, self.tr("File Not Found"), self.tr("Report file '{report_filename}' not found.").format(report_filename=report_filename))
            except Exception as e:
                QMessageBox.critical(self, self.tr("Delete Error"), self.tr("Could not delete report file:\n\n{error}").format(error=str(e)))

    def update_campaign_status(self):
        """Update campaign status display with real data"""
        if not self.campaign_manager.active_campaign_folder:
            self._show_no_campaign_status()
            return
        
        try:
            # Import validation here to avoid circular imports
            from ...utils.validators import validate_campaign_folder
            from ...core.email_sender import EmailSender
            import os
            import csv
            
            campaign_folder = self.campaign_manager.active_campaign_folder
            
            # Validate campaign
            validation_result = validate_campaign_folder(campaign_folder)
            
            # Update overall campaign status
            if validation_result.is_valid:
                self.campaign_status_label.setText(self.tr("✅ Campaign: Ready to Send"))
                self.campaign_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.campaign_status_label.setText(self.tr("❌ Campaign: Issues Found"))
                self.campaign_status_label.setStyleSheet("color: red; font-weight: bold;")
            
            # Update recipients status
            self._update_recipients_status(campaign_folder)
            
            # Update message status
            self._update_message_status(campaign_folder)
            
            # Update attachments status
            self._update_attachments_status(campaign_folder)
            
            # Update pictures status
            self._update_pictures_status(campaign_folder)
            
            # Update validation results
            self._update_validation_results(validation_result)
            
            # Update button states based on validation
            self._update_button_states(validation_result.is_valid)
            
        except Exception as e:
            self.campaign_status_label.setText(self.tr("❌ Campaign: Error - {error}").format(error=str(e)))
            self.campaign_status_label.setStyleSheet("color: red; font-weight: bold;")

    def _show_no_campaign_status(self):
        """Show status when no campaign is loaded"""
        self.campaign_status_label.setText(self.tr("⚠️ No Campaign Loaded"))
        self.campaign_status_label.setStyleSheet("color: orange; font-weight: bold;")
        self.recipients_label.setText(self.tr("👥 Recipients: No campaign"))
        self.message_label.setText(self.tr("📄 Message: No campaign"))
        self.attachments_label.setText(self.tr("📎 Attachments: No campaign"))
        self.pictures_label.setText(self.tr("📎 Pictures: No campaign"))
        
        # Disable buttons
        self.dry_run_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        
        # Clear validation
        self.validation_list.clear()
        self.validation_list.append(self.tr("⚠️ No campaign loaded. Please load a campaign first."))

    def _update_recipients_status(self, campaign_folder):
        """Update recipients status"""
        try:
            recipients_file = os.path.join(campaign_folder, 'recipients.csv')
            if os.path.exists(recipients_file):
                with open(recipients_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    recipients = list(reader)
                    count = len(recipients)
                    
                    # Basic email validation count
                    valid_count = sum(1 for r in recipients if '@' in r.get('email', ''))
                    invalid_count = count - valid_count
                    
                    if invalid_count == 0:
                        self.recipients_label.setText(self.tr("👥 Recipients: {count} valid").format(count=count))
                        self.recipients_label.setStyleSheet("color: green;")
                    else:
                        self.recipients_label.setText(self.tr("👥 Recipients: {valid_count} valid, {invalid_count} errors").format(valid_count=valid_count, invalid_count=invalid_count))
                        self.recipients_label.setStyleSheet("color: red;")
            else:
                self.recipients_label.setText(self.tr("👥 Recipients: File missing"))
                self.recipients_label.setStyleSheet("color: red;")
        except Exception as e:
            self.recipients_label.setText(self.tr("👥 Recipients: Error reading file"))
            self.recipients_label.setStyleSheet("color: red;")

    def _update_message_status(self, campaign_folder):
        """Update message status"""
        msg_txt = os.path.join(campaign_folder, 'msg.txt')
        msg_docx = os.path.join(campaign_folder, 'msg.docx')
        
        if os.path.exists(msg_docx):
            self.message_label.setText(self.tr("📄 Message: msg.docx validated"))
            self.message_label.setStyleSheet("color: green;")
        elif os.path.exists(msg_txt):
            self.message_label.setText(self.tr("📄 Message: msg.txt validated"))
            self.message_label.setStyleSheet("color: green;")
        else:
            self.message_label.setText(self.tr("📄 Message: Missing msg.txt or msg.docx"))
            self.message_label.setStyleSheet("color: red;")

    def _update_attachments_status(self, campaign_folder):
        """Update attachments status"""
        attachments_folder = os.path.join(campaign_folder, 'attachments')
        
        if os.path.exists(attachments_folder):
            try:
                files = [f for f in os.listdir(attachments_folder) 
                        if os.path.isfile(os.path.join(attachments_folder, f)) and not f.startswith('.')]
                
                if files:
                    # Calculate total size
                    total_size = 0
                    for f in files:
                        file_path = os.path.join(attachments_folder, f)
                        total_size += os.path.getsize(file_path)
                    
                    size_mb = total_size / (1024 * 1024)
                    
                    # Format size with appropriate precision
                    if size_mb < 0.1:
                        size_str = f"{size_mb:.2f}"  # Show 2 decimals for small files
                    else:
                        size_str = f"{size_mb:.1f}"  # Show 1 decimal for larger files
                    
                    if size_mb > 25:  # Gmail limit
                        self.attachments_label.setText(self.tr("📎 Attachments: {count} files ({size_mb} MB - Too large!)").format(count=len(files), size_mb=size_str))
                        self.attachments_label.setStyleSheet("color: red;")
                    elif size_mb > 10:  # Warning threshold
                        self.attachments_label.setText(self.tr("📎 Attachments: {count} files ({size_mb} MB)").format(count=len(files), size_mb=size_str))
                        self.attachments_label.setStyleSheet("color: orange;")
                    else:
                        self.attachments_label.setText(self.tr("📎 Attachments: {count} files ({size_mb} MB)").format(count=len(files), size_mb=size_str))
                        self.attachments_label.setStyleSheet("color: green;")
                else:
                    self.attachments_label.setText(self.tr("📎 Attachments: Folder empty"))
                    self.attachments_label.setStyleSheet("color: gray;")
            except Exception as e:
                self.attachments_label.setText(self.tr("📎 Attachments: Error reading folder"))
                self.attachments_label.setStyleSheet("color: red;")
        else:
            self.attachments_label.setText(self.tr("📎 Attachments: No attachments folder"))
            self.attachments_label.setStyleSheet("color: gray;")

    def _update_pictures_status(self, campaign_folder):
        """Update pictures status with count and average size information"""
        try:
            pictures_folder = os.path.join(campaign_folder, 'picture-generator')
            if os.path.exists(pictures_folder) and os.path.isdir(pictures_folder):
                # Check for projects
                projects = [d for d in os.listdir(pictures_folder) 
                           if os.path.isdir(os.path.join(pictures_folder, d))]
                
                if projects:
                    # Check if any project has images and is set to attach
                    total_images = 0
                    attached_projects = 0
                    total_image_size = 0
                    
                    for project in projects:
                        project_path = os.path.join(pictures_folder, project)
                        data_folder = os.path.join(project_path, 'data')
                        attach_file = os.path.join(project_path, 'attach.txt')
                        
                        # Check if project is set to attach
                        is_attached = False
                        if os.path.exists(attach_file):
                            try:
                                with open(attach_file, 'r', encoding='utf-8') as f:
                                    is_attached = f.read().strip().lower() == 'true'
                            except:
                                pass
                        
                        if is_attached:
                            attached_projects += 1
                            # Count images and calculate size in data folder
                            if os.path.exists(data_folder):
                                images = [f for f in os.listdir(data_folder) 
                                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                                total_images += len(images)
                                
                                # Calculate total size of images
                                for img in images:
                                    img_path = os.path.join(data_folder, img)
                                    try:
                                        total_image_size += os.path.getsize(img_path)
                                    except:
                                        pass
                    
                    if attached_projects > 0:
                        if total_images > 0:
                            # Calculate average size per image
                            avg_size_bytes = total_image_size / total_images
                            avg_size_kb = avg_size_bytes / 1024
                            
                            # Format size appropriately
                            if avg_size_kb < 1024:
                                avg_size_str = f"{avg_size_kb:.0f} KB"
                            else:
                                avg_size_mb = avg_size_kb / 1024
                                avg_size_str = f"{avg_size_mb:.1f} MB"
                            
                            # Calculate total size per recipient (assuming 1 image per recipient per project)
                            total_size_per_recipient = total_image_size / total_images * attached_projects
                            total_size_mb = total_size_per_recipient / (1024 * 1024)
                            
                            if total_size_mb < 0.1:
                                total_size_str = f"{total_size_mb:.2f} MB"
                            else:
                                total_size_str = f"{total_size_mb:.1f} MB"
                            
                            self.pictures_label.setText(self.tr("📎 Pictures: {attached_projects} project(s), avg {avg_size}/image (~{total_size}/recipient)").format(
                                attached_projects=attached_projects, 
                                avg_size=avg_size_str,
                                total_size=total_size_str
                            ))
                            self.pictures_label.setStyleSheet("color: green;")
                        else:
                            self.pictures_label.setText(self.tr("📎 Pictures: {attached_projects} project(s) attached, no images generated").format(attached_projects=attached_projects))
                            self.pictures_label.setStyleSheet("color: orange;")
                    else:
                        self.pictures_label.setText(self.tr("📎 Pictures: {total_projects} project(s) exist, none attached").format(total_projects=len(projects)))
                        self.pictures_label.setStyleSheet("color: orange;")
                else:
                    self.pictures_label.setText(self.tr("📎 Pictures: No projects found"))
                    self.pictures_label.setStyleSheet("color: orange;")
            else:
                self.pictures_label.setText(self.tr("📎 Pictures: No folder"))
                self.pictures_label.setStyleSheet("color: orange;")
        except Exception as e:
            self.pictures_label.setText(self.tr("📎 Pictures: Error checking folder"))
            self.pictures_label.setStyleSheet("color: red;")

    def _update_validation_results(self, validation_result):
        """Update validation results display with enhanced messaging"""
        self.validation_list.clear()
        
        if validation_result.is_valid:
            self.validation_list.append(self.tr("✅ All validations passed - Campaign ready to send"))
            
            # Add specific success confirmations
            self.validation_list.append(self.tr("✅ Recipients file validated"))
            self.validation_list.append(self.tr("✅ Message template validated"))
            self.validation_list.append(self.tr("✅ Campaign structure verified"))
            
            # Add any warnings with guidance
            if validation_result.warnings:
                self.validation_list.append(self.tr("\n⚠️ Warnings (campaign can still be sent):"))
                for warning in validation_result.warnings:
                    self.validation_list.append(f"   • {warning}")
                    # Add specific guidance for common warnings
                    if "large" in warning.lower() and "attachment" in warning.lower():
                        self.validation_list.append(self.tr("     → Consider compressing large files or using cloud links"))
                    elif "domain" in warning.lower():
                        self.validation_list.append(self.tr("     → Verify recipient email domains are correct"))
        else:
            self.validation_list.append(self.tr("❌ Campaign validation failed - Fix these issues to continue:"))
            
            # Group errors by category for better organization
            file_errors = []
            content_errors = []
            config_errors = []
            
            for error in validation_result.errors:
                if "file" in error.lower() or "missing" in error.lower():
                    file_errors.append(error)
                elif "recipient" in error.lower() or "email" in error.lower():
                    content_errors.append(error)
                else:
                    config_errors.append(error)
            
            # Display categorized errors with specific guidance
            if file_errors:
                self.validation_list.append(self.tr("\n📁 File Issues:"))
                for error in file_errors:
                    self.validation_list.append(f"   ❌ {error}")
                    if "recipients.csv" in error:
                        self.validation_list.append(self.tr("     → Create recipients.csv with 'name' and 'email' columns"))
                    elif "msg.txt" in error or "msg.docx" in error:
                        self.validation_list.append(self.tr("     → Create msg.txt (plain text) or msg.docx (formatted)"))
                    elif "subject.txt" in error:
                        self.validation_list.append(self.tr("     → Create subject.txt with your email subject line"))
            
            if content_errors:
                self.validation_list.append(self.tr("\n📧 Content Issues:"))
                for error in content_errors:
                    self.validation_list.append(f"   ❌ {error}")
                    if "email" in error.lower():
                        self.validation_list.append(self.tr("     → Check email addresses in recipients.csv"))
                    elif "template" in error.lower():
                        self.validation_list.append(self.tr("     → Verify {{variables}} match CSV column names"))
            
            if config_errors:
                self.validation_list.append(self.tr("\n⚙️ Configuration Issues:"))
                for error in config_errors:
                    self.validation_list.append(f"   ❌ {error}")
                    if "smtp" in error.lower():
                        self.validation_list.append(self.tr("     → Configure SMTP settings in the SMTP tab"))
            
            # Add warnings if any
            if validation_result.warnings:
                self.validation_list.append(self.tr("\n⚠️ Additional Warnings:"))
                for warning in validation_result.warnings:
                    self.validation_list.append(f"   • {warning}")
        
        # Add fresh dry run status with enhanced messaging
        self._add_dry_run_status_to_validation()

    def _update_button_states(self, is_valid):
        """Update button states based on validation"""
        # For now, enable dry run if campaign is valid
        # Send button will be handled later with fresh dry run logic
        self.dry_run_btn.setEnabled(is_valid)
        self.send_btn.setEnabled(False)  # Will be enabled after fresh dry run

    def refresh_dry_run_list(self):
        """Refresh dry run list with existing dry run folders"""
        self.dry_run_list.clear()
        
        if not self.campaign_manager.active_campaign_folder:
            return
        
        dry_run_base_folder = os.path.join(self.campaign_manager.active_campaign_folder, 'dryrun')
        
        if not os.path.exists(dry_run_base_folder):
            return
        
        try:
            # Get all dry run folders
            dry_run_folders = []
            for item in os.listdir(dry_run_base_folder):
                item_path = os.path.join(dry_run_base_folder, item)
                if os.path.isdir(item_path):
                    # Get folder info
                    folder_info = self._get_dry_run_folder_info(item_path, item)
                    if folder_info:
                        dry_run_folders.append(folder_info)
            
            # Sort by creation time (newest first)
            dry_run_folders.sort(key=lambda x: x['mtime'], reverse=True)
            
            # Add to list widget
            for folder_info in dry_run_folders:
                display_text = self._format_dry_run_display(folder_info)
                self.dry_run_list.addItem(display_text)
                
        except Exception as e:
            print(f"Error refreshing dry run list: {e}")

    def _get_dry_run_folder_info(self, folder_path, folder_name):
        """Get information about a dry run folder"""
        try:
            # Get modification time
            mtime = os.path.getmtime(folder_path)
            
            # Count .eml files
            eml_files = [f for f in os.listdir(folder_path) if f.endswith('.eml')]
            eml_count = len(eml_files)
            
            # Get creation date
            from datetime import datetime
            creation_date = datetime.fromtimestamp(mtime)
            
            return {
                'name': folder_name,
                'path': folder_path,
                'mtime': mtime,
                'eml_count': eml_count,
                'creation_date': creation_date
            }
        except Exception:
            return None

    def _format_dry_run_display(self, folder_info):
        """Format dry run folder info for display"""
        name = folder_info['name']
        date_str = folder_info['creation_date'].strftime('%Y-%m-%d %H:%M')
        count = folder_info['eml_count']
        
        return f"📁 {name} - 📅 {date_str} ({count} emails)"

    def refresh_reports_list(self):
        """Refresh sent reports list with existing report files"""
        self.reports_list.clear()
        
        if not self.campaign_manager.active_campaign_folder:
            return
        
        reports_folder = os.path.join(self.campaign_manager.active_campaign_folder, 'sentreport')
        
        if not os.path.exists(reports_folder):
            return
        
        try:
            # Get all report files
            report_files = []
            for item in os.listdir(reports_folder):
                if item.endswith('.json') and not item.startswith('.'):
                    item_path = os.path.join(reports_folder, item)
                    if os.path.isfile(item_path):
                        # Get report info
                        report_info = self._get_report_file_info(item_path, item)
                        if report_info:
                            report_files.append(report_info)
            
            # Sort by creation time (newest first)
            report_files.sort(key=lambda x: x['mtime'], reverse=True)
            
            # Add to list widget
            for report_info in report_files:
                display_text = self._format_report_display(report_info)
                self.reports_list.addItem(display_text)
                
        except Exception as e:
            print(f"Error refreshing reports list: {e}")

    def _get_report_file_info(self, file_path, filename):
        """Get information about a sent report file"""
        try:
            # Get modification time
            mtime = os.path.getmtime(file_path)
            
            # Try to read report content for summary
            report_summary = self._read_report_summary(file_path)
            
            # Get creation date
            from datetime import datetime
            creation_date = datetime.fromtimestamp(mtime)
            
            return {
                'filename': filename,
                'path': file_path,
                'mtime': mtime,
                'creation_date': creation_date,
                'summary': report_summary
            }
        except Exception:
            return None

    def _read_report_summary(self, file_path):
        """Read summary information from report file"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Extract key statistics
            stats = report_data.get('statistics', {})
            sent = stats.get('sent', 0)
            failed = stats.get('failed', 0)
            warnings = stats.get('warnings', 0)
            duration = stats.get('total_time', 'Unknown')
            
            return {
                'sent': sent,
                'failed': failed,
                'warnings': warnings,
                'duration': duration
            }
        except Exception:
            # If we can't read the report, return basic info
            return {
                'sent': '?',
                'failed': '?',
                'warnings': '?',
                'duration': 'Unknown'
            }

    def _format_report_display(self, report_info):
        """Format report info for display"""
        filename = report_info['filename']
        date_str = report_info['creation_date'].strftime('%Y-%m-%d %H:%M')
        summary = report_info['summary']
        
        # Create status line
        sent = summary['sent']
        failed = summary['failed']
        duration = summary['duration']
        
        if failed == 0:
            status = f"✅ {sent} sent, 0 failed ({duration})"
        else:
            status = f"⚠️ {sent} sent, {failed} failed ({duration})"
        
        return f"📊 {filename} - {status}"

    def _send_finished(self, success, message):
        """Handle send completion"""
        # Reset progress system
        self._reset_progress_system()
        
        # Store statistics for report generation (empty since SendWorker doesn't provide them)
        self.last_send_statistics = {}
        
        if success:
            self.stats_label.setText(self.tr("✅ Campaign sent: {message}").format(message=message))
            
            # Generate sent report using EmailSender for consistency with CLI
            self._generate_sent_report(success, message, {})
            
            # Refresh sent reports list
            self.refresh_reports_list()
            
            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("Campaign Sent"), 
                                  f"{self.tr('Email campaign sent successfully!')}\n\n{message}")
        else:
            self.stats_label.setText(self.tr("❌ Campaign failed: {message}").format(message=message))
            
            # Generate failure report using EmailSender for consistency with CLI
            self._generate_sent_report(success, message, {})
            
            # Refresh sent reports list anyway (to show failure report)
            self.refresh_reports_list()
            
            # Show error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Campaign Failed"), self.tr("Email campaign failed:\n\n{message}").format(message=message))
        
        # Re-enable buttons
        self._update_button_states_after_operation()

    def _send_error(self, error_message):
        """Handle send error"""
        self._reset_progress_system()
        self.stats_label.setText(self.tr("❌ Send error: {error_message}").format(error_message=error_message))
        
        # Show error message
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, self.tr("Send Error"), self.tr("An error occurred during sending:\n\n{error_message}").format(error_message=error_message))
        
        # Re-enable buttons
        self._update_button_states_after_operation()
    
    def _generate_sent_report(self, success: bool, message: str, statistics: dict = None):
        """Generate sent report using EmailSender's core method for consistency with CLI"""
        try:
            from ...core.email_sender import EmailSender
            
            # Create EmailSender instance
            email_sender = EmailSender(self.campaign_manager.active_campaign_folder)
            
            # Extract statistics
            sent_count = 0
            failed_count = 0
            total_time = self.tr("Unknown")
            
            if statistics:
                sent_count = statistics.get('sent', 0)
                failed_count = statistics.get('failed', 0)
                total_time = statistics.get('total_time', 'Unknown')
            else:
                # Fallback: try to parse from message
                import re
                # Try different message patterns
                patterns = [
                    r'(\d+)\s+sent,?\s*(\d+)\s+failed',  # "X sent, Y failed"
                    r'Sent\s+(\d+)\s+emails?\s+successfully',  # "Sent X emails successfully"
                    r'(\d+)\s+emails?\s+sent\s+successfully',  # "X emails sent successfully"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, message, re.IGNORECASE)
                    if match:
                        if len(match.groups()) == 2:
                            # Pattern with sent and failed counts
                            sent_count = int(match.group(1))
                            failed_count = int(match.group(2))
                        else:
                            # Pattern with only sent count (success case)
                            sent_count = int(match.group(1))
                            failed_count = 0
                        break
            
            # Use EmailSender's report generation method
            email_sender.generate_sent_report(success, message, sent_count, failed_count, total_time)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not generate sent report: {e}")
            # Note: No fallback - we want to use only the core method for consistency


class DryRunWorker(QThread):
    """Worker thread for dry run operations"""
    
    progress_updated = Signal(int, int, str)  # current, total, message
    finished = Signal(bool, str, str)  # success, message, custom_name
    error = Signal(str)  # error_message
    
    def __init__(self, campaign_folder, custom_name):
        super().__init__()
        self.campaign_folder = campaign_folder
        self.custom_name = custom_name
    
    def run(self):
        """Run the dry run in background thread"""
        try:
            from ...core.email_sender import EmailSender
            import csv
            
            # Get recipient count for progress tracking
            recipients_file = os.path.join(self.campaign_folder, 'recipients.csv')
            recipient_count = 0
            try:
                with open(recipients_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    recipient_count = len(list(reader))
            except:
                pass
            
            # Create email sender
            sender = EmailSender(self.campaign_folder)
            
            # Emit initial progress
            self.progress_updated.emit(0, recipient_count, self.tr("Initializing dry run..."))
            
            # Emit validation progress
            self.progress_updated.emit(0, recipient_count, self.tr("Validating campaign..."))
            
            # Perform dry run with custom name
            result = sender.dry_run(custom_name=self.custom_name, gui_mode=True)
            
            if result == 0:  # Success
                # Count generated emails for final confirmation
                dry_run_folder = os.path.join(self.campaign_folder, 'dryrun', self.custom_name)
                if os.path.exists(dry_run_folder):
                    eml_files = [f for f in os.listdir(dry_run_folder) if f.endswith('.eml')]
                    count = len(eml_files)
                    
                    # Emit completion progress
                    self.progress_updated.emit(count, count, self.tr("Generated {count} email previews").format(count=count))
                    
                    self.finished.emit(True, self.tr("Generated {count} email previews").format(count=count), self.custom_name)
                else:
                    self.finished.emit(True, self.tr("Dry run completed"), self.custom_name)
            else:
                self.finished.emit(False, self.tr("Dry run validation failed"), self.custom_name)
                
        except Exception as e:
            self.error.emit(str(e))
    
    
class SendWorker(QThread):
    """Worker thread for email sending operations"""
    
    progress_updated = Signal(int, int, str)  # current, total, message
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error_message
    
    def __init__(self, campaign_folder):
        super().__init__()
        self.campaign_folder = campaign_folder
    
    def run(self):
        """Run the email sending in background thread"""
        try:
            from ...core.email_sender import EmailSender
            
            # Create email sender
            sender = EmailSender(self.campaign_folder)
            
            # Emit initial progress
            self.progress_updated.emit(0, 100, self.tr("Initializing email sending..."))
            
            # Define progress callback
            def progress_callback(current, total, message):
                self.progress_updated.emit(current, total, message)
            
            # Perform email sending
            result = sender.send_campaign(gui_mode=True, progress_callback=progress_callback)
            
            if result == 0:  # Success
                # Get recipient count for success message
                import csv
                recipients_file = os.path.join(self.campaign_folder, 'recipients.csv')
                try:
                    with open(recipients_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        count = len(list(reader))
                    self.finished.emit(True, self.tr("Sent {count} emails successfully").format(count=count))
                except:
                    self.finished.emit(True, self.tr("Email campaign completed"))
            else:
                self.finished.emit(False, self.tr("Email sending failed - check validation"))
                
        except Exception as e:
            self.error.emit(str(e))
