# 🧰 Dev task shortcuts

install:
	pip install -e .[dev]

test:
	pytest

lint:
	ruff .

format:
	black .

notebook:
	jupyter lab
	
marimo:
	marimo run integrations/notebooks/dev_sandbox.marimo.py

cli:
	hockey-scraper --help

dashboard:
	streamlit run integrations/dashboard/app.py

dagster:
	dagster dev
	
# Launch a pre-wired dev notebook
dev_notebook:
	jupyter notebook integrations/notebooks/dev_sandbox.ipynb