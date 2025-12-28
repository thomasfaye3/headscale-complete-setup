# Installeur client Windows

Ce guide explique comment créer un installeur Windows personnalisé (.exe) pour déployer des clients Tailscale configurés pour votre serveur Headscale.

## Vue d'ensemble

L'installeur fournit :
- ✅ Installation automatisée de Tailscale
- ✅ URL du serveur Headscale pré-configurée
- ✅ Interface graphique conviviale pour nommer les clients
- ✅ Intégration de la clé de pré-authentification
- ✅ Installation silencieuse en arrière-plan
- ✅ Démarrage automatique du service

## Prérequis

- **Python 3.8+** installé sur Windows (pour le développement)
- **PyInstaller** pour créer l'exe
- **SignTool** (optionnel, pour la signature de code)
- **Clé de pré-auth** de votre serveur Headscale

## Étape 1 : Préparer le script Python

### 1.1 Télécharger le script d'installation

Téléchargez `headscale_installer_fr.py` depuis ce dépôt.

### 1.2 Configurer vos paramètres

Éditez le script et mettez à jour ces valeurs :

```python
# Ligne ~17-19
HEADSCALE_URL = "https://vpn.example.com"  # URL de votre serveur Headscale
AUTH_KEY = "votre-cle-preauth-ici"         # Votre clé de pré-auth
BASE_DOMAIN = "vpn.example.com"            # Votre domaine MagicDNS
```

**Pour obtenir votre clé de pré-auth :**
```bash
# Sur votre serveur Headscale
headscale users list  # Obtenir l'ID utilisateur
headscale preauthkeys create --user 1 --reusable --expiration 365d
```

## Étape 2 : Installer les dépendances

```powershell
# Installer les packages Python requis
pip install pyinstaller
```

## Étape 3 : Compiler l'exécutable

### 3.1 Créer le script de compilation

Créez `build.bat` :

```batch
@echo off
echo Compilation de l'installeur Headscale...

REM Nettoyer les compilations précédentes
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Compiler l'exécutable
pyinstaller --onefile --windowed --icon=icon.ico --name="InstallateurHeadscale" headscale_installer_fr.py

echo.
echo Compilation terminee! L'executable est dans dist\InstallateurHeadscale.exe
pause
```

### 3.2 Ajouter une icône (optionnel)

Placez un fichier `icon.ico` dans le même répertoire, ou supprimez `--icon=icon.ico` de la commande de compilation.

### 3.3 Compiler

```powershell
.\build.bat
```

L'exécutable sera créé dans `dist\InstallateurHeadscale.exe`

## Étape 4 : Signature de code (Optionnel mais recommandé)

### Pourquoi signer votre exécutable ?

- ✅ Évite les avertissements Windows Defender
- ✅ Affiche le nom de votre organisation
- ✅ Inspire confiance aux utilisateurs
- ✅ Requis pour le déploiement en entreprise

### 4.1 Obtenir un certificat de signature de code

**Option 1 : Acheter auprès d'une autorité de certification**
- Sectigo, DigiCert, GlobalSign
- Coût : ~100-300€/an
- Fournit un certificat EV ou OV

**Option 2 : Certificat auto-signé (tests uniquement)**

**⚠️ Attention :** Les certificats auto-signés déclencheront toujours des avertissements. Ils ne sont utiles que pour les tests.

```powershell
# Créer un certificat auto-signé (PowerShell en Admin)
$cert = New-SelfSignedCertificate -Subject "CN=VotreEntreprise" -Type CodeSigningCert -CertStoreLocation Cert:\CurrentUser\My

# Exporter le certificat
Export-Certificate -Cert $cert -FilePath "VotreEntreprise.cer"

# Signer l'exécutable
signtool sign /f "VotreEntreprise.cer" /fd SHA256 /t http://timestamp.digicert.com dist\InstallateurHeadscale.exe
```

### 4.2 Signer avec un certificat acheté

```powershell
# Si le certificat est dans le magasin de certificats Windows
signtool sign /n "VotreEntreprise" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\InstallateurHeadscale.exe

# Si le certificat est dans un fichier .pfx
signtool sign /f certificat.pfx /p VotreMotDePasse /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\InstallateurHeadscale.exe
```

### 4.3 Vérifier la signature

```powershell
signtool verify /pa /v dist\InstallateurHeadscale.exe
```

## Étape 5 : Tester l'installeur

1. Exécutez `InstallateurHeadscale.exe` sur une machine de test
2. Remplissez le nom du client et le type d'appareil
3. Cliquez sur "Installer"
4. Vérifiez :
   - Tailscale s'installe avec succès
   - L'appareil apparaît dans Headscale : `headscale nodes list`
   - L'appareil peut communiquer avec d'autres nœuds

## Déploiement

### Pour plusieurs appareils :

1. **Partagez l'exécutable** via :
   - Partage réseau
   - Clé USB
   - Email (si assez petit)
   - Serveur web interne

