"""
Dividend Payment Calendar — Streamlit App (v1.0)

A web application that displays a monthly dividend payment calendar
for B3 (Brazilian stock exchange) listed companies.

The user selects one or more stock tickers from a preloaded list and
the app scrapes dividend history from fundamentus.com.br to build a
calendar table showing which months each company consistently pays dividends.

Modules:
    utils: Contains the scraping and data processing functions:
        - get_dividend_months: Returns months with consistent dividend payments.
        - get_sector: Returns the sector of a given stock.
        - get_dividend_calendar: Builds the full calendar DataFrame.
        - load_stock_options: Loads the stock list from the CSV file.
        - render_calendar: Renders the dividend calendar in the Streamlit app.

Data Source:
    https://www.fundamentus.com.br
"""

import pandas as pd
import streamlit as st
from utils import load_stock_options, render_calendar

# headers is used to identify as a real browser when sending a HTTP request to the server,
# the header identify the OS, browser and Mozilla/5.0 as all browser keep this for compatibility
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Dictnary with the number and the respective month abbreviation
MONTH_NAMES = {
    1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun",
    7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"
}

def main():
    """Entry ponint of the Streamlit app. Renders the full UI."""
    # Load display options and code mapping from the CSV at app startup
    options, code_map = load_stock_options("data/empresas-b3.csv")

    st.title("📈 Calendário de Pagamento de Dividendos")

    # Multiselect shows full name, internally maps to ticker code
    selected_tickers = st.multiselect(
        "Selecioneas ações:",
        options=options,
        placeholder="Ex: VALE3, BBSE3, ITUB4"
    )

    if st.button("🔍 Gerar Calendário de Pagamento de Dividendos."):
        # Condition when button is pressed without stock codes selected
        if len(selected_tickers) == 0:
            st.warning("Selecione pelo menos um código de ação.")
        else:
            render_calendar(selected_tickers, headers, code_map, MONTH_NAMES)

main()


# streamlit run app.py --server.port 8502