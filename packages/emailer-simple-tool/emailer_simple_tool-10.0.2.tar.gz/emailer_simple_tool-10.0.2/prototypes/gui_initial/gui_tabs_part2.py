"""
Continuation of GUI Tab Components - Picture and Send tabs
"""

import os
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
        QTextEdit, QFileDialog, QMessageBox, QProgressBar, QGroupBox, 
        QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox, QCheckBox,
        QTableWidget, QTableWidgetItem
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont, QPixmap
except ImportError:
    print("PySide6 not available")


class PictureTab(QWidget):
    """Picture generator management tab"""
    
    def __init__(self):
        super().__init__()
        self.current_campaign_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize picture tab UI"""
        layout = QHBoxLayout()
        
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Project list and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Projects overview
        projects_group = QGroupBox("🖼️ Picture Generator Projects")
        projects_layout = QVBoxLayout()
        
        self.projects_tree = QTreeWidget()
        self.projects_tree.setHeaderLabels(["Project", "Status", "Images"])
        self.projects_tree.itemClicked.connect(self.on_project_selected)
        
        # Load sample projects for demo
        self.load_sample_projects()
        
        projects_layout.addWidget(self.projects_tree)
        projects_group.setLayout(projects_layout)
        
        # Project controls
        controls_group = QGroupBox("🔧 Project Controls")
        controls_layout = QVBoxLayout()
        
        generate_btn = QPushButton("🎨 Generate Pictures")
        generate_btn.clicked.connect(self.generate_pictures)
        generate_btn.setStyleSheet("QPushButton { background-color: #28a745; font-weight: bold; }")
        
        refresh_btn = QPushButton("🔄 Refresh Projects")
        refresh_btn.clicked.connect(self.refresh_projects)
        refresh_btn.setStyleSheet("QPushButton { background-color: #6c757d; }")
        
        self.generation_progress = QProgressBar()
        self.generation_progress.setVisible(False)
        
        self.generation_status = QLabel("")
        self.generation_status.setStyleSheet("color: #6c757d; padding: 5px;")
        
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(self.generation_progress)
        controls_layout.addWidget(self.generation_status)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        
        # Add to left panel
        left_layout.addWidget(projects_group)
        left_layout.addWidget(controls_group)
        left_panel.setLayout(left_layout)
        
        # Right panel - Project details and preview
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Project details
        details_group = QGroupBox("📋 Project Details")
        details_layout = QVBoxLayout()
        
        self.project_details = QTextEdit()
        self.project_details.setReadOnly(True)
        self.project_details.setMaximumHeight(200)
        self.project_details.setPlainText("Select a project to view details...")
        
        details_layout.addWidget(self.project_details)
        details_group.setLayout(details_layout)
        
        # Fusion configuration preview
        fusion_group = QGroupBox("⚙️ Fusion Configuration")
        fusion_layout = QVBoxLayout()
        
        self.fusion_table = QTableWidget()
        self.fusion_table.setMaximumHeight(200)
        self.fusion_table.setAlternatingRowColors(True)
        
        fusion_layout.addWidget(self.fusion_table)
        fusion_group.setLayout(fusion_layout)
        
        # Generated images preview
        preview_group = QGroupBox("🖼️ Generated Images Preview")
        preview_layout = QVBoxLayout()
        
        self.images_preview = QTextEdit()
        self.images_preview.setReadOnly(True)
        self.images_preview.setPlaceholderText("Generated images will be listed here...")
        
        preview_layout.addWidget(self.images_preview)
        preview_group.setLayout(preview_layout)
        
        # Add to right panel
        right_layout.addWidget(details_group)
        right_layout.addWidget(fusion_group)
        right_layout.addWidget(preview_group)
        right_panel.setLayout(right_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_sample_projects(self):
        """Load sample projects for demonstration"""
        # Sample project 1 - Badges
        badges_item = QTreeWidgetItem(["badges", "✅ Ready", "25 images"])
        badges_item.setData(0, Qt.UserRole, {
            "name": "badges",
            "status": "ready",
            "template": "template.jpg",
            "images_count": 25,
            "fusion_config": [
                {"type": "text", "data": "{{name}}", "position": "100:50", "size": "24"},
                {"type": "text", "data": "Event 2025", "position": "100:200", "size": "18"},
                {"type": "graphic", "data": "{{qr_code}}", "position": "200:100", "size": "80:80"}
            ]
        })
        
        # Sample project 2 - Certificates
        certificates_item = QTreeWidgetItem(["certificates", "⚠️ Needs generation", "0 images"])
        certificates_item.setData(0, Qt.UserRole, {
            "name": "certificates",
            "status": "needs_generation",
            "template": "certificate_template.jpg",
            "images_count": 0,
            "fusion_config": [
                {"type": "formatted-text", "data": "certificate.docx", "position": "150:100", "size": "300:200"},
                {"type": "text", "data": "{{participant_name}}", "position": "200:250", "size": "28"}
            ]
        })
        
        # Sample project 3 - Invitations
        invitations_item = QTreeWidgetItem(["invitations", "🔄 In progress", "12 images"])
        invitations_item.setData(0, Qt.UserRole, {
            "name": "invitations",
            "status": "in_progress",
            "template": "invitation_bg.jpg",
            "images_count": 12,
            "fusion_config": [
                {"type": "text", "data": "Dear {{name}}", "position": "50:100", "size": "20"},
                {"type": "text", "data": "{{event_date}}", "position": "50:300", "size": "16"}
            ]
        })
        
        self.projects_tree.addTopLevelItem(badges_item)
        self.projects_tree.addTopLevelItem(certificates_item)
        self.projects_tree.addTopLevelItem(invitations_item)
        
        # Auto-resize columns
        self.projects_tree.resizeColumnToContents(0)
        self.projects_tree.resizeColumnToContents(1)
        self.projects_tree.resizeColumnToContents(2)
    
    def on_project_selected(self, item, column):
        """Handle project selection"""
        project_data = item.data(0, Qt.UserRole)
        if not project_data:
            return
        
        # Update project details
        details = f"""Project: {project_data['name']}
