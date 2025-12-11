#!/bin/bash
# Launch Streamlit app with correct conda environment

echo "🚀 Starting Aṇubuddhi - Quantum AI Designer"
echo "📦 Using conda environment: agentic-quantum"
echo ""

cd /home/rithvik/nvme_data2/AgenticQuantum/Agentic
conda run -n agentic-quantum streamlit run app.py
