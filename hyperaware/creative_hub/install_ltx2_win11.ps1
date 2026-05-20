# LTX-2 Installation Script for Windows 11
# Target: G:\ai\ltx2
# GPU: RTX 3060 12GB
# Run as Administrator for CUDA toolkit install

$ErrorActionPreference = "Continue"
$AI_ROOT = "G:\ai"
$LTX2_DIR = "$AI_ROOT\ltx2"
$VENV_DIR = "$LTX2_DIR\venv"

Write-Host "=== LTX-2 Creative Hub Installation ===" -ForegroundColor Cyan
Write-Host "Target: $LTX2_DIR" 
Write-Host "GPU: RTX 3060 12GB"
Write-Host ""

# 1. Create directories
Write-Host "[1/5] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $AI_ROOT | Out-Null
New-Item -ItemType Directory -Force -Path $LTX2_DIR | Out-Null

# 2. Check Python
Write-Host "[2/5] Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "  Python: $($pythonCmd.Source)"

# 3. Create venv
Write-Host "[3/5] Creating virtual environment..." -ForegroundColor Yellow
& python -m venv $VENV_DIR
& "$VENV_DIR\Scripts\python" -m pip install --upgrade pip

# 4. Install PyTorch CUDA
Write-Host "[4/5] Installing PyTorch with CUDA..." -ForegroundColor Yellow
& "$VENV_DIR\Scripts\pip" install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. Clone LTX-2
Write-Host "[5/5] Cloning LTX-2 repository..." -ForegroundColor Yellow
if (Test-Path "$LTX2_DIR\LTX-2") {
    Write-Host "  LTX-2 already cloned, updating..."
    Set-Location "$LTX2_DIR\LTX-2"
    & git pull
} else {
    Set-Location $LTX2_DIR
    & git clone https://github.com/Lightricks/LTX-2.git
}

# 6. Install LTX-2 dependencies
Write-Host "[6/6] Installing LTX-2 dependencies..." -ForegroundColor Yellow
Set-Location "$LTX2_DIR\LTX-2"
& "$VENV_DIR\Scripts\pip" install -r requirements.txt
& "$VENV_DIR\Scripts\pip" install huggingface_hub accelerate transformers diffusers

# 7. Download model (lightweight first - just check access)
Write-Host "Downloading LTX-2 model weights..." -ForegroundColor Yellow
& "$VENV_DIR\Scripts\python" -c @"
from huggingface_hub import snapshot_download
print("Downloading LTX-2 model from HuggingFace...")
snapshot_download("Lightricks/LTX-2", local_dir="$LTX2_DIR\models", resume_download=True)
print("Model downloaded successfully!")
"@

# Verify GPU
Write-Host ""
Write-Host "=== Verifying GPU ===" -ForegroundColor Cyan
& "$VENV_DIR\Scripts\python" -c @"
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"CUDA version: {torch.version.cuda}")
"@

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "LTX-2 installed at: $LTX2_DIR"
Write-Host "Activate: $VENV_DIR\Scripts\activate"
