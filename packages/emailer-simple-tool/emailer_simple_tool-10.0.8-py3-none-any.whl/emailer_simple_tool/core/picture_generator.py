"""
Picture generator functionality for creating personalized JPEG documents.
Handles text and graphic fusion into JPEG templates.
"""

import os
import csv
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import re

from ..utils.logger import get_logger
from ..utils.template_processor import TemplateProcessor
from ..utils.document_processor import DocumentProcessor
from ..utils.validators import ValidationResult


class PictureGeneratorProject:
    """Represents a single picture generator project."""
    
    def __init__(self, project_path: str, project_name: str):
        self.project_path = project_path
        self.project_name = project_name
        self.template_file = os.path.join(project_path, 'template.jpg')
        self.fusion_file = os.path.join(project_path, 'fusion.csv')
        self.attach_file = os.path.join(project_path, 'attach.txt')
        self.data_folder = os.path.join(project_path, 'data')
        self.logger = get_logger(__name__)
    
    def exists(self) -> bool:
        """Check if the project folder exists."""
        return os.path.exists(self.project_path) and os.path.isdir(self.project_path)
    
    def is_valid(self) -> ValidationResult:
        """Validate the project structure and files."""
        errors = []
        warnings = []
        
        if not self.exists():
            errors.append(f"Project folder does not exist: {self.project_name}")
            return ValidationResult(False, errors, warnings)
        
        # Check required files
        if not os.path.exists(self.template_file):
            errors.append(f"Template file missing: template.jpg")
        elif not self._is_valid_jpeg(self.template_file):
            errors.append(f"Template file is not a valid JPEG: template.jpg")
        
        if not os.path.exists(self.fusion_file):
            errors.append(f"Fusion file missing: fusion.csv")
        else:
            # Validate fusion CSV
            fusion_result = self._validate_fusion_csv()
            errors.extend(fusion_result.errors)
            warnings.extend(fusion_result.warnings)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def should_attach_to_email(self) -> bool:
        """Check if generated pictures should be attached to emails."""
        if not os.path.exists(self.attach_file):
            return False
        
        try:
            with open(self.attach_file, 'r', encoding='utf-8') as f:
                content = f.read().strip().lower()
                return content == 'true'
        except Exception as e:
            self.logger.warning(f"Could not read attach.txt: {e}")
            return False
    
    def _is_valid_jpeg(self, file_path: str) -> bool:
        """Check if file is a valid JPEG image."""
        try:
            with Image.open(file_path) as img:
                return img.format in ['JPEG', 'JPG']
        except Exception:
            return False
    
    def _validate_fusion_csv(self) -> ValidationResult:
        """Validate the fusion CSV file structure."""
        errors = []
        warnings = []
        
        required_columns = ['fusion-type', 'data', 'positioning', 'size', 'alignment']
        optional_columns = ['orientation', 'font', 'shape', 'color']
        
        try:
            with open(self.fusion_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Check required columns
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    errors.append(f"Missing required columns in fusion.csv: {', '.join(missing_columns)}")
                    return ValidationResult(False, errors, warnings)
                
                # Validate each row
                for row_num, row in enumerate(reader, start=2):
                    row_errors = self._validate_fusion_row(row, row_num)
                    errors.extend(row_errors)
        
        except Exception as e:
            errors.append(f"Error reading fusion.csv: {e}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _validate_fusion_row(self, row: Dict[str, str], row_num: int) -> List[str]:
        """Validate a single fusion CSV row."""
        errors = []
        
        # Validate fusion-type
        fusion_type = row.get('fusion-type', '').strip().lower()
        if fusion_type not in ['text', 'graphic', 'formatted-text']:
            errors.append(f"Row {row_num}: fusion-type must be 'text', 'graphic', or 'formatted-text', got '{fusion_type}'")
        
        # Validate positioning format (x:y) - now supports negative coordinates
        positioning = row.get('positioning', '').strip()
        if not re.match(r'^-?\d+:-?\d+$', positioning):
            errors.append(f"Row {row_num}: positioning must be in format 'x:y' (negative values allowed), got '{positioning}'")
        
        # Validate size based on fusion type
        size = row.get('size', '').strip()
        if fusion_type == 'text':
            if not size.isdigit():
                errors.append(f"Row {row_num}: size for text must be a number, got '{size}'")
        elif fusion_type in ['graphic', 'formatted-text']:
            if not re.match(r'^(\d+:|\d+:\d+|:\d+)$', size):
                errors.append(f"Row {row_num}: size for {fusion_type} must be 'x:', 'x:y', or ':y', got '{size}'")
        
        # Validate alignment
        alignment = row.get('alignment', '').strip().lower()
        if alignment not in ['left', 'center', 'right']:
            errors.append(f"Row {row_num}: alignment must be 'left', 'center', or 'right', got '{alignment}'")
        
        # Validate orientation if provided
        orientation = row.get('orientation', '').strip()
        if orientation:
            try:
                orient_val = float(orientation)
                if not -180 <= orient_val <= 180:
                    errors.append(f"Row {row_num}: orientation must be between -180 and 180, got '{orientation}'")
            except ValueError:
                errors.append(f"Row {row_num}: orientation must be a number, got '{orientation}'")
        
        return errors


class PictureGenerator:
    """Main picture generator class for creating personalized documents."""
    
    def __init__(self, campaign_folder: str):
        self.campaign_folder = campaign_folder
        self.picture_generator_folder = os.path.join(campaign_folder, 'picture-generator')
        self.logger = get_logger(__name__)
        self.template_processor = TemplateProcessor()
        self.document_processor = DocumentProcessor()
    
    def get_projects(self) -> List[PictureGeneratorProject]:
        """Get all picture generator projects in the campaign."""
        projects = []
        
        if not os.path.exists(self.picture_generator_folder):
            return projects
        
        try:
            for item in os.listdir(self.picture_generator_folder):
                project_path = os.path.join(self.picture_generator_folder, item)
                if os.path.isdir(project_path):
                    project = PictureGeneratorProject(project_path, item)
                    projects.append(project)
        except Exception as e:
            self.logger.error(f"Error scanning picture generator projects: {e}")
        
        return projects
    
    def validate_projects(self, recipients: List[Dict[str, str]]) -> ValidationResult:
        """Validate only attached picture generator projects against recipients."""
        errors = []
        warnings = []
        
        projects = self.get_projects()
        
        for project in projects:
            # Only validate projects that are set to be attached to emails
            if not project.should_attach_to_email():
                continue  # Skip non-attached projects
            
            # Validate project structure
            project_result = project.is_valid()
            if not project_result.is_valid:
                errors.extend([f"Project '{project.project_name}': {error}" for error in project_result.errors])
                continue
            
            warnings.extend([f"Project '{project.project_name}': {warning}" for warning in project_result.warnings])
            
            # Check data consistency with recipients
            consistency_result = self._check_data_consistency(project, recipients)
            errors.extend(consistency_result.errors)
            warnings.extend(consistency_result.warnings)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _check_data_consistency(self, project: PictureGeneratorProject, 
                               recipients: List[Dict[str, str]]) -> ValidationResult:
        """Check if generated data is consistent with recipients."""
        errors = []
        warnings = []
        
        if not os.path.exists(project.data_folder):
            errors.append(f"Project '{project.project_name}': No generated data found. Run 'emailer-simple-tool picture generate {project.project_name}' to generate pictures.")
            return ValidationResult(False, errors, warnings)
        
        # Get expected files based on recipients
        if not recipients:
            return ValidationResult(True, errors, warnings)
        
        # Get primary key column (first column)
        primary_key_column = list(recipients[0].keys())[0]
        expected_files = set()
        
        for recipient in recipients:
            primary_key = recipient.get(primary_key_column, '').strip()
            if primary_key:
                # Use new filename pattern with project name
                expected_files.add(f"{primary_key}-{project.project_name}.jpg")
        
        # Get actual files in data folder
        try:
            actual_files = set()
            for item in os.listdir(project.data_folder):
                if item.endswith('.jpg') and os.path.isfile(os.path.join(project.data_folder, item)):
                    actual_files.add(item)
            
            # Check for missing files
            missing_files = expected_files - actual_files
            if missing_files:
                errors.append(f"Project '{project.project_name}': Missing generated files for recipients: {', '.join(sorted(missing_files))}")
            
            # Check for extra files (files that don't correspond to current recipients)
            extra_files = actual_files - expected_files
            if extra_files:
                errors.append(f"Project '{project.project_name}': Found generated files for recipients not in current list: {', '.join(sorted(extra_files))}")
            
            # If there are sync issues, provide guidance
            if missing_files or extra_files:
                errors.append(f"Project '{project.project_name}': Recipients and generated pictures are out of sync. Run 'emailer-simple-tool picture generate {project.project_name}' to regenerate pictures for current recipients.")
        
        except Exception as e:
            errors.append(f"Project '{project.project_name}': Error checking data folder: {e}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def generate_pictures(self, project_name: str, recipients: List[Dict[str, str]], progress_callback=None) -> int:
        """Generate personalized pictures for all recipients.
        
        Args:
            project_name: Name of the picture project
            recipients: List of recipient data dictionaries
            progress_callback: Optional callback function(current, total, message) for progress updates
        
        Returns:
            0 on success, 1 on failure
        """
        projects = self.get_projects()
        project = next((p for p in projects if p.project_name == project_name), None)
        
        if not project:
            print(f"❌ Project '{project_name}' not found")
            return 1
        
        # Validate project
        validation_result = project.is_valid()
        if not validation_result.is_valid:
            print(f"❌ Project validation failed:")
            for error in validation_result.errors:
                print(f"  {error}")
            return 1
        
        if validation_result.warnings:
            print("⚠️  Project warnings:")
            for warning in validation_result.warnings:
                print(f"  {warning}")
        
        # Check primary key is not email
        if not recipients:
            print("❌ No recipients found")
            return 1
        
        primary_key_column = list(recipients[0].keys())[0]
        if primary_key_column.lower() == 'email':
            print("❌ Primary key cannot be 'email' for picture generation")
            print("   Please use an ID column as the first column in recipients.csv")
            return 1
        
        # Create data folder
        os.makedirs(project.data_folder, exist_ok=True)
        
        # Clean up old generated files to ensure sync
        self._cleanup_old_generated_files(project.data_folder)
        
        # Load fusion instructions
        fusion_instructions = self._load_fusion_instructions(project.fusion_file)
        if not fusion_instructions:
            print("❌ No valid fusion instructions found")
            return 1
        
        # Generate pictures
        generated_count = 0
        failed_count = 0
        total_recipients = len(recipients)
        
        print(f"Generating personalized pictures for project '{project_name}'...")
        
        # Initial progress report
        if progress_callback:
            progress_callback(0, total_recipients, "Starting picture generation...")
        
        for i, recipient in enumerate(recipients):
            primary_key = recipient.get(primary_key_column, '').strip()
            if not primary_key:
                print(f"  ⚠️  Skipping recipient with empty primary key")
                failed_count += 1
                if progress_callback:
                    progress_callback(i + 1, total_recipients, f"Skipped recipient {i + 1}/{total_recipients}")
                continue
            
            try:
                # Use project name prefix to avoid filename collisions between projects
                filename = f"{primary_key}-{project.project_name}.jpg"
                output_path = os.path.join(project.data_folder, filename)
                
                # Progress update before generation
                if progress_callback:
                    progress_callback(i, total_recipients, f"Generating {filename}...")
                
                self._generate_single_picture(project, fusion_instructions, recipient, output_path)
                generated_count += 1
                print(f"  ✅ Generated: {filename}")
                
                # Progress update after successful generation
                if progress_callback:
                    progress_callback(i + 1, total_recipients, f"Generated {filename}")
                
            except Exception as e:
                failed_count += 1
                filename = f"{primary_key}-{project.project_name}.jpg"
                self.logger.error(f"Failed to generate picture for {primary_key}: {e}")
                print(f"  ❌ Failed: {filename} - {e}")
                
                # Progress update after failure
                if progress_callback:
                    progress_callback(i + 1, total_recipients, f"Failed: {filename}")
        
        # Final progress report
        if progress_callback:
            progress_callback(total_recipients, total_recipients, 
                            f"Completed: {generated_count} generated, {failed_count} failed")
        
        print(f"\n📸 Picture generation completed: {generated_count} generated, {failed_count} failed")
        return 0 if failed_count == 0 else 1
    
    def _cleanup_old_generated_files(self, data_folder: str) -> None:
        """Remove all old generated .jpg files to ensure clean sync."""
        try:
            if os.path.exists(data_folder):
                for item in os.listdir(data_folder):
                    if item.endswith('.jpg'):
                        file_path = os.path.join(data_folder, item)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            self.logger.debug(f"Removed old generated file: {item}")
        except Exception as e:
            self.logger.warning(f"Error cleaning up old generated files: {e}")
    
    def _load_fusion_instructions(self, fusion_file: str) -> List[Dict[str, str]]:
        """Load fusion instructions from CSV file."""
        instructions = []
        
        try:
            with open(fusion_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    instructions.append(row)
        except Exception as e:
            self.logger.error(f"Error loading fusion instructions: {e}")
        
        return instructions
    
    def _generate_single_picture(self, project: PictureGeneratorProject, 
                                fusion_instructions: List[Dict[str, str]], 
                                recipient: Dict[str, str], output_path: str) -> None:
        """Generate a single personalized picture."""
        # Load template image
        with Image.open(project.template_file) as template:
            # Convert to RGB if necessary
            if template.mode != 'RGB':
                template = template.convert('RGB')
            
            # Create a copy to work with
            image = template.copy()
            draw = ImageDraw.Draw(image)
            
            # Apply each fusion instruction
            for instruction in fusion_instructions:
                self._apply_fusion_instruction(project, image, draw, instruction, recipient)
            
            # Save the result
            image.save(output_path, 'JPEG', quality=95)
    
    def _apply_fusion_instruction(self, project: PictureGeneratorProject, 
                                 image: Image.Image, draw: ImageDraw.Draw,
                                 instruction: Dict[str, str], recipient: Dict[str, str]) -> None:
        """Apply a single fusion instruction to the image."""
        fusion_type = instruction.get('fusion-type', '').strip().lower()
        
        if fusion_type == 'text':
            self._apply_text_fusion(image, draw, instruction, recipient)
        elif fusion_type == 'graphic':
            self._apply_graphic_fusion(project, image, instruction, recipient)
        elif fusion_type == 'formatted-text':
            self._apply_formatted_text_fusion(project, image, instruction, recipient)
    
    def _apply_text_fusion(self, image: Image.Image, draw: ImageDraw.Draw,
                          instruction: Dict[str, str], recipient: Dict[str, str]) -> None:
        """Apply text fusion to the image."""
        # Process template data
        data = instruction.get('data', '')
        text = self.template_processor.process_template(data, recipient)
        
        # Parse positioning
        positioning = instruction.get('positioning', '0:0')
        x, y = map(int, positioning.split(':'))
        
        # Parse size (font size)
        size = int(instruction.get('size', '12'))
        
        # Get font
        font = self._get_font(instruction, size)
        
        # Get color
        color = self._parse_color(instruction.get('color', 'black'))
        
        # Get alignment
        alignment = instruction.get('alignment', 'left').lower()
        
        # Get orientation
        orientation = instruction.get('orientation', '0')
        
        # Check if we need to rotate the text
        if orientation and orientation != '0':
            try:
                angle = float(orientation)
                # Get exact text dimensions
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # DEBUG: Print basic info
                print(f"DEBUG - Text: '{text}'")
                print(f"DEBUG - text_width: {text_width}, text_height: {text_height}")
                print(f"DEBUG - angle: {angle}°")
                print(f"DEBUG - Original position: x={x}, y={y}")
                
                # FIX: Add padding to prevent clipping of descenders and font metrics
                font_size = getattr(font, 'size', 50)
                padding = max(20, int(font_size * 0.3))  # 30% of font size, minimum 20px
                
                # Create temp image with padding to avoid clipping
                temp_img = Image.new('RGBA', (text_width + 2*padding, text_height + 2*padding), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                
                print(f"DEBUG - Temp image size with padding: {temp_img.width} x {temp_img.height} (padding: {padding}px)")
                
                # Draw text with padding offset to avoid clipping
                temp_draw.text((padding, padding), text, fill=color, font=font)
                
                # Let PIL calculate the exact rotated dimensions
                rotated_img = temp_img.rotate(angle, expand=True)
                rotated_width, rotated_height = rotated_img.size
                
                print(f"DEBUG - Rotated image size: {rotated_width} x {rotated_height}")
                
                # For positioning, we need to account for how the rotation affects placement
                # The rotation happens around the center, so we need to adjust accordingly
                
                # Calculate where to place the rotated image based on alignment
                final_x = x
                final_y = y
                
                # Adjust for horizontal alignment
                if alignment == 'center':
                    final_x = x - rotated_width // 2
                elif alignment == 'right':
                    final_x = x - rotated_width
                # For 'left', no adjustment needed
                
                print(f"DEBUG - Final position before Windows adjustment: x={final_x}, y={final_y}")
                
                # For Windows compatibility
                import platform
                if platform.system() == 'Windows' and abs(angle) > 0:
                    font_size = getattr(font, 'size', 50)
                    
                    # For text positioned near the top edge, we need to move DOWN to prevent clipping
                    # For text positioned elsewhere, we use the standard upward adjustment
                    if final_y < 100:  # Near top edge
                        # Calculate padding based on font size and rotation angle
                        # More aggressive padding for larger fonts and angles
                        base_padding = max(10, int(font_size * 0.15))  # Minimum 10px, scales with font
                        angle_factor = abs(angle) / 45  # Normalize angle (45° = 1.0)
                        rotation_padding = int(base_padding * angle_factor)
                        final_y = final_y + rotation_padding
                        print(f"DEBUG - Windows top-edge adjustment: +{rotation_padding}px (moving DOWN)")
                    else:
                        # Standard Windows adjustment for other positions
                        windows_adjustment = int(font_size * 0.1)
                        final_y = final_y - windows_adjustment
                        print(f"DEBUG - Windows standard adjustment: -{windows_adjustment}px (moving UP)")
                
                print(f"DEBUG - FINAL position: x={final_x}, y={final_y}")
                print("=" * 50)
                
                # Paste the rotated text onto the main image
                image.paste(rotated_img, (final_x, final_y), rotated_img)
                
            except ValueError:
                self.logger.warning(f"Invalid orientation value: {orientation}")
                # Fall back to normal text rendering
                self._draw_normal_text(draw, text, x, y, font, color, alignment)
        else:
            # Normal text rendering without rotation
            self._draw_normal_text(draw, text, x, y, font, color, alignment)
    
    def _draw_normal_text(self, draw: ImageDraw.Draw, text: str, x: int, y: int, 
                         font, color, alignment: str) -> None:
        """Draw normal text without rotation."""
        # Adjust position based on alignment
        if alignment == 'center':
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = x - text_width // 2
        elif alignment == 'right':
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = x - text_width
        
        # Windows-specific Y-position adjustment for non-rotated text
        # Fix the 13-pixel difference observed between Windows and Mac
        import platform
        if platform.system() == 'Windows':
            font_size = getattr(font, 'size', 12)
            y = y - max(3, int(font_size * 0.12))  # Adjust upward by ~12% of font size
        
        # Draw text
        draw.text((x, y), text, fill=color, font=font)
    
    def _apply_graphic_fusion(self, project: PictureGeneratorProject, 
                             image: Image.Image, instruction: Dict[str, str], 
                             recipient: Dict[str, str]) -> None:
        """Apply graphic fusion to the image."""
        # Process data to get graphic path
        data = instruction.get('data', '')
        
        # Check if it's a template reference or static path
        if '{{' in data and '}}' in data:
            # Personalized graphic - process template
            graphic_filename = self.template_processor.process_template(data, recipient)
        else:
            # Static graphic
            graphic_filename = data
        
        # Resolve full path
        if not os.path.isabs(graphic_filename):
            graphic_path = os.path.join(project.project_path, graphic_filename)
        else:
            graphic_path = graphic_filename
        
        if not os.path.exists(graphic_path):
            self.logger.warning(f"Graphic file not found: {graphic_path}")
            return
        
        try:
            # Load graphic
            with Image.open(graphic_path) as graphic:
                # Convert to RGBA for transparency support
                if graphic.mode != 'RGBA':
                    graphic = graphic.convert('RGBA')
                
                # Parse size and resize if needed
                size_spec = instruction.get('size', '')
                if size_spec:
                    graphic = self._resize_graphic(graphic, size_spec)
                
                # Parse positioning
                positioning = instruction.get('positioning', '0:0')
                x, y = map(int, positioning.split(':'))
                
                # Apply alignment
                alignment = instruction.get('alignment', 'left').lower()
                if alignment == 'center':
                    x = x - graphic.width // 2
                elif alignment == 'right':
                    x = x - graphic.width
                
                # Paste graphic onto image
                image.paste(graphic, (x, y), graphic)
        
        except Exception as e:
            self.logger.error(f"Error applying graphic fusion: {e}")
    
    def _get_font(self, instruction: Dict[str, str], size: int) -> ImageFont.ImageFont:
        """Get font for text rendering with proper font family and shape support."""
        try:
            # Get font family from font parameter
            font_family = instruction.get('font', 'arial').strip()
            
            # Get font style from shape
            font_style = instruction.get('shape', '').strip().lower()
            
            # Parse font style
            is_bold = 'bold' in font_style
            is_italic = 'italic' in font_style
            
            # Normalize font family name
            font_family_lower = font_family.lower()
            
            # Try to load font from system locations
            font_found = False
            
            # macOS system fonts (try .ttc files first)
            if not font_found:
                macos_fonts = {
                    'arial': 'ArialHB.ttc',
                    'helvetica': 'Helvetica.ttc',
                    'courier': 'Courier.ttc',
                    'times': 'Times.ttc',
                    'georgia': 'Georgia.ttc',
                    'verdana': 'Verdana.ttc'
                }
                
                if font_family_lower in macos_fonts:
                    font_path = f"/System/Library/Fonts/{macos_fonts[font_family_lower]}"
                    if os.path.exists(font_path):
                        try:
                            # For .ttc files, we need to specify the font index
                            # Try different indices for different styles
                            font_indices = [0, 1, 2, 3]  # Regular, Bold, Italic, Bold Italic
                            
                            if is_bold and is_italic:
                                preferred_indices = [3, 1, 0]  # Bold Italic, Bold, Regular
                            elif is_bold:
                                preferred_indices = [1, 0]  # Bold, Regular
                            elif is_italic:
                                preferred_indices = [2, 0]  # Italic, Regular
                            else:
                                preferred_indices = [0]  # Regular
                            
                            for index in preferred_indices:
                                try:
                                    font = ImageFont.truetype(font_path, size, index=index)
                                    self.logger.debug(f"Loaded font {font_family} from {font_path} (index {index})")
                                    return font
                                except Exception as e:
                                    self.logger.debug(f"Failed to load font index {index} from {font_path}: {e}")
                                    continue
                                    
                        except Exception as e:
                            self.logger.debug(f"Failed to load font {font_path}: {e}")
            
            # Try individual .ttf/.otf files in common locations
            if not font_found:
                font_locations = [
                    "/System/Library/Fonts/",
                    "/Library/Fonts/",
                    "/System/Library/Fonts/Helvetica.ttc",  # Special case
                    "C:/Windows/Fonts/",  # Windows
                    "/usr/share/fonts/truetype/dejavu/",  # Linux
                    "/usr/share/fonts/truetype/liberation/",
                    "/usr/share/fonts/TTF/",
                    os.path.expanduser("~/Library/Fonts/"),  # User fonts
                    os.path.expanduser("~/.fonts/"),
                ]
                
                # Generate possible font file names
                font_names = []
                if is_bold and is_italic:
                    font_names = [
                        f"{font_family} Bold Italic",
                        f"{font_family}-BoldItalic",
                        f"{font_family}BI",
                        f"{font_family}bi"
                    ]
                elif is_bold:
                    font_names = [
                        f"{font_family} Bold",
                        f"{font_family}-Bold",
                        f"{font_family}B",
                        f"{font_family}b"
                    ]
                elif is_italic:
                    font_names = [
                        f"{font_family} Italic",
                        f"{font_family}-Italic",
                        f"{font_family}I",
                        f"{font_family}i"
                    ]
                else:
                    font_names = [
                        font_family,
                        f"{font_family} Regular",
                        f"{font_family}-Regular"
                    ]
                
                # Try each font name in each location
                for font_name in font_names:
                    for location in font_locations:
                        if not os.path.exists(location):
                            continue
                            
                        # Try different file extensions
                        extensions = ['.ttf', '.otf', '.ttc']
                        for ext in extensions:
                            font_files = [
                                f"{font_name}{ext}",
                                f"{font_name.replace(' ', '')}{ext}",
                                f"{font_name.lower().replace(' ', '')}{ext}",
                            ]
                            
                            for font_file in font_files:
                                font_path = os.path.join(location, font_file)
                                if os.path.exists(font_path):
                                    try:
                                        font = ImageFont.truetype(font_path, size)
                                        self.logger.debug(f"Loaded font {font_family} from {font_path}")
                                        return font
                                    except Exception as e:
                                        self.logger.debug(f"Failed to load font {font_path}: {e}")
                                        continue
            
            # Special handling for common monospace fonts (like Consolas alternative)
            if font_family_lower in ['consolas', 'monaco', 'menlo']:
                monospace_fonts = [
                    "/System/Library/Fonts/Monaco.ttf",  # macOS
                    "/System/Library/Fonts/Menlo.ttc",   # macOS
                    "/Library/Fonts/Consolas.ttf",       # If installed
                    "C:/Windows/Fonts/consola.ttf",      # Windows Consolas
                    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
                ]
                
                for font_path in monospace_fonts:
                    if os.path.exists(font_path):
                        try:
                            if font_path.endswith('.ttc'):
                                # Try different indices for .ttc files
                                for index in [0, 1, 2, 3]:
                                    try:
                                        font = ImageFont.truetype(font_path, size, index=index)
                                        self.logger.debug(f"Loaded monospace font from {font_path} (index {index})")
                                        return font
                                    except:
                                        continue
                            else:
                                font = ImageFont.truetype(font_path, size)
                                self.logger.debug(f"Loaded monospace font from {font_path}")
                                return font
                        except Exception as e:
                            self.logger.debug(f"Failed to load monospace font {font_path}: {e}")
                            continue
            
            # Log warning about font not found
            self.logger.warning(f"Font '{font_family}' with style '{font_style}' not found, using default font")
            
            # Fallback to default font
            return ImageFont.load_default()
        
        except Exception as e:
            self.logger.error(f"Error loading font: {e}")
            return ImageFont.load_default()
    
    def _parse_color(self, color_str: str) -> str:
        """Parse color string to RGB tuple or color name."""
        color_str = color_str.strip().lower()
        
        # Handle hex colors
        if color_str.startswith('#'):
            return color_str
        
        # Handle named colors
        color_map = {
            'black': '#000000',
            'white': '#FFFFFF',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'cyan': '#00FFFF',
            'magenta': '#FF00FF',
        }
        
        return color_map.get(color_str, '#000000')
    
    def _resize_graphic(self, graphic: Image.Image, size_spec: str) -> Image.Image:
        """Resize graphic according to size specification."""
        if ':' not in size_spec:
            return graphic
        
        width_str, height_str = size_spec.split(':')
        
        if width_str and height_str:
            # Both dimensions specified
            width, height = int(width_str), int(height_str)
            return graphic.resize((width, height), Image.Resampling.LANCZOS)
        elif width_str:
            # Only width specified, maintain aspect ratio
            width = int(width_str)
            aspect_ratio = graphic.height / graphic.width
            height = int(width * aspect_ratio)
            return graphic.resize((width, height), Image.Resampling.LANCZOS)
        elif height_str:
            # Only height specified, maintain aspect ratio
            height = int(height_str)
            aspect_ratio = graphic.width / graphic.height
            width = int(height * aspect_ratio)
            return graphic.resize((width, height), Image.Resampling.LANCZOS)
        
        return graphic
    
    def _apply_formatted_text_fusion(self, project: PictureGeneratorProject, 
                                   image: Image.Image, instruction: Dict[str, str], 
                                   recipient: Dict[str, str]) -> None:
        """Apply formatted text fusion using .docx template to the image."""
        try:
            # Get data path (should point to a .docx file)
            data = instruction.get('data', '')
            
            # Process template data to get the actual path
            docx_path = self.template_processor.process_template(data, recipient)
            
            # If it's a relative path, make it relative to the project folder
            if not os.path.isabs(docx_path):
                docx_path = os.path.join(project.project_path, docx_path)
            
            # Validate that the file exists and is a .docx file
            if not os.path.exists(docx_path):
                self.logger.error(f"Formatted text file not found: {docx_path}")
                return
            
            if not docx_path.lower().endswith('.docx'):
                self.logger.error(f"Formatted text file must be .docx format: {docx_path}")
                return
            
            # Process the .docx template with recipient data
            processed_doc = self.document_processor.process_docx_template(docx_path, recipient)
            
            # Parse positioning
            positioning = instruction.get('positioning', '0:0')
            x, y = map(int, positioning.split(':'))
            
            # Parse size (width:height for the rendered area)
            size_spec = instruction.get('size', '200:100')
            if ':' in size_spec:
                width_str, height_str = size_spec.split(':')
                width = int(width_str) if width_str else 200
                height = int(height_str) if height_str else 100
            else:
                width = height = int(size_spec)
            
            # Render the document to an image
            doc_image_bytes = self.document_processor.render_docx_to_image(
                processed_doc, width=width, height=height
            )
            
            # Load the rendered image
            from io import BytesIO
            doc_image = Image.open(BytesIO(doc_image_bytes))
            
            # Get alignment for positioning adjustment
            alignment = instruction.get('alignment', 'left').lower()
            
            # Adjust position based on alignment
            if alignment == 'center':
                x = x - width // 2
            elif alignment == 'right':
                x = x - width
            
            # Get orientation
            orientation = instruction.get('orientation', '0')
            if orientation and orientation != '0':
                try:
                    angle = float(orientation)
                    doc_image = doc_image.rotate(angle, expand=True)
                except ValueError:
                    self.logger.warning(f"Invalid orientation value: {orientation}")
            
            # Paste the formatted text image onto the main image
            if doc_image.mode != 'RGBA':
                doc_image = doc_image.convert('RGBA')
            
            # Create a mask for transparency
            mask = doc_image.split()[-1] if doc_image.mode == 'RGBA' else None
            
            # Paste the image
            image.paste(doc_image, (x, y), mask)
            
        except Exception as e:
            self.logger.error(f"Error applying formatted text fusion: {e}")
            # Fallback: render as plain text
            self._apply_text_fusion_fallback(image, instruction, recipient)
    
    def _apply_text_fusion_fallback(self, image: Image.Image, instruction: Dict[str, str], 
                                  recipient: Dict[str, str]) -> None:
        """Fallback method to render formatted text as plain text."""
        # Create a simple text representation
        draw = ImageDraw.Draw(image)
        
        # Get basic positioning
        positioning = instruction.get('positioning', '0:0')
        x, y = map(int, positioning.split(':'))
        
        # Use default font and render fallback text
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        fallback_text = "Formatted text (fallback)"
        draw.text((x, y), fallback_text, fill='black', font=font)
