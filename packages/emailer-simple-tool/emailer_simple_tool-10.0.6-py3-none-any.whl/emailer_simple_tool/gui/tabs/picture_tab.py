"""
Picture Tab - Picture generator management with comprehensive GUI
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QGroupBox, QSplitter, QComboBox, QFileDialog,
    QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QCheckBox, QDialog, QWizard, QWizardPage,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal, QFileSystemWatcher, QTimer
from PySide6.QtGui import QFont, QPixmap

from ...core.picture_generator import PictureGenerator, PictureGeneratorProject
from ...core.campaign_manager import CampaignManager
from ...utils.validators import ValidationResult


class PictureTab(QWidget):
    """Picture generator management tab with comprehensive GUI"""
    
    # Signal emitted when picture settings change (like attachment setting)
    picture_settings_changed = Signal()
    
    def __init__(self, campaign_manager: CampaignManager):
        super().__init__()
        self.campaign_manager = campaign_manager
        self.current_project: Optional[PictureGeneratorProject] = None
        self.picture_generator: Optional[PictureGenerator] = None
        self.current_campaign_path: Optional[str] = None
        
        # File system watcher for external editor integration
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        
        # Track current files being watched
        self.watched_files = set()
        
        # Flag to prevent file watcher reload during programmatic writes
        self.updating_attachment_file = False
        
        self.init_ui()
        # Don't call refresh_projects() during init - wait for campaign signals
        self.clear_campaign_state()
    
    def init_ui(self):
        """Initialize picture tab UI with two-panel layout"""
        layout = QVBoxLayout()
        
        # Top section: Project management
        self.create_top_section(layout)
        
        # Main content: Two-panel layout
        self.create_main_content(layout)
        
        self.setLayout(layout)
    
    def create_top_section(self, parent_layout):
        """Create the top section with project dropdown and management buttons"""
        self.top_group = QGroupBox(self.tr("🖼️ Picture Generator Projects"))
        top_layout = QHBoxLayout()
        
        # Project selection dropdown
        self.project_dropdown = QComboBox()
        self.project_dropdown.setMinimumWidth(300)
        self.project_dropdown.currentTextChanged.connect(self.on_project_selected)
        
        # Management buttons
        self.create_button = QPushButton(self.tr("Create"))
        self.create_button.clicked.connect(self.create_project)
        self.create_button.setStyleSheet("QPushButton { background-color: #007bff; }")
        
        self.duplicate_button = QPushButton(self.tr("Duplicate"))
        self.duplicate_button.clicked.connect(self.duplicate_project)
        self.duplicate_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        self.duplicate_button.setEnabled(False)
        
        self.delete_button = QPushButton(self.tr("Delete"))
        self.delete_button.clicked.connect(self.delete_project)
        self.delete_button.setStyleSheet("QPushButton { background-color: #dc3545; }")
        self.delete_button.setEnabled(False)
        
        top_layout.addWidget(self.project_dropdown)
        top_layout.addStretch()
        top_layout.addWidget(self.create_button)
        top_layout.addWidget(self.duplicate_button)
        top_layout.addWidget(self.delete_button)
        
        self.top_group.setLayout(top_layout)
        parent_layout.addWidget(self.top_group)
    
    def create_main_content(self, parent_layout):
        """Create the main two-panel content area"""
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Project properties, help, and validation
        left_panel = self.create_left_panel()
        
        # Right panel: Picture generation and results
        right_panel = self.create_right_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 300])  # 60% left, 40% right
        
        parent_layout.addWidget(splitter)
    
    def create_left_panel(self):
        """Create the left panel with project properties, help, and validation"""
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Project Properties Section
        self.create_project_properties_section(left_layout)
        
        # User Help Section
        self.create_user_help_section(left_layout)
        
        # Validation Panel
        self.create_validation_panel(left_layout)
        
        left_widget.setLayout(left_layout)
        return left_widget
    
    def create_right_panel(self):
        """Create the right panel with generation controls and results"""
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Generation Controls
        self.create_generation_controls(right_layout)
        
        # Generated Images List
        self.create_generated_images_section(right_layout)
        
        right_widget.setLayout(right_layout)
        return right_widget
    
    def create_project_properties_section(self, parent_layout):
        """Create the project properties section with optimized two-column layout"""
        self.properties_group = QGroupBox(self.tr("📋 Project Properties"))
        
        # Create horizontal layout for two columns
        main_properties_layout = QHBoxLayout()
        
        # Left column (narrower) - Core files, attachment control, and file management buttons
        left_column = QVBoxLayout()
        self.create_core_files_section(left_column)
        self.create_attachment_control(left_column)
        self.create_file_management_buttons(left_column)  # New method for the 3 buttons
        left_column.addStretch()  # Push content to top
        
        # Right column (wider) - Additional files list only
        right_column = QVBoxLayout()
        self.create_additional_files_list_only(right_column)  # Modified method
        
        # Create widgets to hold the columns
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        left_widget.setMaximumWidth(400)  # Increased from 300 to 400 for better button text visibility
        
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        # Add columns to main layout
        main_properties_layout.addWidget(left_widget)
        main_properties_layout.addWidget(right_widget)
        
        self.properties_group.setLayout(main_properties_layout)
        parent_layout.addWidget(self.properties_group)
    
    def create_core_files_section(self, parent_layout):
        """Create the core files (fusion.csv, template.jpg) section"""
        # fusion.csv file
        fusion_layout = QHBoxLayout()
        fusion_layout.addWidget(QLabel(self.tr("📄 fusion.csv")))
        
        self.fusion_browse_btn = QPushButton(self.tr("Browse"))
        self.fusion_browse_btn.clicked.connect(self.browse_fusion_file)
        self.fusion_browse_btn.setEnabled(False)
        
        self.fusion_open_btn = QPushButton(self.tr("Open"))
        self.fusion_open_btn.clicked.connect(self.open_fusion_file)
        self.fusion_open_btn.setEnabled(False)
        
        fusion_layout.addStretch()
        fusion_layout.addWidget(self.fusion_browse_btn)
        fusion_layout.addWidget(self.fusion_open_btn)
        
        parent_layout.addLayout(fusion_layout)
        
        # template.jpg file
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel(self.tr("🖼️ template.jpg")))
        
        self.template_browse_btn = QPushButton(self.tr("Browse"))
        self.template_browse_btn.clicked.connect(self.browse_template_file)
        self.template_browse_btn.setEnabled(False)
        
        self.template_open_btn = QPushButton(self.tr("Open"))
        self.template_open_btn.clicked.connect(self.open_template_file)
        self.template_open_btn.setEnabled(False)
        
        template_layout.addStretch()
        template_layout.addWidget(self.template_browse_btn)
        template_layout.addWidget(self.template_open_btn)
        
        parent_layout.addLayout(template_layout)
    
    def create_file_management_buttons(self, parent_layout):
        """Create the file management buttons (Add Files, Add Folder, Open) on same line"""
        files_button_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton(self.tr(self.tr("+ Files")))
        self.add_files_btn.clicked.connect(self.add_files_to_project)
        self.add_files_btn.setEnabled(False)
        
        self.add_folder_btn = QPushButton(self.tr(self.tr("+ Folder")))
        self.add_folder_btn.clicked.connect(self.add_folder_to_project)
        self.add_folder_btn.setEnabled(False)
        
        self.open_additional_file_btn = QPushButton(self.tr("Open"))
        self.open_additional_file_btn.clicked.connect(self.open_selected_additional_file)
        self.open_additional_file_btn.setEnabled(False)
        
        files_button_layout.addWidget(self.add_files_btn)
        files_button_layout.addWidget(self.add_folder_btn)
        files_button_layout.addWidget(self.open_additional_file_btn)
        
        parent_layout.addLayout(files_button_layout)
    
    def create_additional_files_list_only(self, parent_layout):
        """Create only the additional files list (buttons moved to left column)"""
        files_label = QLabel(self.tr("Additional Files:"))
        parent_layout.addWidget(files_label)
        
        # Files list widget - expandable to use all available space with proper scroll bars
        self.additional_files_list = QListWidget()
        # Ensure both horizontal and vertical scroll bars appear when needed
        self.additional_files_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.additional_files_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Allow horizontal scrolling for long file names
        self.additional_files_list.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.additional_files_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        
        parent_layout.addWidget(self.additional_files_list)
        
        # Connect selection change to enable/disable Open button
        self.additional_files_list.itemSelectionChanged.connect(self.on_additional_files_selection_changed)
    
    def create_attachment_control(self, parent_layout):
        """Create the email attachment control"""
        attachment_layout = QHBoxLayout()
        self.attachment_label = QLabel(self.tr("Email Attachment:"))
        attachment_layout.addWidget(self.attachment_label)
        
        self.attachment_checkbox = QCheckBox(self.tr("Attach generated images to emails"))
        self.attachment_checkbox.stateChanged.connect(self.on_attachment_changed)
        self.attachment_checkbox.setEnabled(False)
        
        attachment_layout.addWidget(self.attachment_checkbox)
        attachment_layout.addStretch()
        
        parent_layout.addLayout(attachment_layout)
    
    def create_user_help_section(self, parent_layout):
        """Create the user help and guidance section"""
        self.help_group = QGroupBox(self.tr("📚 User Help & Guidance"))
        help_layout = QVBoxLayout()
        
        # Create scroll area for help content with increased height
        help_scroll = QScrollArea()
        help_scroll.setWidgetResizable(True)
        help_scroll.setMaximumHeight(300)  # Increased from 200 to 300 for better readability
        
        help_content = QWidget()
        help_content_layout = QVBoxLayout()
        
        # Help text content
        self.help_text = QLabel(self.get_help_text())
        self.help_text.setWordWrap(True)
        self.help_text.setStyleSheet("QLabel { padding: 10px; font-size: 12px; }")
        
        help_content_layout.addWidget(self.help_text)
        help_content.setLayout(help_content_layout)
        help_scroll.setWidget(help_content)
        
        help_layout.addWidget(help_scroll)
        self.help_group.setLayout(help_layout)
        parent_layout.addWidget(self.help_group)
    
    def create_validation_panel(self, parent_layout):
        """Create the validation panel"""
        self.validation_group = QGroupBox(self.tr("🔍 Validation Panel"))
        validation_layout = QVBoxLayout()
        
        # Create scroll area for validation content
        validation_scroll = QScrollArea()
        validation_scroll.setWidgetResizable(True)
        validation_scroll.setMaximumHeight(150)
        
        self.validation_content = QLabel(self.tr("No project loaded"))
        self.validation_content.setWordWrap(True)
        self.validation_content.setStyleSheet("QLabel { padding: 10px; font-size: 12px; }")
        
        validation_scroll.setWidget(self.validation_content)
        validation_layout.addWidget(validation_scroll)
        
        self.validation_group.setLayout(validation_layout)
        parent_layout.addWidget(self.validation_group)
    
    def create_generation_controls(self, parent_layout):
        """Create the picture generation controls"""
        self.generation_group = QGroupBox(self.tr("🎨 Picture Generation"))
        generation_layout = QVBoxLayout()
        
        # Generate button
        self.generate_button = QPushButton(self.tr("🎨 Generate Pictures"))
        self.generate_button.clicked.connect(self.generate_pictures)
        self.generate_button.setStyleSheet("QPushButton { background-color: #28a745; font-size: 14px; padding: 10px; }")
        self.generate_button.setEnabled(False)
        
        generation_layout.addWidget(self.generate_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        generation_layout.addWidget(self.progress_bar)
        
        # Status label
        self.generation_status = QLabel("")
        self.generation_status.setWordWrap(True)
        self.generation_status.setStyleSheet("QLabel { padding: 5px; }")
        generation_layout.addWidget(self.generation_status)
        
        self.generation_group.setLayout(generation_layout)
        parent_layout.addWidget(self.generation_group)
    
    def create_generated_images_section(self, parent_layout):
        """Create the generated images management section"""
        self.images_group = QGroupBox(self.tr("📸 Generated Images"))
        images_layout = QVBoxLayout()
        
        # Images list
        self.generated_images_list = QListWidget()
        self.generated_images_list.setSelectionMode(QListWidget.MultiSelection)
        images_layout.addWidget(self.generated_images_list)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.open_selected_btn = QPushButton(self.tr("Open Selected"))
        self.open_selected_btn.clicked.connect(self.open_selected_images)
        self.open_selected_btn.setEnabled(False)
        
        buttons_layout.addWidget(self.open_selected_btn)
        buttons_layout.addStretch()
        
        images_layout.addLayout(buttons_layout)
        self.images_group.setLayout(images_layout)
        parent_layout.addWidget(self.images_group)
    
    def get_help_text(self):
        """Get the comprehensive help text for non-technical users"""
        return self.tr("""
