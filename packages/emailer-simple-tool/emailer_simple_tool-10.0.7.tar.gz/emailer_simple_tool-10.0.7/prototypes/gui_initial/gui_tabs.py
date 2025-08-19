"""
GUI Tab Components for Emailer Simple Tool
Individual tabs for different functionality areas
"""

import os
import csv
from pathlib import Path
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
        QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, 
        QFileDialog, QMessageBox, QProgressBar, QGroupBox, 
        QFormLayout, QCheckBox, QSpinBox, QSplitter, QTreeWidget, 
        QTreeWidgetItem, QComboBox, QScrollArea
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont, QPixmap
except ImportError:
    print("PySide6 not available")


class CampaignTab(QWidget):
    """Campaign management and overview tab"""
    
    def __init__(self):
        super().__init__()
        self.current_campaign_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize campaign tab UI"""
        layout = QVBoxLayout()
        
        # Campaign folder selection
        folder_group = QGroupBox("📁 Campaign Folder")
        folder_layout = QVBoxLayout()
        
        # Folder selection row
        folder_row = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Select your campaign folder...")
        self.folder_path.setReadOnly(True)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_folder)
        browse_button.setStyleSheet("QPushButton { background-color: #6c757d; }")
        
        folder_row.addWidget(self.folder_path)
        folder_row.addWidget(browse_button)
        
        folder_layout.addLayout(folder_row)
        folder_group.setLayout(folder_layout)
        
        # Campaign status overview
        status_group = QGroupBox("📊 Campaign Status")
        status_layout = QVBoxLayout()
        
        self.status_overview = QLabel("No campaign loaded")
        self.status_overview.setStyleSheet("color: #6c757d; font-size: 14px; padding: 10px;")
        self.status_overview.setWordWrap(True)
        
        status_layout.addWidget(self.status_overview)
        status_group.setLayout(status_layout)
        
        # Create splitter for side-by-side content
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Recipients preview
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        recipients_group = QGroupBox("👥 Recipients Preview")
        recipients_layout = QVBoxLayout()
        
        self.recipients_table = QTableWidget()
        self.recipients_table.setMaximumHeight(250)
        self.recipients_table.setAlternatingRowColors(True)
        
        recipients_layout.addWidget(self.recipients_table)
        recipients_group.setLayout(recipients_layout)
        
        left_layout.addWidget(recipients_group)
        left_widget.setLayout(left_layout)
        
        # Right side - Message and attachments preview
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Message preview
        message_group = QGroupBox("📝 Message Template")
        message_layout = QVBoxLayout()
        
        self.message_preview = QTextEdit()
        self.message_preview.setMaximumHeight(150)
        self.message_preview.setPlaceholderText("Message template will appear here...")
        self.message_preview.setReadOnly(True)
        
        message_layout.addWidget(self.message_preview)
        message_group.setLayout(message_layout)
        
        # Attachments preview
        attachments_group = QGroupBox("📎 Attachments")
        attachments_layout = QVBoxLayout()
        
        self.attachments_list = QTextEdit()
        self.attachments_list.setMaximumHeight(100)
        self.attachments_list.setPlaceholderText("No attachments found")
        self.attachments_list.setReadOnly(True)
        
        attachments_layout.addWidget(self.attachments_list)
        attachments_group.setLayout(attachments_layout)
        
        right_layout.addWidget(message_group)
        right_layout.addWidget(attachments_group)
        right_widget.setLayout(right_layout)
        
        # Add widgets to splitter
        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([500, 500])
        
        # Add all components to main layout
        layout.addWidget(folder_group)
        layout.addWidget(status_group)
        layout.addWidget(content_splitter)
        
        self.setLayout(layout)
    
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
            self.load_campaign_preview(folder)
    
    def load_campaign_preview(self, folder_path: str):
        """Load and display campaign preview"""
        try:
            folder_name = Path(folder_path).name
            
            # Check required files
            recipients_csv = Path(folder_path) / "recipients.csv"
            subject_txt = Path(folder_path) / "subject.txt"
            msg_txt = Path(folder_path) / "msg.txt"
            msg_docx = Path(folder_path) / "msg.docx"
            attachments_dir = Path(folder_path) / "attachments"
            picture_gen_dir = Path(folder_path) / "picture-generator"
            
            # Build status overview
            status_parts = [f"✅ Campaign: {folder_name}"]
            
            if recipients_csv.exists():
                recipient_count = self.count_csv_rows(recipients_csv)
                status_parts.append(f"👥 Recipients: {recipient_count}")
                self.load_recipients_preview(recipients_csv)
            else:
                status_parts.append("❌ No recipients.csv found")
                self.recipients_table.clear()
            
            if subject_txt.exists():
                status_parts.append("✅ Subject template found")
            else:
                status_parts.append("❌ No subject.txt found")
            
            if msg_docx.exists():
                status_parts.append("✅ Message template: .docx (formatted)")
                self.load_message_preview(msg_docx, is_docx=True)
            elif msg_txt.exists():
                status_parts.append("✅ Message template: .txt (plain)")
                self.load_message_preview(msg_txt, is_docx=False)
            else:
                status_parts.append("❌ No message template found")
                self.message_preview.clear()
            
            if attachments_dir.exists():
                attachment_count = len([f for f in attachments_dir.iterdir() if f.is_file()])
                status_parts.append(f"📎 Attachments: {attachment_count} files")
                self.load_attachments_preview(attachments_dir)
            else:
                status_parts.append("📎 No attachments folder")
                self.attachments_list.setPlainText("No attachments folder found")
            
            if picture_gen_dir.exists():
                project_count = len([d for d in picture_gen_dir.iterdir() if d.is_dir()])
                status_parts.append(f"🖼️ Picture projects: {project_count}")
            else:
                status_parts.append("🖼️ No picture generator")
            
            self.status_overview.setText("\n".join(status_parts))
            self.status_overview.setStyleSheet("color: #28a745; font-size: 14px; padding: 10px;")
            
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
                data_rows = rows[1:6]  # Show first 5 rows
                
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
                if len(rows) > 6:
                    remaining = len(rows) - 6
                    note = f"... and {remaining} more recipients"
                    self.recipients_table.setRowCount(len(data_rows) + 1)
                    note_item = QTableWidgetItem(note)
                    note_item.setFont(QFont("Arial", 9, QFont.Italic))
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
                    "📄 DOCX Template Detected\n\n"
                    "This is a formatted document template (.docx) that contains:\n"
                    "• Rich text formatting (bold, italic, colors)\n"
                    "• Tables and structured content\n"
                    "• Template variables like {{name}}, {{email}}\n\n"
                    "The actual formatted content would be processed when sending emails."
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
            files = [f for f in attachments_dir.iterdir() if f.is_file()]
            if not files:
                self.attachments_list.setPlainText("Attachments folder is empty")
                return
            
            file_info = []
            total_size = 0
            
            for file_path in files[:10]:  # Show first 10 files
                size = file_path.stat().st_size
                total_size += size
                size_str = self.format_file_size(size)
                file_info.append(f"📄 {file_path.name} ({size_str})")
            
            if len(files) > 10:
                file_info.append(f"... and {len(files) - 10} more files")
            
            file_info.append(f"\nTotal size: {self.format_file_size(total_size)}")
            
            self.attachments_list.setPlainText("\n".join(file_info))
            
        except Exception as e:
            self.attachments_list.setPlainText(f"Error loading attachments: {str(e)}")
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


class SMTPTab(QWidget):
    """SMTP configuration tab"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize SMTP tab UI"""
        layout = QVBoxLayout()
        
        # SMTP Configuration form
        smtp_group = QGroupBox("📧 SMTP Server Configuration")
        smtp_layout = QFormLayout()
        
        # Server settings
        self.smtp_server = QLineEdit()
        self.smtp_server.setPlaceholderText("smtp.gmail.com")
        
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)
        
        self.smtp_username = QLineEdit()
        self.smtp_username.setPlaceholderText("your.email@gmail.com")
        
        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_password.setPlaceholderText("Your app password or email password")
        
        self.use_tls = QCheckBox("Use TLS/STARTTLS (recommended)")
        self.use_tls.setChecked(True)
        
        # Add fields to form
        smtp_layout.addRow("SMTP Server:", self.smtp_server)
        smtp_layout.addRow("Port:", self.smtp_port)
        smtp_layout.addRow("Username:", self.smtp_username)
        smtp_layout.addRow("Password:", self.smtp_password)
        smtp_layout.addRow("", self.use_tls)
        
        smtp_group.setLayout(smtp_layout)
        
        # Quick setup presets
        presets_group = QGroupBox("⚡ Quick Setup")
        presets_layout = QHBoxLayout()
        
        gmail_btn = QPushButton("Gmail")
        gmail_btn.clicked.connect(lambda: self.load_preset("gmail"))
        gmail_btn.setStyleSheet("QPushButton { background-color: #dc3545; }")
        
        outlook_btn = QPushButton("Outlook")
        outlook_btn.clicked.connect(lambda: self.load_preset("outlook"))
        outlook_btn.setStyleSheet("QPushButton { background-color: #0078d4; }")
        
        yahoo_btn = QPushButton("Yahoo")
        yahoo_btn.clicked.connect(lambda: self.load_preset("yahoo"))
        yahoo_btn.setStyleSheet("QPushButton { background-color: #6001d2; }")
        
        presets_layout.addWidget(gmail_btn)
        presets_layout.addWidget(outlook_btn)
        presets_layout.addWidget(yahoo_btn)
        presets_layout.addStretch()
        
        presets_group.setLayout(presets_layout)
        
        # Connection test
        test_group = QGroupBox("🔧 Connection Test")
        test_layout = QVBoxLayout()
        
        test_button = QPushButton("Test SMTP Connection")
        test_button.clicked.connect(self.test_connection)
        test_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        
        self.test_result = QLabel("Click 'Test SMTP Connection' to verify your settings")
        self.test_result.setStyleSheet("color: #6c757d; padding: 10px;")
        self.test_result.setWordWrap(True)
        
        test_layout.addWidget(test_button)
        test_layout.addWidget(self.test_result)
        test_group.setLayout(test_layout)
        
        # Provider help
        help_group = QGroupBox("📚 Provider Setup Help")
        help_layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setMaximumHeight(200)
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h4>Common Email Provider Settings:</h4>
        <p><b>📧 Gmail:</b><br>
        • Server: smtp.gmail.com, Port: 587<br>
        • Enable 2-factor authentication<br>
        • Use App Password (not your regular password)<br>
        • Generate at: <a href="https://myaccount.google.com/apppasswords">Google App Passwords</a></p>
        
        <p><b>📧 Outlook/Hotmail:</b><br>
        • Server: smtp-mail.outlook.com, Port: 587<br>
        • Use your regular email password<br>
        • May need to enable "Less secure app access"</p>
        
        <p><b>📧 Yahoo:</b><br>
        • Server: smtp.mail.yahoo.com, Port: 587<br>
        • Generate App Password in Yahoo Account Security</p>
        """)
        
        help_layout.addWidget(help_text)
        help_group.setLayout(help_layout)
        
        # Add all groups to main layout
        layout.addWidget(smtp_group)
        layout.addWidget(presets_group)
        layout.addWidget(test_group)
        layout.addWidget(help_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def load_preset(self, provider: str):
        """Load preset configuration for email provider"""
        presets = {
            "gmail": {
                "server": "smtp.gmail.com",
                "port": 587,
                "tls": True
            },
            "outlook": {
                "server": "smtp-mail.outlook.com",
                "port": 587,
                "tls": True
            },
            "yahoo": {
                "server": "smtp.mail.yahoo.com",
                "port": 587,
                "tls": True
            }
        }
        
        if provider in presets:
            preset = presets[provider]
            self.smtp_server.setText(preset["server"])
            self.smtp_port.setValue(preset["port"])
            self.use_tls.setChecked(preset["tls"])
            
            self.test_result.setText(f"✅ {provider.title()} settings loaded. Enter your username and password, then test the connection.")
            self.test_result.setStyleSheet("color: #28a745; padding: 10px;")
    
    def test_connection(self):
        """Test SMTP connection"""
        if not self.smtp_server.text() or not self.smtp_username.text():
            self.test_result.setText("❌ Please fill in server and username fields")
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            return
        
        self.test_result.setText("🔄 Testing connection... Please wait")
        self.test_result.setStyleSheet("color: #007bff; padding: 10px;")
        
        # Simulate connection test (in real implementation, use smtp_helper)
        QTimer.singleShot(3000, self.connection_test_result)
    
    def connection_test_result(self):
        """Simulate connection test result"""
        # Mock result for prototype - in real version, this would actually test
        import random
        success = random.choice([True, True, False])  # 66% success rate for demo
        
        if success:
            self.test_result.setText("✅ Connection successful! SMTP settings are working correctly.")
            self.test_result.setStyleSheet("color: #28a745; padding: 10px;")
        else:
            self.test_result.setText("❌ Connection failed. Please check your settings and try again.\n\nCommon issues:\n• Wrong server or port\n• Incorrect username/password\n• App password required\n• Firewall blocking connection")
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")


# Continue with PictureTab and SendTab in the next part...
