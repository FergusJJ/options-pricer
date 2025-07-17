import numpy as np
from scipy.stats import norm


def run():
    """
    Calculates thr theoretical value of an option contract

    5 inputs:
        type of option: call/put

        ? strike price of an option
        current stock price
        time to expiration
        ? risk free rate
        volatility (percentage?)

    ------

    Price follows a geormetric Brownian motion
    with constant drift and volatility

    Assumptions:
        - No dividends are paid out during option lifetime
        - Markets are random
        - No trasaction costs
        - Risk-free rate and volatility are known and constant
        - Returns are normally distributed
        - Options are european and can only be exercised at expiration

    ------
    (real) Risk free rate = inflation rate - yield
    Three month U.S. treasury bill used as proxy for risk free rate of return

    """
    option_type = "put"

    days_to_expiry = 22

    test_stock_prices = [11, 8, 10]

    daily_returns = [0.01, -0.008, 0.004, 0.02, 0.05]
    daily_volatility = np.std(daily_returns)

    #
    option_type = "put"
    strike_price = 10.0
    annual_volatility = daily_volatility * np.sqrt(252)
    time_to_expire = days_to_expiry / 252
    risk_free_rate = 0.05

    print(
        "\n\n---PARAMS---\n\n",
        f"option type: {option_type}\nstrike price: {strike_price}",
        f"\ntime to expire: {time_to_expire}\nrisk-free rate: {risk_free_rate}",
        f"\nannual volatility: {annual_volatility}\n\n",
    )
    for price in test_stock_prices:
        out = bsm(
            option_type=option_type,
            K=strike_price,
            s=price,
            t=time_to_expire,
            r=risk_free_rate,
            sigma=annual_volatility,
        )
        print(f"---OUTPUT---\nprice: {price}\noption price:{out}")
    return


def calc_d1(s: float, K: float, r: float, t: float, sigma: float):
    log_ratio = np.log(s / K)
    volatility_accounted_return = (r + 0.5 * (sigma**2)) * t
    d_1 = (log_ratio + (volatility_accounted_return)) / (sigma * np.sqrt(t))
    return d_1


def bsm(
    option_type: str,
    K: float,
    s: float,
    t: float,
    r: float,
    sigma: float,
) -> float:
    """
    option_type: str
        'call' or 'put'
    K: float
        strike price of the option
    s: float
        current stock price
    t: float
        years to expire
    r: float
        risk percentage
    sigma: float
        volatility

    """
    d1 = calc_d1(s, K, r, t, sigma)
    d2 = d1 - sigma * np.sqrt(t)

    if option_type == "put":
        neg_norm_d1 = norm.cdf(-d1)
        neg_norm_d2 = norm.cdf(-d2)
        strike_term = K * np.exp(-r * t)
        put_price = (strike_term * neg_norm_d2) - (s * neg_norm_d1)
        return put_price

    if option_type == "call":
        norm_d1 = norm.cdf(d1)
        norm_d2 = norm.cdf(d2)
        strike_term = K * np.exp(-r * t)
        call_price = (s * norm_d1) - (strike_term * norm_d2)
        return call_price

    raise ValueError


if __name__ == "__main__":
    run()
