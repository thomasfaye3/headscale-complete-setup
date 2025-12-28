# Guide de compilation de l'installeur Windows

Ce guide explique comment compiler l'installeur Headscale en fichier .exe distributable.

---

## 📋 Prérequis

### Logiciels requis

1. **Python 3.8+**
   - Télécharger : https://www.python.org/downloads/
   - ✅ Cocher "Add Python to PATH" pendant l'installation

2. **PyInstaller**
   ```powershell
   pip install pyinstaller
   ```

3. **Windows SDK** (pour la signature de code - optionnel)
   - Télécharger : https://developer.microsoft.com/windows/downloads/windows-sdk/

### Fichiers nécessaires

```
📁 Dossier de travail/
├── headscale_installer.py      # Script Python (EN)
├── headscale_installer_fr.py   # Script Python (FR)
├── build.bat                   # Script de compilation
├── sign.ps1                    # Script de signature (optionnel)
└── icon.ico                    # Icône (optionnel)
```

---

## 🔧 Étape 1 : Configuration du script

### 1.1 Éditer le script Python

Ouvrez `headscale_installer.py` (ou `headscale_installer_fr.py`) et modifiez :

```python
# Ligne ~17-19
HEADSCALE_URL = "https://vpn.example.com"  # Votre URL Headscale
AUTH_KEY = "VOTRE_CLE_PREAUTH"             # Votre clé pré-auth
BASE_DOMAIN = "vpn.example.com"            # Votre domaine MagicDNS
```

**Pour obtenir votre clé pré-auth :**
```bash
# Sur votre serveur Headscale
headscale users list  # Notez l'ID
headscale preauthkeys create --user 1 --reusable --expiration 365d
```

### 1.2 Sauvegarder le script

Enregistrez les modifications.

---

## 🏗️ Étape 2 : Compilation

### 2.1 Lancer la compilation

**Double-cliquez sur `build.bat`** ou lancez depuis PowerShell :

```powershell
.\build.bat
```

### 2.2 Processus de compilation

Le script va :
1. ✅ Nettoyer les compilations précédentes
2. ✅ Vérifier Python et PyInstaller
3. ✅ Compiler le script en .exe
4. ✅ Créer le dossier `dist\`

### 2.3 Résultat

Si tout va bien :
```
========================================
BUILD SUCCESS!
========================================

Executable: dist\HeadscaleInstaller.exe
Size: ~15 MB
```

L'exécutable se trouve dans : **`dist\HeadscaleInstaller.exe`**

---

## 🔏 Étape 3 : Signature de code (Optionnel mais recommandé)

### Pourquoi signer ?

- ✅ Évite les warnings Windows Defender
- ✅ Montre le nom de votre organisation
- ✅ Inspire confiance aux utilisateurs
- ✅ Requis pour déploiement en entreprise

### 3.1 Obtenir un certificat

**Option A : Acheter un certificat**
- Fournisseurs : Sectigo, DigiCert, GlobalSign
- Coût : ~100-300€/an
- Certificat OV ou EV recommandé

**Option B : Certificat auto-signé (tests uniquement)**
- Gratuit mais génère des warnings
- Uniquement pour tests internes

### 3.2 Signer l'exe

**Lancer le script de signature :**

```powershell
# Clic droit sur PowerShell → Exécuter en tant qu'administrateur
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\sign.ps1
```

**Le script vous demandera :**
1. Méthode de signature (certificat store, PFX, ou self-signed)
2. Informations du certificat
3. Mot de passe (si PFX)

### 3.3 Vérification

Le script vérifie automatiquement la signature. Vous pouvez aussi :

```powershell
# Dans PowerShell
Get-AuthenticodeSignature dist\HeadscaleInstaller.exe | Format-List
```

**Ou clic droit sur l'exe → Propriétés → Signatures numériques**

---

## 📦 Étape 4 : Distribution

### 4.1 Tester l'exe

**Sur une machine de test :**
1. Copiez `dist\HeadscaleInstaller.exe`
2. Lancez-le
3. Vérifiez :
   - ✅ Installation Tailscale
   - ✅ Connexion à Headscale
   - ✅ Appareil visible dans `headscale nodes list`

### 4.2 Méthodes de distribution

**Option A : Partage réseau**
```
\\serveur\partage\HeadscaleInstaller.exe
```

**Option B : Clé USB**
- Copiez l'exe sur une clé
- Distribuez aux utilisateurs

**Option C : Email** (si < 25 MB)
- Attention : certains emails bloquent les .exe
- Compresser en .zip peut aider

**Option D : Serveur web interne**
```
http://intranet.company.com/tools/HeadscaleInstaller.exe
```

### 4.3 Documentation utilisateur

Créez un document simple pour vos utilisateurs :

```
📄 Installation VPN - Guide utilisateur

1. Téléchargez HeadscaleInstaller.exe
2. Double-cliquez sur le fichier
3. Si Windows demande confirmation, cliquez "Exécuter quand même"
4. Remplissez votre nom et le type d'appareil
5. Cliquez "Installer"
6. Attendez la fin de l'installation
7. L'icône Tailscale apparaît dans la barre des tâches

Support : support@votreentreprise.com
```

---

## 🔧 Dépannage

### Erreur : "PyInstaller not found"

```powershell
pip install pyinstaller
```

### Erreur : "SignTool not found"

Installez Windows SDK :
https://developer.microsoft.com/windows/downloads/windows-sdk/

### L'exe est détecté comme virus

**Causes possibles :**
- Pas de signature de code
- Signature self-signed
- PyInstaller flaggé par certains antivirus

**Solutions :**
1. Signer avec un certificat valide
2. Soumettre à VirusTotal
3. Ajouter une exclusion antivirus

### L'exe ne fonctionne pas sur certains PC

**Vérifiez :**
- Windows 10/11 64-bit requis
- Connexion Internet disponible
- Droits administrateur

---

## 📊 Résumé du workflow complet

```
1. Configuration
   ├── Éditer headscale_installer.py
   ├── Configurer URL, AUTH_KEY, DOMAIN
   └── Sauvegarder

2. Compilation
   ├── Lancer build.bat
   ├── Attendre la fin
   └── Vérifier dist\HeadscaleInstaller.exe

3. Signature (optionnel)
   ├── Obtenir certificat
   ├── Lancer sign.ps1
   └── Vérifier signature

4. Test
   ├── Installer sur PC test
   ├── Vérifier connexion Headscale
   └── Valider fonctionnement

5. Distribution
   ├── Copier vers partage/USB/email
   ├── Documenter pour utilisateurs
   └── Fournir support
```

---

## 📝 Fichiers de sortie

Après compilation, vous aurez :

```
dist/
├── HeadscaleInstaller.exe    # Fichier à distribuer (~15 MB)

build/                         # Fichiers temporaires (peut être supprimé)
└── ...

HeadscaleInstaller.spec        # Config PyInstaller (peut être supprimé)
```

**Seul `dist\HeadscaleInstaller.exe` est nécessaire pour la distribution.**

---

## 🔄 Mise à jour de l'installeur

Pour créer une nouvelle version :

1. Modifiez `headscale_installer.py`
2. Changez `VERSION = "1.0.1"` (ligne ~21)
3. Relancez `build.bat`
4. Signez la nouvelle version
5. Redistribuez

---

## 📧 Support

Pour des questions :
- [Documentation Headscale](https://headscale.net/)
- [GitHub Headscale](https://github.com/juanfont/headscale)

---

**Bon déploiement ! 🚀**
