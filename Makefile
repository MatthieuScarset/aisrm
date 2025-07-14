# Makefile for CRM Sales Opportunities Data Processing
.DEFAULT_GOAL := default

###############################################################################
# Global commands
###############################################################################
default:
	@make lint

init:
	-pyenv install $(PYTHON_VERSION)
	-pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_VENV)
	-pyenv local $(PYTHON_VENV)
	@pip install -U pip
	@pip install -r requirements.txt
	@$(MAKE) install_package

install_package:
	@pip uninstall -y $(PACKAGE_NAME) || :
	@pip install -e .

clean:
	@rm -rf data/raw/$(RAW_DATA_ARCHIVE)
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -fr **/__pycache__ **/*.pyc **/.ipynb_checkpoints *.egg-info/ .pytest_cache/
	@rm -f **/.DS_Store **/*Zone.Identifier

lint:
	@find . -iname "*.py" -not -path "./tests/*" | xargs -I {} pylint --output-format=colorized {}; true
	@black .

###############################################################################
# Docker process management commands
###############################################################################
check_ports:
	@echo "Checking what's running on development ports:"
	@lsof -i :$(API_PORT) || echo "Port $(API_PORT) is free"
	@lsof -i :$(APP_PORT) || echo "Port $(APP_PORT) is free"

kill_ports:
	@echo "Killing processes on development ports:"
	@lsof -ti :$(API_PORT) | xargs kill -9 || echo "No process on port $(API_PORT)"
	@lsof -ti :$(APP_PORT) | xargs kill -9 || echo "No process on port $(APP_PORT)"

ps_docker:
	@echo "Running Docker containers:"
	@docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

###############################################################################
# Data-related commands
###############################################################################
data_extract:
	@mkdir -p data/raw
	@curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
	@unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
	@rm -rf data/raw/$(RAW_DATA_ARCHIVE)

data_transform:
	@echo "Work in progress"

###############################################################################
# Backend-related commands
###############################################################################
api_dev:
	@uvicorn api.run:app --reload --port $(API_PORT)

api_docker_build:
	@$(MAKE) docker_build SERVICE=api TAG=$(API_TAG)

api_docker_start:
	@$(MAKE) docker_start SERVICE=api PORT=$(API_PORT) TAG=$(API_TAG)

api_docker_stop:
	@$(MAKE) docker_stop SERVICE=api

###############################################################################
# Frontend-related commands
###############################################################################
app_dev:
	@streamlit run app/run.py

app_docker_build:
	@$(MAKE) docker_build SERVICE=app TAG=$(APP_TAG)

app_docker_start:
	@$(MAKE) docker_start SERVICE=app PORT=$(APP_PORT) TAG=$(APP_TAG)

app_docker_stop:
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
	@gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="user:$(EMAIL)" \
		--role="roles/artifactregistry.writer"
	@gcloud artifacts repositories create $(ARTIFACTSREPO) \
		--repository-format=docker \
		--location=$(REGION) \
		--description="$(PROJECT) Artifact Registry"

# Generic cloud build command with service parameter
cloud_build:
	@docker build -f Dockerfile.$(SERVICE) --platform linux/amd64 --tag=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG) .

# Generic cloud push command with service parameter
cloud_push:
	@docker push $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG)

# Generic cloud deploy command with service parameter
cloud_deploy:
	@echo "Deploying $(SERVICE) with GCloud Run"
	@gcloud run deploy $(PROJECT)-$(SERVICE) \
		--image $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG) \
		--memory $(MEMORY) \
		--region $(REGION)

cloud_pipeline:
	@echo "Running full pipeline..."
	@echo "$(SERVICE) image: $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACTSREPO)/$(PROJECT)-$(SERVICE):$(TAG)"
	@$(MAKE) cloud_build SERVICE=$(SERVICE) TAG=$(TAG)
	@$(MAKE) cloud_push SERVICE=$(SERVICE) TAG=$(TAG)
	@$(MAKE) cloud_deploy SERVICE=$(SERVICE) TAG=$(TAG) MEMORY=$(MEMORY)

cloud_pipeline_api:
	@$(MAKE) cloud_pipeline SERVICE=api TAG=$(API_TAG) MEMORY=$(API_MEMORY)

cloud_pipeline_app:
	@$(MAKE) cloud_pipeline SERVICE=app TAG=$(API_TAG) MEMORY=$(APP_MEMORY)

###############################################################################
# Test commands
###############################################################################
test:
	@pytest -v

test_api:
	@pytest api/tests/test_api.py -v

test_app:
	@pytest app/tests/test_app.py -v

test_data:
	@pytest tests/test_data.py -v