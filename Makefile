# Makefile for CRM Sales Opportunities Data Processing
.DEFAULT_GOAL := default

## #############################################################################
## # Global commands
## #############################################################################
default:
	@make lint

help:	## Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

init:	## Create virtual environment (Pyenv)
	-pyenv install $(PYTHON_VERSION)
	-pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_VENV)
	-pyenv local $(PYTHON_VENV)
	@pip install -U pip
	@pip install -r requirements.txt

install_package:	## Install this package in editable mode.
	@pip uninstall -y $(PACKAGE_NAME) || :
	@pip install -e .

clean:	## Delete temporary files, cache, and build artifacts
	@rm -rf data/**/*.csv
	@rm -rf data/**/$(RAW_DATA_ARCHIVE)
	@rm -rf models/dev-**/
	@find . -type f -name "*.pkl" -delete
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -fr **/__pycache__ **/*.pyc **/.ipynb_checkpoints *.egg-info/ .pytest_cache/
	@rm -f **/.DS_Store **/*Zone.Identifier

lint:	## Run pylint and black code formatting on Python files
	@find . -iname "*.py" -not -path "./tests/*" -not -name ".pylintrc" | xargs -I {} pylint --output-format=colorized {}; true

## #############################################################################
## # Docker process management commands
## #############################################################################
check_ports:	## Check which processes are running on development ports
	@echo "Checking what's running on development ports:"
	@lsof -i :$(API_PORT) || echo "Port $(API_PORT) is free"
	@lsof -i :$(APP_PORT) || echo "Port $(APP_PORT) is free"

kill_ports:	## Kill all processes running on development ports
	@echo "Killing processes on development ports:"
	@lsof -ti :$(API_PORT) | xargs kill -9 || echo "No process on port $(API_PORT)"
	@lsof -ti :$(APP_PORT) | xargs kill -9 || echo "No process on port $(APP_PORT)"

ps_docker:	## List running Docker containers in a formatted table
	@echo "Running Docker containers:"
	@docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

## #############################################################################
## # Data-related commands
## #############################################################################
data_extract:	## Download and extract raw data from remote source
	@mkdir -p data/raw
	@curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
	@unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
	@rm -rf data/raw/$(RAW_DATA_ARCHIVE)

data_prepare:	## Compiles the raw dataset for model training.
	@python -m src.data

.PHONY: data
data:	## Full ETL data pipeline.
	@$(MAKE) data_extract
	@$(MAKE) data_prepare

## #############################################################################
## # Model training-related commands
## #############################################################################
model:	## Train and save model.
	@python -m src.model

## #############################################################################
## # Backend-related commands
## #############################################################################
api_dev:	## Start API server in development mode with auto-reload
	@uvicorn api.run:app --reload --port $(API_PORT)

api_docker_build:	## Build Docker image for API service
	@$(MAKE) docker_build SERVICE=api TAG=$(API_TAG)

api_docker_start:	## Start API service in Docker container
	@$(MAKE) docker_start SERVICE=api PORT=$(API_PORT) TAG=$(API_TAG)

api_docker_stop:	## Stop and remove API Docker container
	@$(MAKE) docker_stop SERVICE=api

## #############################################################################
## # Frontend-related commands
## #############################################################################
app_dev:	## Start Streamlit app in development mode
	@streamlit run app/run.py

app_docker_build:	## Build Docker image for frontend app service
	@$(MAKE) docker_build SERVICE=app TAG=$(APP_TAG)

app_docker_start:	## Start frontend app service in Docker container
	@$(MAKE) docker_start SERVICE=app PORT=$(APP_PORT) TAG=$(APP_TAG)

app_docker_stop:	## Stop and remove frontend app Docker container
	@$(MAKE) docker_stop SERVICE=app

###############################################################################
# Generic docker commands (to reduce duplication)
###############################################################################
docker_build:
	@docker build -f Dockerfile.$(SERVICE) --tag=$(PROJECT)-$(SERVICE):$(TAG) .

docker_start:
	docker run -it -d --name=$(PROJECT)-$(SERVICE) -p $(PORT):$(PORT) -e PORT=$(PORT) $(PROJECT)-$(SERVICE):$(TAG)

docker_stop:
	@docker stop $(PROJECT)-$(SERVICE) && docker rm $(PROJECT)-$(SERVICE)

###############################################################################
# Production build commands
###############################################################################
cloud_init:
	@gcloud auth configure-docker $(REGION)-docker.pkg.dev
	@gcloud projects add-iam-policy-binding $(PROJECT) \
		--member="user:$(EMAIL)" \
		--role="roles/artifactregistry.writer"
	@gcloud artifacts repositories create $(ARTIFACTSREPO) \
		--repository-format=docker \
		--location=$(REGION) \
		--description="$(PROJECT) Artifact Registry"

cloud_build:	
	@docker build -f Dockerfile.$(SERVICE) --platform linux/amd64 --tag=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG) .

cloud_push:
	@docker push $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG)

cloud_deploy:
	@echo "Deploying $(SERVICE) with GCloud Run"
	@gcloud run deploy $(PROJECT)-$(SERVICE) \
		--image $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG) \
		--memory $(MEMORY) \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--port $(PORT)

cloud_pipeline:
	@echo "Running full pipeline..."
	@echo "$(SERVICE) image: $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG)"
	@$(MAKE) cloud_build SERVICE=$(SERVICE) TAG=$(TAG)
	@$(MAKE) cloud_push SERVICE=$(SERVICE) TAG=$(TAG)
	@$(MAKE) cloud_deploy SERVICE=$(SERVICE) TAG=$(TAG) MEMORY=$(MEMORY) PORT=$(PORT)

## ###############################################################################
## # Cloud-related commands
## ###############################################################################
cloud_pipeline_api:	## Deploy API service to Google Cloud using predefined configuration
	@$(MAKE) cloud_pipeline SERVICE=api TAG=$(API_TAG) MEMORY=$(API_MEMORY) PORT=$(API_PORT)

cloud_pipeline_app:	## Deploy frontend app service to Google Cloud using predefined configuration
	@$(MAKE) cloud_pipeline SERVICE=app TAG=$(APP_TAG) MEMORY=$(APP_MEMORY) PORT=$(APP_PORT)

## ###############################################################################
## # Test commands
## ###############################################################################
test:	## Run all tests using pytest
	@pytest -v

test_api:	## Run API-specific tests
	@pytest api/tests/test_api.py -v

test_app:	## Run frontend app-specific tests
	@pytest app/tests/test_app.py -v

test_data:	## Run data processing and validation tests
	@pytest tests/test_data.py -v