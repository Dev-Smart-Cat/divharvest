import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from utils import *

# headers is used to identify as a real browser when sending a HTTP request to the server,
# the header identify the OS, browser and Mozilla/5.0 as all browser keep this for compatibility
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# List with the stock codes to check the months dividend months paid
ticker_list = [
    "CSMG3",
    "GGBR4",
    "BBSE3",
    "TIMS3",
    "VALE3",
    "AURE3",
    "CXSE3",
    "BBDC4",
    "CMIN3",
    "BBAS3",
    "CMIG4",
]

# Dictnary with the number and the respective month abbreviation
MONTH_NAMES = {
    1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun",
    7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"
}



