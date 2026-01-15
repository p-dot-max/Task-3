
#!/bin/bash

# Mini Agent Chatbot Setup Script
# Automates the entire setup process and starts the server

set -e  # Exit on error

echo "========================================"
echo "  Mini Agent Chatbot Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "[OK] Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
else
    echo "[OK] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[SETUP] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "[OK] Virtual environment activated"
echo ""

# Upgrade pip
echo "[INSTALL] Upgrading pip..."
pip install --upgrade pip
echo "[OK] Pip upgraded"
echo ""

# Install dependencies from requirements.txt with visible output
echo "[INSTALL] Installing dependencies from requirements.txt..."
echo "          (This may take a few minutes...)"
echo ""
pip install -r requirements.txt
echo ""
echo "[OK] All dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[SETUP] Creating .env file..."
    touch .env
    
    echo ""
    echo "========================================"
    echo "  API Key Configuration"
    echo "========================================"
    echo ""
    echo "You need a Groq API key to use this chatbot."
    echo "Get your free API key from: https://console.groq.com/keys"
    echo ""
    
    read -p "Enter your Groq API Key (or press Enter to skip): " GROQ_KEY
    
    if [ -n "$GROQ_KEY" ]; then
        echo "GROQ_API_KEY=$GROQ_KEY" > .env
        echo "[OK] API key saved to .env file"
        API_KEY_SET=true
    else
        echo "GROQ_API_KEY=your_api_key_here" > .env
        echo "[WARNING] Please edit .env file and add your Groq API key"
        API_KEY_SET=false
    fi
else
    echo "[OK] .env file already exists"
    
    # Check if API key is set
    if grep -q "your_api_key_here" .env || ! grep -q "GROQ_API_KEY=" .env; then
        echo "[WARNING] Please update your GROQ_API_KEY in .env file"
        API_KEY_SET=false
    else
        echo "[OK] API key is configured"
        API_KEY_SET=true
    fi
fi
echo ""

# Create necessary directories
echo "[SETUP] Creating data directories..."
mkdir -p data/documents
mkdir -p data/chroma_db
echo "[OK] Data directories created"
echo ""

# Check if documents exist
if [ -z "$(ls -A data/documents 2>/dev/null)" ]; then
    echo "[INFO] No documents found in data/documents/"
    echo "       Add .md files to data/documents/ for the knowledge base"
else
    DOC_COUNT=$(ls -1 data/documents/*.md 2>/dev/null | wc -l)
    echo "[OK] Found $DOC_COUNT document(s) in data/documents/"
fi
echo ""

echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""

# Check if API key is set before starting server
if [ "$API_KEY_SET" = true ]; then
    echo "[INFO] Starting FastAPI server..."
    echo ""
    echo "========================================"
    echo "  Server Information"
    echo "========================================"
    echo "  API Base:     http://localhost:8000"
    echo "  Health Check: http://localhost:8000/health"
    echo "  API Docs:     http://localhost:8000/docs"
    echo "========================================"
    echo ""
    echo "[INFO] Server is starting... Press CTRL+C to stop"
    echo ""
    
    # Start the server
    python -m uvicorn app.main:app --reload
else
    echo "[WARNING] API key not configured. Please complete these steps:"
    echo ""
    echo "  1. Edit .env file and add your GROQ_API_KEY"
    echo "  2. Add documents to data/documents/ (optional)"
    echo "  3. Start the server manually:"
    echo ""
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "     venv\\Scripts\\activate"
    else
        echo "     source venv/bin/activate"
    fi
    echo "     python -m uvicorn app.main:app --reload"
    echo ""
    echo "  4. Access the API at: http://localhost:8000"
    echo "  5. Check health: http://localhost:8000/health"
    echo "  6. API docs: http://localhost:8000/docs"
    echo ""
    echo "For testing:"
    echo "  curl -X POST http://localhost:8000/chat \\"
    echo "       -H \"Content-Type: application/json\" \\"
    echo "       -d '{\"question\":\"What is RAG?\"}'"
    echo ""
fi
