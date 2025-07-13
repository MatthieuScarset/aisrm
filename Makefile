# Makefile for CRM Sales Opportunities Data Processing
.DEFAULT_GOAL := default
PMX = python -B -m # Python module executor: -B prevents .pyc generation, -m runs modules
RAW_DATA_URL = https://www.kaggle.com/api/v1/datasets/download/innocentmfa/crm-sales-opportunities
RAW_DATA_ARCHIVE = crm-sales-opportunities.zip

## ===================
## Available commands:
## ===================
## requirements:	Install or update Python dependencies.
## clean:		Clean up temporary files and directories.
## data_extract:	Get or update initial raw data.
## pylint:		Run pylint.
## pytest:		Run unit tests.

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

default: tests

tests: pylint pytest

requirements:
	$(PMX) pip install -U pip
	$(PMX) pip install -r requirements.txt

clean:
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

data_extract:
	mkdir -p data/raw
	curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
	unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)

pylint:
	find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
	$(PYMODEXEC) pytest -v --color=yes