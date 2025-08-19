# Emailer Simple Tool Documentation

**Choose your language / Choisissez votre langue**

---

## 🇺🇸 English Documentation

**Complete user guide in English**

📖 **[Read the English Documentation](DOCUMENTATION_EN.md)**

**What you'll find:**
- Installation instructions for Windows, Mac, and Linux
- 5-minute quick start guide
- Complete user guide with examples
- Advanced features (picture generation, rich text)
- Troubleshooting and FAQ
- Performance guidelines

---

## 🇫🇷 Documentation Française

**Guide utilisateur complet en français**

📖 **[Lire la Documentation Française](DOCUMENTATION_FR.md)**

**Ce que vous trouverez :**
- Instructions d'installation pour Windows, Mac et Linux
- Guide de démarrage rapide en 5 minutes
- Guide utilisateur complet avec exemples
- Fonctionnalités avancées (génération d'images, texte enrichi)
- Dépannage et FAQ
- Directives de performance

---

## Quick Reference / Référence Rapide

### Installation
```bash
pip install emailer-simple-tool
```

### Basic Usage / Utilisation de Base
```bash
# Create campaign / Créer une campagne
emailer-simple-tool config create /path/to/campaign

# Configure email / Configurer l'email
emailer-simple-tool config smtp

# Test first / Tester d'abord
emailer-simple-tool send --dry-run

# Send emails / Envoyer les emails
emailer-simple-tool send
```

### Help / Aide
```bash
emailer-simple-tool --help
emailer-simple-tool config --help
emailer-simple-tool send --help
```

---

## File Structure / Structure des Fichiers

```
Campaign Folder / Dossier Campagne/
├── recipients.csv          # Required / Requis
├── subject.txt            # Required / Requis  
├── msg.txt or msg.docx    # Required / Requis
├── attachments/           # Optional / Optionnel
└── picture-generator/     # Optional / Optionnel
```

---

## Support

- 📖 Read the full documentation in your language
- 🧪 Always test with `--dry-run` first
- 📧 Keep recipient lists under 100 for best performance

**English**: [DOCUMENTATION_EN.md](DOCUMENTATION_EN.md)
**Français**: [DOCUMENTATION_FR.md](DOCUMENTATION_FR.md)

---

*Emailer Simple Tool - Making personalized email campaigns simple and accessible.*
*Emailer Simple Tool - Rendre les campagnes d'emails personnalisés simples et accessibles.*
