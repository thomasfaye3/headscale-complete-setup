# Windows Installer Build Guide

This guide explains how to compile the Headscale installer into a distributable .exe file.

---

## 📋 Prerequisites

### Required Software

1. **Python 3.8+**
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **PyInstaller**
   ```powershell
   pip install pyinstaller
   ```

3. **Windows SDK** (for code signing - optional)
   - Download: https://developer.microsoft.com/windows/downloads/windows-sdk/

### Required Files

```
📁 Working directory/
├── headscale_installer.py      # Python script (EN)
├── headscale_installer_fr.py   # Python script (FR)
├── build.bat                   # Build script
├── sign.ps1                    # Signing script (optional)
└── icon.ico                    # Icon (optional)
```

---

## 🔧 Step 1: Script Configuration

### 1.1 Edit Python Script

Open `headscale_installer.py` (or `headscale_installer_fr.py`) and modify:

```python
# Line ~17-19
HEADSCALE_URL = "https://vpn.example.com"  # Your Headscale URL
AUTH_KEY = "YOUR_PREAUTH_KEY"              # Your pre-auth key
BASE_DOMAIN = "vpn.example.com"            # Your MagicDNS domain
```

**To get your pre-auth key:**
```bash
# On your Headscale server
headscale users list  # Note the ID
headscale preauthkeys create --user 1 --reusable --expiration 365d
```

### 1.2 Save the Script

Save your changes.

---

## 🏗️ Step 2: Compilation

### 2.1 Run Build Script

**Double-click `build.bat`** or launch from PowerShell:

```powershell
.\build.bat
```

### 2.2 Build Process

The script will:
1. ✅ Clean previous builds
2. ✅ Verify Python and PyInstaller
3. ✅ Compile script to .exe
4. ✅ Create `dist\` folder

### 2.3 Result

If successful:
```
========================================
BUILD SUCCESS!
========================================

Executable: dist\HeadscaleInstaller.exe
Size: ~15 MB
```

The executable is located at: **`dist\HeadscaleInstaller.exe`**

---

## 🔏 Step 3: Code Signing (Optional but Recommended)

### Why Sign?

- ✅ Prevents Windows Defender warnings
- ✅ Shows your organization name
- ✅ Builds user trust
- ✅ Required for enterprise deployment

### 3.1 Obtain Certificate

**Option A: Purchase Certificate**
- Providers: Sectigo, DigiCert, GlobalSign
- Cost: ~$100-300/year
- OV or EV certificate recommended

**Option B: Self-signed Certificate (testing only)**
- Free but generates warnings
- Only for internal testing

### 3.2 Sign the Exe

**Run signing script:**

```powershell
# Right-click PowerShell → Run as Administrator
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\sign.ps1
```

**The script will ask for:**
1. Signing method (certificate store, PFX, or self-signed)
2. Certificate information
3. Password (if PFX)

### 3.3 Verification

The script automatically verifies the signature. You can also:

```powershell
# In PowerShell
Get-AuthenticodeSignature dist\HeadscaleInstaller.exe | Format-List
```

**Or right-click exe → Properties → Digital Signatures**

---

## 📦 Step 4: Distribution

### 4.1 Test the Exe

**On a test machine:**
1. Copy `dist\HeadscaleInstaller.exe`
2. Run it
3. Verify:
   - ✅ Tailscale installation
   - ✅ Headscale connection
   - ✅ Device visible in `headscale nodes list`

### 4.2 Distribution Methods

**Option A: Network Share**
```
\\server\share\HeadscaleInstaller.exe
```

**Option B: USB Drive**
- Copy exe to USB
- Distribute to users

**Option C: Email** (if < 25 MB)
- Warning: some emails block .exe files
- Compressing to .zip may help

**Option D: Internal Web Server**
```
http://intranet.company.com/tools/HeadscaleInstaller.exe
```

### 4.3 User Documentation

Create a simple guide for your users:

```
📄 VPN Installation - User Guide

1. Download HeadscaleInstaller.exe
2. Double-click the file
3. If Windows asks for confirmation, click "Run anyway"
4. Fill in your name and device type
5. Click "Install"
6. Wait for installation to complete
7. Tailscale icon appears in system tray

Support: support@yourcompany.com
```

---

## 🔧 Troubleshooting

### Error: "PyInstaller not found"

```powershell
pip install pyinstaller
```

### Error: "SignTool not found"

Install Windows SDK:
https://developer.microsoft.com/windows/downloads/windows-sdk/

### Exe Detected as Virus

**Possible causes:**
- No code signing
- Self-signed signature
- PyInstaller flagged by some antiviruses

**Solutions:**
1. Sign with valid certificate
2. Submit to VirusTotal
3. Add antivirus exclusion

### Exe Doesn't Work on Some PCs

**Check:**
- Windows 10/11 64-bit required
- Internet connection available
- Administrator rights

---

## 📊 Complete Workflow Summary

```
1. Configuration
   ├── Edit headscale_installer.py
   ├── Configure URL, AUTH_KEY, DOMAIN
   └── Save

2. Compilation
   ├── Run build.bat
   ├── Wait for completion
   └── Verify dist\HeadscaleInstaller.exe

3. Signing (optional)
   ├── Obtain certificate
   ├── Run sign.ps1
   └── Verify signature

4. Testing
   ├── Install on test PC
   ├── Verify Headscale connection
   └── Validate functionality

5. Distribution
   ├── Copy to share/USB/email
   ├── Document for users
   └── Provide support
```

---

## 📝 Output Files

After compilation, you'll have:

```
dist/
├── HeadscaleInstaller.exe    # File to distribute (~15 MB)

build/                         # Temporary files (can be deleted)
└── ...

HeadscaleInstaller.spec        # PyInstaller config (can be deleted)
```

**Only `dist\HeadscaleInstaller.exe` is needed for distribution.**

---

## 🔄 Updating the Installer

To create a new version:

1. Modify `headscale_installer.py`
2. Change `VERSION = "1.0.1"` (line ~21)
3. Re-run `build.bat`
4. Sign the new version
5. Redistribute

---

## 📧 Support

For questions:
- [Headscale Documentation](https://headscale.net/)
- [Headscale GitHub](https://github.com/juanfont/headscale)

---

**Happy deploying! 🚀**
