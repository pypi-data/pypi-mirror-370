#!/usr/bin/env python3
"""
Complete ALL remaining translations - 100% coverage
"""

import re
from pathlib import Path

# COMPLETE translation mappings for ALL remaining strings
COMPLETE_TRANSLATIONS = {
    # Wizard and UI elements that were missed
    "Remove Selected": "Supprimer la Sélection",
    "< Back": "< Précédent",
    "Next >": "Suivant >",
    "Error": "Erreur",
    "OK": "OK",
    "Success": "Succès",
    "Browse...": "Parcourir...",
    "Message Template": "Modèle de Message",
    
    # Validation errors - complete set
    "Required file missing: recipients.csv": "Fichier requis manquant : recipients.csv",
    "'recipients.csv' exists but is not a file": "'recipients.csv' existe mais n'est pas un fichier",
    "'subject.txt' exists but is not a file": "'subject.txt' existe mais n'est pas un fichier",
    "'attachments' exists but is not a folder": "'attachments' existe mais n'est pas un dossier",
    "recipients.csv must contain an 'email' column": "recipients.csv doit contenir une colonne 'email'",
    "Primary key (first column) cannot be 'email' when picture generator projects exist. Please use an ID column as the first column.": "La clé primaire (première colonne) ne peut pas être 'email' quand des projets de générateur d'images existent. Veuillez utiliser une colonne ID comme première colonne.",
    "Subject file (subject.txt) must contain only one line. Email subjects cannot be multi-line.": "Le fichier de sujet (subject.txt) ne doit contenir qu'une seule ligne. Les sujets d'email ne peuvent pas être multi-lignes.",
    "'{filename}' exists but is not a file": "'{filename}' existe mais n'est pas un fichier",
    "Invalid email '{email}' in data row {row}": "Email invalide '{email}' dans la ligne de données {row}",
    "Duplicate email '{email}' found in data rows {row1} and {row2}": "Email dupliqué '{email}' trouvé dans les lignes de données {row1} et {row2}",
    "Template reference '{ref}' in {filename} not found in CSV columns": "Référence de modèle '{ref}' dans {filename} non trouvée dans les colonnes CSV",
    
    # File operation messages
    "No campaign loaded": "Aucune campagne chargée",
    "Recipients file successfully replaced with:": "Fichier des destinataires remplacé avec succès par :",
    "Failed to replace recipients file:": "Échec du remplacement du fichier des destinataires :",
    "Subject file successfully replaced with:": "Fichier de sujet remplacé avec succès par :",
    "Failed to replace subject file:": "Échec du remplacement du fichier de sujet :",
    "Failed to replace message file:": "Échec du remplacement du fichier de message :",
    "Failed to delete attachments:": "Échec de la suppression des pièces jointes :",
    
    # Campaign tab validation
    "🔍 Validation Issues": "🔍 Problèmes de Validation",
    "✅ No validation issues found": "✅ Aucun problème de validation trouvé",
    
    # Project management
    "Project '{project_name}' already exists": "Le projet '{project_name}' existe déjà",
    "Project '{project_name}' created successfully!": "Projet '{project_name}' créé avec succès !",
    "Project '{}' created successfully": "Projet '{}' créé avec succès",
    "Failed to load project: {str(e)}": "Échec du chargement du projet : {str(e)}",
    "Failed to delete project: {str(e)}": "Échec de la suppression du projet : {str(e)}",
    "Failed to update fusion.csv: {str(e)}": "Échec de la mise à jour de fusion.csv : {str(e)}",
    "Failed to update template.jpg: {str(e)}": "Échec de la mise à jour de template.jpg : {str(e)}",
    "File '{filename}' already exists. Replace it?": "Le fichier '{filename}' existe déjà. Le remplacer ?",
    "Folder '{folder_name}' already exists. Replace it?": "Le dossier '{folder_name}' existe déjà. Le remplacer ?",
    "Added folder '{folder_name}' to project": "Dossier '{folder_name}' ajouté au projet",
    "Failed to open image: {str(e)}": "Échec de l'ouverture de l'image : {str(e)}",
    
    # Wizard content
    "Select or create a folder where your campaign files will be stored. This folder will contain all your campaign data including recipients, message templates, and attachments.": "Sélectionnez ou créez un dossier où vos fichiers de campagne seront stockés. Ce dossier contiendra toutes vos données de campagne incluant les destinataires, modèles de message et pièces jointes.",
    "Select a CSV file containing your recipients. The file should include an 'email' column and any other data you want to personalize your messages with (like name, company, etc.).": "Sélectionnez un fichier CSV contenant vos destinataires. Le fichier doit inclure une colonne 'email' et toute autre donnée que vous souhaitez utiliser pour personnaliser vos messages (comme nom, entreprise, etc.).",
    
    # SMTP configuration
    "ℹ️ No SMTP configuration found in this campaign": "ℹ️ Aucune configuration SMTP trouvée dans cette campagne",
    "SMTP Server:": "Serveur SMTP :",
    
    # Send tab - all remaining elements
    "📊 Campaign Status": "📊 Statut de la Campagne",
    "⚠️ No Campaign Loaded": "⚠️ Aucune Campagne Chargée",
    "👥 Recipients: No campaign": "👥 Destinataires : Aucune campagne",
    "📄 Message: No campaign": "📄 Message : Aucune campagne",
    "📎 Attachments: No campaign": "📎 Pièces jointes : Aucune campagne",
    "📎 Pictures: No campaign": "📎 Images : Aucune campagne",
    "🚀 Send Controls": "🚀 Contrôles d'Envoi",
    "Dry Run Name:": "Nom du Test :",
    "custom-name-here": "nom-personnalisé-ici",
    "🧪 Dry Run": "🧪 Test à Blanc",
    "🚀 Send Campaign": "🚀 Envoyer la Campagne",
    "🔍 Validation Results": "🔍 Résultats de Validation",
    "Validation results will appear here...": "Les résultats de validation apparaîtront ici...",
    "📁 Dry Run Results": "📁 Résultats des Tests",
    "📂 Open Selected": "📂 Ouvrir la Sélection",
    "📊 Sent Reports": "📊 Rapports d'Envoi",
    "Ready to send": "Prêt à envoyer",
}

