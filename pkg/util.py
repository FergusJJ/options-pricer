import yfinance as yf
from datetime import datetime


def get_risk_free_rate():
    treasury = yf.Ticker("^TNX")
    hist = treasury.history(period="1d")
    rate = hist["Close"].iloc[-1] / 100
    return rate


def diff_date(expiry_date: str):
    d1 = datetime.strptime(expiry_date, "%Y-%m-%d")
    today = datetime.today().strftime("%Y-%m-%d")
    d2 = datetime.strptime(today, "%Y-%m-%d")
    days_til_expiry = abs((d1 - d2).days)
    return days_til_expiry
