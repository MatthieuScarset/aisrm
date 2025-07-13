# Makefile for CRM Sales Opportunities Data Processing
.DEFAULT_GOAL := default
PYTHON_EXEC = python -B -m

## ===================
## Available commands:
## ===================
## init:	Create your virtual environment
## requirements:	Install or update Python dependencies.
## clean:		Clean up temporary files and directories.
## lint:		Run pylint.
## tests:		Run tests.
## docker_build: 	Build app.
## docker_run: 	Run app.
## docker_stop: 	Kill app.
## data_extract:	Get or update initial raw data.

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

default: _default
_default: pylint pytest

init:
	pyenv install $(PYTHON_VERSION)
	pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_VENV)
	pyenv local $(PYTHON_VENV)

requirements:
	$(PYTHON_EXEC) pip install -U pip
	$(PYTHON_EXEC) pip install -r requirements-$(BUILD_ENV).txt

clean:
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

lint:
	find . -iname "*.py" -not -path "./tests/*" | xargs -I {} pylint --output-format=colorized {}; true
	$(PYTHON_EXEC) black .

tests:
	$(PYTHON_EXEC) pytest -v --color=yes

# Data-related commands
data_extract:
	mkdir -p data/raw
	curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
	unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)

# CI-related commands
docker_build:
	docker build --build-arg BUILD_ENV=$(BUILD_ENV) --tag=$(IMAGE_URI) .

docker_run:
	docker run -d --name=$(PROJECT) -e PORT=8000 -p 8080:8000 $(IMAGE_URI)

docker_stop:
	docker stop $(PROJECT) && docker rm $(PROJECT)
