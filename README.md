# AI SRM

_The best sales representative matching tool of all time!_

This project is an MVP for an AI-powered app that recommends the best sales representative for a given client and product.  
It uses real CRM data and machine learning to help sales teams match opportunities with the right agent, every time.

## 🚀 Features

- **Predicts the best sales agent** for a given client-product combination
- **Top 3 recommendations** with probability/confidence
- **Explainability:** Shows why an agent is recommended (past deals, similar features)
- **Streamlit web app:** Easy-to-use interface for demo and experimentation

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

    - Install dependencies

        ```bash
        make requirements
        ```

## 👨‍💻 Develop

1. **Prepare data**

    - Get the raw data

        ```bash
        make data_extract
        ```

    - Clean and preprocess pipeline

        ```bash
        make data_transform
        ```

2. **Build model**

    - To be defined

        ```bash
        make model_train...etc
        ```

3. **Etc...**

## 🏗️ Deploy

1. **To do**

---

Made with ❤️ by the AISRM team
