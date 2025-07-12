# AI SRM

_The best sales representatives matcher of all time!_

This project is an MVP for an AI-powered app that recommends the best sales representative for a given client and product.  
It uses real CRM data and machine learning to help sales teams match opportunities with the right agent, every time.

---

## 🚀 Features

- **Predicts the best sales agent** for a given client-product combination
- **Top 3 recommendations** with probability/confidence
- **Explainability:** Shows why an agent is recommended (past deals, similar features)
- **Streamlit web app:** Easy-to-use interface for demo and experimentation

---

## ⚡️ Getting Started

1. **Clone the repository**

    ```bash
    git clone https://github.com/YOUR-ORG/aisrm.git
    cd aisrm
    ```

2. **Set up your Python environment**

    - Make sure you have [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) installed.
    - Install the correct Python version (if not already):

        ```bash
        pyenv install 3.10.6
        ```

    - Create and activate a new virtual environment:

        ```bash
        pyenv virtualenv 3.10.6 aisrm-env
        pyenv local aisrm-env
        ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Download and prepare the data**

    - Download the [CRM Sales Opportunities dataset](https://www.kaggle.com/datasets/innocentmfa/crm-sales-opportunities) from Kaggle.
    - Unzip it to the `data/raw/crm-sales-opportunities/` folder so it contains:

        - `accounts.csv`
        - `products.csv`
        - `sales_pipeline.csv`
        - `sales_teams.csv`
        - `data_dictionary.csv`

5. **Train the model**

    ```bash
    python -m scripts.train_model
    ```

6. **Launch the Streamlit app**

    ```bash
    streamlit run app.py
    ```

    - The web app will open in your browser. Select a client and product to see the top recommended sales agents and explanations.

---

## 🗂️ Project Structure

```text
aisrm/
├── data/
│   └── raw/
│       └── crm-sales-opportunities/
│           ├── accounts.csv
│           ├── products.csv
│           ├── sales_pipeline.csv
│           ├── sales_teams.csv
│           └── data_dictionary.csv
├── models/
├── notebooks/
├── scripts/
│   ├── load_data.py
│   ├── train_model.py
│   └── predict_agent.py
├── app.py
├── requirements.txt
└── README.md


## 😃 How It Works

- Loads and merges CRM data (clients, products, sales, teams)
- Trains a machine learning model (RandomForest) to predict the best sales agent
- Provides an interactive UI for predictions and explanations

---

## 🤝 Collaboration

- All code is currently in the **MVP / draft phase** — feedback and contributions welcome!
- Please open a Pull Request for any changes
- See TODOs in the code and [Issues] tab for next steps

---
Made with ❤️ by the AISRM team
