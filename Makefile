# Makefile for CRM Sales Opportunities Data Processing

# Load .env file if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif

.DEFAULT_GOAL := default

## #############################################################################
## # Global commands
## #############################################################################
default:
	@make lint

help:	## Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

init:	## Create virtual environment (venv)
	-python3 -m venv $(PYTHON_VENV)
	-$(PYTHON_VENV)/bin/pip install -U pip
	-$(PYTHON_VENV)/bin/pip install --break-system-packages -r requirements.txt
	@echo "Virtual environment '$(PYTHON_VENV)' created and dependencies installed."
	@echo "Start venv as follow:"
	@echo "========================================================================"
	@echo "source .venv/bin/activate"
	@echo "make data"
	@echo "make model"
	@echo "make up"
	@echo "========================================================================"

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
model:	## Train and save model for dev purpose.
	@python -m src.model dev

models_prod:	## Train and save models for deployment purpose.
	@python -m src.model v1
	@python -m src.model v2

## #############################################################################
## # Backend-related commands
## #############################################################################
api_dev:	## Start API server in development mode with auto-reload
	@uvicorn api.run:app --reload --port $(API_PORT)

api_build:	## Build Docker image for API service
	@$(MAKE) docker_build SERVICE=api TAG=$(API_TAG)

api_start:	## Start API service in Docker container
	@$(MAKE) docker_start SERVICE=api PORT=$(API_PORT) TAG=$(API_TAG)

api_stop:	## Stop and remove API Docker container
	@$(MAKE) docker_stop SERVICE=api

## #############################################################################
## # Frontend-related commands
## #############################################################################
app_dev:	## Start Streamlit app in development mode
	@streamlit run app/run.py

app_build:	## Build Docker image for frontend app service
	@$(MAKE) docker_build SERVICE=app TAG=$(APP_TAG)

app_start:	## Start frontend app service in Docker container
	@$(MAKE) docker_start SERVICE=app PORT=$(APP_PORT) TAG=$(APP_TAG)

app_stop:	## Stop and remove frontend app Docker container
	@$(MAKE) docker_stop SERVICE=app

###############################################################################
# Generic docker commands (to reduce duplication)
###############################################################################
docker_build:
	@docker build -f Dockerfile.$(SERVICE) --tag=$(PACKAGE_NAME)-$(SERVICE):$(TAG) .

docker_start:
	docker run -it -d --name=$(PACKAGE_NAME)-$(SERVICE) -p $(PORT):$(PORT) -e PORT=$(PORT) $(PACKAGE_NAME)-$(SERVICE):$(TAG)

docker_stop:
	@docker stop $(PACKAGE_NAME)-$(SERVICE) && docker rm $(PACKAGE_NAME)-$(SERVICE)

up:
	@docker-compose up --build

down:
	@docker-compose down
###############################################################################
# Production build commands
###############################################################################
cloud_init: ## Initialize Google Cloud for deployments
	@gcloud config set project $(PROJECT_ID)
	@$(MAKE) cloud_enable_apis
	@$(MAKE) cloud_create_artifact_repo
	@$(MAKE) cloud_create_service_account
	@$(MAKE) cloud_get_service_account_key

cloud_enable_apis: # Enable required Google Cloud APIs
	@gcloud services enable run.googleapis.com --project=$(PROJECT_ID)

# Create Google Cloud Artifact Registry repository
cloud_create_artifact_repo:
	@gcloud artifacts repositories create $(ARTIFACTSREPO) \
		--repository-format=docker \
		--location=$(REGION) \
		--project=$(PROJECT_ID) \
		--description="$(PACKAGE_NAME) Artifact Registry" || echo "Repository already exists or error occurred"
	@echo "Artifact Registry created: $(ARTIFACTSREPO) in region $(REGION)"

# Create Google Cloud service account with required roles and download key
cloud_create_service_account:
	@gcloud iam service-accounts create $(PACKAGE_NAME)-sa \
		--project=$(PROJECT_ID) \
		--display-name="$(PACKAGE_NAME) Service Account"

	@echo "Service account created: $(PACKAGE_NAME)-sa@$(PROJECT_ID).iam.gserviceaccount.com"
	@gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(PACKAGE_NAME)-sa@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/artifactregistry.writer"
	@gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(PACKAGE_NAME)-sa@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/run.admin"
	@echo "Granted Artifact Registry Writer and Cloud Run Admin roles to: $(PACKAGE_NAME)-sa@$(PROJECT_ID).iam.gserviceaccount.com"

# Download service account key for authentication
cloud_get_service_account_key:
	@gcloud iam service-accounts keys create gcp-sa-key.json \
		--iam-account=$(PACKAGE_NAME)-sa@$(PROJECT_ID).iam.gserviceaccount.com \
		--project=$(PROJECT_ID)
	@echo "Service account key saved to gcp-sa-key.json"

cloud_build:	
	@docker build -f Dockerfile.$(SERVICE) --platform linux/amd64 --tag=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PACKAGE_NAME)-$(SERVICE):$(TAG) .

cloud_push:
	@docker push $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PACKAGE_NAME)-$(SERVICE):$(TAG)

cloud_deploy:
	@echo "Deploying $(SERVICE) with GCloud Run"
	@gcloud config set project $(PROJECT_ID)	
	@gcloud run deploy $(PACKAGE_NAME)-$(SERVICE) \
		--image $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PACKAGE_NAME)-$(SERVICE):$(TAG) \
		--memory $(MEMORY) \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--port $(PORT)

cloud_pipeline:
	@echo "Running full pipeline..."
	@echo "$(SERVICE) image: $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PACKAGE_NAME)-$(SERVICE):$(TAG)"
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

cloud_get_api_url:	## Get the deployed API URL
	@gcloud run services describe $(PACKAGE_NAME)-api --region=$(REGION) --format="value(status.url)" 2>/dev/null || echo "Service not found"

cloud_get_app_url:	## Get the deployed APP URL
	@gcloud run services describe $(PACKAGE_NAME)-app --region=$(REGION) --format="value(status.url)" 2>/dev/null || echo "Service not found"

cloud_get_urls:	## Get URLs of all deployed services
	@echo "Getting deployed service URLs..."
	@echo "API URL:"
	@$(MAKE) cloud_get_api_url
	@echo "APP URL:"
	@$(MAKE) cloud_get_app_url

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