2. **Documentez le processus :**
   - Créez un guide utilisateur avec captures d'écran
   - Incluez un contact support
   - Expliquez ce que fait l'installeur

3. **Suivez les déploiements :**
   - Surveillez `headscale nodes list`
   - Documentez quels appareils sont connectés
   - Gardez la clé de pré-auth sécurisée

## Personnalisation

### Changer l'apparence de la fenêtre

Éditez ces lignes dans `headscale_installer_fr.py` :

```python
# Ligne ~120-130
bg_color = "#f5f5f5"      # Couleur de fond
primary_color = "#2563eb"  # Couleur primaire (bleu)
accent_color = "#1e40af"   # Couleur d'accentuation (bleu foncé)
```

### Modifier le nommage des clients

L'installeur génère des noms d'hôtes comme : `{client}-{type}`

Exemple : `NomEntreprise-PC-Bureau` devient `nomentreprise-pc-bureau.vpn.example.com`

Vous pouvez modifier la fonction `generate_hostname()` pour changer ce comportement.

### Ajouter un logo d'entreprise

1. Convertir le logo en Base64
2. Ajouter au début du script
3. Afficher dans l'interface avec tkinter

## Dépannage

### Avertissement "Windows a protégé votre PC"

**Cause :** L'exécutable n'est pas signé ou utilise un certificat auto-signé

**Solutions :**
1. Cliquez sur "Plus d'infos" → "Exécuter quand même" (tests)
2. Obtenez un certificat de signature de code approprié
3. Ajoutez aux exclusions Windows Defender
4. Distribuez via le centre de logiciels de l'entreprise

### L'installation échoue

**Vérifiez :**
1. L'utilisateur a les droits administrateur
2. Connexion Internet disponible
3. L'antivirus ne bloque pas
4. URL Headscale correcte
5. Clé de pré-auth valide

**Déboguer :**
- Vérifiez les logs dans : `%TEMP%\headscale-install.log`
- Exécutez l'installeur depuis l'invite de commandes pour voir les erreurs

### L'appareil n'apparaît pas dans Headscale

**Vérifiez :**
```bash
# Sur le serveur Headscale
journalctl -u headscale -f

# Devrait montrer les tentatives de connexion
```

**Problèmes courants :**
- Pare-feu bloquant les connexions
- Mauvaise URL du serveur
- Clé de pré-auth expirée
- Service Headscale non démarré

## Considérations de sécurité

1. **Protégez les clés de pré-auth**
   - Ne les committez pas dans des dépôts publics
   - Utilisez des variables d'environnement pour les compilations
   - Faites pivoter les clés régulièrement

2. **Signature de code**
   - Ne partagez pas votre certificat de signature
   - Gardez le mot de passe du certificat sécurisé
   - Utilisez un jeton matériel pour les certificats EV

3. **Distribution**
   - Utilisez HTTPS pour les téléchargements
   - Vérifiez la somme de contrôle avant le déploiement
   - Documentez la version de l'installeur

4. **Antivirus**
   - Certains AV signalent les exécutables PyInstaller
   - Soumettez à VirusTotal avant le déploiement
   - Ajoutez des exclusions si nécessaire

## Avancé : Automatiser le déploiement

### Utilisation de la stratégie de groupe (Domaine Windows)

1. Signez l'exécutable avec un certificat de confiance
2. Placez sur un partage réseau
3. Créez une GPO :
   - Configuration ordinateur → Stratégies → Paramètres logiciels → Installation de logiciels
   - Ajouter un nouveau package
   - Assigner aux ordinateurs

### Utilisation de PowerShell

```powershell
# Déployer sur des ordinateurs distants
$computers = Get-Content ordinateurs.txt
foreach ($computer in $computers) {
    Copy-Item "\\serveur\partage\InstallateurHeadscale.exe" "\\$computer\C$\Temp\"
    Invoke-Command -ComputerName $computer -ScriptBlock {
        Start-Process "C:\Temp\InstallateurHeadscale.exe" -Wait
    }
}
```

## Compilation à partir de zéro (Méthode alternative)

### Utilisation de PyInstaller avec fichier spec

Créez `installer.spec` :

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['headscale_installer_fr.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='InstallateurHeadscale',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
```

Compiler :
```powershell
pyinstaller installer.spec
```

## Support

Pour des problèmes ou questions :
- Consultez la [FAQ](FAQ.md)
- Revoyez la section [Dépannage](#dépannage)
- Ouvrez une issue sur GitHub
- Consultez la documentation Headscale

## Crédits

- Créé avec l'aide de Claude AI
- Basé sur Headscale par Juan Font
- Utilise les clients Tailscale officiels

---

**Note :** Cet installeur est destiné à un usage professionnel/personnel légitime uniquement. Assurez-vous d'avoir l'autorisation appropriée avant de déployer sur des appareils d'entreprise.
