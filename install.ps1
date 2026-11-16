$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Assert-ExitCode {
    param([string]$Action)
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Action failed with exit code $LASTEXITCODE."
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Python = Join-Path $Root "venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $Launcher) {
        Write-Error "The Python launcher was not found. Install Python 3.11 with: winget install -e --id Python.Python.3.11"
    }
    & py -3.11 -m venv venv
    Assert-ExitCode "Creating the virtual environment"
}

$Version = & $Python -c "import sys; print(str(sys.version_info[0]) + '.' + str(sys.version_info[1]))"
if ($Version -ne "3.11") {
    Write-Error "This environment uses Python $Version. Remove the venv folder and run install.ps1 again so it can create a 3.11 environment."
}

Write-Host "Upgrading pip"
& $Python -m pip install --upgrade pip wheel
Assert-ExitCode "Upgrading pip"

Write-Host "Installing PyTorch ROCm for gfx1100"
& $Python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.1" "torchvision[device-gfx1100]==0.27.0+rocm7.14.1" "torchaudio==2.11.0+rocm7.14.1"
Assert-ExitCode "Installing PyTorch ROCm"

Write-Host "Installing Python packages"
& $Python -m pip install -r (Join-Path $Root "requirements.txt")
Assert-ExitCode "Installing Python packages"

$Work = Join-Path $env:TEMP "aurora-ctranslate2-rocm"
$Zip = Join-Path $Work "rocm-python-wheels-Windows.zip"
if (Test-Path $Work) {
    Remove-Item -Recurse -Force $Work
}
New-Item -ItemType Directory -Path $Work | Out-Null

Write-Host "Replacing CTranslate2 with the ROCm wheel"
Invoke-WebRequest -Uri "https://github.com/OpenNMT/CTranslate2/releases/download/v4.9.0/rocm-python-wheels-Windows.zip" -OutFile $Zip
Expand-Archive -Path $Zip -DestinationPath (Join-Path $Work "wheels") -Force
$Wheel = Get-ChildItem -Recurse (Join-Path $Work "wheels") -Filter "ctranslate2-*-cp311-cp311-win_amd64.whl" | Select-Object -First 1
if (-not $Wheel) {
    Write-Error "The ROCm CTranslate2 wheel for Python 3.11 was not in the release archive."
}
& $Python -m pip install --force-reinstall --no-deps $Wheel.FullName
Assert-ExitCode "Installing the ROCm CTranslate2 wheel"
Remove-Item -Recurse -Force $Work

Write-Host "Installing llama.cpp with the prebuilt Vulkan wheel"
& $Python -m pip install --only-binary=llama-cpp-python "llama-cpp-python==0.3.36" --extra-index-url "https://abetlen.github.io/llama-cpp-python/whl/vulkan"
Assert-ExitCode "Installing llama-cpp-python"

Write-Host "Installing test tools"
& $Python -m pip install -r (Join-Path $Root "requirements-dev.txt")
Assert-ExitCode "Installing test tools"

Write-Host "Done. Activate the environment with .\venv\Scripts\Activate.ps1 and start the assistant with python main.py"
