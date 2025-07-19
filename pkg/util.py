import pandas as pd
import yfinance as yf
from datetime import datetime

from .bsm import bsm

ANNUAL_MARKET_OPEN_DAYS = 252


def get_option_dates(ticker: str):
    symbol = yf.Ticker(ticker)
    option_expiries = symbol.options
    expiries_df = pd.DataFrame(
        {"Ticker": [ticker] * len(option_expiries), "Expiration Date": option_expiries}
    )
    return expiries_df


def get_option_chain(ticker: str, date: str, direction: str):
    symbol = yf.Ticker(ticker)
    option_chain = symbol.option_chain(date)
    options = None
    if direction == "CALL":
        options = option_chain.calls.dropna()
    else:
        options = option_chain.puts.dropna()
    df = pd.DataFrame(options)

    return df


def bsm_option_price(
    ticker: str, expiry_date: str, direction: str, selected_option: pd.Series
) -> float:
    if direction != "CALL" and direction != "PUT":
        raise ValueError("option_type must be 'CALL' or 'PUT'")

    symbol = yf.Ticker(ticker)
    last_price = symbol.fast_info["last_price"]
    years_to_expire = diff_date(expiry_date) / ANNUAL_MARKET_OPEN_DAYS
    risk_percentage = get_risk_free_rate()
    strike_price = selected_option["strike"]
    volatility = selected_option["impliedVolatility"]
    option_price_bsm = bsm(
        option_type=direction,
        K=strike_price,
        s=last_price,
        t=years_to_expire,
        r=risk_percentage,
        sigma=volatility,
    )

    return option_price_bsm


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