def extract_all_untranslated_strings(ts_file_path):
    """Extract all untranslated strings from the TS file"""
    with open(ts_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all unfinished translations
    pattern = r'<source>(.*?)</source>\s*<translation type="unfinished"></translation>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    # Clean up the matches (remove extra whitespace, decode HTML entities)
    cleaned_matches = []
    for match in matches:
        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', match.strip())
        # Decode HTML entities
        cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>').replace('&apos;', "'").replace('&quot;', '"').replace('&amp;', '&')
        if cleaned:  # Only add non-empty strings
            cleaned_matches.append(cleaned)
    
    return cleaned_matches

def update_translation_file(ts_file_path):
    """Update the translation file with ALL remaining translations"""
    
    with open(ts_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates = 0
    
    # First, get all untranslated strings to see what we're missing
    untranslated = extract_all_untranslated_strings(ts_file_path)
    print(f"Found {len(untranslated)} untranslated strings:")
    for i, string in enumerate(untranslated[:10]):  # Show first 10
        print(f"  {i+1}. {string[:60]}...")
    if len(untranslated) > 10:
        print(f"  ... and {len(untranslated) - 10} more")
    print()
    
    # Apply all translations we have
    for english, french in COMPLETE_TRANSLATIONS.items():
        # Escape special characters for regex, but handle HTML entities
        escaped_english = re.escape(english)
        escaped_english = escaped_english.replace(r"\'", r"(&apos;|')")  # Handle both ' and &apos;
        escaped_english = escaped_english.replace(r'\"', r'(&quot;|")')  # Handle both " and &quot;
        escaped_english = escaped_english.replace(r'\<', r'(&lt;|<)')    # Handle both < and &lt;
        escaped_english = escaped_english.replace(r'\>', r'(&gt;|>)')    # Handle both > and &gt;
        
        # Pattern to match unfinished translation
        pattern = f'<source>{escaped_english}</source>\\s*<translation type="unfinished"></translation>'
        replacement = f'<source>{english}</source>\n        <translation>{french}</translation>'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updates += 1
            print(f"✅ Translated: {english[:50]}...")
    
    # Write back the updated content
    with open(ts_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎉 Updated {updates} translations!")
    return updates

if __name__ == "__main__":
    ts_file = Path("src/emailer_simple_tool/gui/translations/emailer_simple_tool_fr.ts")
    print("🌐 Completing ALL remaining translations for 100% coverage...")
    updates = update_translation_file(ts_file)
    
    if updates > 0:
        print(f"\n🔄 Recompiling translation file...")
        import subprocess
        result = subprocess.run([
            "pyside6-lrelease", 
            "emailer_simple_tool_fr.ts"
        ], cwd=ts_file.parent, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Translation file recompiled successfully!")
            print(result.stdout)
        else:
            print("❌ Failed to recompile translation file:")
            print(result.stderr)
    else:
        print("ℹ️  No translations were updated.")
