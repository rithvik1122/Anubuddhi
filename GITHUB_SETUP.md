# Setup Instructions for GitHub

## Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rithvik1122/Anubuddhi.git
   cd Anubuddhi
   ```

2. **Create your `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Add your API keys to `.env`:**
   ```bash
   # Edit .env and add your OpenRouter API key
   OPENAI_API_KEY=your_openrouter_api_key_here
   ```

4. **Run the installation script:**
   ```bash
   bash install.sh
   ```

5. **Launch the application:**
   ```bash
   bash launch.sh
   ```

## Important Notes

- **Never commit your `.env` file** - it contains your API keys
- The `.env` file is already in `.gitignore` to prevent accidental commits
- Use `.env.example` as a template for required environment variables
- Get your OpenRouter API key from: https://openrouter.ai/

## Repository Structure

- `Results_FreeSim/` - FreeSim simulation results for all experiments
- `Results_QuTiP/` - QuTiP simulation results
- `paper/` - LaTeX paper and figures
- `src/` - Source code for Aṇubuddhi system
- `Toolbox/` - Quantum optics component toolbox

## Verifying Your Setup

After setup, test the API connection:
```bash
python test_api_credits.py
```

This will verify your API key is working correctly.
