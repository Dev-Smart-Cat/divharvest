import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

def get_dividend_months(stock_code, headers):
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