#!/usr/bin/env python3
"""
Final cleanup - translate the remaining critical strings manually
"""

import re
from pathlib import Path

# Final batch of translations - manually identified critical ones
FINAL_BATCH = {
    # Basic UI elements
    "Remove Selected": "Supprimer la Sélection",
    "< Back": "< Précédent", 
    "Next >": "Suivant >",
    "Finish": "Terminer",
    "Error": "Erreur",
    "Success": "Succès",
    "Warning": "Avertissement",
    "OK": "OK",
    "Yes": "Oui",
    "No": "Non",
    "Cancel": "Annuler",
    "Browse...": "Parcourir...",
    
    # File validation errors that are still missing
    "'recipients.csv' exists but is not a file": "'recipients.csv' existe mais n'est pas un fichier",
    "'subject.txt' exists but is not a file": "'subject.txt' existe mais n'est pas un fichier", 
    "'attachments' exists but is not a folder": "'attachments' existe mais n'est pas un dossier",
    "recipients.csv is empty": "recipients.csv est vide",
    "recipients.csv must contain an 'email' column": "recipients.csv doit contenir une colonne 'email'",
    "CSV must have at least one column when picture generator projects exist": "Le CSV doit avoir au moins une colonne quand des projets de générateur d'images existent",
    "No valid recipients found in CSV file": "Aucun destinataire valide trouvé dans le fichier CSV",
    "Subject file (subject.txt) must contain only one line. Email subjects cannot be multi-line.": "Le fichier de sujet (subject.txt) ne doit contenir qu'une seule ligne. Les sujets d'email ne peuvent pas être multi-lignes.",
    "'{filename}' exists but is not a file": "'{filename}' existe mais n'est pas un fichier",
    "Invalid email '{email}' in data row {row}": "Email invalide '{email}' dans la ligne de données {row}",
    
    # File operations
    "Recipients file successfully replaced with:": "Fichier des destinataires remplacé avec succès par :",
    "Failed to replace recipients file:": "Échec du remplacement du fichier des destinataires :",
    "Subject file successfully replaced with:": "Fichier de sujet remplacé avec succès par :",
    "Failed to replace subject file:": "Échec du remplacement du fichier de sujet :",
    "Failed to replace message file:": "Échec du remplacement du fichier de message :",
    "Failed to delete attachments:": "Échec de la suppression des pièces jointes :",
    
    # Project operations
    "Project '{project_name}' already exists": "Le projet '{project_name}' existe déjà",
    "Project '{project_name}' created successfully!": "Projet '{project_name}' créé avec succès !",
    "Failed to create project: {str(e)}": "Échec de la création du projet : {str(e)}",
    "Failed to load project: {str(e)}": "Échec du chargement du projet : {str(e)}",
    "Failed to delete project: {str(e)}": "Échec de la suppression du projet : {str(e)}",
    "Failed to duplicate project: {}": "Échec de la duplication du projet : {}",
    "A project with this name already exists": "Un projet avec ce nom existe déjà",
    
    # Wizard content
    "Enter email subject line...": "Entrez la ligne d'objet de l'email...",
    "Select destination folder...": "Sélectionnez le dossier de destination...",
    "Select message template (.txt or .docx)...": "Sélectionnez le modèle de message (.txt ou .docx)...",
    "Select recipients CSV file...": "Sélectionnez le fichier CSV des destinataires...",
    
    # Picture tab
    "No project loaded": "Aucun projet chargé",
    "Select the project to load": "Sélectionnez le projet à charger",
    "Error reading projects": "Erreur lors de la lecture des projets",
    "No project created yet": "Aucun projet créé pour l'instant",
    "Please load a campaign first": "Veuillez d'abord charger une campagne",
    "Project deleted successfully": "Projet supprimé avec succès",
    "fusion.csv file updated": "Fichier fusion.csv mis à jour",
    "template.jpg file updated": "Fichier template.jpg mis à jour",
    "Project validation passed": "Validation du projet réussie",
    "No validation issues found": "Aucun problème de validation trouvé",
    "Please fix validation errors before generating pictures": "Veuillez corriger les erreurs de validation avant de générer les images",
    "Starting picture generation...": "Démarrage de la génération d'images...",
    "Please select images to open": "Veuillez sélectionner les images à ouvrir",
    
    # File dialogs
    "Supported files (*.png *.jpg *.jpeg *.docx *.txt)": "Fichiers supportés (*.png *.jpg *.jpeg *.docx *.txt)",
    "Image files (*.jpg *.jpeg)": "Fichiers image (*.jpg *.jpeg)",
    "CSV files (*.csv)": "Fichiers CSV (*.csv)",
    
    # Common status messages
    "Info": "Information",
    "File Exists": "Fichier Existant", 
    "Folder Exists": "Dossier Existant",
    "Validation Error": "Erreur de Validation",
    "Delete Project": "Supprimer le Projet",
    "Duplicate Project": "Dupliquer le Projet",
}

def apply_final_translations(ts_file_path):
    """Apply the final batch of translations"""
    
    with open(ts_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates = 0
    
    for english, french in FINAL_BATCH.items():
        # Handle both regular quotes and HTML entities
        patterns = [
            f'<source>{re.escape(english)}</source>\\s*<translation type="unfinished"></translation>',
            f'<source>{re.escape(english).replace(r"\'", "&apos;")}</source>\\s*<translation type="unfinished"></translation>',
        ]
        
        replacement = f'<source>{english}</source>\n        <translation>{french}</translation>'
        
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updates += 1
                print(f"✅ Translated: {english[:50]}...")
                break
    
    with open(ts_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎉 Applied {updates} final translations!")
    return updates

if __name__ == "__main__":
    ts_file = Path("src/emailer_simple_tool/gui/translations/emailer_simple_tool_fr.ts")
    print("🌐 Applying final batch of critical translations...")
    updates = apply_final_translations(ts_file)
