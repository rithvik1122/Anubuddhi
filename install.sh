#!/bin/bash

# Installation script for Agentic Quantum System
# This script sets up the conda environment and installs all dependencies

set -e  # Exit on any error

echo "🚀 Setting up Agentic Quantum System"
echo "======================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda or Miniconda first."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda found: $(conda --version)"

# Environment name
ENV_NAME="agentic-quantum"

# Check if environment already exists
if conda env list | grep -q "^${ENV_NAME}\s"; then
    echo "📦 Conda environment '${ENV_NAME}' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️ Removing existing environment..."
        conda env remove -n ${ENV_NAME} -y
    else
        echo "⚠️ Using existing environment. Run 'conda activate ${ENV_NAME}' to use it."
        exit 0
    fi
fi

# Create conda environment with Python 3.9
echo "📦 Creating conda environment with Python 3.9..."
conda create -n ${ENV_NAME} python=3.9 -y

# Activate conda environment
echo "🔌 Activating conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ${ENV_NAME}

# Install scientific computing packages from conda-forge first
echo "🔬 Installing scientific computing packages from conda-forge..."
conda install -n ${ENV_NAME} -c conda-forge numpy scipy matplotlib pandas jupyter -y
conda install -n ${ENV_NAME} -c conda-forge qutip -y  # Quantum Toolbox in Python

# Install other dependencies with pip
echo "📚 Installing remaining dependencies with pip..."
pip install --upgrade pip
pip install -r requirements.txt

# Install package in development mode
echo "🔧 Installing agentic-quantum in development mode..."
pip install -e .

# Set up environment variables template
if [ ! -f ".env" ]; then
    echo "📝 Creating environment variables template..."
    cat > .env << EOF
# Agentic Quantum Configuration
# Copy this file and fill in your API keys

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Quantum Simulation Settings
SIMULATION_BACKEND=qutip
MAX_PHOTONS=10
CUTOFF_DIMENSION=20

# Agent Configuration
MAX_CONCURRENT_TASKS=5
TASK_TIMEOUT_SECONDS=300
DEFAULT_EXECUTION_STRATEGY=adaptive

# Vector Database
DB_PATH=./quantum_knowledge_db
COLLECTION_NAME=quantum_experiments
EMBEDDING_DIMENSION=384

# Logging
LOG_LEVEL=INFO
LOG_FILE=agentic_quantum.log
EOF
    echo "📄 Created .env template - please fill in your API keys"
fi

# Create directories for data and logs
echo "📁 Creating data directories..."
mkdir -p data/experiments
mkdir -p data/knowledge_base
mkdir -p logs
mkdir -p outputs

# Run basic tests to verify installation
echo "🧪 Running basic tests..."
python -c "
import sys
print('Testing imports...')

try:
    import numpy as np
    print('✅ NumPy:', np.__version__)
except ImportError as e:
    print('❌ NumPy import failed:', e)
    sys.exit(1)

try:
    import pandas as pd
    print('✅ Pandas:', pd.__version__)
except ImportError as e:
    print('❌ Pandas import failed:', e)
    sys.exit(1)

try:
    import qutip
    print('✅ QuTiP:', qutip.__version__)
except ImportError as e:
    print('❌ QuTiP import failed:', e)
    sys.exit(1)

try:
    import langchain
    print('✅ LangChain:', langchain.__version__)
except ImportError as e:
    print('❌ LangChain import failed:', e)
    sys.exit(1)

try:
    import chromadb
    print('✅ ChromaDB:', chromadb.__version__)
except ImportError as e:
    print('❌ ChromaDB import failed:', e)
    sys.exit(1)

print('🎉 All core dependencies installed successfully!')
"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📖 Next steps:"
echo "1. Edit the .env file and add your API keys"
echo "2. Activate the conda environment: conda activate ${ENV_NAME}"
echo "3. Run the example: python examples/complete_workflow_demo.py"
echo ""
echo "🔄 To activate the environment in the future:"
echo "   conda activate ${ENV_NAME}"
echo ""
echo "📚 Documentation:"
echo "- README.md - Project overview and usage"
echo "- examples/ - Example workflows and demonstrations"
echo "- docs/ - Detailed documentation"
echo ""
echo "🐛 Troubleshooting:"
echo "- Check logs in logs/ directory"
echo "- Verify API keys in .env file"
echo "- Run tests: python -m pytest tests/"
echo ""
echo "🎯 Happy quantum experimenting!"