<b>How to use the Picture Generator:</b>

<b>• Editing fusion.csv:</b>
- Each line adds an element to your personalized images
- fusion-type: Use 'text' for text, 'graphic' for images, 'formatted-text' for styled documents
- data: Type your text or use {{name}} to insert recipient information
- positioning: Use 'x:y' format - first number moves right, second moves down
- size: Font size for text, 'width:height' for images
- alignment: Choose 'left', 'center', or 'right'

<b>• Positioning Guide:</b>
- Top-left corner is 0:0
- Increase first number to move right, second to move down
- Example: 100:50 means 100 pixels from left, 50 pixels from top

<b>• File References:</b>
- Static files: Use exact names like 'logo.png'
- Personalized files: Use {{column_name}} to reference CSV data
- Folder structure: Files can be in subfolders with 'folder/file.png'

<b>• Template Variables:</b>
- Use {{name}}, {{email}}, or any column from your recipients.csv
- Variables will be replaced with actual recipient data
        """)
    
    def on_project_selected(self, project_name: str):
        """Handle project selection from dropdown"""
        if not project_name or project_name in [
            self.tr("No campaign loaded"),
            self.tr("No project created yet"),
            self.tr("Select the project to load"),
            self.tr("Error reading projects")
        ]:
            self.update_ui_state(None)
            return
        
        # Extract actual project name from formatted display name
        actual_project_name = self._extract_project_name(project_name)
        self.load_project(actual_project_name)
    
    def load_project(self, project_name: str):
        """Load a specific project"""
        if not self.campaign_manager.active_campaign_folder:
            return
        
        project_path = os.path.join(
            self.campaign_manager.active_campaign_folder,
            "picture-generator",
            project_name
        )
        
        try:
            self.current_project = PictureGeneratorProject(project_path, project_name)
            self.update_ui_state(self.current_project)
            self.validate_project()
            self.refresh_additional_files()
            self.refresh_generated_images()
            self.load_attachment_setting()
            
            # Setup file watching
            self.setup_file_watching()
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to load project: {error}").format(error=str(e)))
            self.update_ui_state(None)
    
    def update_ui_state(self, project: Optional[PictureGeneratorProject]):
        """Update UI state based on loaded project"""
        has_project = project is not None
        
        # Enable/disable buttons
        self.duplicate_button.setEnabled(has_project)
        self.delete_button.setEnabled(has_project)
        
        # Enable/disable project controls
        self.fusion_browse_btn.setEnabled(has_project)
        self.fusion_open_btn.setEnabled(has_project and os.path.exists(project.fusion_file) if project else False)
        self.template_browse_btn.setEnabled(has_project)
        self.template_open_btn.setEnabled(has_project and os.path.exists(project.template_file) if project else False)
        self.attachment_checkbox.setEnabled(has_project)
        self.add_files_btn.setEnabled(has_project)
        self.add_folder_btn.setEnabled(has_project)
        self.open_additional_file_btn.setEnabled(False)  # Will be enabled when files are selected
        
        # Enable/disable generation
        self.generate_button.setEnabled(has_project)
        
        if not has_project:
            self.validation_content.setText(self.tr("No project loaded"))
            self.generation_status.setText("")
            self.additional_files_list.clear()
            self.generated_images_list.clear()
    
    def create_project(self):
        """Launch the Create Project Wizard"""
        if not self.campaign_manager.active_campaign_folder:
            QMessageBox.warning(self, self.tr("Warning"), 
                              self.tr("Please load a campaign first"))
            return
        
        # Ensure picture-generator directory exists
        picture_projects_path = os.path.join(self.campaign_manager.active_campaign_folder, "picture-generator")
        os.makedirs(picture_projects_path, exist_ok=True)
        
        wizard = CreateProjectWizard(self.campaign_manager.active_campaign_folder, self)
        if wizard.exec() == QDialog.Accepted:
            self.refresh_projects()
            
            # Auto-select the newly created project if it exists
            project_name = wizard.page(0).project_name.text().strip()
            if project_name:
                self._select_project_in_dropdown(project_name)
    
    def _show_duplicate_dialog(self):
        """Show custom duplicate project dialog with proper translations"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Duplicate Project"))
        dialog.setModal(True)
        dialog.resize(400, 150)
        
        layout = QVBoxLayout()
        
        # Add label with proper translation
        label_text = self.tr("Original: {}\n\nNew project name:").format(self.current_project.project_name)
        label = QLabel(label_text)
        layout.addWidget(label)
        
        # Add input field
        name_input = QLineEdit(f"{self.current_project.project_name}_copy")
        layout.addWidget(name_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton(self.tr("Cancel"))
        ok_btn = QPushButton(self.tr("OK"))
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)
        
        # Focus on input and select all text
        name_input.setFocus()
        name_input.selectAll()
        
        if dialog.exec() != QDialog.Accepted:
            return None
        
        new_name = name_input.text().strip()
        return new_name if new_name else None

    def duplicate_project(self):
        """Duplicate the current project"""
        if not self.current_project:
            return
        
        # Get new project name with custom dialog
        new_name = self._show_duplicate_dialog()
        if not new_name:
            return
        
        # Check if name already exists
        picture_projects_path = os.path.join(self.campaign_manager.active_campaign_folder, "picture-generator")
        new_project_path = os.path.join(picture_projects_path, new_name)
        
        if os.path.exists(new_project_path):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.tr("Warning"))
            msg_box.setText(self.tr("A project with this name already exists"))
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
            msg_box.exec()
            return
        
        try:
            # Copy project folder
            shutil.copytree(self.current_project.project_path, new_project_path)
            
            # Load the new project
            self.refresh_projects()
            
            # Select the new project in dropdown
            self._select_project_in_dropdown(new_name)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.tr("Success"))
            msg_box.setText(self.tr("Project '{}' created successfully").format(new_name))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
            msg_box.exec()
            
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.tr("Error"))
            msg_box.setText(self.tr("Failed to duplicate project: {}").format(str(e)))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
            msg_box.exec()
    
    def delete_project(self):
        """Delete the current project"""
        if not self.current_project:
            return
        
        # Confirmation dialog
        # Create custom message box with translated buttons
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("Delete Project"))
        msg_box.setText(self.tr("Are you sure you want to delete the project '{}'?\n\nThis action cannot be undone.").format(self.current_project.project_name))
        msg_box.setIcon(QMessageBox.Question)
        
        # Add custom buttons with translations
        yes_button = msg_box.addButton(self.tr("Yes"), QMessageBox.YesRole)
        no_button = msg_box.addButton(self.tr("No"), QMessageBox.NoRole)
        msg_box.setDefaultButton(no_button)
        
        reply = msg_box.exec()
        
        if msg_box.clickedButton() != yes_button:
            return
        
        try:
            # Remove project folder
            shutil.rmtree(self.current_project.project_path)
            
            # Clear current project
            self.current_project = None
            
            # Refresh UI
            self.refresh_projects()
            
            QMessageBox.information(self, self.tr("Success"), 
                                  self.tr(self.tr("Project deleted successfully")))
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to delete project: {error}").format(error=str(e)))
    
    def browse_fusion_file(self):
        """Browse for a new fusion.csv file"""
        if not self.current_project:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select fusion.csv file"),
            "",
            self.tr("CSV files (*.csv)")
        )
        
        if file_path:
            try:
                # Copy file to project
                shutil.copy2(file_path, self.current_project.fusion_file)
                self.fusion_open_btn.setEnabled(True)
                self.validate_project()
                QMessageBox.information(self, self.tr("Success"), 
                                      self.tr(self.tr("fusion.csv file updated")))
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), 
                                   self.tr("Failed to update fusion.csv: {error}").format(error=str(e)))
    
    def open_fusion_file(self):
        """Open fusion.csv with system default application"""
        if not self.current_project or not os.path.exists(self.current_project.fusion_file):
            return
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.current_project.fusion_file])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.current_project.fusion_file)
            else:  # Linux
                subprocess.call(['xdg-open', self.current_project.fusion_file])
                
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to open fusion.csv: {error}").format(error=str(e)))
    
    def browse_template_file(self):
        """Browse for a new template.jpg file"""
        if not self.current_project:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select template image"),
            "",
            self.tr("Image files (*.jpg *.jpeg)")
        )
        
        if file_path:
            try:
                # Copy file to project
                shutil.copy2(file_path, self.current_project.template_file)
                self.template_open_btn.setEnabled(True)
                self.validate_project()
                QMessageBox.information(self, self.tr("Success"), 
                                      self.tr(self.tr("template.jpg file updated")))
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), 
                                   self.tr("Failed to update template.jpg: {error}").format(error=str(e)))
    
    def open_template_file(self):
        """Open template.jpg with system default application"""
        if not self.current_project or not os.path.exists(self.current_project.template_file):
            return
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.current_project.template_file])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.current_project.template_file)
            else:  # Linux
                subprocess.call(['xdg-open', self.current_project.template_file])
                
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to open template.jpg: {error}").format(error=str(e)))
    
    def add_files_to_project(self):
        """Add files to the current project"""
        if not self.current_project:
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Select Files to Add"),
            "",
            self.tr("Supported files (*.png *.jpg *.jpeg *.docx *.txt);;All Files (*)")
        )
        
        if not files:
            return
        
        try:
            added_count = 0
            for file_path in files:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.current_project.project_path, filename)
                
                # Check if file already exists
                if os.path.exists(dest_path):
                    reply = QMessageBox.question(
                        self,
                        self.tr("File Exists"),
                        self.tr("File '{filename}' already exists. Replace it?").format(filename=filename),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply != QMessageBox.Yes:
                        continue
                
                # Copy file to project
                shutil.copy2(file_path, dest_path)
                added_count += 1
            
            if added_count > 0:
                self.refresh_additional_files()
                self.validate_project()
                QMessageBox.information(
                    self,
                    self.tr("Success"),
                    self.tr("Added {count} file(s) to project").format(count=added_count)
                )
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to add files: {error}").format(error=str(e)))
    
    def add_folder_to_project(self):
        """Add a folder to the current project"""
        if not self.current_project:
            return
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Folder to Add")
        )
        
        if not folder_path:
            return
        
        try:
            folder_name = os.path.basename(folder_path)
            dest_path = os.path.join(self.current_project.project_path, folder_name)
            
            # Check if folder already exists
            if os.path.exists(dest_path):
                reply = QMessageBox.question(
                    self,
                    self.tr("Folder Exists"),
                    self.tr("Folder '{folder_name}' already exists. Replace it?").format(folder_name=folder_name),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
                
                # Remove existing folder
                shutil.rmtree(dest_path)
            
            # Copy folder to project
            shutil.copytree(folder_path, dest_path)
            
            self.refresh_additional_files()
            self.validate_project()
            QMessageBox.information(
                self,
                self.tr("Success"),
                self.tr("Added folder '{folder_name}' to project").format(folder_name=folder_name)
            )
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to add folder: {error}").format(error=str(e)))
    
    def set_campaign_path(self, campaign_path: str):
        """Set the current campaign path and refresh projects"""
        self.current_campaign_path = campaign_path
        self.refresh_projects()
    
    def clear_campaign(self):
        """Clear campaign-specific data"""
        self.current_campaign_path = None
        self.clear_campaign_state()
    
    def clear_campaign_state(self):
        """Clear all campaign-related state"""
        self.current_project = None
        self.picture_generator = None
        self.project_dropdown.clear()
        self.project_dropdown.addItem(self.tr("No campaign loaded"))
        self.project_dropdown.setEnabled(False)
        self.update_ui_state(None)
        
        # Clear all lists and content
        self.additional_files_list.clear()
        self.generated_images_list.clear()
        self.validation_content.setText(self.tr("No campaign loaded"))
        self.generation_status.setText("")
        
        # Clear file watcher
        if self.watched_files:
            self.file_watcher.removePaths(list(self.watched_files))
            self.watched_files.clear()
    
    def _select_project_in_dropdown(self, project_name):
        """Select a project in the dropdown by its actual name"""
        for i in range(self.project_dropdown.count()):
            item_text = self.project_dropdown.itemText(i)
            actual_name = self._extract_project_name(item_text)
            if actual_name == project_name:
                self.project_dropdown.setCurrentIndex(i)
                break

    def _extract_project_name(self, formatted_name):
        """Extract actual project name from formatted display name"""
        if formatted_name.endswith(" (attached)"):
            return formatted_name[:-11]  # Remove " (attached)"
        return formatted_name

    def _is_project_attached(self, project_name):
        """Check if a project is attached to emails"""
        if not self.current_campaign_path or not project_name:
            return False
        
        try:
            attach_file = os.path.join(
                self.current_campaign_path, 
                "picture-generator", 
                project_name, 
                "attach.txt"
            )
            
            if os.path.exists(attach_file):
                with open(attach_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip().lower()
                    return content == 'true'
            return False
        except Exception:
            return False

    def _format_project_name_with_status(self, project_name):
        """Format project name with attachment status"""
        if self._is_project_attached(project_name):
            return f"{project_name} (attached)"
        return project_name

    def refresh_projects(self):
        """Refresh the projects dropdown"""
        self.project_dropdown.clear()
        
        # Use current_campaign_path instead of campaign_manager.active_campaign_folder
        # This ensures we only show projects when explicitly told there's a campaign
        if not self.current_campaign_path:
            self.project_dropdown.addItem(self.tr("No campaign loaded"))
            self.project_dropdown.setEnabled(False)
            self.update_ui_state(None)
            self.picture_generator = None
            return
        
        # Initialize picture generator for this campaign
        self.picture_generator = PictureGenerator(self.current_campaign_path)
        
        # Find picture generator projects
        picture_projects_path = os.path.join(self.current_campaign_path, "picture-generator")
        
        if not os.path.exists(picture_projects_path):
            self.project_dropdown.addItem(self.tr("No project created yet"))
            self.project_dropdown.setEnabled(False)
            self.update_ui_state(None)
            return
        
        # Get list of projects
        projects = []
        try:
            for item in os.listdir(picture_projects_path):
                project_path = os.path.join(picture_projects_path, item)
                if os.path.isdir(project_path):
                    projects.append(item)
        except Exception as e:
            self.project_dropdown.addItem(self.tr("Error reading projects"))
            self.project_dropdown.setEnabled(False)
            return
        
        if not projects:
            self.project_dropdown.addItem(self.tr("No project created yet"))
            self.project_dropdown.setEnabled(False)
            self.update_ui_state(None)
        elif len(projects) == 1:
            # Auto-select single project with attachment status
            formatted_name = self._format_project_name_with_status(projects[0])
            self.project_dropdown.addItem(formatted_name)
            self.project_dropdown.setEnabled(True)
            self.load_project(projects[0])
        else:
            # Multiple projects - require selection
            self.project_dropdown.addItem(self.tr("Select the project to load"))
            for project in sorted(projects):
                formatted_name = self._format_project_name_with_status(project)
                self.project_dropdown.addItem(formatted_name)
            self.project_dropdown.setEnabled(True)
            self.update_ui_state(None)
    
    def tr(self, text: str) -> str:
        """Translate text using translation manager"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "PictureTab")
    
    def refresh_translations(self):
        """Refresh all translatable UI elements when language changes"""
        # Update group box titles
        if hasattr(self, 'top_group'):
            self.top_group.setTitle(self.tr("🖼️ Picture Generator Projects"))
        if hasattr(self, 'properties_group'):
            self.properties_group.setTitle(self.tr("📋 Project Properties"))
        if hasattr(self, 'help_group'):
            self.help_group.setTitle(self.tr("📚 User Help & Guidance"))
        if hasattr(self, 'validation_group'):
            self.validation_group.setTitle(self.tr("🔍 Validation Panel"))
        if hasattr(self, 'generation_group'):
            self.generation_group.setTitle(self.tr("🎨 Picture Generation"))
        if hasattr(self, 'images_group'):
            self.images_group.setTitle(self.tr("📸 Generated Images"))
        
        # Update button texts
        if hasattr(self, 'create_button'):
            self.create_button.setText(self.tr("Create"))
        if hasattr(self, 'duplicate_button'):
            self.duplicate_button.setText(self.tr("Duplicate"))
        if hasattr(self, 'delete_button'):
            self.delete_button.setText(self.tr("Delete"))
        if hasattr(self, 'fusion_browse_btn'):
            self.fusion_browse_btn.setText(self.tr("Browse"))
        if hasattr(self, 'fusion_open_btn'):
            self.fusion_open_btn.setText(self.tr("Open"))
        if hasattr(self, 'template_browse_btn'):
            self.template_browse_btn.setText(self.tr("Browse"))
        if hasattr(self, 'template_open_btn'):
            self.template_open_btn.setText(self.tr("Open"))
        if hasattr(self, 'add_files_btn'):
            self.add_files_btn.setText(self.tr(self.tr("+ Files")))
        if hasattr(self, 'add_folder_btn'):
            self.add_folder_btn.setText(self.tr(self.tr("+ Folder")))
        if hasattr(self, 'open_additional_file_btn'):
            self.open_additional_file_btn.setText(self.tr("Open"))
        if hasattr(self, 'generate_button'):
            self.generate_button.setText(self.tr("🎨 Generate Pictures"))
        if hasattr(self, 'open_selected_btn'):
            self.open_selected_btn.setText(self.tr("Open Selected"))
        
        # Update dropdown text if no campaign is loaded
        if hasattr(self, 'project_dropdown') and self.project_dropdown.count() > 0:
            current_text = self.project_dropdown.itemText(0)
            if "No campaign loaded" in current_text or "Aucune campagne chargée" in current_text:
                self.project_dropdown.setItemText(0, self.tr("No campaign loaded"))
        
        # Update validation content if showing "No campaign loaded"
        if hasattr(self, 'validation_content'):
            current_validation = self.validation_content.text()
            if "No campaign loaded" in current_validation or "Aucune campagne chargée" in current_validation:
                self.validation_content.setText(self.tr("No campaign loaded"))
        
        # Update checkbox text
        if hasattr(self, 'attachment_checkbox'):
            self.attachment_checkbox.setText(self.tr("Attach generated images to emails"))
        
        # Update attachment label
        if hasattr(self, 'attachment_label'):
            self.attachment_label.setText(self.tr("Email Attachment:"))
        
        # Update help text
        if hasattr(self, 'help_text'):
            self.help_text.setText(self.get_help_text())
        
        # Update additional files label
        if hasattr(self, 'additional_files_label'):
            # Find the label widget in the layout
            for i in range(self.additional_files_list.parent().layout().count()):
                item = self.additional_files_list.parent().layout().itemAt(i)
                if item and hasattr(item.widget(), 'text') and 'Additional Files' in item.widget().text():
                    item.widget().setText(self.tr("Additional Files:"))
        
        # Update validation content if needed
        if hasattr(self, 'validation_content') and self.current_project:
            self.validate_project()
        elif hasattr(self, 'validation_content'):
            self.validation_content.setText(self.tr("No project loaded"))
    
    def get_system_files_filter(self):
        """Get comprehensive system files filter for all operating systems"""
        return {
            # macOS system files
            '.DS_Store',           # Finder metadata
            '.AppleDouble',        # Resource fork files
            '._*',                 # AppleDouble resource fork prefix (handled separately)
            '.Spotlight-V100',     # Spotlight index
            '.Trashes',           # Trash folder
            '.VolumeIcon.icns',   # Volume icon
            '.fseventsd',         # File system events
            '.TemporaryItems',    # Temporary items
            '.apdisk',            # Apple Partition Map
            
            # Windows system files
            'Thumbs.db',          # Thumbnail cache
            'ehthumbs.db',        # Enhanced thumbnail cache
            'Desktop.ini',        # Folder customization
            'desktop.ini',        # Folder customization (lowercase)
            '$RECYCLE.BIN',       # Recycle bin
            'System Volume Information',  # System restore
            'pagefile.sys',       # Virtual memory
            'hiberfil.sys',       # Hibernation file
            'swapfile.sys',       # Swap file
            'DumpStack.log.tmp',  # Crash dump
            
            # Linux system files
            '.directory',         # KDE folder settings
            '.Trash-*',          # Trash folders (pattern handled separately)
            '.gvfs',             # GNOME virtual file system
            '.cache',            # Cache directory
            '.config',           # Configuration directory (when at root)
            '.local',            # Local data directory (when at root)
            
            # Version control system files
            '.git',              # Git repository
            '.gitignore',        # Git ignore file
            '.gitkeep',          # Git keep file
            '.gitattributes',    # Git attributes
            '.svn',              # Subversion
            '.hg',               # Mercurial
            '.bzr',              # Bazaar
            'CVS',               # CVS
            
            # IDE and editor files
            '.vscode',           # Visual Studio Code
            '.idea',             # IntelliJ IDEA
            '.vs',               # Visual Studio
            '.sublime-project',  # Sublime Text
            '.sublime-workspace', # Sublime Text
            '*.swp',             # Vim swap files (pattern handled separately)
            '*.swo',             # Vim swap files
            '*.tmp',             # Temporary files (pattern handled separately)
            '*~',                # Backup files (pattern handled separately)
            
            # Build and dependency files
            'node_modules',      # Node.js dependencies
            '__pycache__',       # Python cache
            '.pytest_cache',     # Pytest cache
            '.coverage',         # Coverage reports
            '.tox',              # Tox testing
            'dist',              # Distribution files
            'build',             # Build files
            '*.egg-info',        # Python egg info (pattern handled separately)
            
            # Other common system/hidden files
            '.htaccess',         # Apache configuration
            '.env',              # Environment variables
            '.dockerignore',     # Docker ignore
            'Dockerfile',        # Docker (might be legitimate, but often system)
            '.editorconfig',     # Editor configuration
            '.eslintrc*',        # ESLint configuration (pattern handled separately)
            '.prettierrc*',      # Prettier configuration (pattern handled separately)
        }
    
    def is_system_file(self, filename: str) -> bool:
        """Check if a file should be filtered out as a system file"""
        system_files = self.get_system_files_filter()
        
        # Direct match
        if filename in system_files:
            return True
        
        # Pattern matching for files with wildcards or prefixes
        import fnmatch
        
        # AppleDouble resource fork files (._filename)
        if filename.startswith('._'):
            return True
        
        # Trash folders (.Trash-1000, .Trash-user, etc.)
        if filename.startswith('.Trash-'):
            return True
        
        # Vim swap files (.filename.swp, .filename.swo)
        if fnmatch.fnmatch(filename, '*.swp') or fnmatch.fnmatch(filename, '*.swo'):
            return True
        
        # Temporary files
        if fnmatch.fnmatch(filename, '*.tmp') or fnmatch.fnmatch(filename, '*.temp'):
            return True
        
        # Backup files (filename~, filename.bak)
        if filename.endswith('~') or filename.endswith('.bak'):
            return True
        
        # Python egg info directories
        if fnmatch.fnmatch(filename, '*.egg-info'):
            return True
        
        # ESLint configuration files
        if filename.startswith('.eslintrc'):
            return True
        
        # Prettier configuration files
        if filename.startswith('.prettierrc'):
            return True
        
        # Log files (often system-generated)
        if fnmatch.fnmatch(filename, '*.log'):
            return True
        
        # Lock files
        if fnmatch.fnmatch(filename, '*.lock') or filename.endswith('.lockfile'):
            return True
        
        # Hidden files starting with . (but allow some legitimate ones)
        if filename.startswith('.') and filename not in {
            '.env.example',      # Example environment file
            '.gitkeep',         # Already in system_files but good to be explicit
            '.htaccess',        # Already in system_files
        }:
            # Additional check for hidden files that might be legitimate
            # Allow hidden files that are commonly used in projects
            legitimate_hidden = {
                '.editorconfig', '.dockerignore', '.gitignore', '.gitattributes'
            }
            if filename not in legitimate_hidden:
                return True
        
        return False
    
    def refresh_additional_files(self):
        """Refresh the additional files list"""
        self.additional_files_list.clear()
        
        if not self.current_project:
            return
        
        try:
            for item in os.listdir(self.current_project.project_path):
                # Skip system files using comprehensive filter
                if self.is_system_file(item):
                    continue
                
                item_path = os.path.join(self.current_project.project_path, item)
                
                # Skip core files and data folder
                if item in ['template.jpg', 'fusion.csv', 'attach.txt', 'data']:
                    continue
                
                if os.path.isfile(item_path):
                    list_item = QListWidgetItem(f"📄 {item}")
                    list_item.setData(Qt.UserRole, item_path)
                    self.additional_files_list.addItem(list_item)
                elif os.path.isdir(item_path):
                    # Count files in directory, excluding system files
                    file_count = 0
                    try:
                        for f in os.listdir(item_path):
                            if os.path.isfile(os.path.join(item_path, f)) and not self.is_system_file(f):
                                file_count += 1
                    except (PermissionError, OSError):
                        # If we can't read the directory, show it anyway
                        file_count = 0
                    
                    list_item = QListWidgetItem(f"📂 {item}/ ({file_count} files)")
                    list_item.setData(Qt.UserRole, item_path)
                    self.additional_files_list.addItem(list_item)
        except Exception as e:
            print(f"Error refreshing additional files: {e}")
    
    def on_additional_files_selection_changed(self):
        """Handle additional files selection change"""
        has_selection = len(self.additional_files_list.selectedItems()) > 0
        self.open_additional_file_btn.setEnabled(has_selection)
    
    def open_selected_additional_file(self):
        """Open selected additional file or folder"""
        selected_items = self.additional_files_list.selectedItems()
        if not selected_items:
            return
        
        # Open the first selected item
        item = selected_items[0]
        self.open_additional_file(item)
    
    def open_additional_file(self, item: QListWidgetItem):
        """Open additional file or folder"""
        file_path = item.data(Qt.UserRole)
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
                
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to open file: {error}").format(error=str(e)))
    
    def on_attachment_changed(self, state):
        """Handle attachment checkbox change"""
        if not self.current_project:
            return
        
        try:
            # Set flag to prevent file watcher from reloading
            self.updating_attachment_file = True
            
            # Fix the comparison - state is an integer: 0=unchecked, 2=checked
            is_checked = state == 2  # Qt.Checked.value is 2
            value_to_write = 'true' if is_checked else 'false'
            
            with open(self.current_project.attach_file, 'w', encoding='utf-8') as f:
                f.write(value_to_write)
                
            # Emit signal to notify other tabs about the change
            self.picture_settings_changed.emit()
            
            # Refresh dropdown to show updated attachment status
            current_project_name = self.current_project.project_name if self.current_project else None
            self.refresh_projects()
            
            # Restore selection if we had a current project
            if current_project_name:
                self._select_project_in_dropdown(current_project_name)
                
            # Reset flag after a short delay to allow file system to settle
            QTimer.singleShot(100, lambda: setattr(self, 'updating_attachment_file', False))
            
        except Exception as e:
            self.updating_attachment_file = False
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to update attachment setting: {error}").format(error=str(e)))
    
    def load_attachment_setting(self):
        """Load the attachment setting from attach.txt"""
        if not self.current_project:
            return
        
        try:
            if os.path.exists(self.current_project.attach_file):
                with open(self.current_project.attach_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip().lower()
                    # Use blockSignals to prevent signal emission during programmatic change
                    self.attachment_checkbox.blockSignals(True)
                    self.attachment_checkbox.setChecked(content == 'true')
                    self.attachment_checkbox.blockSignals(False)
            else:
                self.attachment_checkbox.blockSignals(True)
                self.attachment_checkbox.setChecked(False)
                self.attachment_checkbox.blockSignals(False)
                
        except Exception as e:
            self.attachment_checkbox.blockSignals(True)
            self.attachment_checkbox.setChecked(False)
            self.attachment_checkbox.blockSignals(False)
    
    def validate_project(self):
        """Validate the current project and update validation panel"""
        if not self.current_project:
            self.validation_content.setText(self.tr("No project loaded"))
            return
        
        validation_result = self.current_project.is_valid()
        
        # Build validation text
        validation_text = ""
        
        if validation_result.is_valid:
            validation_text += "✅ " + self.tr("Project validation passed") + "\n"
        
        # Show errors
        for error in validation_result.errors:
            validation_text += f"❌ {error}\n"
        
        # Show warnings
        for warning in validation_result.warnings:
            validation_text += f"⚠️ {warning}\n"
        
        if not validation_text:
            validation_text = self.tr("No validation issues found")
        
        self.validation_content.setText(validation_text.strip())
    
    def setup_file_watching(self):
        """Setup file system watching for external editor integration"""
        # Clear existing watches
        if self.watched_files:
            self.file_watcher.removePaths(list(self.watched_files))
            self.watched_files.clear()
        
        if not self.current_project:
            return
        
        # Watch core files
        files_to_watch = [
            self.current_project.fusion_file,
            self.current_project.template_file,
            self.current_project.attach_file
        ]
        
        for file_path in files_to_watch:
            if os.path.exists(file_path):
                self.file_watcher.addPath(file_path)
                self.watched_files.add(file_path)
    
    def on_file_changed(self, file_path: str):
        """Handle external file changes"""
        if not self.current_project:
            return
        
        # Delay validation to avoid multiple rapid updates
        QTimer.singleShot(500, self.validate_project)
        
        if file_path == self.current_project.attach_file:
            # Only reload if we're not the ones updating the file
            if not getattr(self, 'updating_attachment_file', False):
                QTimer.singleShot(500, self.load_attachment_setting)
    
    def on_generation_progress(self, current: int, total: int, message: str):
        """Handle progress updates from picture generation"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
        
        # Update status message
        self.generation_status.setText(f"🎨 {message}")
        
        # Force GUI update
        QApplication.processEvents()
    
    def generate_pictures(self):
        """Generate pictures for the current project"""
        if not self.current_project or not self.picture_generator:
            return
        
        # Validate project first
        validation_result = self.current_project.is_valid()
        if not validation_result.is_valid:
            QMessageBox.warning(self, self.tr("Validation Error"), 
                              self.tr("Please fix validation errors before generating pictures"))
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generation_status.setText(self.tr("Starting picture generation..."))
        self.generate_button.setEnabled(False)
        
        try:
            # Get recipients from campaign
            recipients_file = os.path.join(self.campaign_manager.active_campaign_folder, "recipients.csv")
            if not os.path.exists(recipients_file):
                raise Exception("recipients.csv not found in campaign")
            
            # Read recipients
            import csv
            recipients = []
            with open(recipients_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                recipients = list(reader)
            
            # Generate pictures using the core module with progress callback
            result = self.picture_generator.generate_pictures(
                self.current_project.project_name,
                recipients,
                progress_callback=self.on_generation_progress
            )
            
            if result == 0:  # Success
                self.progress_bar.setValue(100)  # Ensure 100% completion
                self.generation_status.setText(
                    f"✅ {self.tr('Successfully generated pictures')}"
                )
                self.refresh_generated_images()
            else:
                self.progress_bar.setValue(100)  # Show completion even if some failed
                self.generation_status.setText(f"❌ {self.tr('Generation failed with code')}: {result}")
            
        except Exception as e:
            self.progress_bar.setValue(0)  # Reset on error
            self.generation_status.setText(f"❌ {self.tr('Error')}: {str(e)}")
        
        finally:
            # Keep progress bar visible for a moment to show completion
            QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
            self.generate_button.setEnabled(True)
    
    def refresh_generated_images(self):
        """Refresh the generated images list"""
        self.generated_images_list.clear()
        
        if not self.current_project or not os.path.exists(self.current_project.data_folder):
            self.open_selected_btn.setEnabled(False)
            return
        
        try:
            images = [f for f in os.listdir(self.current_project.data_folder) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            for image in sorted(images):
                item = QListWidgetItem(f"📸 {image}")
                item.setData(Qt.UserRole, os.path.join(self.current_project.data_folder, image))
                self.generated_images_list.addItem(item)
            
            self.open_selected_btn.setEnabled(len(images) > 0)
            
        except Exception as e:
            print(f"Error refreshing generated images: {e}")
    
    def open_selected_images(self):
        """Open selected generated images"""
        selected_items = self.generated_images_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, self.tr("Info"), self.tr("Please select images to open"))
            return
        
        for item in selected_items:
            image_path = item.data(Qt.UserRole)
            if image_path and os.path.exists(image_path):
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', image_path])
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(image_path)
                    else:  # Linux
                        subprocess.call(['xdg-open', image_path])
                        
                except Exception as e:
                    QMessageBox.critical(self, self.tr("Error"), 
                                       self.tr("Failed to open image: {error}").format(error=str(e)))
    

class CreateProjectWizard(QWizard):
    """Wizard for creating new picture generator projects"""
    
    def __init__(self, campaign_path: str, parent=None):
        super().__init__(parent)
        self.campaign_path = campaign_path
        self.picture_projects_path = os.path.join(campaign_path, "picture-generator")
        
        # Ensure the picture-generator directory exists
        os.makedirs(self.picture_projects_path, exist_ok=True)
        
        self.setWindowTitle(self.tr("Create Picture Generator Project"))
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(600, 500)
        
        # Set translatable button texts
        self.setButtonText(QWizard.BackButton, self.tr("< Back"))
        self.setButtonText(QWizard.NextButton, self.tr("Next >"))
        self.setButtonText(QWizard.FinishButton, self.tr("Finish"))
        self.setButtonText(QWizard.CancelButton, self.tr("Cancel"))
        
        # Create wizard pages
        self.addPage(ProjectBasicsPage(self))
        self.addPage(AdditionalFilesPage(self))
    
    def accept(self):
        """Handle wizard completion and create the project"""
        try:
            # Get data from wizard pages
            basics_page = self.page(0)  # ProjectBasicsPage
            files_page = self.page(1)   # AdditionalFilesPage
            
            project_name = basics_page.project_name.text().strip()
            template_path = basics_page.template_path.text().strip()
            fusion_path = basics_page.fusion_path.text().strip()
            additional_files = files_page.additional_files
            
            # Validate inputs
            if not project_name:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.tr("Error"))
                msg_box.setText(self.tr("Please enter a project name"))
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
                msg_box.exec()
                return
            
            if not template_path:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.tr("Error"))
                msg_box.setText(self.tr("Please select a template image"))
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
                msg_box.exec()
                return
            
            # Create project folder
            project_folder = os.path.join(self.picture_projects_path, project_name)
            
            # Check if project already exists
            if os.path.exists(project_folder):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.tr("Error"))
                msg_box.setText(self.tr("Project '{project_name}' already exists").format(project_name=project_name))
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
                msg_box.exec()
                return
            
            # Create the project
            self.create_project_files(project_folder, template_path, fusion_path, additional_files)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.tr("Success"))
            msg_box.setText(self.tr("Project '{project_name}' created successfully!").format(project_name=project_name))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
            msg_box.exec()
            
            # Call parent accept to close wizard
            super().accept()
            
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.tr("Error"))
            msg_box.setText(self.tr("Failed to create project: {error}").format(error=str(e)))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.addButton(self.tr("OK"), QMessageBox.AcceptRole)
            msg_box.exec()
    
    def create_project_files(self, project_folder, template_path, fusion_path, additional_files):
        """Create the actual project files and folders"""
        import shutil
        import csv
        
        # Create project directory
        os.makedirs(project_folder, exist_ok=True)
        
        # Copy template image
        template_dest = os.path.join(project_folder, "template.jpg")
        shutil.copy2(template_path, template_dest)
        
        # Handle fusion.csv
        fusion_dest = os.path.join(project_folder, "fusion.csv")
        if fusion_path and fusion_path != "CREATE_EMPTY":
            # Copy existing fusion.csv
            shutil.copy2(fusion_path, fusion_dest)
        else:
            # Create empty fusion.csv with headers
            fusion_headers = ['fusion-type', 'data', 'positioning', 'size', 'alignment', 
                            'orientation', 'font', 'shape', 'color']
            with open(fusion_dest, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(fusion_headers)
        
        # Create attach.txt (default to false)
        attach_dest = os.path.join(project_folder, "attach.txt")
        with open(attach_dest, 'w', encoding='utf-8') as f:
            f.write('false')
        
        # Create data folder
        data_folder = os.path.join(project_folder, "data")
        os.makedirs(data_folder, exist_ok=True)
        
        # Copy additional files
        for file_path in additional_files:
            if os.path.isfile(file_path):
                # Copy individual file
                filename = os.path.basename(file_path)
                dest_path = os.path.join(project_folder, filename)
                shutil.copy2(file_path, dest_path)
            elif os.path.isdir(file_path):
                # Copy entire folder
                folder_name = os.path.basename(file_path)
                dest_path = os.path.join(project_folder, folder_name)
                shutil.copytree(file_path, dest_path)
    
    def tr(self, text: str) -> str:
        """Translate text"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "CreateProjectWizard")


class ProjectBasicsPage(QWizardPage):
    """First page: Project name, template, and fusion configuration"""
    
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle(self.tr("Project Basics"))
        self.setSubTitle(self.tr("Set up the basic project information"))
        
        layout = QVBoxLayout()
        
        # Project name
        layout.addWidget(QLabel(self.tr("Project Name:")))
        self.project_name = QLineEdit()
        self.project_name.textChanged.connect(self.completeChanged)
        layout.addWidget(self.project_name)
        
        # Template image
        layout.addWidget(QLabel(self.tr("Template Image (required):")))
        template_layout = QHBoxLayout()
        self.template_path = QLineEdit()
        self.template_path.setReadOnly(True)
        self.template_path.textChanged.connect(self.completeChanged)
        
        template_browse = QPushButton(self.tr("Browse..."))
        template_browse.clicked.connect(self.browse_template)
        
        template_layout.addWidget(self.template_path)
        template_layout.addWidget(template_browse)
        layout.addLayout(template_layout)
        
        # Fusion configuration
        layout.addWidget(QLabel(self.tr("Fusion Configuration:")))
        fusion_layout = QHBoxLayout()
        
        self.fusion_path = QLineEdit()
        self.fusion_path.setReadOnly(True)
        self.fusion_path.setPlaceholderText(self.tr("Optional: Select existing fusion.csv"))
        
        fusion_browse = QPushButton(self.tr("Browse..."))
        fusion_browse.clicked.connect(self.browse_fusion)
        
        create_empty = QPushButton(self.tr("Create Empty"))
        create_empty.clicked.connect(self.create_empty_fusion)
        
        fusion_layout.addWidget(self.fusion_path)
        fusion_layout.addWidget(fusion_browse)
        fusion_layout.addWidget(create_empty)
        layout.addLayout(fusion_layout)
        
        self.setLayout(layout)
    
    def browse_template(self):
        """Browse for template image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Template Image"),
            "",
            self.tr("Image files (*.jpg *.jpeg)")
        )
        if file_path:
            self.template_path.setText(file_path)
    
    def browse_fusion(self):
        """Browse for fusion CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Fusion CSV"),
            "",
            self.tr("CSV files (*.csv)")
        )
        if file_path:
            self.fusion_path.setText(file_path)
    
    def create_empty_fusion(self):
        """Create empty fusion CSV"""
        self.fusion_path.setText("CREATE_EMPTY")
    
    def isComplete(self):
        """Check if page is complete"""
        return bool(self.project_name.text().strip() and self.template_path.text().strip())
    
    def tr(self, text: str) -> str:
        """Translate text"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "ProjectBasicsPage")


