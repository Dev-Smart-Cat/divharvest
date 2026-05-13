import pandas as pd
import streamlit as st
from utils import get_dividend_calendar

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

# Load the list with stock codes in .csv when initializing the app
df_stocks = pd.read_csv("data/w-stock-codes.csv")
# Display options
options = df_stocks["Codigo/Empresa"].to_list()

# Mapping stock codes: "CSMG3 - Copasa MG" → "CSMG3"
code_map = df_stocks.set_index("Codigo/Empresa")["Codigo"].to_dict()

# Set the application's title 
st.title("📈 Calendário de Pagamento de Dividendos")

# Multiselect use the loaded stock list from the CSV with the options
selected_tickers = st.multiselect(
    "selecione as ações:",
    options=options,
    placeholder="Ex: VALE3, BBSE3, ITUB4"
)

# Displays a orintation to the customer
st.caption("Separe múltiplos códigos por vírgula.")

if st.button("🔍 Gerar Calendário de Pagamento de Dividendos."):
    # Condition when the button is pressed without stock codes input
    if len(selected_tickers) == 0:
        st.warning("Digite pelo menos um código de ação.")
    else:
        with st.spinner("Buscando dados..."):
            # Extract only the ticker code: "CSMG3 - Copasa MG" → "CSMG3"
            ticker_list = [code_map[t] for t in selected_tickers]

            # Call the function to webscrap the dividend calender
            # and create a df with the result
            df_result = get_dividend_calendar(
                ticker_list, 
                headers, 
                MONTH_NAMES
            )

            st.success(f"{len(ticker_list)} ação(ões) processada (s).")
            st.dataframe(df_result, use_container_width=True)

# streamlit run app.py --server.port 8502