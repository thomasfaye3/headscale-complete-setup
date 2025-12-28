# Headscale Installation Guide with Web Interface

[![Made with Claude AI](https://img.shields.io/badge/Made%20with-Claude%20AI-5A67D8?logo=anthropic)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Language: English](https://img.shields.io/badge/Language-English-red)](README-EN.md)
[![Version Française](https://img.shields.io/badge/Français-README-blue)](README.md)

> **🤖 This guide was entirely created with the help of Claude AI**  
> The author had no development experience and wanted to connect homelabs without exposing external ports.

---

**📖 [Version française disponible ici](README.md)**

---

Complete guide to install Headscale on a VPS (Hetzner Cloud) with HTTPS (Let's Encrypt) and a modern web management interface.

## 📋 Table of Contents

- [What is Headscale?](#what-is-headscale)
- [About This Guide](#about-this-guide)
- [Prerequisites](#prerequisites)
- [Step 1: VPS Setup](#step-1-vps-setup)
- [Step 2: Headscale Installation](#step-2-headscale-installation)
- [Step 3: Caddy Installation (HTTPS)](#step-3-caddy-installation-https)
- [Step 4: Web Interface Installation](#step-4-web-interface-installation)
- [Step 5: Initial Configuration](#step-5-initial-configuration)
- [Usage](#usage)
- [Automated Windows Installer](#-automated-windows-installer)
- [Troubleshooting](#troubleshooting)

---

## What is Headscale?

**Headscale** is an open-source, self-hosted implementation of the Tailscale control server. It allows you to create your own private mesh VPN network without relying on Tailscale's servers.

**Benefits:**
- ✅ Full control over your data
- ✅ No limits on number of devices
- ✅ Free and open-source
- ✅ Compatible with official Tailscale clients

---

## About This Guide

This guide was created with the assistance of **Claude AI** (Anthropic) to help users set up their own self-hosted VPN infrastructure. The author had no prior development experience and wanted to connect multiple homelabs without exposing external ports.

**Why this guide exists:**
- Personal use case: Secure homelab connectivity
- No programming knowledge required from author
- Complete walkthrough built with AI assistance
- Tested on real infrastructure (Hetzner Cloud)
- Community-driven improvements welcome

**Acknowledgments:**
- Built with Claude AI's assistance
- Based on Headscale project by Juan Font
- Uses Headscale-Admin by GoodiesHQ
- Community feedback and contributions

---

## Prerequisites

- A domain name (e.g., `vpn.example.com`)
- A VPS (we use Hetzner Cloud in this guide)
- Basic Linux command line knowledge
- DNS access to configure A records

**Recommended VPS specs:**
- RAM: 2 GB minimum
- CPU: 1 vCore
- Storage: 20 GB
- OS: Ubuntu 24.04 LTS

---

## Step 1: VPS Setup

### 1.1 Create Hetzner Cloud VPS

1. Go to [Hetzner Cloud](https://www.hetzner.com/cloud)
2. Create a new project
3. Add a server:
   - **Location:** Choose closest to you
   - **Image:** Ubuntu 24.04
   - **Type:** Shared vCPU → CX22 (2 GB RAM) or ARM → Ampere A1 (free tier)
   - **SSH Key:** Add your public key
   - **Name:** `headscale-server`

### 1.2 Configure Firewall (Hetzner)

**During VPS creation or after:**

1. Go to your Hetzner project
2. Navigate to **Firewalls**
3. Create a new firewall or edit existing one
4. Add the following **Inbound Rules:**

```
Protocol | Port  | Source      | Description
---------|-------|-------------|------------------
TCP      | 22    | 0.0.0.0/0   | SSH
TCP      | 80    | 0.0.0.0/0   | HTTP (Let's Encrypt)
TCP      | 443   | 0.0.0.0/0   | HTTPS (Headscale)
TCP      | 8080  | 0.0.0.0/0   | Headscale (optional)
UDP      | 3478  | 0.0.0.0/0   | STUN (Tailscale)
UDP      | 41641 | 0.0.0.0/0   | Tailscale
```

5. Apply firewall to your server

**Note:** This guide uses **Hetzner Cloud Firewall** instead of iptables/ufw for simplicity. The firewall is managed from the Hetzner web interface.

### 1.3 Configure DNS

Add an A record in your DNS provider pointing to your VPS IP:

```
Type: A
Name: vpn (or your subdomain)
Content: YOUR_VPS_IP
TTL: Auto
```

**If using Cloudflare:** Disable the proxy (gray cloud, not orange)

### 1.4 Initial Server Setup

```bash
# Connect via SSH
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y
```

---

## Step 2: Headscale Installation

### 2.1 Install Headscale

```bash
# Download latest Headscale release (adjust architecture if needed)
wget https://github.com/juanfont/headscale/releases/download/v0.27.1/headscale_0.27.1_linux_amd64.deb

# For ARM servers (Ampere):
# wget https://github.com/juanfont/headscale/releases/download/v0.27.1/headscale_0.27.1_linux_arm64.deb

# Install
dpkg -i headscale_0.27.1_linux_amd64.deb

# Verify installation
headscale version
```

### 2.2 Configure Headscale

```bash
# Edit configuration
nano /etc/headscale/config.yaml
```

**Key settings to modify:**

```yaml
# Line ~8 - Your public URL
server_url: https://vpn.example.com

# Line ~18 - Listen address
listen_addr: 0.0.0.0:8080

# Line ~60 - Base domain for MagicDNS
base_domain: vpn.example.com

# Line ~100 - IP range
prefixes:
  v4: 100.64.0.0/10
```

**Important:** Comment out or leave empty the Let's Encrypt settings (Caddy will handle HTTPS):

```yaml
# Line ~240-260
# tls_letsencrypt_hostname: ""
# tls_letsencrypt_cache_dir: /var/lib/headscale/cache
# tls_letsencrypt_challenge_type: HTTP-01
# tls_letsencrypt_listen: ""
```

Save: `Ctrl+X` → `Y` → `Enter`

### 2.3 Start Headscale

```bash
# Enable and start service
systemctl enable headscale
systemctl start headscale

# Check status
systemctl status headscale
```

### 2.4 Create User

```bash
# Create a user for your devices
headscale users create default-user

# List users to get their ID
headscale users list
```

**Output example:**
```
ID | Name         | Created
1  | default-user | 2025-12-26 10:00:00
```

**📋 Note the user ID (in this example: 1)** - you'll need it for the next step!

### 2.5 Generate Pre-auth Key

```bash
# Generate a reusable pre-auth key (valid for 1 year recommended)
# Replace "1" with your user ID from the previous command
headscale preauthkeys create --user 1 --reusable --expiration 365d
```

**Important:**
- Use the **user ID number** (e.g., `1`), not the username
- Recommended expiration: **30-365 days** for security
- For longer validity (less secure): use `3650d` (10 years)

**📋 Save this key!** You'll need it to connect devices.

---

## Step 3: Caddy Installation (HTTPS)

Caddy automatically obtains and renews Let's Encrypt certificates.

### 3.1 Install Caddy

```bash
# Install dependencies
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

# Add Caddy repository
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

# Install Caddy
apt update
apt install caddy
```

### 3.2 Configure Caddy

```bash
# Create Caddyfile
cat > /etc/caddy/Caddyfile << 'EOF'
vpn.example.com {
    reverse_proxy localhost:8080
}
EOF
```

**Replace `vpn.example.com` with your actual domain!**

### 3.3 Start Caddy

```bash
# Restart Caddy
systemctl restart caddy
systemctl status caddy
```

### 3.4 Verify HTTPS

```bash
# Test from server
curl https://vpn.example.com/health
```

Should return: `{"status":"ok"}`

---

## Step 4: Web Interface Installation

We'll use [Headscale-Admin](https://github.com/GoodiesHQ/headscale-admin) for the web management interface.

### 4.1 Install Docker

```bash
apt install -y docker.io docker-compose
```

### 4.2 Create Headscale-Admin Directory

```bash
mkdir -p /opt/headscale-admin
cd /opt/headscale-admin
```

### 4.3 Create Docker Compose File

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
      - BASIC_AUTH_PASS=ChangeThisPassword
      - SCRIPT_NAME=/admin
    extra_hosts:
      - "localhost:127.0.0.1"

EOF
```

**Edit the file to set your password:**

```bash
nano docker-compose.yml
```

Change `BASIC_AUTH_PASS=ChangeThisPassword` to a secure password.

Save: `Ctrl+X` → `Y` → `Enter`

### 4.4 Start Container

```bash
docker-compose up -d

# Check status
docker ps
```

### 4.5 Configure Caddy for Admin Interface

```bash
cat > /etc/caddy/Caddyfile << 'EOF'
vpn.example.com {
    # Headscale API
    reverse_proxy localhost:8080
    
    # Admin Interface
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

**Replace `vpn.example.com` with your domain!**

```bash
# Restart Caddy
systemctl restart caddy
```

---

## Step 5: Initial Configuration

### 5.1 Access Web Interface

Open in your browser:
```
https://vpn.example.com/admin/
```

**Login:**
- Username: `admin`
- Password: The password you set in docker-compose.yml

### 5.2 Configure API Settings

In the Settings page:

1. **API URL:** `https://vpn.example.com`
2. **API Key:** Generate one with:

```bash
# Recommended: 30 days for security
headscale apikeys create --expiration 30d

# Or longer if needed (90 days, 1 year, etc.)
# headscale apikeys create --expiration 365d
```

Copy the generated key and paste it into the web interface.

3. Click **"Save Settings"**

### 5.3 Verify Connection

Navigate to **"Nodes"** in the sidebar. You should see an empty list (no devices connected yet).

---

## Usage

### Managing Nodes

```bash
# List all connected devices
headscale nodes list

# List devices for specific user
headscale nodes list --user default-user

# View node details
headscale nodes show <NODE_ID>

# Delete a node
headscale nodes delete <NODE_ID>
```

### Managing Users

```bash
# List users
headscale users list

# Create new user
headscale users create <username>

# Delete user
headscale users delete <username>
```

### Managing Pre-auth Keys

```bash
# List pre-auth keys
headscale preauthkeys list --user <username>

# Create new pre-auth key
# First, list users to get the ID
headscale users list
# Then use the ID number (e.g., 1)
headscale preauthkeys create --user 1 --reusable --expiration 365d

# Expire a key
headscale preauthkeys expire --user <username> --key <key>
```

### Connecting Devices

**On Windows/Mac/Linux:**

1. Install [Tailscale client](https://tailscale.com/download)
2. Configure to use your Headscale server:

```bash
# Windows (PowerShell as Admin)
tailscale login --login-server=https://vpn.example.com --authkey=YOUR_PREAUTH_KEY

# Linux/Mac
sudo tailscale login --login-server=https://vpn.example.com --authkey=YOUR_PREAUTH_KEY
```

**On Android/iOS:**
- Install Tailscale app
- Go to Settings → Use custom control server
- Enter: `https://vpn.example.com`
- Login with pre-auth key

---

## 💻 Automated Windows Installer

To facilitate deployment on multiple Windows workstations, an **automated installer with graphical interface** is available in this repository.

### ✨ Features

- ✅ **Automatic installation** of Tailscale
- ✅ **Automatic configuration** of Headscale server
- ✅ **User-friendly GUI** - no command line required
- ✅ **No technical intervention** required from end users
- ✅ **Automatic startup** on Windows boot
- ✅ **Customizable** with your URL and pre-auth key

### 📥 Quick Usage

**To deploy on your workstations:**

1. **Download Python scripts:**
   - [`headscale_installer.py`](headscale_installer.py) - English version
   - [`headscale_installer_fr.py`](headscale_installer_fr.py) - French version

2. **Configure your settings** (lines 17-19 in script):
   ```python
   HEADSCALE_URL = "https://vpn.example.com"  # Your URL
   AUTH_KEY = "your-preauth-key"              # Your key
   BASE_DOMAIN = "vpn.example.com"            # Your domain
   ```

3. **Build to .exe** (complete guide provided):
   - Double-click `build.bat`
   - Result: `dist\HeadscaleInstaller.exe`

4. **Distribute the exe** to your users (USB, network share, email...)

### 📖 Complete Documentation

**Detailed guides available:**
- 🇬🇧 [**Installer Guide EN**](CLIENT-INSTALLER.md) - Usage and deployment
- 🇫🇷 [**Installer Guide FR**](CLIENT-INSTALLER-FR.md) - Utilisation et déploiement
- 🔨 [**Build Guide EN**](BUILD-GUIDE-EN.md) - Create exe step-by-step
- 🔨 [**Build Guide FR**](BUILD-GUIDE.md) - Créer l'exe pas-à-pas

**Scripts provided:**
- `build.bat` - One-click automated compilation
- `sign.ps1` - Code signing (prevents Windows warnings)

### 🎯 Ideal Use Case

Perfect for:
- Deployment on 10-200+ Windows workstations
- Non-technical users
- Enterprise environments
- Rapid deployment without IT intervention on each workstation

### 📸 Preview

The installer displays a simple interface asking for:
- **Client name** (e.g., "Company X")
- **Device type** (e.g., "Desktop", "Laptop")

Then automatically installs and configures Tailscale with your Headscale server!

---

## Troubleshooting

### Headscale Not Starting

```bash
# Check logs
journalctl -u headscale -n 50

# Check config syntax
headscale configtest
```

### Certificate Issues

```bash
# Check Caddy logs
journalctl -u caddy -n 50

# Verify DNS points to correct IP
nslookup vpn.example.com

# Test certificate
curl -v https://vpn.example.com/health
```

### Web Interface Not Accessible

```bash
# Check Docker container
docker ps
docker logs headscale-admin

# Test local access
curl http://localhost:5000/admin/

# Check Caddy config
cat /etc/caddy/Caddyfile
systemctl restart caddy
```

### Devices Not Connecting

```bash
# Check Headscale is accessible
curl https://vpn.example.com/health

# Verify firewall allows connections
ufw status

# Check Headscale logs during connection attempt
journalctl -u headscale -f
```

---

## Security Recommendations

1. **Change default admin password** in docker-compose.yml
2. **Use strong pre-auth keys** and rotate them periodically
3. **Configure ACLs** to restrict traffic between devices
4. **Keep Headscale updated** regularly
5. **Enable firewall** (ufw) and only allow necessary ports
6. **Monitor logs** for suspicious activity

---

## 📢 Support and Contributions

**This repository is a personal guide shared with the community.**

- ✅ Feel free to fork and adapt to your needs
- ✅ Improvements and suggestions are welcome via Pull Request
- 📧 For technical questions about Headscale, consult the official resources:
  - [Headscale Documentation](https://headscale.net/)
  - [Headscale GitHub](https://github.com/juanfont/headscale/issues)
  - [Headscale Discord](https://discord.gg/c84AZQhmpx)

**Note:** This guide was created with the help of Claude AI by someone with no development experience. It may contain errors or approximations. Constructive feedback is appreciated!

---

## 📜 License

This guide is provided under the MIT License. Headscale and related projects have their own licenses.

## Contributing

Feel free to submit issues or pull requests to improve this guide!
