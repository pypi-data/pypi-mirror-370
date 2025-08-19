"""
SMTP Tab - Email server configuration
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QGroupBox, QFormLayout, QCheckBox, QScrollArea
)
from PySide6.QtCore import QTimer, QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator


class SMTPTab(QWidget):
    """SMTP configuration tab"""
    
    def __init__(self, campaign_manager):
        super().__init__()
        self.campaign_manager = campaign_manager
        self.current_campaign_path = None
        self.init_ui()
    
    def tr(self, text: str) -> str:
        """Translate text using translation manager"""
        from ..translation_manager import translation_manager
        return translation_manager.tr(text, "SMTPTab")
    
    def refresh_translations(self):
        """Refresh all translatable UI elements when language changes"""
        # Update button texts
        if hasattr(self, 'test_button'):
            self.test_button.setText(self.tr("Test SMTP Connection"))
        if hasattr(self, 'save_button'):
            self.save_button.setText(self.tr("Save Configuration"))
        if hasattr(self, 'gmail_btn'):
            self.gmail_btn.setText(self.tr("Gmail"))
        if hasattr(self, 'outlook_btn'):
            self.outlook_btn.setText(self.tr("Outlook"))
        if hasattr(self, 'laposte_btn'):
            self.laposte_btn.setText(self.tr("La Poste"))
        
        # Update group box titles
        if hasattr(self, 'config_group'):
            self.config_group.setTitle(self.tr("📧 SMTP Server Configuration"))
        if hasattr(self, 'presets_group'):
            self.presets_group.setTitle(self.tr("⚡ Quick Setup"))
        if hasattr(self, 'test_group'):
            self.test_group.setTitle(self.tr("🧪 Connection Test"))
        if hasattr(self, 'guidance_group'):
            self.guidance_group.setTitle(self.tr("📚 Setup Guidance"))
        if hasattr(self, 'results_group'):
            self.results_group.setTitle(self.tr("🔍 Connection Test Results"))
        if hasattr(self, 'storage_group'):
            self.storage_group.setTitle(self.tr("🔒 Configuration Storage"))
        
        # Update storage content text
        if hasattr(self, 'storage_text'):
            self.storage_text.setText(self.tr("""<p><strong>How your SMTP configuration is saved:</strong></p>
        <ul>
        <li>📁 <strong>Location:</strong> Saved in your campaign folder as <code>.smtp-credentials.enc</code></li>
        <li>🔐 <strong>Security:</strong> Credentials are encrypted and never stored in plain text</li>
        <li>🚀 <strong>Portability:</strong> Configuration travels with your campaign folder</li>
        <li>🗑️ <strong>Privacy:</strong> Deleting a campaign removes all stored credentials</li>
        </ul>
        <p><em>Your email credentials are secure and only accessible to this application.</em></p>
        """))
        
        # Update checkbox text
        if hasattr(self, 'use_tls'):
            self.use_tls.setText(self.tr("Use TLS/STARTTLS (recommended)"))
        
        # Update placeholder texts
        if hasattr(self, 'smtp_server'):
            self.smtp_server.setPlaceholderText(self.tr("smtp.gmail.com"))
        if hasattr(self, 'smtp_username'):
            self.smtp_username.setPlaceholderText(self.tr("your.email@gmail.com"))
        if hasattr(self, 'smtp_password'):
            self.smtp_password.setPlaceholderText(self.tr("Your app password"))
        
        # Update test result if it has default text
        if hasattr(self, 'test_result'):
            current_text = self.test_result.text()
            if "Click 'Test SMTP Connection'" in current_text:
                self.test_result.setText(self.tr("Click 'Test SMTP Connection' to verify settings"))
        
        # Update form labels by recreating the form layout
        if hasattr(self, 'config_group'):
            # Get the current form layout
            from PySide6.QtWidgets import QFormLayout
            layout = self.config_group.layout()
            if layout and isinstance(layout, QFormLayout):
                # Update row labels - be more aggressive about translation
                for i in range(layout.rowCount()):
                    label_item = layout.itemAt(i, QFormLayout.LabelRole)
                    if label_item and label_item.widget():
                        label_widget = label_item.widget()
                        if hasattr(label_widget, 'text'):
                            current_text = label_widget.text()
                            # Always update labels regardless of current text
                            if i == 0:  # First row is SMTP Server
                                label_widget.setText(self.tr("SMTP Server:"))
                            elif i == 1:  # Second row is Port
                                label_widget.setText(self.tr("Port:"))
                            elif i == 2:  # Third row is Username
                                label_widget.setText(self.tr("Username:"))
                            elif i == 3:  # Fourth row is Password
                                label_widget.setText(self.tr("Password:"))
                            # Also check by content for robustness
                            elif "SMTP Server" in current_text or "Serveur SMTP" in current_text:
                                label_widget.setText(self.tr("SMTP Server:"))
                            elif "Port" in current_text and ":" in current_text:
                                label_widget.setText(self.tr("Port:"))
                            elif "Username" in current_text or "utilisateur" in current_text:
                                label_widget.setText(self.tr("Username:"))
                            elif "Password" in current_text or "passe" in current_text:
                                label_widget.setText(self.tr("Password:"))
        
        # Update guidance HTML content
        self.update_campaign_status()
    
    def set_campaign_path(self, campaign_path: str):
        """Set the current campaign path and load SMTP configuration"""
        self.current_campaign_path = campaign_path
        self.load_smtp_configuration()
    
    def clear_campaign(self):
        """Clear campaign-specific data"""
        self.current_campaign_path = None
        self.clear_smtp_form()
        self.update_campaign_status()
    
    def load_smtp_configuration(self):
        """Load SMTP configuration from current campaign"""
        if not self.current_campaign_path:
            self.clear_smtp_form()
            return
        
        try:
            # Load campaign and get SMTP credentials
            result = self.campaign_manager.create_or_load_campaign(self.current_campaign_path)
            
            if self.campaign_manager.credential_manager.has_credentials():
                smtp_config = self.campaign_manager.credential_manager.load_credentials()
                
                # Populate form with loaded configuration
                self.smtp_server.setText(smtp_config.get('server', ''))
                self.smtp_port.setText(str(smtp_config.get('port', 587)))
                self.smtp_username.setText(smtp_config.get('username', ''))
                # Load password from encrypted storage
                self.smtp_password.setText(smtp_config.get('password', ''))
                
                # Set TLS based on security setting
                security = smtp_config.get('security', 'tls')
                self.use_tls.setChecked(security in ['tls', 'ssl'])
                
                # Update test result to show configuration loaded
                self.test_result.setText(f"✅ SMTP configuration loaded from campaign\n📧 Server: {smtp_config.get('server', 'Unknown')}\n👤 Username: {smtp_config.get('username', 'Unknown')}\n🔐 Password: Loaded from encrypted storage")
                self.test_result.setStyleSheet("color: #28a745; padding: 10px;")
                
            else:
                self.clear_smtp_form()
                self.test_result.setText(self.tr("ℹ️ No SMTP configuration found in this campaign\nUse Quick Setup or enter settings manually"))
                self.test_result.setStyleSheet("color: #6c757d; padding: 10px;")
                
        except Exception as e:
            self.test_result.setText(self.tr("❌ Error loading SMTP configuration: {error}").format(error=str(e)))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
        
        self.update_campaign_status()
    
    def save_smtp_configuration(self, silent=True):
        """Save current SMTP configuration to campaign"""
        if not self.current_campaign_path:
            return False
        
        try:
            # Get current form values
            server = self.smtp_server.text().strip()
            port_text = self.smtp_port.text().strip()
            username = self.smtp_username.text().strip()
            password = self.smtp_password.text().strip()
            
            # Validate required fields
            if not server or not username or not password:
                return False
            
            # Validate port
            try:
                port = int(port_text) if port_text else 587
                if not (1 <= port <= 65535):
                    return False
            except ValueError:
                return False
            
            smtp_config = {
                'server': server,
                'port': port,
                'username': username,
                'password': password,
                'security': 'tls' if self.use_tls.isChecked() else 'none'
            }
            
            # Save credentials
            self.campaign_manager.credential_manager.store_credentials(smtp_config)
            
            if not silent:
                print(f"SMTP configuration saved for campaign: {os.path.basename(self.current_campaign_path)}")
            
            return True
            
        except Exception as e:
            if not silent:
                print(f"Error saving SMTP configuration: {e}")
            return False
    
    def clear_smtp_form(self):
        """Clear all SMTP form fields"""
        self.smtp_server.setText('')
        self.smtp_port.setText('587')
        self.smtp_username.setText('')
        self.smtp_password.setText('')
        self.use_tls.setChecked(True)
    
    def update_campaign_status(self):
        """Update the guidance text based on campaign status"""
        if self.current_campaign_path:
            campaign_name = os.path.basename(self.current_campaign_path)
            guidance_html = self.tr("""<h3>📧 SMTP Configuration Help</h3>
            <p><strong>Current Campaign:</strong> {campaign_name}</p>
            <p><strong>💾 Auto-Save:</strong> Configuration is automatically saved when you fill all required fields (server, username, password).</p>
            <p><strong>Quick Setup:</strong> Use the buttons on the left for popular email providers.</p>
            <ul>
            <li><strong>Gmail:</strong> Requires app password (not your regular password)</li>
            <li><strong>Outlook:</strong> Use your Microsoft account credentials</li>
            <li><strong>La Poste:</strong> Use your La Poste email credentials</li>
            </ul>
            <p><strong>Manual Setup:</strong> Enter your email provider's SMTP settings manually.</p>
            <p><strong>Security:</strong> Always use TLS/STARTTLS for secure connections.</p>
            <p><em>💾 Use 'Save Configuration' button to save manually, or 'Test SMTP Connection' to test and save.</em></p>
            """).format(campaign_name=campaign_name)
        else:
            guidance_html = self.tr("""<h3>📧 SMTP Configuration Help</h3>
            <p><strong>⚠️ No Campaign Loaded:</strong> Please select a campaign folder first.</p>
            <p>You can test SMTP connections, but settings won't be saved without a campaign.</p>
            <ul>
            <li><strong>Gmail:</strong> Requires app password (not your regular password)</li>
            <li><strong>Outlook:</strong> Use your Microsoft account credentials</li>
            <li><strong>La Poste:</strong> Use your La Poste email credentials</li>
            </ul>
            <p><strong>To save settings:</strong> Go to Campaign tab and select a folder first.</p>
            """)
        
        self.guidance_text.setHtml(guidance_html)
    
    def save_configuration_manually(self):
        """Save SMTP configuration manually (triggered by Save button)"""
        if not self.current_campaign_path:
            self.test_result.setText(self.tr("⚠️ No campaign loaded - cannot save configuration\n\nPlease load a campaign first from the Campaign tab."))
            self.test_result.setStyleSheet("color: #ffc107; padding: 10px;")
            return
        
        if self.save_smtp_configuration():
            self.test_result.setText(self.tr("✅ Configuration saved successfully!\n\n💾 SMTP settings have been saved to the campaign folder."))
            self.test_result.setStyleSheet("color: #28a745; padding: 10px;")
        else:
            self.test_result.setText(self.tr("❌ Failed to save configuration\n\nPlease check that all required fields are filled."))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
    
    def on_field_changed(self):
        """Auto-save when fields change (if campaign is loaded and fields are valid)"""
        if not self.current_campaign_path:
            return  # Don't auto-save if no campaign loaded
        
        # Check if we have minimum required fields for auto-save
        if (self.smtp_server.text().strip() and 
            self.smtp_username.text().strip() and 
            self.smtp_password.text().strip()):
            
            # Auto-save silently (don't update test result for auto-save)
            self.save_smtp_configuration()
    
    def init_ui(self):
        """Initialize SMTP tab UI"""
        main_layout = QHBoxLayout()
        
        # Left panel: Configuration (with scroll area)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # SMTP Configuration form
        self.config_group = QGroupBox(self.tr("📧 SMTP Server Configuration"))
        smtp_layout = QFormLayout()
        
        # Server settings
        self.smtp_server = QLineEdit()
        self.smtp_server.setPlaceholderText(self.tr("smtp.gmail.com"))
        
        self.smtp_port = QLineEdit()
        self.smtp_port.setPlaceholderText("587")
        self.smtp_port.setText("587")
        # Add numeric validator for port (1-65535)
        port_validator = QRegularExpressionValidator(QRegularExpression(r"^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"))
        self.smtp_port.setValidator(port_validator)
        
        self.smtp_username = QLineEdit()
        self.smtp_username.setPlaceholderText(self.tr("your.email@gmail.com"))
        
        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_password.setPlaceholderText(self.tr("Your app password"))
        
        self.use_tls = QCheckBox(self.tr("Use TLS/STARTTLS (recommended)"))
        self.use_tls.setChecked(True)
        
        # Add fields to form
        smtp_layout.addRow(self.tr("SMTP Server:"), self.smtp_server)
        smtp_layout.addRow(self.tr("Port:"), self.smtp_port)
        smtp_layout.addRow(self.tr("Username:"), self.smtp_username)
        smtp_layout.addRow(self.tr("Password:"), self.smtp_password)
        smtp_layout.addRow("", self.use_tls)
        
        # Connect field change signals for auto-save
        self.smtp_server.textChanged.connect(self.on_field_changed)
        self.smtp_port.textChanged.connect(self.on_field_changed)
        self.smtp_username.textChanged.connect(self.on_field_changed)
        self.smtp_password.textChanged.connect(self.on_field_changed)
        self.use_tls.toggled.connect(self.on_field_changed)
        
        self.config_group.setLayout(smtp_layout)
        
        # Quick setup presets
        self.presets_group = QGroupBox(self.tr("⚡ Quick Setup"))
        presets_layout = QVBoxLayout()
        
        self.gmail_btn = QPushButton(self.tr("Gmail"))
        self.gmail_btn.clicked.connect(lambda: self.load_preset("gmail"))
        self.gmail_btn.setStyleSheet("QPushButton { background-color: #dc3545; }")
        
        self.outlook_btn = QPushButton(self.tr("Outlook"))
        self.outlook_btn.clicked.connect(lambda: self.load_preset("outlook"))
        self.outlook_btn.setStyleSheet("QPushButton { background-color: #0078d4; }")
        
        self.laposte_btn = QPushButton(self.tr("La Poste"))
        self.laposte_btn.clicked.connect(lambda: self.load_preset("laposte"))
        self.laposte_btn.setStyleSheet("QPushButton { background-color: #ff6b35; }")
        
        presets_layout.addWidget(self.gmail_btn)
        presets_layout.addWidget(self.outlook_btn)
        presets_layout.addWidget(self.laposte_btn)
        
        self.presets_group.setLayout(presets_layout)
        
        # Connection test and save
        self.test_group = QGroupBox(self.tr("🧪 Connection Test"))
        test_layout = QVBoxLayout()
        
        # Test connection button
        self.test_button = QPushButton(self.tr("Test SMTP Connection"))
        self.test_button.clicked.connect(self.test_connection)
        self.test_button.setStyleSheet("QPushButton { background-color: #28a745; }")
        
        # Save configuration button
        self.save_button = QPushButton(self.tr("Save Configuration"))
        self.save_button.clicked.connect(self.save_configuration_manually)
        self.save_button.setStyleSheet("QPushButton { background-color: #007bff; }")
        
        test_layout.addWidget(self.test_button)
        test_layout.addWidget(self.save_button)
        self.test_group.setLayout(test_layout)
        
        # Add all groups to left panel
        left_layout.addWidget(self.config_group)
        left_layout.addWidget(self.presets_group)
        left_layout.addWidget(self.test_group)
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        left_scroll.setWidget(left_panel)
        
        # Right panel: Guidance and Help (with scroll area)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Guidance section
        self.guidance_group = QGroupBox(self.tr("📚 Setup Guidance"))
        guidance_layout = QVBoxLayout()
        
        self.guidance_text = QTextEdit()
        self.guidance_text.setReadOnly(True)
        self.guidance_text.setMaximumHeight(200)
        self.guidance_text.setHtml(self.tr("""<h3>📧 SMTP Configuration Help</h3>
        <p><strong>Quick Setup:</strong> Use the buttons on the left for popular email providers.</p>
        <ul>
        <li><strong>Gmail:</strong> Requires app password (not your regular password)</li>
        <li><strong>Outlook:</strong> Use your Microsoft account credentials</li>
        <li><strong>La Poste:</strong> Use your La Poste email credentials</li>
        </ul>
        <p><strong>Manual Setup:</strong> Enter your email provider's SMTP settings manually.</p>
        <p><strong>Security:</strong> Always use TLS/STARTTLS for secure connections.</p>
        """))
        
        guidance_layout.addWidget(self.guidance_text)
        self.guidance_group.setLayout(guidance_layout)
        
        # Test results section
        self.results_group = QGroupBox(self.tr("🔍 Connection Test Results"))
        results_layout = QVBoxLayout()
        
        self.test_result = QLabel(self.tr("Click 'Test SMTP Connection' to verify settings"))
        self.test_result.setStyleSheet("color: #6c757d; padding: 10px;")
        self.test_result.setWordWrap(True)
        self.test_result.setMinimumHeight(100)
        
        results_layout.addWidget(self.test_result)
        self.results_group.setLayout(results_layout)
        
        # Configuration storage explanation
        self.storage_group = QGroupBox(self.tr("🔒 Configuration Storage"))
        storage_layout = QVBoxLayout()
        
        storage_text = QLabel(self.tr("""<p><strong>How your SMTP configuration is saved:</strong></p>
        <ul>
        <li>📁 <strong>Location:</strong> Saved in your campaign folder as <code>.smtp-credentials.enc</code></li>
        <li>🔐 <strong>Security:</strong> Credentials are encrypted and never stored in plain text</li>
        <li>🚀 <strong>Portability:</strong> Configuration travels with your campaign folder</li>
        <li>🗑️ <strong>Privacy:</strong> Deleting a campaign removes all stored credentials</li>
        </ul>
        <p><em>Your email credentials are secure and only accessible to this application.</em></p>
        """))
        storage_text.setWordWrap(True)
        storage_text.setStyleSheet("color: #495057; padding: 10px;")
        
        # Store reference for refresh_translations
        self.storage_text = storage_text
        
        storage_layout.addWidget(storage_text)
        self.storage_group.setLayout(storage_layout)
        
        # Add all groups to right panel
        right_layout.addWidget(self.guidance_group)
        right_layout.addWidget(self.results_group)
        right_layout.addWidget(self.storage_group)
        right_layout.addStretch()
        
        right_panel.setLayout(right_layout)
        right_scroll.setWidget(right_panel)
        
        # Add scroll areas to main layout (60% left, 40% right)
        main_layout.addWidget(left_scroll, 3)  # 60%
        main_layout.addWidget(right_scroll, 2)  # 40%
        
        self.setLayout(main_layout)
    
    def load_preset(self, provider: str):
        """Load preset configuration for email provider"""
        presets = {
            "gmail": {"server": self.tr("smtp.gmail.com"), "port": 587, "tls": True},
            "outlook": {"server": "smtp-mail.outlook.com", "port": 587, "tls": True},
            "laposte": {"server": "smtp.laposte.net", "port": 587, "tls": True}
        }
        
        if provider in presets:
            preset = presets[provider]
            self.smtp_server.setText(preset["server"])
            self.smtp_port.setText(str(preset["port"]))
            self.use_tls.setChecked(preset["tls"])
            
            self.test_result.setText(self.tr("✅ {provider} settings loaded").format(provider=provider.title()))
            self.test_result.setStyleSheet("color: #28a745; padding: 10px;")
    
    def test_connection(self):
        """Test SMTP connection with comprehensive validation"""
        # Check if campaign is loaded
        if not self.current_campaign_path:
            self.test_result.setText(self.tr("⚠️ No campaign loaded - settings will not be saved\n\nYou can test the connection, but configuration won't be saved without a campaign folder.\nGo to Campaign tab and select a folder first."))
            self.test_result.setStyleSheet("color: #ffc107; padding: 10px;")
            
            # Ask user if they want to continue
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 
                self.tr("No Campaign Loaded"),
                self.tr("No campaign is currently loaded. You can test the SMTP connection, but the settings won't be saved.\n\nDo you want to continue with the test?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                self.test_result.setText(self.tr("Test cancelled - Please load a campaign first"))
                self.test_result.setStyleSheet("color: #6c757d; padding: 10px;")
                return
        
        self.test_result.setText(self.tr("🔄 Testing connection..."))
        self.test_result.setStyleSheet("color: #007bff; padding: 10px;")
        
        # Get configuration values
        server = self.smtp_server.text().strip()
        port_text = self.smtp_port.text().strip()
        username = self.smtp_username.text().strip()
        password = self.smtp_password.text().strip()
        use_tls = self.use_tls.isChecked()
        
        # Validate inputs
        if not server:
            self.test_result.setText(self.tr("❌ Please enter SMTP server"))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            return
            
        if not port_text:
            self.test_result.setText(self.tr("❌ Please enter port number"))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            return
            
        try:
            port = int(port_text)
            if not (1 <= port <= 65535):
                raise ValueError("Port out of range")
        except ValueError:
            self.test_result.setText(self.tr("❌ Invalid port number (must be 1-65535)"))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            return
            
        if not username:
            self.test_result.setText(self.tr("❌ Please enter username/email"))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            return
            
        if not password:
            self.test_result.setText(self.tr("❌ Please enter password"))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            return
        
        # Perform actual SMTP test
        self._perform_smtp_test(server, port, username, password, use_tls)
    
    def _perform_smtp_test(self, server, port, username, password, use_tls):
        """Perform the actual SMTP connection test"""
        import smtplib
        import socket
        from email.mime.text import MIMEText
        
        try:
            # Step 1: TCP connection test
            self.test_result.setText(self.tr("🔄 Step 1/3: Testing TCP connection..."))
            
            # Test basic TCP connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result != 0:
                self.test_result.setText(self.tr("❌ Cannot connect to {server}:{port}\nCheck server address and port number.").format(server=server, port=port))
                self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
                return
            
            # Step 2: SMTP connection and TLS test
            self.test_result.setText(self.tr("🔄 Step 2/3: Testing SMTP connection and TLS..."))
            
            if use_tls:
                smtp = smtplib.SMTP(server, port, timeout=10)
                smtp.starttls()
            else:
                smtp = smtplib.SMTP(server, port, timeout=10)
            
            # Step 3: Authentication test
            self.test_result.setText(self.tr("🔄 Step 3/3: Testing authentication..."))
            
            smtp.login(username, password)
            smtp.quit()
            
            # Success!
            tls_status = self.tr("with TLS") if use_tls else self.tr("without TLS")
            success_message = f"""✅ Connection successful!
            
