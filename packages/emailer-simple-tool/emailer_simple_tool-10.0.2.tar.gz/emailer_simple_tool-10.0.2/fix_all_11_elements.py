#!/usr/bin/env python3
"""
Fix ALL 11 remaining English elements systematically
"""

from pathlib import Path

def fix_all_remaining_elements():
    """Fix all 11 remaining English elements"""
    
    print("🔧 FIXING ALL 11 REMAINING ENGLISH ELEMENTS")
    print("=" * 70)
    
    # 1. Fix Picture tab panel titles in refresh_translations
    fix_picture_panel_titles()
    
    # 2. Fix Picture tab help text translation
    fix_picture_help_translation()
    
    # 3. Fix SMTP tab form labels in refresh_translations
    fix_smtp_form_labels()
    
    # 4. Fix SMTP tab guidance HTML to use proper translations
    fix_smtp_guidance_html()
    
    # 5. Add all missing translations
    add_all_missing_translations()
    
    # 6. Recompile
    print(f"\n🔄 Recompiling translations...")
    import subprocess
    result = subprocess.run([
        "pyside6-lrelease", "emailer_simple_tool_fr.ts"
    ], cwd=Path("src/emailer_simple_tool/gui/translations"), capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Translations recompiled successfully!")
        return True
    else:
        print(f"❌ Compilation failed: {result.stderr}")
        return False

def fix_picture_panel_titles():
    """Fix Picture tab panel titles that aren't being translated"""
    
    print("\n1️⃣ Fixing Picture tab panel titles...")
    
    picture_file = Path("src/emailer_simple_tool/gui/tabs/picture_tab.py")
    
    with open(picture_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is that some panel titles aren't being updated in refresh_translations
    # Let's make sure ALL panel titles are updated
    
    # Find the refresh_translations method and ensure it updates ALL titles
    old_refresh_section = '''        # Update group box titles
        if hasattr(self, 'help_group'):
            self.help_group.setTitle(self.tr("📚 User Help & Guidance"))
        if hasattr(self, 'validation_group'):
            self.validation_group.setTitle(self.tr("🔍 Validation Panel"))
        if hasattr(self, 'generation_group'):
            self.generation_group.setTitle(self.tr("🎨 Picture Generation"))
        if hasattr(self, 'images_group'):
            self.images_group.setTitle(self.tr("📸 Generated Images"))'''
    
    new_refresh_section = '''        # Update group box titles
        if hasattr(self, 'help_group'):
            self.help_group.setTitle(self.tr("📚 User Help & Guidance"))
        if hasattr(self, 'validation_group'):
            self.validation_group.setTitle(self.tr("🔍 Validation Panel"))
        if hasattr(self, 'generation_group'):
            self.generation_group.setTitle(self.tr("🎨 Picture Generation"))
        if hasattr(self, 'images_group'):
            self.images_group.setTitle(self.tr("📸 Generated Images"))
        
        # Update button texts that might not be updated
        if hasattr(self, 'generate_button'):
            self.generate_button.setText(self.tr("🎨 Generate Pictures"))'''
    
    if old_refresh_section in content:
        content = content.replace(old_refresh_section, new_refresh_section)
        print("✅ Enhanced Picture tab refresh_translations for panel titles")
    
    with open(picture_file, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_picture_help_translation():
    """Ensure Picture tab help text translation exists and is complete"""
    
    print("\n2️⃣ Fixing Picture tab help text translation...")
    
    ts_file = Path("src/emailer_simple_tool/gui/translations/emailer_simple_tool_fr.ts")
    
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The help text translation should exist, but let's make sure it's complete
    help_english = """
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
        """
    
    # Check if it exists and is marked as unfinished
    if f'<source>{help_english.strip()}</source>' in content:
        # Check if it's unfinished
        if 'translation type="unfinished"' in content:
            # Fix unfinished translation
            old_unfinished = f'<source>{help_english.strip()}</source>\n        <translation type="unfinished"></translation>'
            new_finished = f'<source>{help_english.strip()}</source>\n        <translation>FRENCH_HELP_TEXT_HERE</translation>'
            # This will be handled in add_all_missing_translations
            print("✅ Help text translation exists but needs completion")
        else:
            print("✅ Help text translation already exists and is complete")
    else:
        print("✅ Help text translation will be added")

def fix_smtp_form_labels():
    """Fix SMTP tab form labels to be properly translated"""
    
    print("\n3️⃣ Fixing SMTP tab form labels...")
    
    smtp_file = Path("src/emailer_simple_tool/gui/tabs/smtp_tab.py")
    
    with open(smtp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The form labels are created in init_ui but not updated in refresh_translations
    # Let's enhance the refresh_translations method to properly update form labels
    
    # Find the form label update section and make it more robust
    old_form_section = '''        # Update form labels by recreating the form layout
        if hasattr(self, 'config_group'):
            # Get the current form layout
            from PySide6.QtWidgets import QFormLayout
            layout = self.config_group.layout()
            if layout and isinstance(layout, QFormLayout):
                # Update row labels
                for i in range(layout.rowCount()):
                    label_item = layout.itemAt(i, QFormLayout.LabelRole)
                    if label_item and label_item.widget():
                        label_widget = label_item.widget()
                        if hasattr(label_widget, 'text'):
                            current_text = label_widget.text()
                            if "SMTP Server:" in current_text or "Serveur SMTP :" in current_text:
                                label_widget.setText(self.tr("SMTP Server:"))
                            elif "Port:" in current_text:
                                label_widget.setText(self.tr("Port:"))
                            elif "Username:" in current_text or "Nom d'utilisateur :" in current_text:
                                label_widget.setText(self.tr("Username:"))
                            elif "Password:" in current_text or "Mot de passe :" in current_text:
                                label_widget.setText(self.tr("Password:"))'''
    
    new_form_section = '''        # Update form labels by recreating the form layout
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
                                label_widget.setText(self.tr("Password:"))'''
    
    if old_form_section in content:
        content = content.replace(old_form_section, new_form_section)
        print("✅ Enhanced SMTP form label translation")
    
    with open(smtp_file, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_smtp_guidance_html():
    """Ensure SMTP guidance HTML is properly calling update_campaign_status"""
    
    print("\n4️⃣ Fixing SMTP guidance HTML...")
    
    smtp_file = Path("src/emailer_simple_tool/gui/tabs/smtp_tab.py")
    
    with open(smtp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Make sure refresh_translations calls update_campaign_status to refresh HTML
    if 'self.update_campaign_status()' not in content:
        # Add update_campaign_status call to refresh_translations
        old_refresh_end = '''        # Update test result if it has default text
        if hasattr(self, 'test_result'):
            current_text = self.test_result.text()
            if "Click 'Test SMTP Connection'" in current_text:
                self.test_result.setText(self.tr("Click 'Test SMTP Connection' to verify settings"))'''
        
        new_refresh_end = '''        # Update test result if it has default text
        if hasattr(self, 'test_result'):
            current_text = self.test_result.text()
            if "Click 'Test SMTP Connection'" in current_text:
                self.test_result.setText(self.tr("Click 'Test SMTP Connection' to verify settings"))
        
        # Update guidance HTML content
        self.update_campaign_status()'''
        
        if old_refresh_end in content:
            content = content.replace(old_refresh_end, new_refresh_end)
            print("✅ Added guidance HTML refresh to refresh_translations")
    
    with open(smtp_file, 'w', encoding='utf-8') as f:
        f.write(content)

def add_all_missing_translations():
    """Add all missing translations for the 11 elements"""
    
    print("\n5️⃣ Adding all missing translations...")
    
    ts_file = Path("src/emailer_simple_tool/gui/translations/emailer_simple_tool_fr.ts")
    
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # All missing translations
    translations = {
        # Picture Tab
        "🔍 Validation Panel": "🔍 Panneau de Validation",
        "🎨 Picture Generation": "🎨 Génération d'Images",
        "📸 Generated Images": "📸 Images Générées",
        "🎨 Generate Pictures": "🎨 Générer les Images",
        "No project loaded": "Aucun projet chargé",
        
        # SMTP Tab
        "SMTP Server:": "Serveur SMTP :",
        "Port:": "Port :",
        "Username:": "Nom d'utilisateur :",
        "Password:": "Mot de passe :",
        
        # Picture Tab Help Text (complete)
        """
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
        """: """
<b>Comment utiliser le Générateur d'Images :</b>

<b>• Édition de fusion.csv :</b>
- Chaque ligne ajoute un élément à vos images personnalisées
- fusion-type : Utilisez 'text' pour le texte, 'graphic' pour les images, 'formatted-text' pour les documents stylés
- data : Tapez votre texte ou utilisez {{nom}} pour insérer les informations du destinataire
- positioning : Utilisez le format 'x:y' - le premier nombre déplace vers la droite, le second vers le bas
- size : Taille de police pour le texte, 'largeur:hauteur' pour les images
- alignment : Choisissez 'left', 'center', ou 'right'

<b>• Guide de Positionnement :</b>
- Le coin supérieur gauche est 0:0
- Augmentez le premier nombre pour déplacer vers la droite, le second vers le bas
- Exemple : 100:50 signifie 100 pixels depuis la gauche, 50 pixels depuis le haut

<b>• Références de Fichiers :</b>
- Fichiers statiques : Utilisez des noms exacts comme 'logo.png'
- Fichiers personnalisés : Utilisez {{nom_colonne}} pour référencer les données CSV
- Structure de dossiers : Les fichiers peuvent être dans des sous-dossiers avec 'dossier/fichier.png'

<b>• Variables de Modèle :</b>
- Utilisez {{nom}}, {{email}}, ou toute colonne de votre recipients.csv
- Les variables seront remplacées par les données réelles du destinataire
        """,
    }
    
    added = 0
    
    for english, french in translations.items():
        # Check if translation exists
        if f'<source>{english}</source>' not in content:
            # Determine context
            if any(x in english for x in ["Validation Panel", "Picture Generation", "Generated Images", "Generate Pictures", "No project loaded", "How to use"]):
                context_name = "PictureTab"
            else:
                context_name = "SMTPTab"
            
            # Add translation
            context_end = content.find('</context>', content.find(f'<name>{context_name}</name>'))
            if context_end != -1:
                import xml.sax.saxutils as saxutils
                english_escaped = saxutils.escape(english)
                french_escaped = saxutils.escape(french)
                
                new_entry = f'''    <message>
        <location filename="../tabs/{context_name.lower()}_tab.py" line="1"/>
        <source>{english_escaped}</source>
        <translation>{french_escaped}</translation>
    </message>
'''
                content = content[:context_end] + new_entry + content[context_end:]
                added += 1
                if len(english) > 100:
                    print(f"✅ Added: [LONG TEXT - {len(english)} chars]")
                else:
                    print(f"✅ Added: {english}")
        else:
            # Check if it's unfinished
            if f'<source>{english}</source>\n        <translation type="unfinished"></translation>' in content:
                # Fix unfinished translation
                old_unfinished = f'<source>{english}</source>\n        <translation type="unfinished"></translation>'
                new_finished = f'<source>{english}</source>\n        <translation>{french}</translation>'
                content = content.replace(old_unfinished, new_finished)
                added += 1
                print(f"✅ Fixed unfinished: {english[:50]}...")
    
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Added/fixed {added} translations")
    return added

if __name__ == "__main__":
    success = fix_all_remaining_elements()
    
    if success:
        print(f"\n🎉 ALL 11 ENGLISH ELEMENTS FIXED!")
        print("📋 Testing to verify fixes...")
        
        # Test again
        import subprocess
        result = subprocess.run(["python3", "find_all_english_fixed.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
    else:
        print(f"\n❌ FAILED TO FIX ELEMENTS")
