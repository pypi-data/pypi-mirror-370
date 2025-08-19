"""
Campaign management functionality.
Handles campaign creation, loading, and SMTP configuration.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..utils.validators import validate_campaign_folder
from ..utils.credential_manager import CredentialManager
from ..utils.logger import get_logger
from ..utils.smtp_helper import SMTPHelper
from .picture_generator import PictureGenerator
from ..utils.global_config import GlobalConfig


class CampaignManager:
    """Manages email campaigns and their configurations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.global_config = GlobalConfig()
        self.active_campaign_folder: Optional[str] = None
        self.campaign_config: Optional[Dict[str, Any]] = None
        self.credential_manager: Optional[CredentialManager] = None
        self.picture_generator: Optional[PictureGenerator] = None
        
        # Try to load active campaign from global config first
        self._load_active_campaign()
        
        # If no active campaign, try to auto-detect in current directory
        if not self.active_campaign_folder:
            self._try_auto_detect_campaign()
    
    
    def _load_active_campaign(self):
        """Load active campaign from global configuration."""
        campaign_path = self.global_config.get_active_campaign()
        if campaign_path:
            # Validate that the campaign is still valid
            validation_result = validate_campaign_folder(campaign_path)
            if validation_result.is_valid:
                self.active_campaign_folder = campaign_path
                self.credential_manager = CredentialManager(campaign_path)
                self.picture_generator = PictureGenerator(campaign_path)
                self._load_campaign_config()
            else:
                # Campaign is no longer valid, clear it from global config
                self.global_config.clear_active_campaign()
    
    def _try_auto_detect_campaign(self):
        """Try to auto-detect campaign in current directory."""
        current_dir = os.getcwd()
        
        # Check if current directory has campaign files
        required_files = ['recipients.csv', 'msg.txt', 'subject.txt']
        has_all_files = all(os.path.exists(os.path.join(current_dir, f)) for f in required_files)
        
        if has_all_files:
            # Validate the campaign folder
            validation_result = validate_campaign_folder(current_dir)
            if validation_result.is_valid:
                self.active_campaign_folder = current_dir
                self.credential_manager = CredentialManager(current_dir)
                self.picture_generator = PictureGenerator(current_dir)
                self._load_campaign_config()
    
    def create_or_load_campaign(self, folder_path: str, gui_mode: bool = False) -> int:
        """Create or load a campaign from the specified folder.
        
        Args:
            folder_path: Path to the campaign folder
            gui_mode: If True, skip interactive prompts (for GUI usage)
        """
        folder_path = os.path.abspath(folder_path)
        
        if not os.path.exists(folder_path):
            if not gui_mode:
                print(f"Error: Folder '{folder_path}' does not exist.")
            return 1
        
        # Validate campaign folder structure
        validation_result = validate_campaign_folder(folder_path)
        if not validation_result.is_valid:
            if not gui_mode:
                print("Campaign folder validation failed:")
                for error in validation_result.errors:
                    print(f"  ❌ {error}")
                
                if validation_result.warnings:
                    print("\nWarnings:")
                    for warning in validation_result.warnings:
                        print(f"  ⚠️  {warning}")
            
            return 1
        
        # Show warnings if any
        if validation_result.warnings:
            if not gui_mode:
                print("Warnings found:")
                for warning in validation_result.warnings:
                    print(f"  ⚠️  {warning}")
                
                response = input("Continue anyway? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Campaign loading cancelled.")
                    return 1
            # In GUI mode, warnings are handled by the GUI, so we continue
        
        # Load campaign (only after successful validation)
        self.active_campaign_folder = folder_path
        self.credential_manager = CredentialManager(folder_path)
        self.picture_generator = PictureGenerator(folder_path)
        
        # Save to global config for persistence between CLI invocations
        self.global_config.set_active_campaign(folder_path)
        
        # Create necessary directories
        self._ensure_campaign_directories()
        
        # Load or create campaign config
        self._load_campaign_config()
        
        print(f"✅ Campaign loaded successfully: {folder_path}")
        return 0
    
    def configure_smtp(self, gui_mode: bool = False) -> int:
        """Configure SMTP settings for the active campaign.
        
        Args:
            gui_mode: If True, skip interactive prompts (for GUI usage)
        """
        if not self.has_active_campaign():
            if not gui_mode:
                print("No active campaign. Use 'emailer-simple-tool config create <folder>' first.")
            return 1
        
        if not gui_mode:
            print("SMTP Configuration")
            print("=" * 50)
        
        # Get SMTP settings from user
        smtp_config = self._get_smtp_config_from_user(gui_mode)
        
        # Test SMTP connection
        smtp_helper = SMTPHelper(smtp_config)
        if not smtp_helper.test_connection():
            if not gui_mode:
                print("SMTP connection test failed.")
                response = input("Save configuration anyway? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("SMTP configuration cancelled.")
                    return 1
            else:
                # In GUI mode, return error code to let GUI handle the failure
                return 2  # Special code for connection test failure
        
        # Save credentials
        self.credential_manager.store_credentials(smtp_config)
        print("✅ SMTP configuration saved successfully.")
        return 0
    
    def show_configuration(self) -> int:
        """Show current campaign configuration."""
        if not self.has_active_campaign():
            print("No active campaign loaded.")
            return 1
        
        print("Current Campaign Configuration")
        print("=" * 50)
        print(f"Campaign Folder: {self.active_campaign_folder}")
        
        # Show SMTP status
        if self.credential_manager.has_credentials():
            smtp_config = self.credential_manager.load_credentials()
            print(f"SMTP Server: {smtp_config.get('server', 'Not configured')}")
            print(f"SMTP Port: {smtp_config.get('port', 'Not configured')}")
            print(f"Username: {smtp_config.get('username', 'Not configured')}")
            print("Password: *** (configured)")
        else:
            print("SMTP: Not configured")
        
        # Show campaign files status
        recipients_file = os.path.join(self.active_campaign_folder, 'recipients.csv')
        subject_file = os.path.join(self.active_campaign_folder, 'subject.txt')
        attachments_folder = os.path.join(self.active_campaign_folder, 'attachments')
        
        # Check for message file (both .txt and .docx)
        msg_txt = os.path.join(self.active_campaign_folder, 'msg.txt')
        msg_docx = os.path.join(self.active_campaign_folder, 'msg.docx')
        has_message_file = os.path.exists(msg_txt) or os.path.exists(msg_docx)
        
        # Show which message file type is present
        if os.path.exists(msg_docx) and os.path.exists(msg_txt):
            message_status = "⚠️  Both msg.txt and msg.docx exist"
        elif os.path.exists(msg_docx):
            message_status = "✅ msg.docx"
        elif os.path.exists(msg_txt):
            message_status = "✅ msg.txt"
        else:
            message_status = "❌"
        
        print(f"Recipients file: {'✅' if os.path.exists(recipients_file) else '❌'}")
        print(f"Message file: {message_status}")
        print(f"Subject file: {'✅' if os.path.exists(subject_file) else '❌'}")
        
        # Show attachment status
        if os.path.exists(attachments_folder) and os.path.isdir(attachments_folder):
            attachment_files = [f for f in os.listdir(attachments_folder) 
                              if os.path.isfile(os.path.join(attachments_folder, f))]
            if attachment_files:
                total_size = sum(os.path.getsize(os.path.join(attachments_folder, f)) 
                               for f in attachment_files)
                print(f"Attachments: ✅ {len(attachment_files)} files ({self._format_file_size(total_size)})")
                for filename in attachment_files[:5]:  # Show first 5 files
                    file_path = os.path.join(attachments_folder, filename)
                    file_size = os.path.getsize(file_path)
                    print(f"  - {filename} ({self._format_file_size(file_size)})")
                if len(attachment_files) > 5:
                    print(f"  ... and {len(attachment_files) - 5} more files")
            else:
                print("Attachments: ⚠️  Folder exists but empty")
        else:
            print("Attachments: ❌ No attachments folder")
        
        # Show picture generator projects
        if self.picture_generator:
            projects = self.picture_generator.get_projects()
            if projects:
                print(f"\nPicture Generator Projects ({len(projects)}):")
                
                # Load recipients for consistency check
                recipients = self._load_recipients_for_validation()
                
                for project in projects:
                    validation_result = project.is_valid()
                    consistency_result = self.picture_generator._check_data_consistency(project, recipients)
                    
                    status_icon = "✅" if validation_result.is_valid and consistency_result.is_valid else "❌"
                    attach_status = "📎" if project.should_attach_to_email() else "📋"
                    
                    print(f"  {status_icon} {attach_status} {project.project_name}")
                    
                    if not validation_result.is_valid:
                        for error in validation_result.errors:
                            print(f"    ❌ {error}")
                    
                    if consistency_result.warnings:
                        for warning in consistency_result.warnings:
                            print(f"    ⚠️  {warning}")
            else:
                print("\nPicture Generator Projects: ❌ No projects found")
        
        return 0
    
    def has_active_campaign(self) -> bool:
        """Check if there's an active campaign loaded."""
        return self.active_campaign_folder is not None
    
    def get_active_campaign(self) -> str:
        """Get the active campaign folder path."""
        return self.active_campaign_folder
    
    def _ensure_campaign_directories(self):
        """Create necessary directories in the campaign folder."""
        directories = ['logs', 'dryrun']
        
        for directory in directories:
            dir_path = os.path.join(self.active_campaign_folder, directory)
            os.makedirs(dir_path, exist_ok=True)
    
    def _load_campaign_config(self):
        """Load or create campaign configuration."""
        config_file = os.path.join(self.active_campaign_folder, '.emailer-config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.campaign_config = json.load(f)
        else:
            self.campaign_config = {
                'version': '1.0.0',
                'log_level': 'INFO',
                'created_at': None
            }
            self._save_campaign_config()
    
    def _save_campaign_config(self):
        """Save campaign configuration to file."""
        config_file = os.path.join(self.active_campaign_folder, '.emailer-config.json')
        
        with open(config_file, 'w') as f:
            json.dump(self.campaign_config, f, indent=2)
    
    def _get_smtp_config_from_user(self, gui_mode: bool = False) -> Dict[str, Any]:
        """Get SMTP configuration from user input.
        
        Args:
            gui_mode: If True, return empty config (GUI will handle configuration)
        """
        if gui_mode:
            # In GUI mode, return empty config - GUI will handle SMTP configuration
            return {}
        
        print("\nSMTP Configuration Options:")
        print("1. Quick Setup (Gmail, Outlook, La Poste)")
        print("2. Manual Configuration")
        
        while True:
            choice = input("Choose configuration method (1-2): ").strip()
            if choice in ['1', '2']:
                break
            print("❌ Please choose 1 or 2.")
        
        if choice == '1':
            return self._get_preset_config()
        else:
            return self._get_manual_config()
    
    def _get_preset_config(self) -> Dict[str, Any]:
        """Get SMTP configuration using presets."""
        print("\nQuick Setup - Choose your email provider:")
        print("1. Gmail (smtp.gmail.com:587)")
        print("2. Outlook (smtp-mail.outlook.com:587)")
        print("3. La Poste (smtp.laposte.net:587)")
        print("4. Manual configuration")
        
        presets = {
            '1': {'server': 'smtp.gmail.com', 'port': 587, 'security': 'tls', 'name': 'Gmail'},
            '2': {'server': 'smtp-mail.outlook.com', 'port': 587, 'security': 'tls', 'name': 'Outlook'},
            '3': {'server': 'smtp.laposte.net', 'port': 587, 'security': 'tls', 'name': 'La Poste'}
        }
        
        while True:
            preset_choice = input("Choose provider (1-4): ").strip()
            if preset_choice in presets:
                preset = presets[preset_choice]
                print(f"\n✅ Using {preset['name']} settings:")
                print(f"   Server: {preset['server']}")
                print(f"   Port: {preset['port']}")
                print(f"   Security: {preset['security'].upper()}")
                break
            elif preset_choice == '4':
                return self._get_manual_config()
            else:
                print("❌ Please choose 1, 2, 3, or 4.")
        
        # Get username and password for the preset
        while True:
            username = input(f"\n{preset['name']} Username/Email: ").strip()
            if username:
                break
            print("❌ Username cannot be empty. Please enter your email or username.")
        
        # Provider-specific guidance
        if preset_choice == '1':  # Gmail
            print("\n💡 Gmail Setup Tips:")
            print("   • Use an App Password (not your regular Gmail password)")
            print("   • Enable 2-Factor Authentication first")
            print("   • Generate App Password at: https://myaccount.google.com/apppasswords")
        elif preset_choice == '2':  # Outlook
            print("\n💡 Outlook Setup Tips:")
            print("   • Use your Microsoft account password")
            print("   • If 2FA is enabled, you may need an app password")
        elif preset_choice == '3':  # La Poste
            print("\n💡 La Poste Setup Tips:")
            print("   • Use your La Poste email credentials")
            print("   • Make sure SMTP access is enabled in your account settings")
        
        # Hide password input with validation
        import getpass
        while True:
            password = getpass.getpass("Password: ")
            if password:
                break
            print("❌ Password cannot be empty. Please enter your password.")
        
        return {
            'server': preset['server'],
            'port': preset['port'],
            'username': username,
            'password': password,
            'security': preset['security']
        }
    
    def _get_manual_config(self) -> Dict[str, Any]:
        """Get SMTP configuration manually."""
        print("\nEnter SMTP server details:")
        
        # Get server with validation
        while True:
            server = input("SMTP Server (e.g., smtp.gmail.com): ").strip()
            if server:
                break
            print("❌ Server address cannot be empty. Please enter a valid SMTP server.")
        
        # Get port with validation
        while True:
            port_input = input("SMTP Port (587 for TLS, 465 for SSL, 25 for plain): ").strip()
            if not port_input:
                port = 587  # Default to 587
                break
            elif port_input.isdigit():
                port = int(port_input)
                if 1 <= port <= 65535:
                    break
                else:
                    print("❌ Port must be between 1 and 65535.")
            else:
                print("❌ Port must be a number.")
        
        # Get username with validation
        while True:
            username = input("Username/Email: ").strip()
            if username:
                break
            print("❌ Username cannot be empty. Please enter your email or username.")
        
        # Hide password input with validation
        import getpass
        while True:
            password = getpass.getpass("Password: ")
            if password:
                break
            print("❌ Password cannot be empty. Please enter your password.")
        
        # Security type
        print("\nSecurity options:")
        print("1. TLS (recommended)")
        print("2. SSL")
        print("3. None (not recommended)")
        
        while True:
            security_choice = input("Choose security type (1-3): ").strip()
            security_map = {'1': 'tls', '2': 'ssl', '3': 'none'}
            if security_choice in security_map:
                security = security_map[security_choice]
                break
            else:
                print("❌ Please choose 1, 2, or 3.")
        
        return {
            'server': server,
            'port': port,
            'username': username,
            'password': password,
            'security': security
        }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def run_picture_generator(self, project_name: Optional[str] = None) -> int:
        """Run picture generator for a specific project."""
        if not self.has_active_campaign():
            print("No active campaign. Use 'emailer-simple-tool config create <folder>' first.")
            return 1
        
        if not self.picture_generator:
            print("Picture generator not initialized.")
            return 1
        
        # Get available projects
        projects = self.picture_generator.get_projects()
        if not projects:
            print("No picture generator projects found.")
            print("Create a project folder in 'picture-generator/' with template.jpg and fusion.csv")
            return 1
        
        # Select project
        if project_name:
            selected_project = next((p for p in projects if p.project_name == project_name), None)
            if not selected_project:
                print(f"Project '{project_name}' not found.")
                print(f"Available projects: {', '.join(p.project_name for p in projects)}")
                return 1
        else:
            # Interactive selection
            if len(projects) == 1:
                selected_project = projects[0]
                print(f"Using project: {selected_project.project_name}")
            else:
                print("Available picture generator projects:")
                for i, project in enumerate(projects, 1):
                    status = "✅" if project.is_valid().is_valid else "❌"
                    attach = "📎" if project.should_attach_to_email() else "📋"
                    print(f"  {i}. {status} {attach} {project.project_name}")
                
                try:
                    choice = int(input("Select project (number): ")) - 1
                    if 0 <= choice < len(projects):
                        selected_project = projects[choice]
                    else:
                        print("Invalid selection.")
                        return 1
                except (ValueError, KeyboardInterrupt):
                    print("Selection cancelled.")
                    return 1
        
        # Load recipients
        recipients = self._load_recipients_for_validation()
        if not recipients:
            print("No recipients found. Make sure recipients.csv exists and has data.")
            return 1
        
        # Generate pictures
        print(f"\nGenerating pictures for project: {selected_project.project_name}")
        return self.picture_generator.generate_pictures(selected_project.project_name, recipients)
    
    def _load_recipients_for_validation(self) -> List[Dict[str, str]]:
        """Load recipients for validation purposes."""
        recipients_file = os.path.join(self.active_campaign_folder, 'recipients.csv')
        recipients = []
        
        if not os.path.exists(recipients_file):
            return recipients
        
        try:
            import csv
            with open(recipients_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    recipients.append(row)
        except Exception as e:
            self.logger.error(f"Error loading recipients: {e}")
        
        return recipients
