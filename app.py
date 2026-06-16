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
import pandas as pd
from utils import *

# Set the simbol and page title on browser tab
st.set_page_config(
    page_title="Dividend Harvest",
    page_icon="🌾💰",
    layout="wide"
)

st.title("🌾💰📈 Dividend Harvest - Calendário de Pagamento de Dividendos")

st.info("""
📌 Notas importantes ao usuário:

- O calendário mostra apenas meses em que houve recorrência de pagamento de dividendos por pelo menos 4 ocorrências. 
- O resultado reflete pagamentos observados antes da data da consulta; isso não garante que a empresa pagará dividendos nos mesmos meses no futuro.
- Este calendário deve ser utilizado como referência de previsibilidade.
- Além disso, o investidor deve consultar a data-com / data-ex para confirmar a data de compra necessária para ter direito aos próximos proventos.
""")

# Call the function to load the companies list stored in the Supabase database
options, code_map = load_stock_options_from_supabase("companies_list")

# Initialize session state to persist the calendar across reruns.
# if guard make sure the calendar session state is None (without calendar),
# as soon as the application is initialized and it is possible to load a new calendar
if "df_calendar" not in st.session_state:
    st.session_state.df_calendar = None

# Multiselect shows full name, internally maps to ticker code
selected_tickers = st.multiselect(
    "Selecione as ações:",
    options=options,
    placeholder="Ex: VALE3, BBSE3, ITUB4"
)

# Set up button positions horizontally to generate the calendar and another one to clear the calendar
col1, col2 = st.columns([1, 1])
with col1:
    generate_btn = st.button("🔍 Gerar Calendário de Pagamento de Dividendos.")
with col2:
    clear_btn = st.button("🗑️ Limpar Calendário")

# Clear button resets the session state calendar
if clear_btn:
    st.session_state.df_calendar = None     # Clear the stored DataFrame
    st.rerun()                              # Runs the full script 

if generate_btn:
    # Condition when button is pressed without stock codes selected
    if len(selected_tickers) == 0:
        st.warning("Selecione pelo menos um código de ação.")
    else:
        with st.spinner("Buscando dados..."):
            df_new = render_calendar(selected_tickers, headers, code_map, MONTH_NAMES)  # Call the function to create the dividend calendar

        # Merge new results with existing calendar, avoiding duplicate stock codes
        # if guard to confirm when the calendar already exists, merge new companies into it
        if st.session_state.df_calendar is not None:
            # Convert the current session stock codes to a list,
            # and store them to a variable 
            existing_codes = st.session_state.df_calendar["STOCK CODE"].tolist()
            # Create a new DataFrame by filtering the new stock codes selected,
            # and when they are not in the current calendar avoiding duplicate stock codes
            df_new_filtered = df_new[~df_new["STOCK CODE"].isin(existing_codes)]
            st.session_state.df_calendar = pd.concat(               # Concatenate the existing calendar DataFrame with the new DataFrame containing the current the codes selected 
                [st.session_state.df_calendar, df_new_filtered],
                ignore_index=True
            )
        else:
            st.session_state.df_calendar = df_new       # Generate a new calendar when the session state has no calendar (None)

        # Call the function to mark the companies that had 0
        # or the dividend payment occurrence does not match the standard period of >= 4
        non_recurrent_companies = companies_without_recurrence(df_new, MONTH_NAMES)

        # Condition to display a message when there is 1 or more companies without
        # dividend payment occurrence
        if non_recurrent_companies:
            if len(non_recurrent_companies) == 1:
                st.warning(
                    f"Atenção: a(s) empresa(s) {non_recurrent_companies[0]} não teve/tiveram "
                    f" pagamento(s) recorrente(s) no mesmo mês por pelo menos 4 ocorrências."
                )
            else:
                companies_txt = ", ".join(non_recurrent_companies)
                st.warning(
                    f"Atenção: as empresas {companies_txt} não tiveram "
                    f"pagamento recorrente no mesmo mês por pelo menos 4 ocorrências."
                )

# Display the calendar if it exists in session state
if st.session_state.df_calendar is not None:
    st.success(f"{len(st.session_state.df_calendar)} ação(ões) no calendário.")     # Display a success message with the total number of companies in the calendar
    # Render the accumulated DataFrame as a static table.
    # st.session_state.df_calendar: anytime the user interacts with any widget,
    # holds the accumulated Dataframe (not a local variable).
    st.table(st.session_state.df_calendar)  

# streamlit run app.py --server.port 8502