📧 Server: {server}:{port}
🔐 Authentication: Verified
🛡️ Security: {tls_status}
👤 Username: {username}

Your SMTP configuration is working correctly."""
            
            # Save configuration if campaign is loaded
            if self.current_campaign_path:
                if self.save_smtp_configuration(silent=False):
                    success_message += self.tr("\n\n💾 Configuration saved to campaign folder.")
                else:
                    success_message += self.tr("\n\n⚠️ Configuration tested successfully but could not be saved.")
            else:
                success_message += self.tr("\n\n⚠️ Configuration not saved (no campaign loaded).")
            
            self.test_result.setText(success_message)
            self.test_result.setStyleSheet("color: #28a745; padding: 10px;")
            
        except smtplib.SMTPAuthenticationError as e:
            self.test_result.setText(f"""❌ Authentication failed
            
The server rejected your username/password.

💡 Common solutions:
• For Gmail: Use an App Password (not your regular password)
• For Outlook: Check if 2FA is enabled
• For La Poste: Verify your email credentials
• Check for typos in username/password

Error details: {str(e)}""")
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            
        except smtplib.SMTPConnectError as e:
            self.test_result.setText(f"""❌ Connection failed
            
Cannot establish SMTP connection.

💡 Possible causes:
• Incorrect server address or port
• Firewall blocking the connection
• Server temporarily unavailable

Error details: {str(e)}""")
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            
        except smtplib.SMTPException as e:
            self.test_result.setText(f"""❌ SMTP error
            
An SMTP protocol error occurred.

💡 Try:
• Check if TLS is required/supported
• Verify server settings with your email provider

Error details: {str(e)}""")
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            
        except socket.timeout:
            self.test_result.setText(f"""❌ Connection timeout
            
The server did not respond within 10 seconds.

💡 Possible causes:
• Server is overloaded or down
• Network connectivity issues
• Firewall blocking the connection""")
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
            
        except Exception as e:
            self.test_result.setText(self.tr("❌ Unexpected error\n\nAn unexpected error occurred during testing.\n\nError details: {error}\n\n💡 Please check your network connection and try again.").format(error=str(e)))
            self.test_result.setStyleSheet("color: #dc3545; padding: 10px;")
