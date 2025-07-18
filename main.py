import yfinance as yf
from pprint import pprint

from pkg import bsm, get_risk_free_rate, diff_date

ANNUAL_MARKET_OPEN_DAYS = 252


def bsm_option_price(ticker: str, option_type: str):
    if option_type != "call" and option_type != "put":
        raise ValueError
    symbol = yf.Ticker(ticker)
    last_price = symbol.fast_info["last_price"]

    options_expiries = symbol.options
    option_expiry_date = options_expiries[len(options_expiries) - 1]
    years_to_expire = diff_date(option_expiry_date) / ANNUAL_MARKET_OPEN_DAYS

    risk_percentage = get_risk_free_rate()

    option_chain = symbol.option_chain(option_expiry_date)

    options = None
    if option_type == "call":
        options = option_chain.calls.dropna()
    else:
        options = option_chain.puts.dropna()

    in_the_money = options[options["inTheMoney"]]
    out_of_the_money = options[~options["inTheMoney"]]

    selected_option_itm = in_the_money.iloc[0]
    strike_price_itm = selected_option_itm.loc["strike"]
    volatility_itm = selected_option_itm.loc["impliedVolatility"]

    selected_option_ootm = out_of_the_money.iloc[0]
    strike_price_ootm = selected_option_ootm.loc["strike"]
    volatility_ootm = selected_option_ootm.loc["impliedVolatility"]

    option_price_itm_bsm = bsm(
        option_type=option_type,
        K=strike_price_itm,
        s=last_price,
        t=years_to_expire,
        r=risk_percentage,
        sigma=volatility_itm,
    )

    option_price_ootm_bsm = bsm(
        option_type=option_type,
        K=strike_price_ootm,
        s=last_price,
        t=years_to_expire,
        r=risk_percentage,
        sigma=volatility_ootm,
    )

    print(f"In the money option: {selected_option_itm.loc['lastPrice']}")
    print(f"option price bsm: {option_price_itm_bsm}\n\n")

    print(f"Out of the money option: {selected_option_ootm.loc['lastPrice']}")
    print(f"option price bsm: {option_price_ootm_bsm}\n\n")


if __name__ == "__main__":
    print("CALLS:")
    bsm_option_price("TSLA", "call")
    print("PUTS:")
    bsm_option_price("TSLA", "put")
