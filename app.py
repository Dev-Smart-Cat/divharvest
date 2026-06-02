"""
Dividend Payment Calendar — Streamlit App (v1.0)

A web application that displays a monthly dividend payment calendar
for B3 (Brazilian stock exchange) listed companies.

The user selects one or more stock tickers from a preloaded list and
the app scrapes dividend history from fundamentus.com.br to build a
calendar table showing which months each company consistently pays dividends.

Modules:
    utils: Contains the scraping, Supabase connection, and data processing functions.

Data Source:
    https://www.fundamentus.com.br
"""

import streamlit as st
from utils import *

st.title("📈 Calendário de Pagamento de Dividendos")

options, code_map = load_stock_options_from_supabase("companies_list")

# Multiselect shows full name, internally maps to ticker code
selected_tickers = st.multiselect(
    "Selecione as ações:",
    options=options,
    placeholder="Ex: VALE3, BBSE3, ITUB4"
)

if st.button("🔍 Gerar Calendário de Pagamento de Dividendos."):
    # Condition when button is pressed without stock codes selected
    if len(selected_tickers) == 0:
        st.warning("Selecione pelo menos um código de ação.")
    else:
        render_calendar(selected_tickers, headers, code_map, MONTH_NAMES)

# streamlit run ui.py --server.port 8502