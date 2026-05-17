import requests
import pandas as pd
import yfinance as yf
import streamlit as st
from bs4 import BeautifulSoup


def get_dividend_months(stock_code, headers):
    """Scrape the dividend payment history for a stock and return the months with consistent payments.

    Accesses the fundamentus.com.br dividend history page for the given stock code,
    extracts all payment dates, and returns only the months that appear 5 or more times,
    indicating a consistent dividend payment pattern.

    Args:
        stock_code (str): The B3 stock ticker code. e.g. "VALE3", "BBSE3".
        headers (dict): HTTP request headers used to simulate a browser request.
            Must contain a valid "User-Agent" key.

    Return:
        set: A set of integers representing the months (1-12) in which the stock
            has paid dividends at least 5 times historically.
            Returns an empty set if no dividend history table is found.
    """
    # url to access the dividend history adding the stock code
    div_url = f"https://www.fundamentus.com.br/proventos.php?papel={stock_code}&tipo=2"

    # Make the HTTP request to the server using the url and the human identifier (User-Agent) 
    stock_response = requests.get(div_url, headers=headers)

    # Parse (analyse) the HTML response/text into a structured object, 
    # making it possible to search and extract the dividend paymente date using HTML tags (e.g. <table>, <td>)
    stock_soup = BeautifulSoup(stock_response.text, "html.parser")

    # Search for content using the tag <table>, 
    # since the dividends history is in a table
    stock_table = stock_soup.find("table")

    # Condition to confirm when there is dividend history available
    if stock_table is None:
        return set()            # Create an empty set

    # Search for the table's content using the tag <tbody>,
    # then collect all rows using <tr> tag to iterate line by line 
    div_payment_info_rows = stock_table.find("tbody").find_all("tr")

    # List to append the dividends payment dates
    payment_dates_list = []

    # Iterate over all columns to find all table data (td)
    for row in div_payment_info_rows:
        cols = row.find_all("td")
        # Confirm if at least 1 column is available
        if len(cols) >= 1:
            # Append only column 3 where the dividend payment date is located
            payment_dates_list.append({
                "PAY DATE": cols[3].text.strip()})
    
    # Create a df with the payment dates
    df_div_pay_dates = pd.DataFrame(payment_dates_list)

    # Convert date to datetime
    df_div_pay_dates["PAY DATE"] = pd.to_datetime(df_div_pay_dates["PAY DATE"], format="%d/%m/%Y", errors="coerce")

    # Add month colun
    df_div_pay_dates["Month"] = df_div_pay_dates["PAY DATE"].dt.month

    # Count the month dividend paied month frequency
    div_pay_frequency = df_div_pay_dates.groupby("Month").size().reset_index(name="MONTH COUNTER")

    # Filter only the months which the payment frequency is >= 5 times,
    # set: creates a set with the values filtered {}
    return set(div_pay_frequency[div_pay_frequency["MONTH COUNTER"] >= 5]["Month"].tolist())


def get_sector(stock_code, headers):
    """Scrape the sector of a company listed on B3 from fundamentus.com.br.

    Accesses the company details page on fundamentus.com.br and searches for
    the table data cell containing the label 'Setor', returning the value
    of the adjacent cell.

    Args:
        stock_code (str): The B3 stock ticker code. e.g. "VALE3", "BBSE3".
        headers (dict): HTTP request headers used to simulate a browser request.
            Must contain a valid "User-Agent" key.

    Return:
        str: The sector name of the company. e.g. "Mineração", "Bancos".
            Returns "N/A" if the sector label is not found on the page.
    """
    # Get the company's sector
    url_det = f"https://www.fundamentus.com.br/detalhes.php?papel={stock_code}"

    # Get the response from the page where the company's sectior is located
    sector_response = requests.get(url_det, headers=headers)

    # Parse (analyse) the HTML response/text into a structured object,
    # making it possible to seach and extract the company's sector using HTML tags (e.g. <table>, <td>)
    soup_comp_sector = BeautifulSoup(sector_response.text, "html.parser")

    # Iterate over the soup and find all table data to extract the company's sector
    for td in soup_comp_sector.find_all("td"):
        # Select only the table data containing the string "Setor"
        if "Setor" in td.get_text(strip=True):
            # Inside the table data with the word "Setor", get the data of the next <td>,
            # and then get the text inside it
            return td.find_next("td").get_text(strip=True).replace('\xa0', '')
    return "N/A"


