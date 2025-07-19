import numpy as np
from scipy.stats import norm


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
    dividends: float = 0,
) -> float:
    """
    option_type: str
        'CALL' or 'PUT'
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

    if option_type == "PUT":
        neg_norm_d1 = norm.cdf(-d1)
        neg_norm_d2 = norm.cdf(-d2)
        strike_term = K * np.exp(-r * t)
        put_price = (strike_term * neg_norm_d2) - (s * neg_norm_d1)
        return put_price

    if option_type == "CALL":
        norm_d1 = norm.cdf(d1)
        norm_d2 = norm.cdf(d2)
        strike_term = K * np.exp(-r * t)
        call_price = (s * norm_d1) - (strike_term * norm_d2)
        return call_price

    raise ValueError
