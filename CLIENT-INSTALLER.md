# Windows Client Installer

This guide explains how to create a custom Windows installer (.exe) to deploy Tailscale clients configured for your Headscale server.

## Overview

The installer provides:
- ✅ Automated Tailscale installation
- ✅ Pre-configured Headscale server URL
- ✅ User-friendly GUI for client naming
- ✅ Pre-authentication key integration
- ✅ Silent background installation
- ✅ Automatic service startup

## Prerequisites

- **Python 3.8+** installed on Windows (for development)
- **PyInstaller** for creating .exe
- **SignTool** (optional, for code signing)
- **Pre-auth key** from your Headscale server

## Step 1: Prepare the Python Script

### 1.1 Download the installer script

Download `headscale_installer.py` from this repository.

### 1.2 Configure your settings

Edit the script and update these values:

```python
# Line ~17-19
HEADSCALE_URL = "https://vpn.example.com"  # Your Headscale server URL
AUTH_KEY = "your-preauth-key-here"          # Your pre-auth key
BASE_DOMAIN = "vpn.example.com"             # Your MagicDNS domain
```

**To get your pre-auth key:**
```bash
# On your Headscale server
headscale users list  # Get user ID
headscale preauthkeys create --user 1 --reusable --expiration 365d
```

## Step 2: Install Dependencies

```powershell
# Install required Python packages
pip install pyinstaller
```

## Step 3: Build the Executable

### 3.1 Create build script

Create `build.bat`:

```batch
@echo off
echo Building Headscale Installer...

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build executable
pyinstaller --onefile --windowed --icon=icon.ico --name="HeadscaleInstaller" headscale_installer.py

echo.
echo Build complete! Executable is in dist\HeadscaleInstaller.exe
pause
```

### 3.2 Add icon (optional)

Place an `icon.ico` file in the same directory, or remove `--icon=icon.ico` from the build command.

### 3.3 Build

```powershell
.\build.bat
```

The executable will be created in `dist\HeadscaleInstaller.exe`

## Step 4: Code Signing (Optional but Recommended)

### Why sign your executable?

- ✅ Prevents Windows Defender warnings
- ✅ Shows your organization name
- ✅ Builds user trust
- ✅ Required for enterprise deployment

### 4.1 Get a code signing certificate

**Option 1: Buy from Certificate Authority**
- Sectigo, DigiCert, GlobalSign
- Cost: ~$100-300/year
- Provides EV or OV certificate

**Option 2: Self-signed certificate (testing only)**

**⚠️ Warning:** Self-signed certificates will still trigger warnings. They're only useful for testing.

```powershell
# Create self-signed certificate (PowerShell as Admin)
$cert = New-SelfSignedCertificate -Subject "CN=YourCompany" -Type CodeSigningCert -CertStoreLocation Cert:\CurrentUser\My

# Export certificate
Export-Certificate -Cert $cert -FilePath "YourCompany.cer"

# Sign executable
signtool sign /f "YourCompany.cer" /fd SHA256 /t http://timestamp.digicert.com dist\HeadscaleInstaller.exe
```

### 4.2 Sign with purchased certificate

```powershell
# If certificate is in Windows Certificate Store
signtool sign /n "YourCompany" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\HeadscaleInstaller.exe

# If certificate is in .pfx file
signtool sign /f certificate.pfx /p YourPassword /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\HeadscaleInstaller.exe
```

### 4.3 Verify signature

```powershell
signtool verify /pa /v dist\HeadscaleInstaller.exe
```

## Step 5: Test the Installer

1. Run `HeadscaleInstaller.exe` on a test machine
2. Fill in client name and device type
3. Click "Install"
4. Verify:
   - Tailscale installs successfully
   - Device appears in Headscale: `headscale nodes list`
   - Device can communicate with other nodes

## Deployment

### For multiple devices:

1. **Share the executable** via:
   - Network share
   - USB drive
   - Email (if small enough)
   - Internal web server

2. **Document the process:**
   - Create user guide with screenshots
   - Include support contact
   - Explain what the installer does

3. **Track deployments:**
   - Monitor `headscale nodes list`
   - Document which devices are connected
   - Keep pre-auth key secure

## Customization

### Change window appearance

Edit these lines in `headscale_installer.py`:

```python
# Line ~120-130
bg_color = "#f5f5f5"      # Background color
primary_color = "#2563eb"  # Primary color (blue)
accent_color = "#1e40af"   # Accent color (dark blue)
```

### Modify client naming

The installer generates hostnames like: `{client}-{type}`

Example: `CompanyName-PC-Bureau` becomes `companyname-pc-bureau.vpn.example.com`

You can modify the `generate_hostname()` function to change this behavior.

### Add company logo

1. Convert logo to Base64
2. Add to script header
3. Display in GUI using tkinter

## Troubleshooting

### "Windows Protected your PC" warning

**Cause:** Executable is not code-signed or uses self-signed certificate

**Solutions:**
1. Click "More info" → "Run anyway" (testing)
2. Get proper code signing certificate
3. Add to Windows Defender exclusions
4. Distribute via company software center

### Installation fails

**Check:**
1. User has administrator rights
2. Internet connection available
3. Antivirus not blocking
4. Correct Headscale URL
5. Valid pre-auth key

**Debug:**
- Check logs in: `%TEMP%\headscale-install.log`
- Run installer from command prompt to see errors

### Device doesn't appear in Headscale

**Verify:**
```bash
# On Headscale server
journalctl -u headscale -f

# Should show connection attempts
```

**Common issues:**
- Firewall blocking connections
- Wrong server URL
- Expired pre-auth key
- Headscale service not running

## Security Considerations

1. **Protect pre-auth keys**
   - Don't commit to public repositories
   - Use environment variables for builds
   - Rotate keys regularly

2. **Code signing**
   - Don't share your signing certificate
   - Keep certificate password secure
   - Use hardware token for EV certificates

3. **Distribution**
   - Use HTTPS for downloads
   - Verify checksum before deployment
   - Document installer version

4. **Antivirus**
   - Some AVs flag PyInstaller executables
   - Submit to VirusTotal before deployment
   - Add exclusions if needed

## Advanced: Automating Deployment

### Using Group Policy (Windows Domain)

1. Sign executable with trusted certificate
2. Place on network share
3. Create GPO:
   - Computer Configuration → Policies → Software Settings → Software Installation
   - Add new package
   - Assign to computers

### Using PowerShell

```powershell
# Deploy to remote computers
$computers = Get-Content computers.txt
foreach ($computer in $computers) {
    Copy-Item "\\server\share\HeadscaleInstaller.exe" "\\$computer\C$\Temp\"
    Invoke-Command -ComputerName $computer -ScriptBlock {
        Start-Process "C:\Temp\HeadscaleInstaller.exe" -Wait
    }
}
```

## Building from Scratch (Alternative Method)

### Using PyInstaller with spec file

Create `installer.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['headscale_installer.py'],
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
    name='HeadscaleInstaller',
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

Build:
```powershell
pyinstaller installer.spec
```

## Support

For issues or questions:
- Check the [FAQ](FAQ.md)
- Review [Troubleshooting](#troubleshooting) section
- Open an issue on GitHub
- Consult Headscale documentation

## Credits

- Built with assistance from Claude AI
- Based on Headscale by Juan Font
- Uses official Tailscale clients

---

**Note:** This installer is for legitimate business/personal use only. Ensure you have proper authorization before deploying on company devices.
