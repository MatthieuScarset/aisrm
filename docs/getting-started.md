# Getting Started

## Data Source

We use a public dataset specifically designed for testing and learning purposes, which includes five CSV files:

```bash
https://www.kaggle.com/datasets/innocentmfa/crm-sales-opportunities
├── accounts.csv
├── data_dictionary.csv
├── products.csv
├── sales_pipeline.csv
└── sales_teams.csv
```

## Data Pipeline

AISRM provides `make` commands to streamline all repetitive tasks. Our entire Extract Transform Load (ETL) process can be executed with this simple terminal command:

```bash
make data
```

Let's break down the step-by-step process:

### Extract the Dataset Files

We use a `.env` file where `RAW_DATA_ARCHIVE` and `RAW_DATA_URL` are specified.

```bash
# Download and extract raw data from remote source
mkdir -p data/raw
curl -L -o ./data/raw/$(RAW_DATA_ARCHIVE) $(RAW_DATA_URL)
unzip -u data/raw/$(RAW_DATA_ARCHIVE) -d data/raw
rm -rf data/raw/$(RAW_DATA_ARCHIVE)
```

### Merge Data into a Single CSV File

Our custom Python module merges all files by relevant columns (e.g., `sales_agent`, `product`, etc.), reorders, removes or renames columns for better usage, and ensures correct data types (e.g., numeric).

```bash
# Compile the raw dataset for model training
python -m src.data
```

The dataset is now ready for model training.

Your data folder structure should look like this:

```bash
data
├── processed
│   └── dataset.csv
└── raw
    ├── accounts.csv
    ├── data_dictionary.csv
    ├── products.csv
    ├── sales_pipeline.csv
    └── sales_teams.csv

3 directories, 6 files
```

## Model Training

We provide a convenient make command to train and save a new model:

```bash
# Train and save model for development
make model
```

This is equivalent to running:

```bash
python -m src.model dev
```

This command saves a new model, its preprocessor, and metadata as Pickle binary files under `models/`.

For production, we use model versioning with this command:

```bash
# Train and save models for deployment
make models_prod
```

Behind the scenes, this runs:

```bash
python -m src.model v1
python -m src.model v2
```

Your models folder structure should look like this:

```bash
models
├── dev-1753300409
│   ├── metadata.pkl
│   ├── model.pkl
│   └── preprocessor.pkl
├── dev-1753300434
│   ├── metadata.pkl
│   ├── model.pkl
│   └── preprocessor.pkl
├── dev-1753807777
│   ├── metadata.pkl
│   ├── model.pkl
│   └── preprocessor.pkl
├── v1
│   ├── metadata.pkl
│   ├── model.pkl
│   └── preprocessor.pkl
└── v2
    ├── metadata.pkl
    ├── model.pkl
    └── preprocessor.pkl

6 directories, 15 files
```

## Development

```bash
# Run both backend and frontend services at once.
# Shorthand for: "docker-compose up --build".
make up
# Kill services
# Shorthand for: "docker-compose down".
make down
```

### Running and testing the backend only

The backend application handles **prediction making** and is built with FastAPI. It can run locally and be shipped as a Docker container for production.

```bash
# Run locally for development
# Available at http://localhost:8500
make api_dev

# Build the Docker application
make api_build

# Start and test the application
make api_start
make test_api

# Stop the service
make api_stop
```

### Running and testing the frontend only

The frontend application serves as our decision-making tool and is built with Streamlit. It can run locally and be shipped as a Docker container for production.

```bash
# Run locally for development
# Available at http://localhost:8501
make app_dev

# Build the Docker application
make app_build

# Start and test the application
make app_start
make test_app

# Stop the service
make app_stop
```

## Deployment

Backend and frontend applications are decoupled to ensure better performance, scalability, and the ability to deploy individual applications when needed.

Deployments are triggered automatically via GitHub workflow when creating a new release tag:

```bash
# Check latest tags
git fetch --tags
git tag

# Tag must be named release-{app|api}-{0.0.x}
# See .github/workflows/deploy.yml -> on.push.tag
git tag -a release-app-0.0.1 -m "Describe this version"
git push --tags

# Monitor the GitHub Actions workflow
# See https://github.com/MatthieuScarset/aisrm/actions/workflows/deploy.yml
```

Once deployed, you can retrieve the URLs from Google Cloud using these make commands:

```bash
# Get the deployed API URL
make cloud_get_api_url

# Get the deployed APP URL
make cloud_get_app_url
```