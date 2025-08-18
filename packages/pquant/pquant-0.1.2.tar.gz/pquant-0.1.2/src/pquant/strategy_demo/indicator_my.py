
import numpy as np
import pandas as pd

# ------------------- 核心工具函数 -------------------


def my_round(a, decimals): return np.round(a, decimals)
def my_ret(x, n=1): return np.array(x)[-n]
def my_abs(x): return np.abs(x)
def my_ln(x): return np.log(x)
def my_pow(x1, x2): return np.power(x1, x2)
def my_sqrt(x): return np.sqrt(x)
def my_max(x1, x2): return np.maximum(x1, x2)
def my_min(x1, x2): return np.minimum(x1, x2)
def my_if(condition, x, y): return np.where(condition, x, y)


def my_ref(data, periods=1):
    return pd.Series(data).shift(periods).values


def my_diff(data, periods=1):
    return pd.Series(data).diff(periods).values


def my_std(data, periods):
    return pd.Series(data).rolling(periods).std(ddof=1).values


def my_sum(data, periods):
    return pd.Series(data).rolling(periods).sum().values if periods > 0 else pd.Series(data).cumsum().values


def my_const(data):
    return np.full(len(data), data[-1])


def my_hhv(data, periods):
    return pd.Series(data).rolling(periods).max().values


def my_llv(data, periods):
    return pd.Series(data).rolling(periods).min().values


def my_hhv_bars(data, periods):
    return pd.Series(data).rolling(periods).apply(lambda x: np.argmax(x[::-1]), raw=True).values


def my_llv_bars(data, periods):
    return pd.Series(data).rolling(periods).apply(lambda x: np.argmin(x[::-1]), raw=True).values


def my_ma(data, periods):
    return pd.Series(data).rolling(periods).mean().values


def my_ema(data, periods):
    return pd.Series(data).ewm(span=periods, adjust=False).mean().values


def my_sma(data, n, m):
    return pd.Series(data).ewm(span=m/n, adjust=False).mean().values


def my_wma(data, periods):
    return pd.Series(data).rolling(periods).apply(
        lambda x: x[::-1].cumsum().sum()*2/periods/(periods+1), raw=True
    ).values


def my_dma(data, periods):
    if isinstance(periods, (int, float)):
        return pd.Series(data).ewm(alpha=periods, adjust=False).mean().values

    periods = np.array(periods)
    periods[np.isnan(periods)] = 1.0
    result = np.zeros(len(data))
    result[0] = data[0]

    for i in range(1, len(data)):
        result[i] = periods[i] * data[i] + (1 - periods[i]) * result[i - 1]
    return result


def my_ave_dev(data, periods):
    return pd.Series(data).rolling(periods).apply(lambda x: (np.abs(x - x.mean())).mean()).values


def my_slope(data, periods):
    return pd.Series(data).rolling(periods).apply(
        lambda x: np.polyfit(range(periods), x, deg=1)[0],
        raw=True
    ).values


def my_forcast(data, periods):
    return pd.Series(data).rolling(periods).apply(
        lambda x: np.polyval(np.polyfit(range(periods), x, deg=1), periods - 1),
        raw=True
    ).values


def my_last(data, n, m):
    return np.array(
        pd.Series(data).rolling(n + 1).apply(
            lambda x: np.all(x[::-1][m:]),
            raw=True),
        dtype=bool
    )


# ------------------- 应用层函数 -------------------


def my_count(data, periods):
    return my_sum(data, periods)


def my_every(data, periods):
    return my_if(my_sum(data, periods) == periods, True, False)


def my_exist(data, periods):
    return my_if(my_sum(data, periods) > 0, True, False)


def my_filter(data, periods):
    for i in range(len(data)):
        data[(i + 1):(i + 1 + periods)] = 0 if data[i] else data[(i + 1):(i + 1 + periods)]
    return data


def my_bars_last(data):
    rt = np.concatenate(([0], np.where(data, 1, 0)))
    for i in range(1, len(rt)):
        rt[i] = 0 if rt[i] else rt[i - 1] + 1
    return rt[1:]


def my_bars_last_count(data):
    rt = np.zeros(len(data) + 1)
    for i in range(len(data)):
        rt[i + 1] = rt[i] + 1 if data[i] else rt[i + 1]
    return rt[1:]


def my_bars_since(data, periods):
    return pd.Series(data).rolling(periods).apply(
        lambda x: periods - 1 - np.argmax(x) if np.argmax(x) or x[0] else 0,
        raw=True
    ).fillna(0).values.astype(int)


def my_cross(d1, d2):
    is_na_d1 = np.isnan(d1)
    is_na_d2 = np.isnan(d2)
    return np.concatenate(([False], np.logical_not((d1 > d2)[:-1]) & ~is_na_d1[:-1] & ~is_na_d2[:-1]
                           & (d1 > d2)[1:] & ~is_na_d1[1:] & ~is_na_d2[1:]))


def my_long_cross(d1, d2, periods):
    return np.array(np.logical_and(my_last(d1 < d2, periods, 1), (d1 > d2)), dtype=bool)


def my_value_when(condition, value):
    return pd.Series(np.where(condition, value, np.nan)).ffill().values


def my_between(data, r1, r2):
    return (r1 < data < r2) | (r2 < data < r1)


def my_top_range(data):
    rt = np.zeros(len(data))

    for i in range(1, len(data)):
        rt[i] = np.argmin(np.flipud(data[:i] < data[i]))
    return rt.astype('int')


def my_low_range(data):
    rt = np.zeros(len(data))

    for i in range(1, len(data)):
        rt[i] = np.argmin(np.flipud(data[:i] > data[i]))
    return rt.astype('int')


def my_macd(data, short=12, long=26, m=9):
    dif = my_ema(data, short) - my_ema(data, long)
    dea = my_ema(dif, m)
    macd = (dif - dea) * 2
    return dif, dea, macd


def my_boll(data, period=20, multiply=2):
    mid = my_ma(data, period)
    lower = mid - my_std(data, period) * multiply
    upper = mid + my_std(data, period) * multiply
    return lower, mid, upper


def my_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period=14) -> np.ndarray:
    high_low = high - low
    high_close = np.abs(high - np.roll(close, 1))
    low_close = np.abs(low - np.roll(close, 1))
    true_range = np.maximum(np.maximum(high_low, high_close), low_close)
    atr = np.convolve(true_range, np.ones(period) / period, mode='valid')
    return atr
