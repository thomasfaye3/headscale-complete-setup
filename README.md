# Guide d'installation Headscale avec interface web

[![Made with Claude AI](https://img.shields.io/badge/Made%20with-Claude%20AI-5A67D8?logo=anthropic)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Language: Français](https://img.shields.io/badge/Language-Français-blue)](README.md)
[![English Version](https://img.shields.io/badge/English-README-red)](README-EN.md)

> **🤖 Ce guide a été entièrement créé avec l'aide de Claude AI**  
> L'auteur n'avait aucune expérience en développement et cherchait à connecter ses homelabs sans exposer de ports externes.

---

**📖 [English version available here](README-EN.md)**

---

Guide complet pour installer Headscale sur un VPS (Hetzner Cloud) avec HTTPS (Let's Encrypt) et une interface web de gestion moderne.

## 📋 Table des matières

- [Qu'est-ce que Headscale ?](#quest-ce-que-headscale-)
- [À propos de ce guide](#à-propos-de-ce-guide)
- [Prérequis](#prérequis)
- [Étape 1 : Configuration du VPS](#étape-1--configuration-du-vps)
- [Étape 2 : Installation de Headscale](#étape-2--installation-de-headscale)
- [Étape 3 : Installation de Caddy (HTTPS)](#étape-3--installation-de-caddy-https)
- [Étape 4 : Installation de l'interface web](#étape-4--installation-de-linterface-web)
- [Étape 5 : Configuration initiale](#étape-5--configuration-initiale)
- [Utilisation](#utilisation)
- [Installeur Windows automatisé](#-installeur-windows-automatisé)
- [Dépannage](#dépannage)

---

## Qu'est-ce que Headscale ?

**Headscale** est une implémentation open-source et auto-hébergée du serveur de contrôle Tailscale. Il vous permet de créer votre propre réseau VPN mesh privé sans dépendre des serveurs de Tailscale.

**Avantages :**
- ✅ Contrôle total de vos données
- ✅ Pas de limite sur le nombre d'appareils
- ✅ Gratuit et open-source
- ✅ Compatible avec les clients Tailscale officiels

---

## À propos de ce guide

Ce guide a été créé avec l'aide de **Claude AI** (Anthropic) pour aider les utilisateurs à configurer leur propre infrastructure VPN auto-hébergée. L'auteur n'avait aucune expérience en développement et souhaitait connecter plusieurs homelabs sans exposer de ports externes.

**Pourquoi ce guide existe :**
- Cas d'usage personnel : Connexion sécurisée entre homelabs
- Aucune connaissance en programmation requise de la part de l'auteur
- Guide complet construit avec l'assistance d'une IA
- Testé sur une infrastructure réelle (Hetzner Cloud)
- Améliorations communautaires bienvenues

**Remerciements :**
- Créé avec l'aide de Claude AI
- Basé sur le projet Headscale de Juan Font
- Utilise Headscale-Admin par GoodiesHQ
- Retours et contributions de la communauté

---

## Prérequis

- Un nom de domaine (ex: `vpn.example.com`)
- Un VPS (nous utilisons Hetzner Cloud dans ce guide)
- Connaissances de base en ligne de commande Linux
- Accès DNS pour configurer les enregistrements A

**Spécifications VPS recommandées :**
- RAM : 2 Go minimum
- CPU : 1 vCore
- Stockage : 20 Go
- OS : Ubuntu 24.04 LTS

---

## Étape 1 : Configuration du VPS

### 1.1 Créer un VPS Hetzner Cloud

1. Allez sur [Hetzner Cloud](https://www.hetzner.com/cloud)
2. Créez un nouveau projet
3. Ajoutez un serveur :
   - **Localisation :** Choisissez la plus proche de vous
   - **Image :** Ubuntu 24.04
   - **Type :** Shared vCPU → CX22 (2 Go RAM) ou ARM → Ampere A1 (gratuit)
   - **Clé SSH :** Ajoutez votre clé publique
   - **Nom :** `headscale-server`

### 1.2 Configurer le pare-feu (Hetzner)

**Pendant la création du VPS ou après :**

1. Allez dans votre projet Hetzner
2. Naviguez vers **Firewalls**
3. Créez un nouveau pare-feu ou modifiez celui existant
4. Ajoutez les **règles entrantes** suivantes :

```
Protocole | Port  | Source      | Description
----------|-------|-------------|------------------
TCP       | 22    | 0.0.0.0/0   | SSH
TCP       | 80    | 0.0.0.0/0   | HTTP (Let's Encrypt)
TCP       | 443   | 0.0.0.0/0   | HTTPS (Headscale)
TCP       | 8080  | 0.0.0.0/0   | Headscale (optionnel)
UDP       | 3478  | 0.0.0.0/0   | STUN (Tailscale)
UDP       | 41641 | 0.0.0.0/0   | Tailscale
```

5. Appliquez le pare-feu à votre serveur

**Note :** Ce guide utilise le **pare-feu Hetzner Cloud** au lieu d'iptables/ufw pour plus de simplicité. Le pare-feu est géré depuis l'interface web Hetzner.

### 1.3 Configurer le DNS

Ajoutez un enregistrement A dans votre fournisseur DNS pointant vers l'IP de votre VPS :

```
Type: A
Nom: vpn (ou votre sous-domaine)
Contenu: IP_DE_VOTRE_VPS
TTL: Auto
```

**Si vous utilisez Cloudflare :** Désactivez le proxy (nuage gris, pas orange)

### 1.4 Configuration initiale du serveur

```bash
# Connexion via SSH
ssh root@IP_DE_VOTRE_VPS

# Mise à jour du système
apt update && apt upgrade -y
```

---

## Étape 2 : Installation de Headscale

### 2.1 Installer Headscale

```bash
# Télécharger la dernière version de Headscale (ajustez l'architecture si nécessaire)
wget https://github.com/juanfont/headscale/releases/download/v0.27.1/headscale_0.27.1_linux_amd64.deb

# Pour serveurs ARM (Ampere):
# wget https://github.com/juanfont/headscale/releases/download/v0.27.1/headscale_0.27.1_linux_arm64.deb

# Installer
dpkg -i headscale_0.27.1_linux_amd64.deb

# Vérifier l'installation
headscale version
```

### 2.2 Configurer Headscale

```bash
# Éditer la configuration
nano /etc/headscale/config.yaml
```

**Paramètres clés à modifier :**

```yaml
# Ligne ~8 - Votre URL publique
server_url: https://vpn.example.com

# Ligne ~18 - Adresse d'écoute
listen_addr: 0.0.0.0:8080

# Ligne ~60 - Domaine de base pour MagicDNS
base_domain: vpn.example.com

# Ligne ~100 - Plage IP
prefixes:
  v4: 100.64.0.0/10
```

**Important :** Commentez ou laissez vides les paramètres Let's Encrypt (Caddy s'en occupera) :

```yaml
# Ligne ~240-260
# tls_letsencrypt_hostname: ""
# tls_letsencrypt_cache_dir: /var/lib/headscale/cache
# tls_letsencrypt_challenge_type: HTTP-01
# tls_letsencrypt_listen: ""
```

Sauvegarder : `Ctrl+X` → `Y` → `Entrée`

### 2.3 Démarrer Headscale

```bash
# Activer et démarrer le service
systemctl enable headscale
systemctl start headscale

# Vérifier le statut
systemctl status headscale
```

### 2.4 Créer un utilisateur

```bash
# Créer un utilisateur pour vos appareils
headscale users create utilisateur-par-defaut

# Lister les utilisateurs pour obtenir leur ID
headscale users list
```

**Exemple de sortie :**
```
ID | Name                 | Created
1  | utilisateur-par-defaut | 2025-12-26 10:00:00
```

**📋 Notez l'ID utilisateur (dans cet exemple : 1)** - vous en aurez besoin pour l'étape suivante !

### 2.5 Générer une clé de pré-authentification

```bash
# Générer une clé réutilisable (validité 1 an recommandée)
# Remplacez "1" par l'ID de votre utilisateur de la commande précédente
headscale preauthkeys create --user 1 --reusable --expiration 365d
```

**Important :**
- Utilisez le **numéro d'ID utilisateur** (ex: `1`), pas le nom d'utilisateur
- Expiration recommandée : **30-365 jours** pour la sécurité
- Pour une validité plus longue (moins sécurisé) : utilisez `3650d` (10 ans)

**📋 Sauvegardez cette clé !** Vous en aurez besoin pour connecter les appareils.

---

## Étape 3 : Installation de Caddy (HTTPS)

Caddy obtient et renouvelle automatiquement les certificats Let's Encrypt.

### 3.1 Installer Caddy

```bash
# Installer les dépendances
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

# Ajouter le dépôt Caddy
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

# Installer Caddy
apt update
apt install caddy
```

### 3.2 Configurer Caddy

```bash
# Créer le Caddyfile
cat > /etc/caddy/Caddyfile << 'EOF'
vpn.example.com {
    reverse_proxy localhost:8080
}
EOF
```

**Remplacez `vpn.example.com` par votre domaine réel !**

### 3.3 Démarrer Caddy

```bash
# Redémarrer Caddy
systemctl restart caddy
systemctl status caddy
```

### 3.4 Vérifier HTTPS

```bash
# Tester depuis le serveur
curl https://vpn.example.com/health
```

Devrait retourner : `{"status":"ok"}`

---

## Étape 4 : Installation de l'interface web

Nous utiliserons [Headscale-Admin](https://github.com/GoodiesHQ/headscale-admin) pour l'interface de gestion web.

### 4.1 Installer Docker

```bash
apt install -y docker.io docker-compose
```

### 4.2 Créer le répertoire Headscale-Admin

```bash
mkdir -p /opt/headscale-admin
cd /opt/headscale-admin
```

### 4.3 Créer le fichier Docker Compose

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  headscale-admin:
    image: goodieshq/headscale-admin:latest
    container_name: headscale-admin
    restart: unless-stopped
    ports:
      - "5000:80"
    environment:
      - HS_SERVER=http://localhost:8080
      - AUTH_TYPE=basic
      - BASIC_AUTH_USER=admin
      - BASIC_AUTH_PASS=ChangezCeMotDePasse
      - SCRIPT_NAME=/admin
    extra_hosts:
      - "localhost:127.0.0.1"

EOF
```

**Éditez le fichier pour définir votre mot de passe :**

```bash
nano docker-compose.yml
```

Changez `BASIC_AUTH_PASS=ChangezCeMotDePasse` par un mot de passe sécurisé.

Sauvegarder : `Ctrl+X` → `Y` → `Entrée`

### 4.4 Démarrer le conteneur

```bash
docker-compose up -d

# Vérifier le statut
docker ps
```

### 4.5 Configurer Caddy pour l'interface admin

```bash
cat > /etc/caddy/Caddyfile << 'EOF'
vpn.example.com {
    # API Headscale
    reverse_proxy localhost:8080
    
    # Interface Admin
    @admin path /admin*
    handle @admin {
        reverse_proxy localhost:5000 {
            header_up Host {host}
            header_up X-Real-IP {remote}
            header_up X-Forwarded-For {remote}
            header_up X-Forwarded-Proto {scheme}
        }
    }
}
EOF
```

**Remplacez `vpn.example.com` par votre domaine !**

```bash
# Redémarrer Caddy
systemctl restart caddy
```

---

## Étape 5 : Configuration initiale

### 5.1 Accéder à l'interface web

Ouvrez dans votre navigateur :
```
https://vpn.example.com/admin/
```

**Connexion :**
- Nom d'utilisateur : `admin`
- Mot de passe : Le mot de passe défini dans docker-compose.yml

### 5.2 Configurer les paramètres API

Dans la page Settings :

1. **API URL :** `https://vpn.example.com`
2. **API Key :** Générez-en une avec :

```bash
# Recommandé : 30 jours pour la sécurité
headscale apikeys create --expiration 30d

# Ou plus long si nécessaire (90 jours, 1 an, etc.)
# headscale apikeys create --expiration 365d
```

Copiez la clé générée et collez-la dans l'interface web.

3. Cliquez sur **"Save Settings"**

### 5.3 Vérifier la connexion

Naviguez vers **"Nodes"** dans la barre latérale. Vous devriez voir une liste vide (aucun appareil connecté pour le moment).

---

## Utilisation

### Gestion des nœuds

```bash
# Lister tous les appareils connectés
headscale nodes list

# Lister les appareils d'un utilisateur spécifique
headscale nodes list --user utilisateur-par-defaut

# Voir les détails d'un nœud
headscale nodes show <NODE_ID>

# Supprimer un nœud
headscale nodes delete <NODE_ID>
```

### Gestion des utilisateurs

```bash
# Lister les utilisateurs
headscale users list

# Créer un nouvel utilisateur
headscale users create <nom-utilisateur>

# Supprimer un utilisateur
headscale users delete <nom-utilisateur>
```

### Gestion des clés de pré-authentification

```bash
# Lister les clés de pré-auth
headscale preauthkeys list --user <nom-utilisateur>

# Créer une nouvelle clé de pré-auth
# D'abord, lister les utilisateurs pour obtenir l'ID
headscale users list
# Puis utiliser le numéro d'ID (ex: 1)
headscale preauthkeys create --user 1 --reusable --expiration 365d

# Expirer une clé
headscale preauthkeys expire --user <nom-utilisateur> --key <clé>
```

### Connexion des appareils

**Sur Windows/Mac/Linux :**

1. Installez le [client Tailscale](https://tailscale.com/download)
2. Configurez-le pour utiliser votre serveur Headscale :

```bash
# Windows (PowerShell en Admin)
tailscale login --login-server=https://vpn.example.com --authkey=VOTRE_CLE_PREAUTH

# Linux/Mac
sudo tailscale login --login-server=https://vpn.example.com --authkey=VOTRE_CLE_PREAUTH
```

**Sur Android/iOS :**
- Installez l'application Tailscale
- Allez dans Paramètres → Utiliser un serveur de contrôle personnalisé
- Entrez : `https://vpn.example.com`
- Connectez-vous avec la clé de pré-auth

---

## 💻 Installeur Windows automatisé

Pour faciliter le déploiement sur plusieurs postes Windows, un **installeur automatisé avec interface graphique** est disponible dans ce dépôt.

### ✨ Caractéristiques

- ✅ **Installation automatique** de Tailscale
- ✅ **Configuration automatique** du serveur Headscale
- ✅ **Interface graphique conviviale** - aucune ligne de commande
- ✅ **Aucune intervention technique** requise de l'utilisateur final
- ✅ **Démarrage automatique** au boot Windows
- ✅ **Personnalisable** avec votre URL et clé pré-auth

### 📥 Utilisation rapide

**Pour déployer sur vos postes :**

1. **Téléchargez les scripts Python :**
   - [`headscale_installer_fr.py`](headscale_installer_fr.py) - Version française
   - [`headscale_installer.py`](headscale_installer.py) - Version anglaise

2. **Configurez vos paramètres** (lignes 17-19 du script) :
   ```python
   HEADSCALE_URL = "https://vpn.example.com"  # Votre URL
   AUTH_KEY = "votre-clé-preauth"             # Votre clé
   BASE_DOMAIN = "vpn.example.com"            # Votre domaine
   ```

3. **Compilez en .exe** (guide complet fourni) :
   - Double-clic sur `build.bat`
   - Résultat : `dist\HeadscaleInstaller.exe`

4. **Distribuez l'exe** à vos utilisateurs (USB, réseau, email...)

### 📖 Documentation complète

**Guides détaillés disponibles :**
- 🇫🇷 [**Guide installeur FR**](CLIENT-INSTALLER-FR.md) - Utilisation et déploiement
- 🇬🇧 [**Guide installeur EN**](CLIENT-INSTALLER.md) - Usage and deployment
- 🔨 [**Guide compilation FR**](BUILD-GUIDE.md) - Créer l'exe étape par étape
- 🔨 [**Guide compilation EN**](BUILD-GUIDE-EN.md) - Build exe step-by-step

**Scripts fournis :**
- `build.bat` - Compilation automatique en un clic
- `sign.ps1` - Signature de code (évite les warnings Windows)

### 🎯 Cas d'usage idéal

Parfait pour :
- Déploiement sur 10-200+ postes Windows
- Utilisateurs non-techniques
- Environnements d'entreprise
- Déploiement rapide sans intervention IT sur chaque poste

### 📸 Aperçu

L'installeur affiche une interface simple demandant :
- **Nom du client** (ex: "Entreprise X")
- **Type d'appareil** (ex: "Bureau", "Portable")

Puis installe et configure automatiquement Tailscale avec votre serveur Headscale !

---

## Dépannage

### Headscale ne démarre pas

```bash
# Vérifier les logs
journalctl -u headscale -n 50

# Vérifier la syntaxe de la config
headscale configtest
```

### Problèmes de certificat

```bash
# Vérifier les logs Caddy
journalctl -u caddy -n 50

# Vérifier que le DNS pointe vers la bonne IP
nslookup vpn.example.com

# Tester le certificat
curl -v https://vpn.example.com/health
```

### Interface web inaccessible

```bash
# Vérifier le conteneur Docker
docker ps
docker logs headscale-admin

# Tester l'accès local
curl http://localhost:5000/admin/

# Vérifier la config Caddy
cat /etc/caddy/Caddyfile
systemctl restart caddy
```

### Les appareils ne se connectent pas

```bash
# Vérifier que Headscale est accessible
curl https://vpn.example.com/health

# Vérifier que le pare-feu autorise les connexions
ufw status

# Vérifier les logs Headscale pendant la tentative de connexion
journalctl -u headscale -f
```

---

## Recommandations de sécurité

1. **Changez le mot de passe admin par défaut** dans docker-compose.yml
2. **Utilisez des clés de pré-auth fortes** et faites-les pivoter périodiquement
3. **Configurez les ACL** pour restreindre le trafic entre appareils
4. **Maintenez Headscale à jour** régulièrement
5. **Activez le pare-feu** (ufw) et n'autorisez que les ports nécessaires
6. **Surveillez les logs** pour détecter toute activité suspecte

---

## 📢 Support et contributions

**Ce dépôt est un guide personnel partagé avec la communauté.**

- ✅ N'hésitez pas à forker et adapter à vos besoins
- ✅ Les améliorations et suggestions sont bienvenues via Pull Request
- 📧 Pour des questions techniques sur Headscale, consultez les ressources officielles :
  - [Documentation Headscale](https://headscale.net/)
  - [GitHub Headscale](https://github.com/juanfont/headscale/issues)
  - [Discord Headscale](https://discord.gg/c84AZQhmpx)

**Note :** Ce guide a été créé avec l'aide de Claude AI par quelqu'un sans expérience en développement. Il peut contenir des erreurs ou des approximations. Les retours constructifs sont appréciés !

---

## 📜 Licence

Ce guide est fourni sous licence MIT. Headscale et les projets associés ont leurs propres licences.
