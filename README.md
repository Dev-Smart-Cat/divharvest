# 🌾 Dividend Harvest — B3 Dividend Payment Calendar

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.0%2B-red)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Project Status](https://img.shields.io/badge/project-working%20in%20progress-orange)]()

## About the Project

**Dividend Harvest** is a Streamlit web app that lets you explore the dividend payment calendar of companies listed on B3 (Brazilian Stock Exchange).

At this stage, the application includes the dividend calendar. In future releases, it will include features ranging from beginner-friendly investor analysis to deeper fundamental analysis, such as evaluating company financial results.

### 📊 Methodology:

This project follows the investment philosophy of **Luiz Barsi**, known as the "Dividend King", focusing on companies with a **consistent** dividend payment history.

The methodology used in this application is aimed at investors who seek monthly passive income and want to analyze companies that pay consistent dividends, as well as identify the months in which the selected companies usually distribute dividends. This helps investors make better portfolio decisions about which companies are most suitable to hold. The app also confirms each company's sector, which is a key factor for many investors when deciding whether to buy a specific stock.

**Selection Criteria:**
- Only months in which the company paid dividends **4 times or more** over the years are displayed in the calendar
- This reinforces a **predictable and reliable** dividend distribution pattern
- It is ideal for **long-term investors** seeking passive income

### 🎯 Goal

Make financial planning easier for investors who follow a dividend strategy by showing:
- Which months each stock has historically paid dividends
- Companies with stronger payment consistency
- A consolidated view of when to expect payouts throughout the year

Important notes:
- The calendar result reflects months with payments observed before the query date. It does not guarantee that the company will pay dividends in those same months in the future. The calendar should be used as a predictability reference.
- In addition, investors should check the ex-dividend/record date table to confirm the required purchase date in order to be eligible for upcoming dividend payments.

---

## 🚀 Installation and Run

### Prerequisites
- Python 3.10+
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/weversonbarbieri/divharvest.git
cd divharvest
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment:

**Windows:**
```bash
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase credentials

Create a `.streamlit/secrets.toml` file in the project root:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-or-publishable-key"
```

### 5. Run the application

```bash
streamlit run app.py --server.port 8502
```

The application will open automatically at `http://localhost:8502`

---

## 📁 Folder Structure

```
divharvest/
├── app.py                          # Streamlit app entry point
├── utils.py                        # Scraping and data processing functions
├── requirements.txt                # Project dependencies
├── .streamlit/
│   └── secrets.toml               # Supabase credentials (do not commit)
├── data/
│   └── df_code_company.csv        # Ticker and company name list
├── notebook/
│   └── company's_name_search.ipynb # Notebook for scraping and Supabase load
└── README.md                       # This file
```

---

## 🔧 Technologies

- **Streamlit**: Python web app framework
- **Pandas**: Data manipulation
- **BeautifulSoup**: Web scraping
- **Supabase**: Cloud PostgreSQL database
- **Requests**: HTTP requests

---

## 📝 How to Use

1. **Open the app** at `http://localhost:8502`
2. **Select one or more stocks** from the B3 company list
3. **Click "Generate Calendar"**
4. **Review the result**:
    - Company ticker and sector
    - Months where the company historically pays dividends (marked with "R$")
    - Months with no recent payments (blank)

---

## 🔄 Data Flow

```
B3 (Fundamentus.com.br)
    ↓
Web Scraping (BeautifulSoup)
    ↓
Processing (Pandas)
    ↓
Supabase (Storage)
    ↓
Streamlit UI (Visualization)
```

---

## 📌 Data Source

Data is sourced from:
- **Fundamentus** (https://www.fundamentus.com.br): Dividend history and company information
- **Supabase**: Centralized storage for the ticker list

---

## 🤝 Contributions

Suggestions and improvements are welcome. Feel free to open issues or pull requests.

---

## 📄 Author

Developed by [Weverson Barbieri de Oliveira](https://github.com/weversonbarbieri)

---

## 📜 License

MIT

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**Plant today, harvest tomorrow. 🌾💰**
