"""
Template processing utilities for email personalization.
"""

import re
from typing import Dict, List, Set
from .validators import ValidationResult
from .logger import get_logger


class TemplateProcessor:
    """Processes email templates with recipient data."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def process_template(self, template: str, data: Dict[str, str]) -> str:
        """Process template by replacing {{field}} placeholders with data."""
        try:
            # Replace all {{field}} patterns with corresponding data
            def replace_placeholder(match):
                field_name = match.group(1).strip()
                return data.get(field_name, f"{{{{MISSING: {field_name}}}}}")
            
            # Use regex to find and replace all {{field}} patterns
            pattern = r'\{\{([^}]+)\}\}'
            result = re.sub(pattern, replace_placeholder, template)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing template: {e}")
            return template
    
    def validate_templates(self, subject_template: str, message_template: str, 
                          available_fields: List[str]) -> ValidationResult:
        """Validate that all template references exist in available fields."""
        errors = []
        warnings = []
        
        try:
            available_fields_set = set(available_fields)
            
            # Extract references from both templates
            subject_refs = self._extract_template_references(subject_template)
            message_refs = self._extract_template_references(message_template)
            
            all_refs = subject_refs.union(message_refs)
            
            # Check if all references are valid
            for ref in all_refs:
                if ref not in available_fields_set:
                    errors.append(f"Template reference '{{{{{ref}}}}}' not found in CSV columns")
            
            # Check for unused fields (warning only)
            used_fields = all_refs
            unused_fields = available_fields_set - used_fields
            
            if unused_fields:
                warnings.append(f"Unused CSV columns: {', '.join(sorted(unused_fields))}")
            
        except Exception as e:
            errors.append(f"Error validating templates: {e}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _extract_template_references(self, content: str) -> Set[str]:
        """Extract template references from content using {{field}} pattern."""
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, content)
        return set(match.strip() for match in matches)
    
    def get_template_fields(self, template: str) -> List[str]:
        """Get list of all fields referenced in a template."""
        refs = self._extract_template_references(template)
        return sorted(list(refs))
    
    def preview_template(self, template: str, sample_data: Dict[str, str]) -> str:
        """Preview template with sample data for testing."""
        return self.process_template(template, sample_data)
