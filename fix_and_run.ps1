Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DocIntel AI - RAG Document Intelligence" -ForegroundColor Cyan
Write-Host "  Powered by Groq Cloud AI" -ForegroundColor DarkCyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if clean_env exists, if not create it
if (-Not (Test-Path ".\clean_env\Scripts\python.exe")) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv clean_env
    Write-Host "      Done!" -ForegroundColor Green
} else {
    Write-Host "[1/4] Virtual environment found." -ForegroundColor Green
}

Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
.\clean_env\Scripts\pip install -r requirements.txt --quiet 2>$null
Write-Host "      Done!" -ForegroundColor Green

# Check .env file
Write-Host "[3/4] Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path ".\.env") {
    $envContent = Get-Content ".\.env" -Raw
    if ($envContent -match "GROQ_API_KEY=.+") {
        Write-Host "      .env file found with GROQ_API_KEY!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "  WARNING: .env file exists but GROQ_API_KEY is not set!" -ForegroundColor Red
        Write-Host "  Please add: GROQ_API_KEY=your_key_here" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Press Enter to continue anyway, or Ctrl+C to exit..." -ForegroundColor DarkGray
        Read-Host
    }
} else {
    Write-Host ""
    Write-Host "  WARNING: .env file not found!" -ForegroundColor Red
    Write-Host "  Create a .env file in the project root with:" -ForegroundColor Yellow
    Write-Host '    GROQ_API_KEY=your_groq_api_key_here' -ForegroundColor White
    Write-Host ""
    Write-Host "  Get your free API key at: https://console.groq.com/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Press Enter to continue anyway, or Ctrl+C to exit..." -ForegroundColor DarkGray
    Read-Host
}

Write-Host ""
Write-Host "[4/4] Starting application..." -ForegroundColor Yellow
Write-Host ""

# Start backend in a new window
Write-Host "  > Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\clean_env\Scripts\Activate.ps1; uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# Start frontend in this window
Write-Host "  > Starting Streamlit frontend on http://localhost:8501 ..." -ForegroundColor Cyan
Write-Host ""
.\clean_env\Scripts\python.exe -m streamlit run frontend\streamlit_app.py
