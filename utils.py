import requests
import pandas as pd
import yfinance as yf
import streamlit as st
from bs4 import BeautifulSoup
from supabase import create_client, Client

# headers is used to identify as a real browser when sending an HTTP request to the server,
# the header identify the OS, browser and Mozilla/5.0 as all browser keep this for compatibility
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Dictionary with the number and the respective month abbreviation
MONTH_NAMES = {
    1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun",
    7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"
}

# Number of dividend paid occurrences on the same month
MIN_REPEATED_OCCURENCIES = 4

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
        set: Months (1-12) in which the stock paid dividends with at least
        MIN_REPEATED_OCCURENCIES occurrences in history.
        Returns an empty set if no dividend history table is found.
    """
    # url to access the dividend history adding the stock code
    div_url = f"https://www.fundamentus.com.br/proventos.php?papel={stock_code}&tipo=2"
    # Make the HTTP request to the server using the url and the human identifier (User-Agent) 
    stock_response = requests.get(div_url, headers=headers)
    # Parse (analyse) the HTML response/text into a structured object,
    # making it possible to search and extract the dividend payment date using HTML tags (e.g. <table>, <td>)
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
    if df_div_pay_dates.empty:
        return set()

    # Convert date to datetime
    df_div_pay_dates["PAY DATE"] = pd.to_datetime(df_div_pay_dates["PAY DATE"], format="%d/%m/%Y", errors="coerce")

    # Add month column
    df_div_pay_dates["Month"] = df_div_pay_dates["PAY DATE"].dt.month

    # Count the month dividend paid month frequency
    div_pay_frequency = (
        df_div_pay_dates
        .dropna(subset=["Month"])
        .groupby("Month")
        .size()
        .reset_index(name="MONTH COUNTER")
    )

    # Filter only the months which the payment frequency is >= 5 times,
    # set: creates a set with the values filtered {}
    return set(div_pay_frequency[div_pay_frequency["MONTH COUNTER"] >= MIN_REPEATED_OCCURENCIES]["Month"].tolist())


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

    # Get the response from the page where the company's sector is located
    sector_response = requests.get(url_det, headers=headers)

    # Parse (analyse) the HTML response/text into a structured object,
    # making it possible to search and extract the company's sector using HTML tags (e.g. <table>, <td>)
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

        # Dictionary with the stock code and the extracted sector
        stock_code_sector = {"STOCK CODE": stock_code, "SECTOR": sector}

        # Iterate over the dictionary with the mon_num: mon_name
        for num, name in MONTH_NAMES.items():
            # Anytime a number is found on the df div_pay_frequency_max
            # fills out the row with symbol 🌾
            if num in div_pay_frequency_max:
                stock_code_sector[name] = "🌾"
            # Otherwise leave it blank
            else:
                stock_code_sector[name] = ""
        stock_rows.append(stock_code_sector)

    return pd.DataFrame(stock_rows)


def render_calendar(selected_tickers, headers, code_map, month_list):
    """
    Build the dividend calendar DataFrame for the selected tickers.

    Extracts the ticker codes from the selected display labels using the code map
    and builds the dividend calendar DataFrame.

    Args:
        selected_tickers (list of str): Display labels selected by the user in the multiselect.

        headers (dict): HTTP request headers used to simulate a browser request.

        code_map (dict): Maps display label to ticker code.
        
        month_list (dict): A dictionary mapping month numbers to abbreviated month names.

    Return:
        pandas.DataFrame: The dividend calendar for the selected companies.
    """
    # Extract only the ticker codes from the display labels
    ticker_list = [code_map[t] for t in selected_tickers]
    # Get the dividend calendar based on the companies selected
    df_result = get_dividend_calendar(ticker_list, headers, month_list)

    return df_result


def get_supabase_client() -> Client:
    """Create and return a Supabase client from Streamlit secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_PUBLISHABLE_KEY"]
    return create_client(url, key)

def load_stock_options_from_supabase(table_name: str = "companies_list"):
    """Load display options and code map from Supabase table.
    
    Args: 
        table_name (str): name of the Supabase table containing the stock list.

    Return:
        tuple: A tuple containing:
        - options (list or dict): Display labels from the column codigo_empresa.
        - code_map (dict): Maps display label to ticker code.
    """
    supabase = get_supabase_client()

    # Get the response from Supabase with the table companies_list
    response = (
        supabase
        .table(table_name)
        .select("codigo,codigo_empresa")
        .order("codigo")
        .execute()
    )

    # Assign the response to a variable 
    rows = response.data or []
    # Condition to confirm when the response is empty from the database
    if not rows:
        return[], {}
    
    options = [row["codigo_empresa"] for row in rows]                   # List comprehension to append the ticker and codes into a list
    code_map = {row["codigo_empresa"]: row["codigo"] for row in rows}   # Append into a dictionary ticker and code: code
    
    return options, code_map

def companies_without_recurrence(df_result, month_list, stock_code_column="STOCK CODE"):
    """Return companies with no recurring dividend month in the generated calendar.

    A company is considered non-recurring when none of its month columns
    contains the marker 🌾 in the calendar output.

    Args:
        df_result (pandas.DataFrame): Calendar DataFrame returned by get_dividend_calendar.

        month_list (dict): Dictionary mapping month numbers to month names used as columns.
            Example: {1: "Jan", 2: "Fev", ..., 12: "Dez"}.
        
        stock_code_column (str): Column name containing the stock ticker code.
            Default: "STOCK CODE".

    Return:
        list[str]: List of stock codes that did not match the recurrence rule
        (i.e., no month marked as 🌾).
    """
    # Condition to confirm if the calendar is empty
    if df_result is None or df_result.empty:
        # Return empty list
        return []
    
    # Get the values (Jan, Fev, Mar) from the month dict and convert to list,
    # which will be the column name on the dividend calendar  
    month_columns = list(month_list.values())

    recurring_mask = df_result[month_columns].eq("🌾")

    return df_result.loc[~recurring_mask.any(axis=1), stock_code_column].tolist()

"""
next steps:
6. display a graph with the dividend yield
"""