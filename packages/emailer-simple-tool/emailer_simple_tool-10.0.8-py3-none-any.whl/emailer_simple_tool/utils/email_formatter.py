"""
Email formatting utilities for generating .eml files with rich content.
"""

import os
import base64
import mimetypes
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional

from .logger import get_logger


class EmailFormatter:
    """Formats emails with rich content and generates .eml files."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_rich_email(self, 
                         from_email: str,
                         to_email: str, 
                         subject: str,
                         html_body: str,
                         plain_text_body: str,
                         attachment_files: List[str] = None) -> MIMEMultipart:
        """
        Create a rich email message with HTML and plain text versions.
        
        Args:
            from_email: Sender email address
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML formatted body content
            plain_text_body: Plain text version of body
            attachment_files: List of file paths to attach
            
        Returns:
            MIMEMultipart email message
        """
        # Create multipart message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Create plain text and HTML parts
        text_part = MIMEText(plain_text_body, 'plain', 'utf-8')
        html_part = MIMEText(html_body, 'html', 'utf-8')
        
        # Add both parts to message
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachment_files:
            # Convert to mixed multipart to support attachments
            mixed_msg = MIMEMultipart('mixed')
            mixed_msg['From'] = from_email
            mixed_msg['To'] = to_email
            mixed_msg['Subject'] = subject
            mixed_msg['Date'] = msg['Date']
            
            # Add the alternative part (text + html)
            mixed_msg.attach(msg)
            
            # Add attachments
            for attachment_path in attachment_files:
                try:
                    self._attach_file(mixed_msg, attachment_path)
                except Exception as e:
                    self.logger.error(f"Failed to attach file {attachment_path}: {e}")
            
            return mixed_msg
        
        return msg
    
    def create_plain_email(self,
                          from_email: str,
                          to_email: str,
                          subject: str,
                          plain_text_body: str,
                          attachment_files: List[str] = None) -> MIMEMultipart:
        """
        Create a plain text email message.
        
        Args:
            from_email: Sender email address
            to_email: Recipient email address
            subject: Email subject
            plain_text_body: Plain text body content
            attachment_files: List of file paths to attach
            
        Returns:
            MIMEMultipart email message
        """
        # Create multipart message
        if attachment_files:
            msg = MIMEMultipart('mixed')
        else:
            msg = MIMEMultipart()
            
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Add plain text part
        text_part = MIMEText(plain_text_body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Add attachments if provided
        if attachment_files:
            for attachment_path in attachment_files:
                try:
                    self._attach_file(msg, attachment_path)
                except Exception as e:
                    self.logger.error(f"Failed to attach file {attachment_path}: {e}")
        
        return msg
    
    def save_as_eml(self, email_msg: MIMEMultipart, output_path: str) -> None:
        """
        Save email message as .eml file.
        
        Args:
            email_msg: Email message to save
            output_path: Path where to save the .eml file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(email_msg.as_string())
            
            self.logger.info(f"Email saved as .eml file: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save .eml file: {e}")
            raise
    
    def create_email_preview_html(self,
                                 to_email: str,
                                 subject: str, 
                                 html_body: str,
                                 attachment_files: List[str] = None,
                                 generated_time: str = None) -> str:
        """
        Create an HTML preview of the email for display purposes.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML body content
            attachment_files: List of attachment file paths
            generated_time: When the email was generated
            
        Returns:
            HTML string for email preview
        """
        if not generated_time:
            generated_time = datetime.now().isoformat()
        
        # Create email preview HTML
        preview_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .email-header {{ 
            background-color: #f5f5f5; 
            padding: 15px; 
            border: 1px solid #ddd; 
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .email-body {{ 
            border: 1px solid #ddd; 
            padding: 20px;
            border-radius: 5px;
            background-color: white;
        }}
        .attachment-list {{ 
            margin-top: 15px; 
            padding: 10px; 
            background-color: #f9f9f9; 
            border-radius: 5px;
        }}
        .attachment-item {{ 
            margin: 5px 0; 
            padding: 5px; 
            background-color: white; 
            border-radius: 3px;
        }}
        .metadata {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="email-header">
        <h2>Email Preview</h2>
        <div class="metadata">
            <strong>To:</strong> {to_email}<br>
            <strong>Subject:</strong> {subject}<br>
            <strong>Generated:</strong> {generated_time}
        </div>
        """
        
        # Add attachment information
        if attachment_files:
            preview_html += f"""
        <div class="attachment-list">
            <strong>Attachments ({len(attachment_files)}):</strong>
            """
            
            for attachment_path in attachment_files:
                filename = os.path.basename(attachment_path)
                try:
                    file_size = os.path.getsize(attachment_path)
                    size_str = self._format_file_size(file_size)
                except:
                    size_str = "Unknown size"
                
                preview_html += f"""
            <div class="attachment-item">📎 {filename} ({size_str})</div>
                """
            
            preview_html += """
        </div>
            """
        
        preview_html += f"""
    </div>
    
    <div class="email-body">
        {html_body}
    </div>
</body>
</html>
        """
        
        return preview_html
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email message."""
        filename = os.path.basename(file_path)
        
        # Guess the content type based on the file's extension
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
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
