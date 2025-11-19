#!/bin/bash
# ARGO v9.0 Clean - Quick Install Script

echo "=========================================="
echo "ARGO v9.0 Clean - Installation"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

echo "Python version:"
python3 --version

# Create .env if doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env created from example"
    echo "⚠ Please edit .env and add your OPENAI_API_KEY"
else
    echo "✓ .env already exists"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Run: python scripts/audit_architecture.py"
echo "3. Run: streamlit run app/ui.py"
echo ""
