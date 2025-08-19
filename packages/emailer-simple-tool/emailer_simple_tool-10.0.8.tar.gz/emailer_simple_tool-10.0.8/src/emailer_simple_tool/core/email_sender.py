"""
Email sending functionality.
Handles email composition, template processing, and sending.
"""

import os
import csv
import smtplib
import mimetypes
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional

from ..utils.credential_manager import CredentialManager
from ..utils.template_processor import TemplateProcessor
from ..utils.document_processor import DocumentProcessor
from ..utils.email_formatter import EmailFormatter
from ..utils.validators import CampaignValidator
from ..utils.logger import get_logger
from ..utils.smtp_helper import SMTPHelper
from .picture_generator import PictureGenerator


class EmailSender:
    """Handles email campaign sending and dry runs."""
    
    def __init__(self, campaign_folder: str):
        self.campaign_folder = campaign_folder
        self.logger = get_logger(__name__)
        self.credential_manager = CredentialManager(campaign_folder)
        self.template_processor = TemplateProcessor()
        self.document_processor = DocumentProcessor()
        self.email_formatter = EmailFormatter()
        self.validator = CampaignValidator()
        self.attachments_folder = os.path.join(campaign_folder, 'attachments')
        self.picture_generator = PictureGenerator(campaign_folder)
    
    def dry_run(self, custom_name: Optional[str] = None, gui_mode: bool = False) -> int:
        """Generate emails without sending them.
        
        Args:
            custom_name: Custom name for the dry run folder
            gui_mode: If True, skip interactive prompts (for GUI use)
        """
        try:
            # Load recipients and templates
            recipients = self._load_recipients()
            subject_template = self._load_template('subject.txt')
            
            # Detect and load message template (txt or docx)
            template_type, template_content, _ = self._load_message_template()
            
            # Validate templates based on type
            if template_type == 'txt':
                validation_result = self.template_processor.validate_templates(
                    subject_template, template_content, recipients[0].keys() if recipients else []
                )
            else:  # docx
                # For docx, validate using document processor
                validation_result = self.document_processor.validate_docx_template(
                    template_content, recipients[0].keys() if recipients else []
                )
            
            if not validation_result.is_valid:
                print("Template validation failed:")
                for error in validation_result.errors:
                    print(f"  ❌ {error}")
                return 1
            
            # Validate attachments
            attachment_files = []
            if os.path.exists(self.attachments_folder):
                attachment_result = self.validator.validate_attachments(self.attachments_folder)
                
                if not attachment_result.is_valid:
                    print("Attachment validation failed:")
                    for error in attachment_result.errors:
                        print(f"  ❌ {error}")
                    return 1
                
                if attachment_result.warnings:
                    print("Attachment warnings:")
                    for warning in attachment_result.warnings:
                        print(f"  ⚠️  {warning}")
                    
                    if not gui_mode:
                        response = input("Continue with dry run anyway? (y/N): ").strip().lower()
                        if response not in ['y', 'yes']:
                            print("Dry run cancelled.")
                            return 1
                    # In GUI mode, continue automatically with warnings
                
                attachment_files = attachment_result.attachment_files
            
            # Validate picture generator projects
            picture_projects = []
            pg_validation = self.picture_generator.validate_projects(recipients)
            if not pg_validation.is_valid:
                print("Picture generator validation failed:")
                for error in pg_validation.errors:
                    print(f"  ❌ {error}")
                return 1
            
            if pg_validation.warnings:
                print("Picture generator warnings:")
                for warning in pg_validation.warnings:
                    print(f"  ⚠️  {warning}")
                
                if not gui_mode:
                    response = input("Continue with dry run anyway? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("Dry run cancelled.")
                        return 1
                # In GUI mode, continue automatically with warnings
            
            # Get projects that should be attached
            for project in self.picture_generator.get_projects():
                if project.should_attach_to_email():
                    picture_projects.append(project)
            
            # Create dry run folder
            dry_run_folder = self._create_dry_run_folder(custom_name, gui_mode)
            
            # Generate emails
            generated_count = 0
            for i, recipient in enumerate(recipients):
                try:
                    # Process templates
                    subject = self.template_processor.process_template(subject_template, recipient)
                    plain_text_message, html_message = self._process_message_for_recipient(
                        template_type, template_content, recipient
                    )
                    
                    # Collect all attachments
                    all_attachments = []
                    all_attachments.extend(attachment_files)
                    
                    # Add personalized picture attachments
                    personalized_attachments = self._get_personalized_attachments(recipient, picture_projects)
                    all_attachments.extend(personalized_attachments)
                    
                    # Create rich email message
                    from_email = "noreply@example.com"  # Default sender for dry run
                    to_email = recipient.get('email', 'unknown@example.com')
                    
                    if html_message:
                        # Rich email with HTML content
                        email_msg = self.email_formatter.create_rich_email(
                            from_email=from_email,
                            to_email=to_email,
                            subject=subject,
                            html_body=html_message,
                            plain_text_body=plain_text_message,
                            attachment_files=all_attachments
                        )
                    else:
                        # Plain text email
                        email_msg = self.email_formatter.create_plain_email(
                            from_email=from_email,
                            to_email=to_email,
                            subject=subject,
                            plain_text_body=plain_text_message,
                            attachment_files=all_attachments
                        )
                    
                    # Save as .eml file
                    email_filename = f"email_{i+1:03d}_{recipient.get('email', 'unknown').replace('@', '_at_')}.eml"
                    email_path = os.path.join(dry_run_folder, email_filename)
                    
                    self.email_formatter.save_as_eml(email_msg, email_path)
                    
                    generated_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error generating email for recipient {i+1}: {e}")
                    print(f"  ❌ Error generating email for recipient {i+1}: {e}")
            
            print(f"✅ Dry run completed: {generated_count} .eml files generated in {dry_run_folder}")
            print(f"📧 You can open these .eml files with your email client to preview the formatted emails")
            if attachment_files:
                total_size = sum(os.path.getsize(f) for f in attachment_files)
                print(f"📎 Static attachments: {len(attachment_files)} files, total size: {self._format_file_size(total_size)}")
            if picture_projects:
                print(f"🖼️  Picture projects: {len(picture_projects)} projects will attach personalized images")
                for project in picture_projects:
                    print(f"   - {project.project_name}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Dry run failed: {e}")
            print(f"Error during dry run: {e}")
            return 1
    
    def send_campaign(self, gui_mode: bool = False, progress_callback=None, generate_report: bool = True) -> int:
        """Send the email campaign.
        
        Args:
            gui_mode: If True, skip interactive prompts (for GUI use)
            progress_callback: Optional callback function(current, total, message) for progress updates
            generate_report: If True, generate a JSON report after sending (default: True)
        """
        start_time = time.time()  # Track timing for report
        
        try:
            # Check SMTP credentials
            if not self.credential_manager.has_credentials():
                print("No SMTP credentials configured. Use 'emailer-simple-tool config smtp' first.")
                return 1
            
            # Load data
            recipients = self._load_recipients()
            subject_template = self._load_template('subject.txt')
            
            # Detect and load message template (txt or docx)
            template_type, template_content, _ = self._load_message_template()
            smtp_config = self.credential_manager.load_credentials()
            
            # Validate templates based on type
            if template_type == 'txt':
                validation_result = self.template_processor.validate_templates(
                    subject_template, template_content, recipients[0].keys() if recipients else []
                )
            else:  # docx
                # For docx, validate using document processor
                validation_result = self.document_processor.validate_docx_template(
                    template_content, recipients[0].keys() if recipients else []
                )
            
            if not validation_result.is_valid:
                print("Template validation failed:")
                for error in validation_result.errors:
                    print(f"  ❌ {error}")
                return 1
            
            # Validate attachments
            attachment_files = []
            if os.path.exists(self.attachments_folder):
                attachment_result = self.validator.validate_attachments(self.attachments_folder)
                
                if not attachment_result.is_valid:
                    print("Attachment validation failed:")
                    for error in attachment_result.errors:
                        print(f"  ❌ {error}")
                    return 1
                
                if attachment_result.warnings:
                    print("Attachment warnings:")
                    for warning in attachment_result.warnings:
                        print(f"  ⚠️  {warning}")
                    
                    if not gui_mode:
                        response = input("Continue with sending anyway? (y/N): ").strip().lower()
                        if response not in ['y', 'yes']:
                            print("Email sending cancelled.")
                            return 1
                    # In GUI mode, continue automatically with warnings
                
                attachment_files = attachment_result.attachment_files
            
            # Validate picture generator projects
            picture_projects = []
            pg_validation = self.picture_generator.validate_projects(recipients)
            if not pg_validation.is_valid:
                print("Picture generator validation failed:")
                for error in pg_validation.errors:
                    print(f"  ❌ {error}")
                return 1
            
            if pg_validation.warnings:
                print("Picture generator warnings:")
                for warning in pg_validation.warnings:
                    print(f"  ⚠️  {warning}")
                
                if not gui_mode:
                    response = input("Continue with sending anyway? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("Email sending cancelled.")
                        return 1
                # In GUI mode, continue automatically with warnings
            
            # Get projects that should be attached
            for project in self.picture_generator.get_projects():
                if project.should_attach_to_email():
                    picture_projects.append(project)
            
            # Show campaign summary
            print(f"Ready to send {len(recipients)} emails.")
            if attachment_files:
                total_size = sum(os.path.getsize(f) for f in attachment_files)
                print(f"📎 Static attachments: {len(attachment_files)} files, total size: {self._format_file_size(total_size)}")
                for attachment_path in attachment_files:
                    filename = os.path.basename(attachment_path)
                    file_size = os.path.getsize(attachment_path)
                    print(f"   - {filename} ({self._format_file_size(file_size)})")
            
            if picture_projects:
                print(f"🖼️  Picture projects: {len(picture_projects)} projects will attach personalized images")
                for project in picture_projects:
                    print(f"   - {project.project_name}")
            
            if not gui_mode:
                response = input("Proceed with sending? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Email sending cancelled.")
                    return 1
            # In GUI mode, proceed automatically (user already confirmed via GUI)
            
            # Send emails
            smtp_helper = SMTPHelper(smtp_config)
            sent_count = 0
            failed_count = 0
            
            print("Sending emails...")
            
            for i, recipient in enumerate(recipients, 1):
                # Update progress if callback provided
                if progress_callback:
                    progress_callback(i-1, len(recipients), f"Sending email {i}/{len(recipients)} to {recipient.get('email', 'unknown')}")
                
                try:
                    # Process templates
                    subject = self.template_processor.process_template(subject_template, recipient)
                    plain_text_message, html_message = self._process_message_for_recipient(
                        template_type, template_content, recipient
                    )
                    
                    # Get personalized attachments for this recipient
                    personalized_attachments = self._get_personalized_attachments(recipient, picture_projects)
                    all_attachments = attachment_files + personalized_attachments
                    
                    # Create email with all attachments
                    if html_message:
                        # Rich email with HTML content
                        msg = self.email_formatter.create_rich_email(
                            from_email=smtp_config['username'],
                            to_email=recipient['email'],
                            subject=subject,
                            html_body=html_message,
                            plain_text_body=plain_text_message,
                            attachment_files=all_attachments
                        )
                    else:
                        # Plain text email
                        msg = self.email_formatter.create_plain_email(
                            from_email=smtp_config['username'],
                            to_email=recipient['email'],
                            subject=subject,
                            plain_text_body=plain_text_message,
                            attachment_files=all_attachments
                        )
                    
                    # Send email
                    if smtp_helper.send_email(msg):
                        sent_count += 1
                        print(f"  ✅ Sent to {recipient['email']} ({i}/{len(recipients)})")
                    else:
                        failed_count += 1
                        print(f"  ❌ Failed to send to {recipient['email']} ({i}/{len(recipients)})")
                    
                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Error sending email to {recipient.get('email', 'unknown')}: {e}")
                    print(f"  ❌ Error sending to {recipient.get('email', 'unknown')}: {e}")
            
            # Final progress update
            if progress_callback:
                progress_callback(len(recipients), len(recipients), f"Campaign completed: {sent_count} sent, {failed_count} failed")
            
            # Calculate total time
            end_time = time.time()
            total_seconds = int(end_time - start_time)
            if total_seconds < 60:
                total_time_str = f"{total_seconds}s"
            else:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                total_time_str = f"{minutes}m{seconds}s"
            
            print(f"\nCampaign completed: {sent_count} sent, {failed_count} failed (took {total_time_str})")
            
            # Generate report if requested
            if generate_report:
                success = failed_count == 0
                message = f"{sent_count} sent, {failed_count} failed"
                self.generate_sent_report(success, message, sent_count, failed_count, total_time_str)
            
            return 0 if failed_count == 0 else 1
            
        except Exception as e:
            # Calculate total time even for errors
            end_time = time.time()
            total_seconds = int(end_time - start_time)
            if total_seconds < 60:
                total_time_str = f"{total_seconds}s"
            else:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                total_time_str = f"{minutes}m{seconds}s"
            
            self.logger.error(f"Campaign sending failed: {e}")
            print(f"Error during campaign sending: {e}")
            
            # Generate error report if requested
            if generate_report:
                self.generate_sent_report(False, f"Campaign failed: {str(e)}", 0, 0, total_time_str)
            
            return 1
    
    def _load_recipients(self) -> List[Dict[str, str]]:
        """Load recipients from CSV file."""
        recipients_file = os.path.join(self.campaign_folder, 'recipients.csv')
        recipients = []
        
        with open(recipients_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipients.append(row)
        
        return recipients
    
    def _load_template(self, filename: str) -> str:
        """Load template content from file."""
        template_file = os.path.join(self.campaign_folder, filename)
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _create_dry_run_folder(self, custom_name: Optional[str] = None, gui_mode: bool = False) -> str:
        """Create a folder for dry run output.
        
        Args:
            custom_name: Custom name for the dry run folder
            gui_mode: If True, automatically generate unique names instead of prompting
        """
        dry_run_base = os.path.join(self.campaign_folder, 'dryrun')
        
        if custom_name:
            folder_name = custom_name
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            folder_name = timestamp
        
        dry_run_folder = os.path.join(dry_run_base, folder_name)
        
        # Check if folder exists
        if os.path.exists(dry_run_folder):
            if not gui_mode:
                response = input(f"Dry run folder '{folder_name}' already exists. Replace? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    # Generate unique name
                    counter = 1
                    while os.path.exists(f"{dry_run_folder}_{counter}"):
                        counter += 1
                    dry_run_folder = f"{dry_run_folder}_{counter}"
            else:
                # In GUI mode, automatically generate unique name
                counter = 1
                while os.path.exists(f"{dry_run_folder}_{counter}"):
                    counter += 1
                dry_run_folder = f"{dry_run_folder}_{counter}"
        
        os.makedirs(dry_run_folder, exist_ok=True)
        return dry_run_folder
    
    def _create_email_with_attachments(self, from_email: str, to_email: str, 
                                     subject: str, message: str, 
                                     attachment_files: List[str]) -> MIMEMultipart:
        """Create email message with attachments."""
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Add attachments
        for attachment_path in attachment_files:
            try:
                self._attach_file(msg, attachment_path)
            except Exception as e:
                self.logger.error(f"Failed to attach file {attachment_path}: {e}")
                # Continue with other attachments
        
        return msg
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email message."""
        filename = os.path.basename(file_path)
        
        # Guess the content type based on the file's extension
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        
        maintype, subtype = ctype.split('/', 1)
        
        with open(file_path, 'rb') as fp:
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
        
        # Encode the payload using Base64
        encoders.encode_base64(attachment)
        
        # Set the filename parameter
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        
        msg.attach(attachment)
    
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
    
    def _get_personalized_attachments(self, recipient: Dict[str, str], 
                                    picture_projects: List) -> List[str]:
        """Get personalized picture attachments for a specific recipient."""
        attachments = []
        
        if not recipient:
            return attachments
        
        # Get primary key for this recipient
        primary_key_column = list(recipient.keys())[0]
        primary_key = recipient.get(primary_key_column, '').strip()
        
        if not primary_key:
            return attachments
        
        # Check each picture project
        for project in picture_projects:
            # Use new filename pattern with project name to avoid collisions
            picture_path = os.path.join(project.data_folder, f"{primary_key}-{project.project_name}.jpg")
            if os.path.exists(picture_path):
                attachments.append(picture_path)
            else:
                self.logger.warning(f"Personalized picture not found: {primary_key}-{project.project_name}.jpg")
        
        return attachments
    
    def _detect_message_template(self) -> tuple[str, str]:
        """
        Detect the message template type and path.
        
        Returns:
            Tuple of (template_type, template_path) where template_type is 'txt' or 'docx'
        """
        txt_path = os.path.join(self.campaign_folder, 'msg.txt')
        docx_path = os.path.join(self.campaign_folder, 'msg.docx')
        
        txt_exists = os.path.exists(txt_path)
        docx_exists = os.path.exists(docx_path)
        
        if txt_exists and docx_exists:
            raise ValueError("Both msg.txt and msg.docx exist. Please keep only one message template.")
        
        if docx_exists:
            return 'docx', docx_path
        elif txt_exists:
            return 'txt', txt_path
        else:
            raise FileNotFoundError("No message template found. Please provide either msg.txt or msg.docx")
    
    def _load_message_template(self) -> tuple[str, str, str]:
        """
        Load the message template and return processed content.
        
        Returns:
            Tuple of (template_type, plain_text_content, html_content)
        """
        template_type, template_path = self._detect_message_template()
        
        if template_type == 'txt':
            # Load plain text template
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return 'txt', content, None
        
        elif template_type == 'docx':
            # For docx, we'll process it per recipient, so just return the path
            return 'docx', template_path, None
        
        else:
            raise ValueError(f"Unsupported template type: {template_type}")
    
    def _process_message_for_recipient(self, template_type: str, template_content: str, 
                                     recipient_data: Dict[str, str]) -> tuple[str, str]:
        """
        Process message template for a specific recipient.
        
        Args:
            template_type: 'txt' or 'docx'
            template_content: Template content or path for docx
            recipient_data: Recipient data for substitution
            
        Returns:
            Tuple of (plain_text_message, html_message)
        """
        if template_type == 'txt':
            # Process plain text template
            plain_text = self.template_processor.process_template(template_content, recipient_data)
            return plain_text, None
        
        elif template_type == 'docx':
            # Process docx template
            processed_doc = self.document_processor.process_docx_template(template_content, recipient_data)
            
            # Convert to HTML and plain text
            html_content = self.document_processor.convert_to_html(processed_doc)
            plain_text = self.document_processor.convert_to_plain_text(processed_doc)
            
            return plain_text, html_content
        
        else:
            raise ValueError(f"Unsupported template type: {template_type}")
    
    def generate_sent_report(self, success: bool, message: str, sent_count: int = 0, failed_count: int = 0, total_time: str = "Unknown") -> bool:
        """Generate a comprehensive sent report (for CLI and GUI consistency)
        
        Args:
            success: Whether the campaign was successful
            message: Summary message
            sent_count: Number of emails sent successfully
            failed_count: Number of emails that failed
            total_time: Total time taken for the campaign
            
        Returns:
            bool: True if report was generated successfully, False otherwise
        """
        try:
            import json
            from datetime import datetime
            
            # Create sentreport folder if it doesn't exist
            reports_folder = os.path.join(self.campaign_folder, 'sentreport')
            os.makedirs(reports_folder, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = f"{timestamp}.json"
            report_path = os.path.join(reports_folder, report_filename)
            
            # Gather campaign information
            campaign_info = self._gather_campaign_info()
            
            # Create report data structure
            report_data = {
                "campaign": campaign_info,
                "execution": {
                    "timestamp": datetime.now().isoformat(),
                    "success": success,
                    "message": message
                },
                "statistics": {
                    "sent": sent_count,
                    "failed": failed_count,
                    "warnings": 0,  # Could be enhanced later
                    "total_time": total_time,
                    "send_rate": f"{sent_count + failed_count}/{total_time}" if total_time != "Unknown" else "Unknown"
                },
                "recipients": self._gather_recipient_results(sent_count, failed_count),
                "configuration": self._gather_configuration_snapshot()
            }
            
            # Write report to file
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Sent report generated: {report_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating sent report: {e}")
            print(f"⚠️  Warning: Could not generate sent report: {e}")
            return False
    
    def _gather_campaign_info(self):
        """Gather basic campaign information"""
        campaign_name = os.path.basename(self.campaign_folder) if self.campaign_folder else "Unknown"
        
        # Get subject
        try:
            subject = self._load_template('subject.txt')[:100] + "..." if len(self._load_template('subject.txt')) > 100 else self._load_template('subject.txt')
        except:
            subject = "Unknown"
        
        # Get recipient count
        try:
            recipients = self._load_recipients()
            recipient_count = len(recipients)
        except:
            recipient_count = 0
        
        return {
            "name": campaign_name,
            "folder": self.campaign_folder,
            "subject": subject,
            "total_recipients": recipient_count
        }
    
    def _gather_recipient_results(self, sent_count: int, failed_count: int):
        """Gather per-recipient results (basic implementation for CLI)"""
        try:
            recipients = self._load_recipients()
            results = []
            
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            # Mark first sent_count as sent, rest as failed
            for i, recipient in enumerate(recipients):
                status = "sent" if i < sent_count else "failed"
                smtp_response = "250 Message accepted" if status == "sent" else "Error: Send failed"
                
                results.append({
                    "email": recipient.get('email', ''),
                    "name": recipient.get('name', ''),
                    "status": status,
                    "timestamp": timestamp,
                    "smtp_response": smtp_response
                })
            
            return results
        except Exception:
            return []
    
    def _gather_configuration_snapshot(self):
        """Gather configuration snapshot for audit purposes"""
        config = {
            "message_file": None,
            "attachments": [],
            "pictures_enabled": False
        }
        
        # Check message file
        if os.path.exists(os.path.join(self.campaign_folder, 'msg.docx')):
            config["message_file"] = "msg.docx"
        elif os.path.exists(os.path.join(self.campaign_folder, 'msg.txt')):
            config["message_file"] = "msg.txt"
        
        # Check attachments
        attachments_folder = os.path.join(self.campaign_folder, 'attachments')
        if os.path.exists(attachments_folder):
            try:
                files = [f for f in os.listdir(attachments_folder) 
                        if os.path.isfile(os.path.join(attachments_folder, f)) and not f.startswith('.')]
                config["attachments"] = files
            except:
                pass
        
        # Check pictures
        pictures_folder = os.path.join(self.campaign_folder, 'picture-generator')
        if os.path.exists(pictures_folder):
            try:
                # Check if any project has attachment enabled
                for item in os.listdir(pictures_folder):
                    if os.path.isdir(os.path.join(pictures_folder, item)):
                        attach_file = os.path.join(pictures_folder, item, 'attach.txt')
                        if os.path.exists(attach_file):
                            with open(attach_file, 'r') as f:
                                content = f.read().strip().lower()
                                if content == 'true':
                                    config["pictures_enabled"] = True
                                    break
            except:
                pass
        
        return config
