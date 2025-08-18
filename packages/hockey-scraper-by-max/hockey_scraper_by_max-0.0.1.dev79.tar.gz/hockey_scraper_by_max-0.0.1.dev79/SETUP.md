# 🏒 NHL Hockey Scraper - Environment Setup Guide

This guide will help you recreate the virtual environment outside of VS Code.

## Quick Setup

### Option 1: Using pip with requirements.txt

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (required for scraping)
playwright install chromium
```

### Option 2: Using pip with minimal requirements

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install minimal dependencies only
pip install -r requirements-minimal.txt

# Install Playwright browser
playwright install chromium
```

### Option 3: Using pyproject.toml with pip

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install in editable mode with all dependencies
pip install -e .

# Or with specific extras
pip install -e ".[dev,viz,notebook,dashboard]"

# Install Playwright browser
playwright install chromium
```

### Option 4: Using uv (recommended for speed)

```bash
# Create virtual environment with uv
uv venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
uv pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Important Notes

1. **Always install Playwright browser**: After installing the dependencies, you MUST run:
   ```bash
   playwright install chromium
   ```
   This downloads the browser engine required for web scraping.

2. **Python Version**: Requires Python 3.10 or higher.

3. **Testing your setup**:

   ```bash
   python -c "import pandas, polars, aiohttp, playwright; print('✅ All dependencies installed correctly!')"
   ```

## Dependencies Explanation

### Core Dependencies

- `aiohttp`: Async HTTP client for API calls
- `beautifulsoup4` + `lxml`: HTML parsing
- `selectolax`: Fast HTML parsing alternative
- `playwright`: Browser automation for dynamic content
- `pandas` + `polars`: Data manipulation
- `requests`: HTTP client for simple requests

### Optional Dependencies

- `matplotlib` + `seaborn`: Data visualization
- `jupyter` + `jupyterlab`: Notebook environment
- `streamlit`: Dashboard/web app framework
- `pytest` + development tools: Testing and code quality

## Usage

After setup, you can use the scraper:

```python
import asyncio
from nhl_scraper.scraper import Scraper

async def main():
    scraper = Scraper()
    teams = await scraper.scrape_teams()
    print(teams)

# Run in script
asyncio.run(main())

# Or in Jupyter notebook
await scraper.scrape_teams()
```
