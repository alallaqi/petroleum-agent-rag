# 🛢️ Petroleum Agent RAG - Windows Setup Script
# Run this script in PowerShell to set up the environment automatically

Write-Host "🛢️ Petroleum Agent RAG - Windows Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if Python is installed
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.12+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if Ollama is installed
Write-Host "🤖 Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version
    Write-Host "✅ Found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
    Write-Host "After installing Ollama, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r Requirements.txt

# Download Ollama models
Write-Host "🧠 Downloading AI models..." -ForegroundColor Yellow
Write-Host "⏳ This may take a few minutes..." -ForegroundColor Cyan

ollama pull llama3.2:latest
ollama pull mxbai-embed-large

# Create .env file from template
Write-Host "🔧 Setting up environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item "env-example.txt" ".env"
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file to customize your configuration (optional)" -ForegroundColor White
Write-Host "2. Add your PDF files to the 'data' folder" -ForegroundColor White
Write-Host "3. Run: python 1_pdf_to_embeddings.py" -ForegroundColor White
Write-Host "4. Run: python 5_website_scraper.py (optional)" -ForegroundColor White
Write-Host "5. Run: streamlit run 4_chatbot.py" -ForegroundColor White
Write-Host "6. Open browser to: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "🛢️ Happy Petroleum Engineering! 🛢️" -ForegroundColor Green 