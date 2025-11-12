# Olist Agentic Analytics
Conversational analytics system for the Olist Brazilian e-commerce dataset.

## Overview
**APMollar** is an AI-powered interactive data analysis app built using **Streamlit** and **Python**.  
It leverages agentic reasoning to interpret large e-commerce datasets (based on the Olist dataset) and allows users to query data in natural language to gain actionable insights.

This project demonstrates how Large Language Models (LLMs) can assist in real-time business intelligence — transforming data queries into visual and textual explanations dynamically.

---

## Architecture Diagram
![Architecture Diagram](A_flowchart-style_digital_diagram_illustrates_the_.png)

---

## Features
- **LLM-Driven Agentic System** — Uses a prompt-driven agent (`agent.py`) to analyze datasets and generate context-aware insights.
- **Automated Data Visualization** — Generates charts and tables dynamically based on user queries.
- **Integrated Olist Dataset** — Includes various CSVs covering customers, orders, sellers, products, and payments.
- **Natural Language Queries** — Ask questions like “Top selling categories in 2017” or “Average delivery time per state.”
- **Streamlit Frontend** — Responsive dashboard UI with a modern and clean design.

---

## 🏗️ Project Structure
```
apmollar/
│
├── app.py                  # Main Streamlit app entry point
├── agent.py                # LLM/agent logic for data query interpretation
├── prompts.py              # Predefined prompt templates
│
├── tools/
│   ├── charts.py           # Chart creation and visualization utilities
│   ├── geo.py              # Geolocation-based analysis tools
│   ├── sql_tool.py         # SQL query and data transformation helper
│
├── data/olist/             # E-commerce datasets (CSV files)
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   └── ...
│
├── frontend/               # Optional UI media and visuals
│
├── .streamlit/config.toml  # Streamlit app configuration
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

---

## Installation & Setup

### 1️ Clone the Repository
```bash
git clone https://github.com/yourusername/apmollar.git
cd apmollar
```

### 2️  Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # (on Mac/Linux)
venv\Scripts\activate     # (on Windows)
```

### 3️ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️ Run the App
```bash
streamlit run app.py
```

Then open your browser and go to:
```
http://localhost:8501
```

---

## Dataset Information
The app uses **Olist e-commerce datasets** that cover:
- Customer demographics and geolocation
- Order, item, and payment details
- Product metadata
- Seller information and customer reviews  

All CSVs are included under the `data/olist/` directory.

---

##  Example Queries
You can interact with the system by asking:
- “Show me the top 5 cities by revenue.”
- “Plot monthly order trends for 2017.”
- “Which categories have the highest average review scores?”
- “What is the average delivery time by state?”

---

Future Improvements
- Integrate **live database connections** (PostgreSQL or DuckDB) instead of static CSVs.
- Enhance the **agent’s reasoning** with retrieval-augmented generation (RAG) and memory.
- Add **user authentication** for personalized dashboards.
- Build an **automated reporting system** to export insights to PDF or email.
- Incorporate **forecasting models** for sales and demand prediction.