def get_dividend_calendar(ticker_list, headers, MONTH_NAMES):
    """Build a dividend payment calendar DataFrame for a list of B3 stock tickers.

    For each ticker, scrapes the sector and the months with consistent dividend
    payments from fundamentus.com.br, then assembles a DataFrame where each row
    represents a stock and each month column contains 'R$' if the stock has paid
    dividends in that month consistently, or an empty string otherwise.

    Args:
        ticker_list (list of str): A list of B3 stock ticker codes. e.g. ["VALE3", "BBSE3"].
        headers (dict): HTTP request headers used to simulate a browser request.
            Must contain a valid "User-Agent" key.
        MONTH_NAMES (dict): A dictionary mapping month numbers to abbreviated month names.
            e.g. {1: "Jan", 2: "Fev", ..., 12: "Dez"}.

    Return:
        pandas.DataFrame: A DataFrame with the following columns:
            - "STOCK CODE" (str): The ticker code of the stock.
            - "SECTOR" (str): The sector of the company.
            - "Jan" to "Dez" (str): "R$" if the stock pays dividends in that month,
              or "" if it does not.
    """
    # Create a list to append the info from the company (s) entered:
    # stock code: code
    # sector: company's sector
    # month: "R$" or ""
    stock_rows = []

    for stock_code in ticker_list:
        sector = get_sector(stock_code, headers)
        div_pay_frequency_max = get_dividend_months(stock_code, headers)

        # Dictonary with the stock code and the extracted sector
        stock_code_sector = {"STOCK CODE": stock_code, "SECTOR": sector}

        # Iterate over the dictionary with the mon_num: mon_name
        for num, name in MONTH_NAMES.items():
            # Anytime a number is found on the df div_pay_frequency_max
            # fills out the row with simbol "R$" 
            if num in div_pay_frequency_max:
                stock_code_sector[name] = "R$"
            # Otherwise leave it blank
            else:
                stock_code_sector[name] = ""
        stock_rows.append(stock_code_sector)

    return pd.DataFrame(stock_rows)

def load_stock_options(filepath):
    """Load the stock list from a CSV file and return display options and a code mapping.

    Args:
        filepath (str): Relative path to the CSV file containing stock data.
            The file must have the columns 'Codigo' and 'Codigo/Empresa'.

    Return:
        tuple: A tuple containing:
            - options (list of str): Display labels. e.g. ["CSMG3 - Copasa MG", ...].
            - code_map (dict): Maps display label to ticker code.
              e.g. {"CSMG3 - Copasa MG": "CSMG3", ...}.
    """

    # Load the list with stock codes in .csv when initializing the app
    df_stocks = pd.read_csv(filepath)
    # Display options
    options = df_stocks["Codigo/Empresa"].tolist()
    # Mapping stock codes: "CSMG3 - Copasa MG" → "CSMG3"
    code_map = df_stocks.set_index("Codigo/Empresa")["Codigo"].to_dict()
    # Return a list and a dictionary
    return options, code_map

def render_calendar(selected_tickers, headers, code_map, month_list):
    """Scrape dividend data for selected tickers and render the calendar in the Streamlit app.

    Extracts the ticker codes from the selected display labels using the code map,
    calls get_dividend_calendar to build the result DataFrame, and renders
    a success message and the calendar table directly in the Streamlit interface.

    Args:
        selected_tickers (list of str): Display labels selected by the user in the multiselect.
            e.g. ["CSMG3 - Copasa MG", "VALE3 - Vale S.A."].
        headers (dict): HTTP request headers used to simulate a browser request.
            Must contain a valid "User-Agent" key.
        code_map (dict): Maps display label to ticker code.
            e.g. {"CSMG3 - Copasa MG": "CSMG3"}.
        month_list (dict): A dictionary mapping month numbers to abbreviated month names.
            e.g. {1: "Jan", 2: "Fev", ..., 12: "Dez"}.

    Return:
        None: Renders the result directly in the Streamlit app.
    """
    # Extract only the ticker codes from the display labels
    ticker_list = [code_map[t] for t in selected_tickers]

    # Show spinner only while scraping is in progress
    with st.spinner("Buscando dados..."):
        df_result = get_dividend_calendar(ticker_list, headers, month_list)

    # Render success message and calendar table after spinner closes
    st.success(f"{len(ticker_list)} ação(ões) processada(s).")
    
    st.dataframe(df_result, use_container_width=True)