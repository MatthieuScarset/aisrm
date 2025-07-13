# Makefile for CRM Sales Opportunities Data Processing
.DEFAULT_GOAL := default
PYTHON_EXEC := python -B -m
IMAGE_URI = $(REGION)-docker.pkg.dev/$(PROJECT)/$(ARTIFACTSREPO)/$(IMAGE_NAME)$(COLON)$(TAG)
COLON = :

## ===================
## Available commands:
## ===================
## 
## Global
## ------
## init:		Create your virtual environment
## requirements:	Install or update Python dependencies.
## clean:		Clean up temporary files and directories.
## lint:		Run pylint.
## tests:		Run tests.
## 
## Data:
## ------
## data_extract:	Get or update initial raw data.
## 
## Development:
## ------
## dev_api: 	Run the backend service.
## dev_app: 	Run the frontend service.
## 
## Deployment:
## ------
## docker_build: 	Build app.
## docker_run: 	Run app.
## docker_stop: 	Kill app.
## docker_build_prod: 	Build app for production.
## docker_push_prod: 	Publish app to artifact repository.
## deploy_to_cloud: 	Deploy app to production.

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

default:
	make lint
	make tests

init:
	pyenv install $(PYTHON_VERSION)
	pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_VENV)
	pyenv local $(PYTHON_VENV)
	make requirements

requirements:
	$(PYTHON_EXEC) pip install -U pip
	$(PYTHON_EXEC) pip install -r requirements.txt

clean:
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

lint:
	find . -iname "*.py" -not -path "./tests/*" | xargs -I {} pylint --output-format=colorized {}; true
	$(PYTHON_EXEC) black .

.PHONY: tests
tests:
	$(PYTHON_EXEC) pytest -v --color=yes

# Data-related commands
data_extract:
	mkdir -p data/raw
	curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
	unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
	rm -rf data/raw/$(RAW_DATA_ARCHIVE)

# Dev commands
dev_api:
	$(PYTHON_EXEC) uvicorn api.run:app --reload --port 8000

dev_app:
	$(PYTHON_EXEC) streamlit run app/run.py

# CI-related commands
docker_build:
	docker build --tag=$(PROJECT):dev .

docker_run:
	docker run -it -d --name=$(PROJECT) -e PORT=8000 -p 8080:8000 $(PROJECT):dev

docker_stop:
	docker stop $(PROJECT) && docker rm $(PROJECT)

# Production build commands
cloud_init:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev
	gcloud projects add-iam-policy-binding $(PROJECT) \
		--member="user:$(EMAIL)" \
		--role="roles/artifactregistry.writer"
	gcloud artifacts repositories create $(ARTIFACTSREPO) \
		--repository-format=docker \
		--location=$(REGION) \
		--description="$(PROJECT)"

docker_build_prod:
	@echo "Building image: $(IMAGE_URI)"
	cp requirements.txt requirements-dev.txt
	cp requirements-prod.txt requirements.txt
	docker build --platform linux/amd64 --tag=$(IMAGE_URI) .
	mv requirements-dev.txt requirements.txt

docker_push_prod:
	@echo "Pushing image: $(IMAGE_URI)"
	docker push $(IMAGE_URI)

deploy_to_cloud:
	@echo "Work in progress"