# sign.ps1
# PowerShell script to sign the Headscale Installer executable
# Run as Administrator

param(
    [string]$CertPath = "",
    [string]$CertPassword = "",
    [string]$ExePath = "dist\HeadscaleInstaller.exe"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Code Signing Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some signing methods require Administrator privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Check if executable exists
if (-not (Test-Path $ExePath)) {
    Write-Host "ERROR: Executable not found at: $ExePath" -ForegroundColor Red
    Write-Host "Please run build.bat first" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/4] Checking for SignTool..." -ForegroundColor Green

# Find signtool.exe
$signtool = $null
$sdkPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
)

foreach ($path in $sdkPaths) {
    $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $signtool = $found.FullName
        break
    }
}

if (-not $signtool) {
    Write-Host "ERROR: SignTool not found" -ForegroundColor Red
    Write-Host "Please install Windows SDK from:" -ForegroundColor Yellow
    Write-Host "https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found: $signtool" -ForegroundColor Gray
Write-Host ""

# Signing method selection
Write-Host "[2/4] Select signing method:" -ForegroundColor Green
Write-Host "1. Certificate from Windows Certificate Store"
Write-Host "2. Certificate from PFX file"
Write-Host "3. Self-signed certificate (testing only)"
Write-Host ""
$method = Read-Host "Enter choice (1-3)"

Write-Host ""
Write-Host "[3/4] Signing executable..." -ForegroundColor Green

switch ($method) {
    "1" {
        # Certificate Store
        Write-Host "Available certificates:" -ForegroundColor Yellow
        Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Format-Table Subject, Thumbprint
        
        $certName = Read-Host "Enter certificate Subject (name shown above)"
        
        $cmd = "& `"$signtool`" sign /n `"$certName`" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `"$ExePath`""
    }
    
    "2" {
        # PFX file
        if ($CertPath -eq "") {
            $CertPath = Read-Host "Enter path to .pfx file"
        }
        
        if (-not (Test-Path $CertPath)) {
            Write-Host "ERROR: Certificate file not found: $CertPath" -ForegroundColor Red
            exit 1
        }
        
        if ($CertPassword -eq "") {
            $securePassword = Read-Host "Enter certificate password" -AsSecureString
            $CertPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
                [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
            )
        }
        
        $cmd = "& `"$signtool`" sign /f `"$CertPath`" /p `"$CertPassword`" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `"$ExePath`""
    }
    
    "3" {
        # Self-signed (testing only)
        Write-Host "Creating self-signed certificate..." -ForegroundColor Yellow
        
        $cert = New-SelfSignedCertificate `
            -Subject "CN=Headscale Installer Test" `
            -Type CodeSigningCert `
            -CertStoreLocation Cert:\CurrentUser\My
        
        Write-Host "Certificate created: $($cert.Thumbprint)" -ForegroundColor Gray
        
        $cmd = "& `"$signtool`" sign /sha1 $($cert.Thumbprint) /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `"$ExePath`""
        
        Write-Host ""
        Write-Host "WARNING: Self-signed certificates will trigger SmartScreen warnings!" -ForegroundColor Red
        Write-Host "This is only suitable for testing, not distribution." -ForegroundColor Red
        Write-Host ""
    }
    
    default {
        Write-Host "ERROR: Invalid choice" -ForegroundColor Red
        exit 1
    }
}

# Execute signing
try {
    Invoke-Expression $cmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[4/4] Verifying signature..." -ForegroundColor Green
        
        $verifyCmd = "& `"$signtool`" verify /pa /v `"$ExePath`""
        Invoke-Expression $verifyCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "SIGNING SUCCESSFUL!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Signed executable: $ExePath" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "You can now distribute this file." -ForegroundColor Yellow
        } else {
            Write-Host ""
            Write-Host "WARNING: Signature verification failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "ERROR: Signing failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Read-Host "Press Enter to exit"
