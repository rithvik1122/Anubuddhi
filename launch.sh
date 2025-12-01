#!/bin/bash
# Complete setup and launch guide for Aṇubuddhi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Aṇubuddhi - AI-Powered Quantum Experiment Designer         ║"
echo "║  Complete Setup and Launch Guide                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check conda environment
echo "📦 Checking conda environment..."
if conda env list | grep -q "agentic-quantum"; then
    echo "✅ agentic-quantum environment found"
else
    echo "❌ agentic-quantum environment not found!"
    echo "Please create it with: conda create -n agentic-quantum python=3.9"
    exit 1
fi

# Check API key
echo ""
echo "🔑 Checking API configuration..."
if [ -f .env ]; then
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "✅ API key configured in .env"
    else
        echo "⚠️  .env exists but API key may not be set"
        echo "Make sure OPENAI_API_KEY is set to your OpenRouter key"
    fi
else
    echo "❌ No .env file found!"
    echo "Create .env with: OPENAI_API_KEY=your_openrouter_key_here"
    exit 1
fi

# Check if embedding model is cached
echo ""
echo "🧠 Checking embedding model cache..."
if [ -f "$HOME/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz" ]; then
    # Check if file size is correct (should be ~79MB when fully downloaded)
    filesize=$(stat -f%z "$HOME/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz" 2>/dev/null || stat -c%s "$HOME/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz" 2>/dev/null || echo "0")
    if [ "$filesize" -gt "70000000" ]; then
        echo "✅ Embedding model cached (fast startup)"
    else
        echo "⚠️  Embedding model partially downloaded ($filesize bytes)"
        echo "❗ IMPORTANT: First design will download remaining data (~79MB)"
        echo "   This happens in background - watch terminal for progress"
        echo "   Download may take 5-10 minutes depending on connection"
        echo "   The app will be SLOW to respond during download"
        echo ""
        echo "Continue anyway? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
else
    echo "⚠️  Embedding model not cached"
    echo "❗ IMPORTANT: First design will download ~79MB (5-10 minutes)"
    echo "   This happens in background during app startup"
    echo "   The app will appear FROZEN during download - this is normal!"
    echo "   Watch terminal output for download progress"
    echo ""
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 LAUNCHING STREAMLIT APP                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 What to expect:"
echo "   - App will start at http://localhost:8501 or 8502"
echo "   - Memory system will initialize (5-10 seconds)"
echo "   - Simple designs: 30-60 seconds"
echo "   - Complex designs: 2-3 minutes"
echo ""
echo "💡 Tips:"
echo "   - Watch the terminal for detailed progress"
echo "   - Don't refresh the browser during design"
echo "   - Check sidebar for system status"
echo "   - Memory tab shows learned knowledge"
echo ""
echo "⚠️  If designs are getting stuck:"
echo "   1. Check terminal output - should show refinement cycles"
echo "   2. Test API: python test_api_credits.py"
echo "   3. Check credits at: https://openrouter.ai/credits"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""
sleep 2

cd /home/rithvik/nvme_data2/AgenticQuantum/Agentic
conda run -n agentic-quantum streamlit run app.py