Status: {project_data['status']}
Template: {project_data['template']}
Generated Images: {project_data['images_count']}

Configuration:
• Template file: {project_data['template']}
• Fusion operations: {len(project_data['fusion_config'])}
• Output format: JPG images named with recipient ID
"""
        self.project_details.setPlainText(details)
        
        # Update fusion configuration table
        fusion_config = project_data['fusion_config']
        self.fusion_table.setRowCount(len(fusion_config))
        self.fusion_table.setColumnCount(4)
        self.fusion_table.setHorizontalHeaderLabels(["Type", "Data", "Position", "Size"])
        
        for row, config in enumerate(fusion_config):
            self.fusion_table.setItem(row, 0, QTableWidgetItem(config['type']))
            self.fusion_table.setItem(row, 1, QTableWidgetItem(config['data']))
            self.fusion_table.setItem(row, 2, QTableWidgetItem(config['position']))
            self.fusion_table.setItem(row, 3, QTableWidgetItem(config.get('size', 'auto')))
        
        self.fusion_table.resizeColumnsToContents()
        
        # Update images preview
        if project_data['images_count'] > 0:
            preview_text = f"Generated {project_data['images_count']} personalized images:\n\n"
            for i in range(min(5, project_data['images_count'])):
                preview_text += f"📄 00{i+1}-{project_data['name']}.jpg\n"
            if project_data['images_count'] > 5:
                preview_text += f"... and {project_data['images_count'] - 5} more images"
        else:
            preview_text = "No images generated yet. Click 'Generate Pictures' to create personalized images."
        
        self.images_preview.setPlainText(preview_text)
    
    def generate_pictures(self):
        """Generate pictures for selected project"""
        current_item = self.projects_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a project first.")
            return
        
        project_data = current_item.data(0, Qt.UserRole)
        project_name = project_data['name']
        
        # Show confirmation
        reply = QMessageBox.question(
            self, 
            "Generate Pictures", 
            f"Generate personalized pictures for project '{project_name}'?\n\nThis will create individual images for each recipient.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_generation(project_name, current_item)
    
    def start_generation(self, project_name: str, tree_item):
        """Start picture generation process"""
        self.generation_progress.setVisible(True)
        self.generation_progress.setValue(0)
        self.generation_status.setText(f"🎨 Generating pictures for {project_name}...")
        
        # Simulate generation progress
        self.generation_timer = QTimer()
        self.generation_step = 0
        self.generation_project = project_name
        self.generation_item = tree_item
        
        def update_generation():
            self.generation_step += 1
            progress = min(self.generation_step * 10, 100)
            self.generation_progress.setValue(progress)
            
            if progress >= 100:
                self.generation_timer.stop()
                self.generation_complete()
        
        self.generation_timer.timeout.connect(update_generation)
        self.generation_timer.start(300)
    
    def generation_complete(self):
        """Handle generation completion"""
        self.generation_progress.setVisible(False)
        self.generation_status.setText(f"✅ Pictures generated successfully for {self.generation_project}!")
        
        # Update tree item
        project_data = self.generation_item.data(0, Qt.UserRole)
        project_data['images_count'] = 25  # Simulate generated count
        project_data['status'] = 'ready'
        
        self.generation_item.setText(1, "✅ Ready")
        self.generation_item.setText(2, "25 images")
        
        # Refresh details if this project is selected
        if self.projects_tree.currentItem() == self.generation_item:
            self.on_project_selected(self.generation_item, 0)
        
        QMessageBox.information(
            self, 
            "Generation Complete", 
            f"Successfully generated 25 personalized images for '{self.generation_project}'!\n\nImages are saved in the project's data folder."
        )
    
    def refresh_projects(self):
        """Refresh projects list"""
        self.generation_status.setText("🔄 Refreshing projects...")
        QTimer.singleShot(1000, lambda: self.generation_status.setText("✅ Projects refreshed"))


class SendTab(QWidget):
    """Email sending and dry run tab"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize send tab UI"""
        layout = QVBoxLayout()
        
        # Pre-send validation
        validation_group = QGroupBox("✅ Pre-Send Validation")
        validation_layout = QVBoxLayout()
        
        self.validation_status = QLabel("Click 'Validate Campaign' to check your campaign setup")
        self.validation_status.setStyleSheet("color: #6c757d; padding: 10px;")
        self.validation_status.setWordWrap(True)
        
        validate_btn = QPushButton("🔍 Validate Campaign")
        validate_btn.clicked.connect(self.validate_campaign)
        validate_btn.setStyleSheet("QPushButton { background-color: #17a2b8; }")
        
        validation_layout.addWidget(self.validation_status)
        validation_layout.addWidget(validate_btn)
        validation_group.setLayout(validation_layout)
        
        # Send options
        options_group = QGroupBox("🚀 Send Options")
        options_layout = QVBoxLayout()
        
        # Dry run section
        dry_run_section = QHBoxLayout()
        
        dry_run_btn = QPushButton("🧪 Dry Run (Preview Only)")
        dry_run_btn.clicked.connect(self.dry_run)
        dry_run_btn.setStyleSheet("QPushButton { background-color: #ffc107; color: #212529; font-weight: bold; }")
        
        self.dry_run_name = QLineEdit()
        self.dry_run_name.setPlaceholderText("Optional: custom dry run name")
        self.dry_run_name.setMaximumWidth(200)
        
        dry_run_section.addWidget(dry_run_btn)
        dry_run_section.addWidget(QLabel("Name:"))
        dry_run_section.addWidget(self.dry_run_name)
        dry_run_section.addStretch()
        
        # Send section
        send_section = QHBoxLayout()
        
        send_btn = QPushButton("📧 Send Campaign")
        send_btn.clicked.connect(self.send_campaign)
        send_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; font-size: 14px; padding: 12px 24px; }")
        
        self.send_confirmation = QCheckBox("I have tested with dry run and am ready to send")
        
        send_section.addWidget(send_btn)
        send_section.addWidget(self.send_confirmation)
        send_section.addStretch()
        
        options_layout.addLayout(dry_run_section)
        options_layout.addLayout(send_section)
        options_group.setLayout(options_layout)
        
        # Progress tracking
        progress_group = QGroupBox("📊 Progress Tracking")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready to send")
        self.progress_label.setStyleSheet("color: #6c757d; padding: 5px;")
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_sent = QLabel("Sent: 0")
        self.stats_failed = QLabel("Failed: 0")
        self.stats_remaining = QLabel("Remaining: 0")
        
        for label in [self.stats_sent, self.stats_failed, self.stats_remaining]:
            label.setStyleSheet("padding: 5px; font-weight: bold;")
        
        stats_layout.addWidget(self.stats_sent)
        stats_layout.addWidget(self.stats_failed)
        stats_layout.addWidget(self.stats_remaining)
        stats_layout.addStretch()
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addLayout(stats_layout)
        progress_group.setLayout(progress_layout)
        
        # Results log
        results_group = QGroupBox("📝 Results Log")
        results_layout = QVBoxLayout()
        
        self.results_log = QTextEdit()
        self.results_log.setReadOnly(True)
        self.results_log.setPlaceholderText("Send results and logs will appear here...")
        self.results_log.setMaximumHeight(200)
        
        # Log controls
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.results_log.clear)
        clear_log_btn.setStyleSheet("QPushButton { background-color: #6c757d; }")
        
        save_log_btn = QPushButton("Save Log")
        save_log_btn.clicked.connect(self.save_log)
        save_log_btn.setStyleSheet("QPushButton { background-color: #6c757d; }")
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(save_log_btn)
        log_controls.addStretch()
        
        results_layout.addWidget(self.results_log)
        results_layout.addLayout(log_controls)
        results_group.setLayout(results_layout)
        
        # Add all groups to main layout
        layout.addWidget(validation_group)
        layout.addWidget(options_group)
        layout.addWidget(progress_group)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
    
    def validate_campaign(self):
        """Validate campaign before sending"""
        self.validation_status.setText("🔄 Validating campaign...")
        self.validation_status.setStyleSheet("color: #007bff; padding: 10px;")
        
        # Simulate validation
        QTimer.singleShot(2000, self.validation_complete)
    
    def validation_complete(self):
        """Complete validation process"""
        # Mock validation results
        validation_results = [
            "✅ Recipients CSV: 25 valid recipients found",
            "✅ Email addresses: All valid and unique",
            "✅ Message template: msg.docx found and valid",
            "✅ Subject template: subject.txt found",
            "✅ SMTP configuration: Connection successful",
            "✅ Picture projects: 2 projects ready (50 images)",
            "✅ Attachments: 3 files ready (2.1 MB total)",
            "⚠️ Large attachment warning: Total size is 2.1 MB"
        ]
        
        self.validation_status.setText("\n".join(validation_results))
        self.validation_status.setStyleSheet("color: #28a745; padding: 10px;")
        
        # Update stats
        self.stats_remaining.setText("Remaining: 25")
    
    def dry_run(self):
        """Perform dry run"""
        self.progress_label.setText("🧪 Running dry run...")
        self.progress_bar.setValue(0)
        self.results_log.clear()
        
        dry_run_name = self.dry_run_name.text() or "preview"
        self.results_log.append(f"🧪 Starting dry run: {dry_run_name}")
        self.results_log.append(f"📁 Output folder: dryrun/{dry_run_name}/")
        
        # Simulate dry run progress
        self.simulate_progress("dry_run", 25)
    
    def send_campaign(self):
        """Send email campaign"""
        if not self.send_confirmation.isChecked():
            QMessageBox.warning(
                self, 
                "Confirmation Required", 
                "Please check the confirmation box to verify you have tested with dry run."
            )
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirm Send", 
            "⚠️ Are you sure you want to send emails to all 25 recipients?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.progress_label.setText("📧 Sending emails...")
            self.progress_bar.setValue(0)
            self.results_log.clear()
            
            self.results_log.append("📧 Starting email campaign...")
            self.results_log.append("🔐 SMTP connection established")
            
            # Simulate sending progress
            self.simulate_progress("send", 25)
    
    def simulate_progress(self, operation: str, total_count: int):
        """Simulate progress for demo"""
        self.operation_timer = QTimer()
        self.operation_step = 0
        self.operation_total = total_count
        self.operation_type = operation
        self.sent_count = 0
        self.failed_count = 0
        
        def update_progress():
            self.operation_step += 1
            progress = int((self.operation_step / self.operation_total) * 100)
            self.progress_bar.setValue(progress)
            
            if self.operation_type == "dry_run":
                self.results_log.append(f"📄 Generated preview for recipient {self.operation_step:03d}")
                if self.operation_step >= self.operation_total:
                    self.operation_timer.stop()
                    self.dry_run_complete()
            else:  # send
                # Simulate occasional failures
                import random
                if random.random() < 0.1:  # 10% failure rate
                    self.failed_count += 1
                    self.results_log.append(f"❌ Failed to send to recipient {self.operation_step:03d}")
                    self.stats_failed.setText(f"Failed: {self.failed_count}")
                    self.stats_failed.setStyleSheet("color: #dc3545; padding: 5px; font-weight: bold;")
                else:
                    self.sent_count += 1
                    self.results_log.append(f"✅ Sent to recipient {self.operation_step:03d}")
                    self.stats_sent.setText(f"Sent: {self.sent_count}")
                    self.stats_sent.setStyleSheet("color: #28a745; padding: 5px; font-weight: bold;")
                
                remaining = self.operation_total - self.operation_step
                self.stats_remaining.setText(f"Remaining: {remaining}")
                
                if self.operation_step >= self.operation_total:
                    self.operation_timer.stop()
                    self.send_complete()
        
        self.operation_timer.timeout.connect(update_progress)
        self.operation_timer.start(200)
    
    def dry_run_complete(self):
        """Handle dry run completion"""
        self.progress_label.setText("✅ Dry run completed!")
        self.results_log.append("🎉 Dry run completed successfully!")
        self.results_log.append("📁 Check the dryrun/ folder for .eml preview files")
        self.results_log.append("💡 Open .eml files with your email client to preview")
        
        QMessageBox.information(
            self, 
            "Dry Run Complete", 
            "Dry run completed successfully!\n\n📁 Preview files saved in dryrun/ folder\n💡 Open .eml files with your email client to preview the formatted emails"
        )
    
    def send_complete(self):
        """Handle send completion"""
        self.progress_label.setText(f"✅ Campaign completed! Sent: {self.sent_count}, Failed: {self.failed_count}")
        self.results_log.append("🎉 Email campaign completed!")
        self.results_log.append(f"📊 Final stats: {self.sent_count} sent, {self.failed_count} failed")
        
        if self.failed_count > 0:
            self.results_log.append("⚠️ Some emails failed - check SMTP settings and recipient addresses")
        
        QMessageBox.information(
            self, 
            "Campaign Complete", 
            f"Email campaign completed!\n\n✅ Successfully sent: {self.sent_count}\n❌ Failed: {self.failed_count}\n\nCheck the results log for details."
        )
    
    def save_log(self):
        """Save results log to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Results Log", 
            "email_campaign_log.txt", 
            "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_log.toPlainText())
                QMessageBox.information(self, "Log Saved", f"Results log saved to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save log:\n{str(e)}")
