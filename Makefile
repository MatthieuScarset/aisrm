# Makefile for CRM Sales Opportunities Data Processing
.DEFAULT_GOAL := default
PYTHON_EXEC = python -B -m # Python module executor: -B prevents .pyc generation, -m runs modules
PYTHON_VENV = aisrm-env
PYTHON_VERSION = 3.10.6
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

init:
	pyenv install $(PYTHON_VERSION)
	pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_VENV)
	pyenv local $(PYTHON_VENV)

requirements:
	$(PYTHON_EXEC) pip install -U pip cython wheel
	$(PYTHON_EXEC) pip install -r requirements.txt

clean:
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

pylint:
	find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true
	$(PYTHON_EXEC) black .

pytest:
	$(PYTHON_EXEC) pytest -v --color=yes

# Data-related commands
data_extract:
	mkdir -p data/raw
	curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
	unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)

# CI-related commands
docker_build_dev:
	docker build --tag=$(IMAGE):dev .

docker_build_prod:
	docker build --tag=$(IMAGE_URI) .

docker_run_dev:
	docker run -it -e PORT=8000 -p 8080:8000 $(IMAGE):dev