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

st.title("🌾📈 divharvest - Calendário de Pagamento de Dividendos")

st.info("""
📌 Notas importantes ao usuário:

- O calendário mostra apenas meses em que houve recorrência de pagamento de dividendos por pelo menos 4 ocorrências. 
- O resultado reflete pagamentos observados antes da data da consulta; isso não garante que a empresa pagará dividendos nos mesmos meses no futuro.
- Este calendário deve ser utilizado como referência de previsibilidade.
- Além disso, o investidor deve consultar a data-com / data-ex para confirmar a data de compra necessária para ter direito aos próximos proventos.
""")

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
        with st.spinner("Buscando dados..."):
            df_result = render_calendar(selected_tickers, headers, code_map, MONTH_NAMES)

        non_recurrent_companies = companies_without_recurrence(df_result, MONTH_NAMES)

        if non_recurrent_companies:
            if len(non_recurrent_companies) == 1:
                st.warning(
                    f"Atenção: a(s) empresa(s) {non_recurrent_companies[0]} não teve/tiveram "
                    f" pagamento(s) recorrente(s) no mesmo mês por pelo menos 4 ocorrências."
                )
            else:
                companies_txt = ", ".join(non_recurrent_companies)
                st.warning(
                    f"Atenção: a empresa {companies_txt} não teve"
                    f"pagamento recorrente no mesmo mês por pelo menos 4 ocorrências."
                )

        st.success(f"{len(selected_tickers)} ação(ões) processadas(s).")
        st.table(df_result)

"""
next steps:
1. set the page name, instead of "streamlit"
2. set a simbol on the page
3. put a comment in all code lines
4. fix the load session, anytime a company is selected, the current calendar goes and reload a new one
5. check the  "Notas importantes ao usuário:" if there is no typo
"""

# streamlit run app.py --server.port 8502