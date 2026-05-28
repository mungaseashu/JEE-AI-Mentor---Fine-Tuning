# ==============================================================================
# JEE MENTOR AI - AUTOMATED WINDOWS SETUP SCRIPT
# ==============================================================================
Write-Host "🚀 Starting JEE Mentor AI Setup Wizard..." -ForegroundColor Cyan

# 1. Check for Python Installation
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Error: Python 3.8+ is required but was not found. Please install Python and add it to your PATH." -ForegroundColor Red
    Exit
}

# 2. Check for Node.js Installation
if (Get-Command npm -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detected: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️ Warning: Node.js (npm) was not found. Frontend development server requires Node.js." -ForegroundColor Yellow
}

# 3. Create Local Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating Python virtual environment (venv)..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "ℹ️ Virtual environment 'venv' already exists. Skipping creation." -ForegroundColor Gray
}

# 4. Activate Venv and Install Dependencies
Write-Host "🔌 Installing Python backend dependencies (this might take a couple of minutes)..." -ForegroundColor Cyan
& .\venv\Scripts\pip install -r requirements.txt
Write-Host "✅ Backend dependencies successfully installed." -ForegroundColor Green

# 5. Handle environment configuration files
if (-not (Test-Path ".env")) {
    Write-Host "📝 Copying environment variable template to '.env'..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Custom .env file initialized! You can customize database and model choices inside it." -ForegroundColor Green
} else {
    Write-Host "ℹ️ Custom '.env' file already exists. Skipping initialization." -ForegroundColor Gray
}

# 6. Initialize Folder Structures
Write-Host "📂 Ensuring directory structure matches clean architecture guidelines..." -ForegroundColor Cyan
$folders = @("backend", "frontend", "training", "rag", "dataset", "evaluation", "deployment", "docker", "scripts", "tests", "docs", "models/adapters", "data/chroma", "backend/plots")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
}
Write-Host "✅ Folder structures successfully verified." -ForegroundColor Green

Write-Host "`n🎉 SETUP COMPLETED SUCCESSFULLY! 🎉" -ForegroundColor Magenta
Write-Host "To start the application locally in development mode:" -ForegroundColor White
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "2. Launch backend API: uvicorn backend.main:app --reload --port 8000" -ForegroundColor Yellow
Write-Host "3. Setup and start Frontend: cd frontend; npm install; npm run dev" -ForegroundColor Yellow
Write-Host "4. Alternatively, launch everything using multi-container Docker: docker-compose up --build" -ForegroundColor Yellow
