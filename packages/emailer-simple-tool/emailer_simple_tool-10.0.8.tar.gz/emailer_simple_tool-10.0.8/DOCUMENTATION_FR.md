# Emailer Simple Tool - Documentation Utilisateur Complète

**Envoyez des emails personnalisés à plusieurs personnes facilement et en toute sécurité**

---

## Table des Matières

1. [Qu'est-ce qu'Emailer Simple Tool ?](#quest-ce-quemailer-simple-tool)
2. [Installation](#installation)
3. [Démarrage Rapide (5 minutes)](#démarrage-rapide-5-minutes)
4. [Guide Utilisateur Complet](#guide-utilisateur-complet)
5. [Fonctionnalités Avancées](#fonctionnalités-avancées)
6. [Dépannage et FAQ](#dépannage-et-faq)
7. [Performance et Limites](#performance-et-limites)

---

## Qu'est-ce qu'Emailer Simple Tool ?

Emailer Simple Tool est une application simple qui permet aux utilisateurs d'envoyer des emails personnalisés à une liste de destinataires via une interface en ligne de commande intuitive.

### Fonctionnalités Principales
- **Personnalisation d'Emails**: Personnalisez l'objet et le corps du message en utilisant les données des destinataires depuis des fichiers CSV
- **Support de Texte Enrichi**: Utilisez des fichiers .docx formatés avec polices, couleurs et styles
- **Génération d'Images**: Créez des images personnalisées avec texte et graphiques
- **Pièces Jointes Statiques**: Joignez des documents à tous les emails d'une campagne
- **Gestion de Campagnes**: Sauvegardez, rouvrez et gérez les campagnes email avec une structure basée sur des dossiers
- **Validation des Données**: Validation complète des données des destinataires et des modèles d'email
- **Test à Blanc**: Prévisualisez les emails générés sous forme de fichiers .eml avant envoi
- **Dépannage SMTP**: Guidance intégrée pour les problèmes de livraison d'emails

### Parfait Pour
- Invitations d'événements avec détails personnels
- Newsletters avec noms des destinataires
- Communications d'affaires à plusieurs clients
- Campagnes marketing avec images personnalisées
- Tout email où vous voulez inclure des informations personnelles pour chaque destinataire

---

## Installation

### Pour les Utilisateurs Windows

#### Méthode 1 : Installation Simple (Recommandée)

1. **Téléchargez Python** (si pas déjà installé) :
   - Allez sur https://python.org/downloads
   - Cliquez sur "Download Python" (dernière version)
   - Lancez l'installateur
   - ⚠️ **Important** : Cochez "Add Python to PATH" pendant l'installation

2. **Installez Emailer Simple Tool** :
   - Appuyez sur `Touche Windows + R`
   - Tapez `cmd` et appuyez sur Entrée
   - Dans la fenêtre noire qui s'ouvre, tapez :
     ```
     pip install emailer-simple-tool
     ```
   - Appuyez sur Entrée et attendez que l'installation se termine

3. **Vérifiez l'Installation** :
   ```
   emailer-simple-tool --version
   ```

### Pour les Utilisateurs Mac

1. **Installez Python** (si pas déjà installé) :
   - Téléchargez depuis https://python.org/downloads
   - Ou utilisez Homebrew : `brew install python`

2. **Installez Emailer Simple Tool** :
   ```bash
   pip3 install emailer-simple-tool
   ```

3. **Vérifiez l'Installation** :
   ```bash
   emailer-simple-tool --version
   ```

### Pour les Utilisateurs Linux

1. **Installez Python** (généralement pré-installé) :
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Installez Emailer Simple Tool** :
   ```bash
   pip3 install emailer-simple-tool
   ```

3. **Vérifiez l'Installation** :
   ```bash
   emailer-simple-tool --version
   ```

---

## Démarrage Rapide (5 minutes)

### Ce Dont Vous Avez Besoin
- Un dossier sur votre ordinateur
- Une liste d'adresses email (peut venir d'Excel)
- Les informations de votre compte email

### Étape 1 : Créez Vos Fichiers (2 minutes)

**Créez un dossier** appelé "Ma Campagne Email" sur votre bureau.

**Dans ce dossier, créez 3 fichiers :**

**Fichier 1 : `recipients.csv`** (votre liste d'emails)
```csv
email,nom,entreprise
jean@exemple.com,Jean Dupont,ACME Corp
marie@exemple.com,Marie Martin,Tech Inc
pierre@exemple.com,Pierre Durand,Design Co
```

**Fichier 2 : `subject.txt`** (l'objet de votre email)
```
Bienvenue {{nom}} à notre événement !
```

**Fichier 3 : `msg.txt`** (votre message email)
```
Cher {{nom}},

Nous sommes ravis de vous inviter depuis {{entreprise}} à notre événement spécial.

Cordialement,
L'Équipe Événement
```

### Étape 2 : Configurez Votre Campagne (1 minute)

Ouvrez votre invite de commande/terminal et naviguez vers votre dossier :
```bash
cd "Bureau/Ma Campagne Email"
emailer-simple-tool config create .
```

### Étape 3 : Configurez les Paramètres Email (1 minute)

```bash
emailer-simple-tool config smtp
```

Suivez les instructions pour entrer vos paramètres email :
- **Gmail** : smtp.gmail.com, port 587, utilisez un mot de passe d'application
- **Outlook** : smtp-mail.outlook.com, port 587
- **Yahoo** : smtp.mail.yahoo.com, port 587

### Étape 4 : Testez et Envoyez (1 minute)

**Testez d'abord** (crée des fichiers de prévisualisation) :
```bash
emailer-simple-tool send --dry-run
```

**Envoyez pour de vrai** :
```bash
emailer-simple-tool send
```

🎉 **Terminé !** Vos emails personnalisés sont envoyés !

---

## Guide Utilisateur Complet

### Structure de Campagne

Chaque campagne email est organisée dans un dossier avec ces fichiers :

```
Ma Campagne/
├── recipients.csv          # Requis : Liste des destinataires
├── subject.txt            # Requis : Ligne d'objet email
├── msg.txt ou msg.docx    # Requis : Message email
├── attachments/           # Optionnel : Fichiers à joindre
│   ├── document.pdf
│   └── image.jpg
└── picture-generator/     # Optionnel : Images personnalisées
    └── mon-projet/
        ├── template.jpg
        ├── fusion.csv
        └── data/
```

### Fichier Destinataires (recipients.csv)

Ce fichier CSV contient votre liste de destinataires. La première ligne définit les noms de colonnes, que vous pouvez utiliser comme variables dans vos messages.

**Exemple Basique :**
```csv
email,nom,entreprise
jean@exemple.com,Jean Dupont,ACME Corp
marie@exemple.com,Marie Martin,Tech Inc
```

**Exemple Avancé :**
```csv
email,nom,entreprise,date_evenement,type_billet
jean@exemple.com,Jean Dupont,ACME Corp,2024-03-15,VIP
marie@exemple.com,Marie Martin,Tech Inc,2024-03-15,Standard
```

**Règles :**
- La première colonne doit être `email`
- Les noms de colonnes deviennent des variables : `{{nom}}`, `{{entreprise}}`
- Pas d'espaces dans les noms de colonnes (utilisez des underscores : `date_evenement`)
- Sauvegardez au format CSV depuis Excel

### Fichiers de Message

#### Messages Texte Simple (msg.txt)
```
Cher {{nom}},

Bienvenue à notre événement le {{date_evenement}}.
Votre billet {{type_billet}} est confirmé.

Cordialement,
Équipe Événement
```

#### Messages Formatés Enrichis (msg.docx)
Créez un document Word avec :
- **Polices** : Différentes polices, tailles, couleurs
- **Formatage** : Gras, italique, souligné
- **Tableaux** : Données structurées
- **Images** : Images statiques (logos, etc.)
- **Variables** : Utilisez `{{nom}}` n'importe où dans le document

**Exemple de message formaté :**
- Titre en texte large, gras, bleu : "Bienvenue {{nom}} !"
- Corps en texte normal avec nom d'entreprise en rouge : "De {{entreprise}}"
- Pied de page avec informations de contact en italique

### Ligne d'Objet (subject.txt)
```
Invitation Événement pour {{nom}} - {{date_evenement}}
```

### Pièces Jointes
Placez tous les fichiers que vous voulez joindre dans le dossier `attachments/` :
- PDFs, documents Word, images
- Tous les fichiers seront joints à chaque email
- Gardez la taille totale sous 25MB par email

### Référence des Commandes

#### Gestion de Campagne
```bash
# Créer/charger une campagne
emailer-simple-tool config create /chemin/vers/campagne

# Afficher le statut de la campagne actuelle
emailer-simple-tool config show

# Basculer vers une campagne différente
emailer-simple-tool config create /chemin/vers/autre/campagne
```

#### Configuration SMTP
```bash
# Configurer les paramètres email
emailer-simple-tool config smtp

# Tester la connexion email
emailer-simple-tool config smtp --test
```

#### Envoi d'Emails
```bash
# Prévisualiser les emails (crée des fichiers .eml)
emailer-simple-tool send --dry-run

# Envoyer les emails pour de vrai
emailer-simple-tool send

# Envoyer avec délai personnalisé entre emails
emailer-simple-tool send --delay 2
```

#### Génération d'Images
```bash
# Lister les projets d'images
emailer-simple-tool picture list

# Générer des images pour un projet
emailer-simple-tool picture generate nom-projet

# Générer tous les projets d'images
emailer-simple-tool picture generate-all
```

---

## Fonctionnalités Avancées

### Génération d'Images

Créez des images personnalisées pour chaque destinataire avec texte, graphiques et formatage.

#### Configuration des Projets d'Images

1. **Créez le dossier projet :**
   ```
   picture-generator/
   └── mon-invitation/
       ├── template.jpg      # Image de fond
       ├── fusion.csv        # Instructions
       └── data/            # Images générées apparaissent ici
   ```

2. **Créez l'image modèle** (`template.jpg`) :
   - Image de fond (JPG, PNG)
   - Toute taille, recommandé 800x600 ou plus

3. **Créez les instructions de fusion** (`fusion.csv`) :
   ```csv
   fusion-type,data,positioning,size,alignment,orientation,font,shape,color
   text,{{nom}},100:50,24,center,0,Arial,bold,red
   text,{{entreprise}},100:100,16,center,0,Helvetica,italic,blue
   formatted-text,invitation.docx,50:200,400:200,left,0,,,
   ```

#### Types de Fusion

**Fusion Texte :**
- `fusion-type` : `text`
- `data` : Texte à afficher (peut utiliser `{{variables}}`)
- `positioning` : coordonnées `x:y`
- `size` : Taille de police en points
- `alignment` : `left`, `center`, `right`
- `font` : Famille de police (`Arial`, `Helvetica`, `Courier`, `Monaco`)
- `shape` : Style de police (`bold`, `italic`, `bold italic`)
- `color` : Couleur du texte (`red`, `blue`, `green`, `black`, etc.)

**Fusion Texte Formaté :**
- `fusion-type` : `formatted-text`
- `data` : Chemin vers fichier .docx avec formatage riche
- `positioning` : coordonnées `x:y` pour le coin supérieur gauche
- `size` : `largeur:hauteur` de la zone rendue
- `alignment` : `left`, `center`, `right`

**Fusion Graphique :**
- `fusion-type` : `graphic`
- `data` : Chemin vers fichier image (peut utiliser `{{variables}}` pour images personnalisées)
- `positioning` : coordonnées `x:y`
- `size` : `largeur:hauteur` ou valeur unique pour mise à l'échelle proportionnelle

#### Exemple : Invitation Événement

**Modèle :** Image de fond avec thème d'événement
**Instructions de fusion :**
```csv
fusion-type,data,positioning,size,alignment,orientation,policy,shape,color
text,Bienvenue {{nom}} !,400:100,32,center,0,Arial,bold,white
text,{{entreprise}},400:150,18,center,0,Arial,,white
text,Date Événement: 15 Mars 2024,400:300,16,center,0,Courier,,yellow
formatted-text,details-evenement.docx,50:400,700:200,left,0,,,
```

### Messages Texte Enrichi (.docx)

Utilisez Microsoft Word pour créer des messages email formatés :

1. **Créez un document Word** avec formatage :
   - Polices, couleurs, tailles
   - Gras, italique, souligné
   - Tableaux et listes
   - Images statiques

2. **Ajoutez des variables** n'importe où : `{{nom}}`, `{{entreprise}}`

3. **Sauvegardez en .docx** dans le dossier campagne comme `msg.docx`

4. **Prévisualisez avec test à blanc** - crée des fichiers .eml que vous pouvez ouvrir dans votre client email

### Prévisualisation Email (fichiers .eml)

Quand vous lancez `--dry-run`, le système crée des fichiers .eml que vous pouvez :
- Double-cliquer pour ouvrir dans votre client email
- Prévisualiser exactement comment les emails apparaîtront
- Vérifier le formatage, images et personnalisation
- Vérifier avant envoi

---

## Dépannage et FAQ

### Questions Générales

**Q : Dois-je être technique pour utiliser ceci ?**
R : Non ! Si vous savez utiliser Excel et l'email, vous pouvez utiliser cet outil.

**Q : Est-ce sûr à utiliser ?**
R : Oui. Vos mots de passe email sont chiffrés et stockés uniquement sur votre ordinateur.

**Q : Combien d'emails puis-je envoyer ?**
R : Conçu pour jusqu'à 100 destinataires par campagne. Pour des listes plus grandes, divisez en groupes plus petits.

### Paramètres Fournisseurs Email

**Gmail :**
- Serveur : `smtp.gmail.com`
- Port : `587`
- Sécurité : Utilisez un Mot de Passe d'Application (pas le mot de passe normal)
- Activez d'abord l'authentification à 2 facteurs

**Outlook/Hotmail :**
- Serveur : `smtp-mail.outlook.com`
- Port : `587`
- Utilisez le mot de passe normal

**Yahoo :**
- Serveur : `smtp.mail.yahoo.com`
- Port : `587`
- Utilisez un Mot de Passe d'Application

**Email d'Entreprise :**
- Contactez votre département IT pour les paramètres SMTP

### Problèmes Courants

**"Échec d'authentification"**
- Vérifiez nom d'utilisateur/mot de passe
- Pour Gmail : Utilisez un Mot de Passe d'Application
- Activez "Applications moins sécurisées" si nécessaire

**"Connexion refusée"**
- Vérifiez l'adresse serveur et le port
- Vérifiez la connexion internet
- Essayez un port différent (25, 465, 587)

**"Fichier non trouvé"**
- Vérifiez les chemins de fichiers dans fusion.csv
- Assurez-vous que tous les fichiers référencés existent
- Utilisez des barres obliques dans les chemins

**"Variables de modèle non remplacées"**
- Vérifiez l'orthographe : `{{nom}}` pas `{nom}`
- Assurez-vous que la colonne existe dans recipients.csv
- Pas d'espaces dans les noms de colonnes

**Images ne se génèrent pas**
- Vérifiez que l'image modèle existe
- Vérifiez le format de fusion.csv
- Assurez-vous que les coordonnées de positionnement sont dans les limites de l'image

### Conseils de Performance

- Gardez les listes de destinataires sous 100 pour de meilleures performances
- Utilisez l'option `--delay` pour les grandes listes
- Optimisez les tailles d'images (sous 1MB recommandé)
- Testez avec de petits groupes d'abord

---

## Performance et Limites

### Performance Testée
- **Génération d'Images** : 180 images/seconde
- **Traitement d'Emails** : 478 emails/seconde
- **Opérations Concurrentes** : 976 emails/seconde

### Limites Recommandées
- **Destinataires** : Jusqu'à 100 par campagne
- **Pièces Jointes** : Taille totale sous 25MB
- **Images** : Sous 1MB chacune pour de meilleures performances
- **Taux d'Email** : Utilisez des délais pour les grandes listes pour éviter les limites des fournisseurs

### Exigences Système
- **Python** : 3.8 ou supérieur
- **Mémoire** : 512MB de RAM disponible
- **Stockage** : 100MB pour l'installation + données de campagne
- **Réseau** : Connexion internet pour envoyer les emails

---

## Support

Pour les problèmes ou questions :
1. Consultez cette documentation
2. Examinez attentivement les messages d'erreur
3. Testez avec de petites listes de destinataires d'abord
4. Vérifiez tous les chemins de fichiers et formats

**Rappel** : Testez toujours avec `--dry-run` avant d'envoyer de vrais emails !

---

*Emailer Simple Tool - Rendre les campagnes d'emails personnalisés simples et accessibles.*