class AdditionalFilesPage(QWizardPage):
    """Second page: Additional files and folders"""
    
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle(self.tr("Additional Files"))
        self.setSubTitle(self.tr("Add additional files and folders to your project"))
        
        layout = QVBoxLayout()
        
        # File upload interface
        buttons_layout = QHBoxLayout()
        
        add_files_btn = QPushButton(self.tr(self.tr("+ Files")))
        add_files_btn.clicked.connect(self.add_files)
        
        add_folder_btn = QPushButton(self.tr(self.tr("+ Folder")))
        add_folder_btn.clicked.connect(self.add_folder)
        
        buttons_layout.addWidget(add_files_btn)
        buttons_layout.addWidget(add_folder_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Files list
        layout.addWidget(QLabel(self.tr("Selected Files and Folders:")))
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)
        
        # Remove button
        remove_btn = QPushButton(self.tr("Remove Selected"))
        remove_btn.clicked.connect(self.remove_selected)
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
        self.additional_files = []
    
    def add_files(self):
        """Add individual files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Select Additional Files"),
            "",
            self.tr("Supported files (*.png *.jpg *.jpeg *.docx *.txt)")
        )
        
        for file_path in files:
            if file_path not in self.additional_files:
                self.additional_files.append(file_path)
                item = QListWidgetItem(f"📄 {os.path.basename(file_path)}")
                item.setData(Qt.UserRole, file_path)
                self.files_list.addItem(item)
    
    def add_folder(self):
        """Add folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Folder")
        )
        
        if folder_path and folder_path not in self.additional_files:
            self.additional_files.append(folder_path)
            file_count = sum(len(files) for _, _, files in os.walk(folder_path))
            item = QListWidgetItem(f"📂 {os.path.basename(folder_path)}/ ({file_count} files)")
            item.setData(Qt.UserRole, folder_path)
            self.files_list.addItem(item)
    
    def remove_selected(self):
        """Remove selected files"""
        for item in self.files_list.selectedItems():
            file_path = item.data(Qt.UserRole)
            if file_path in self.additional_files:
                self.additional_files.remove(file_path)
            self.files_list.takeItem(self.files_list.row(item))
    
    def tr(self, text: str) -> str:
        """Translate text"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "AdditionalFilesPage")
