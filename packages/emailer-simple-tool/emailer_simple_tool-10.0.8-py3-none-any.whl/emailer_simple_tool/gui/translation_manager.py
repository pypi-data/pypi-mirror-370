"""
Translation Manager for GUI Internationalization
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTranslator, QCoreApplication, QLocale
from PySide6.QtWidgets import QApplication


class TranslationManager:
    """Manages GUI translations and language switching"""
    
    def __init__(self):
        self.current_translator: Optional[QTranslator] = None
        self.translations_dir = Path(__file__).parent / "translations"
        
        # Supported languages (language code -> display name)
        self.supported_languages = {
            "en": "English",
            "fr": "Français"
        }
        
        # Default to system locale or English
        self.current_language = self.detect_system_language()
    
    def detect_system_language(self) -> str:
        """Detect system language and return supported language code"""
        system_locale = QLocale.system().name()[:2]  # Get language part (e.g., 'en' from 'en_US')
        
        if system_locale in self.supported_languages:
            return system_locale
        else:
            return "en"  # Default to English
    
    def get_supported_languages(self) -> dict:
        """Get dictionary of supported languages"""
        return self.supported_languages.copy()
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language
    
    def set_language(self, language_code: str) -> bool:
        """Set application language"""
        if language_code not in self.supported_languages:
            return False
        
        # Remove current translator if exists
        if self.current_translator:
            QCoreApplication.removeTranslator(self.current_translator)
            self.current_translator = None
        
        # Don't load translator for English (base language)
        if language_code == "en":
            self.current_language = language_code
            return True
        
        # Load translation file
        translation_file = self.translations_dir / f"emailer_simple_tool_{language_code}.qm"
        
        if not translation_file.exists():
            print(f"Warning: Translation file not found: {translation_file}")
            return False
        
        # Create and install translator
        translator = QTranslator()
        if translator.load(str(translation_file)):
            QCoreApplication.installTranslator(translator)
            self.current_translator = translator
            self.current_language = language_code
            return True
        else:
            print(f"Error: Failed to load translation file: {translation_file}")
            return False
    
    def tr(self, text: str, context: str = None) -> str:
        """Translate text (convenience method)"""
        if context:
            return QCoreApplication.translate(context, text)
        else:
            return QCoreApplication.translate("", text)


# Global translation manager instance
translation_manager = TranslationManager()
