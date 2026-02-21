#!/bin/bash
# setup.sh — Codex Astartes deployment ritual

echo "Ultramarines — Beginning deployment ritual..."
echo "   World: $(hostname)"
echo ""

# Check Python version
python3 --version || { echo "Python 3 required. Aborting."; exit 1; }

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify .env exists
if [ ! -f .env ]; then
    echo "No .env file found."
    echo "   Copy the template: cp worlds/NEW_WORLD_TEMPLATE.env .env"
    echo "   Then fill in your ElevenLabs API key."
    exit 1
fi

echo ""
echo "Deployment complete. The Chapter stands ready."
echo "   Run: python main.py"
echo ""
echo "   For His Word and His Glory."
