# AI SRM

_The best sales representative matching tool of all time!_

This project is an MVP for an AI-powered app that recommends the best sales representative for a given client and product.
It uses real CRM data and machine learning to help sales teams match opportunities with the right agent, every time.

## 🚀 Features

- **Predicts the best sales agent** for a given client-product combination
- **Top 3 recommendations** with probability/confidence
- **Explainability:** Shows why an agent is recommended (past deals, similar features)
- **Streamlit web app:** Easy-to-use interface for demo and experimentation
- **Automatic build and deploy to GCP:** Github PRs trigger code quality checks and release tags trigger a new deployment.

## ⚡️ Getting Started

1. **Clone the repository**

    ```bash
    git clone https://github.com/YOUR-ORG/aisrm.git
    cd aisrm
    ```

2. **Set up your Python environment**

    - Make sure you have [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) installed.

    - Create your environment file:

        ```bash
    	cp .env.example .env
        ```

    - Create and activate a new virtual environment:

        ```bash
        make init
        ```

    - Run `make` help to learn more about all available commands

## 👨‍💻 Develop

1. **Data & Model training**

```bash
# Get the raw data.
# Clean and compiled into a new raw dataset.
make data
# Build and save model files.
make data_preprocess
```

2. **Application development**

```bash
# Start the backend application in dev mode:
make api_dev
# Start the frontend application in dev mode:
make app_dev
```


## 🏗️ Deploy

1. **Docker images**

    - Build and test the containers:

        ```bash
        make api_docker_build
        make api_docker_start
        # Test the API routes in your browser:
        # http://localhost:8500
        make api_docker_stop
        ```

        ```bash
        make app_docker_build
        make app_docker_start
        # Test the frontend in your browser:
        # http://localhost:8501
        make app_docker_stop
        ```

2. **Cloud build**

    - Option 1: Manual deployment

        ```bash
        # Build, push and publish the backend to GCP 
        make cloud_pipeline_api
        # Build, push and publish the fronted to GCP 
        make cloud_pipeline_app
        ```

    - Option 2: Create a release tag 

        ```bash
        # Check latest tags
        git fetch --tags
        git tag
        # Tag must be named release-{app|api}-{0.0.x}
        # @see .github/workflows/deploy.yml -> on.push.tag
        git tag -a release-app-0.0.1 -m "Describe this version"
        git push --tags
        # Watch the Github Actions run
        # @see https://github.com/MatthieuScarset/aisrm/actions/workflows/deploy.yml
        ```

---

Made with ❤️ by the AISRM team
