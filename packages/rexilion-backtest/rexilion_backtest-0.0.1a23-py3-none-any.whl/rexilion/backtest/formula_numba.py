import math
from numba import njit
import numpy as np

@njit(cache=True)
def diff(arr: np.ndarray) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if n > 0:
        out[0] = np.nan
        for i in range(1, n):
            out[i] = arr[i] - arr[i - 1]
    return out

@njit(cache=True)
def rolling_sum(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    s = 0.0
    for i in range(window):
        s += arr[i]
    for i in range(window - 1):
        out[i] = np.nan
    out[window - 1] = s
    for i in range(window, n):
        s += arr[i] - arr[i - window]
        out[i] = s
    return out

@njit(cache=True)
def rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    s = 0.0
    for i in range(window):
        s += arr[i]
    for i in range(window - 1):
        out[i] = np.nan
    out[window - 1] = s / window
    for i in range(window, n):
        s += arr[i] - arr[i - window]
        out[i] = s / window
    return out

@njit(cache=True)
def rolling_ema(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    multiplier = 2.0 / (window + 1)
    # initial SMA
    s = 0.0
    for i in range(window):
        s += arr[i]
    out[window - 1] = s / window
    # EMA
    for i in range(window, n):
        out[i] = (arr[i] - out[i - 1]) * multiplier + out[i - 1]
    for i in range(window - 1):
        out[i] = np.nan
    return out

@njit(cache=True)
def rolling_wma(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    denom = window * (window + 1) / 2.0
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        s = 0.0
        for j in range(window):
            s += arr[i - j] * (j + 1)
        out[i] = s / denom
    return out

@njit(cache=True)
def rolling_std(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, dtype=np.float64)
    if window > n:
        out[:] = np.nan
        return out

    # initialize first window
    s = 0.0
    s2 = 0.0
    for i in range(window):
        s += arr[i]
        s2 += arr[i] * arr[i]

    for i in range(window - 1):
        out[i] = np.nan

    mean = s / window
    var = (s2 - window * mean * mean) / (window - 1)
    out[window - 1] = np.sqrt(var) if var > 0 else 0.0

    for i in range(window, n):
        x_add = arr[i]
        x_sub = arr[i - window]

        s += x_add - x_sub
        s2 += x_add * x_add - x_sub * x_sub

        mean = s / window
        var = (s2 - window * mean * mean) / (window - 1)
        out[i] = np.sqrt(var) if var > 0 else 0.0

    return out

@njit(cache=True)
def rolling_zscore_mean(arr: np.ndarray, window: int) -> np.ndarray:
    """
    Numba-compiled version of:
        z = (arr - rolling_mean(arr)) / rolling_std(arr)
        return z - rolling_mean(z)
    """
    n = arr.shape[0]
    out = np.empty(n, np.float64)

    # If window is larger than the array, return all NaNs
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out

    # 1) compute the simple moving average of the original array
    sma = rolling_mean(arr, window)

    # 2) compute the rolling standard deviation
    stddev = rolling_std(arr, window)

    # 3) build the z-score series
    z = np.empty(n, np.float64)
    for i in range(n):
        # guard against NaN or zero stddev
        if math.isnan(stddev[i]) or stddev[i] == 0.0:
            z[i] = np.nan
        else:
            z[i] = (arr[i] - sma[i]) / stddev[i]

    # 4) compute the rolling mean of the z-score series
    mz = rolling_mean(z, window)

    # 5) subtract the rolling-mean-of-z from z to get the final output
    for i in range(n):
        out[i] = z[i] - mz[i]

    return out

@njit(cache=True)
def rolling_min(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        m = arr[i - window + 1]
        for j in range(i - window + 2, i + 1):
            if arr[j] < m:
                m = arr[j]
        out[i] = m
    return out

@njit(cache=True)
def rolling_max(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        m = arr[i - window + 1]
        for j in range(i - window + 2, i + 1):
            if arr[j] > m:
                m = arr[j]
        out[i] = m
    return out

@njit(cache=True)
def rolling_mean_normalize(arr: np.ndarray, window: int) -> np.ndarray:
    sma = rolling_mean(arr, window)
    mn = rolling_min(arr, window)
    mx = rolling_max(arr, window)
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (arr[i] - sma[i]) / (mx[i] - mn[i] + 1e-9)
    return out

@njit(cache=True)
def rolling_zscore(arr: np.ndarray, window: int) -> np.ndarray:
    sma = rolling_mean(arr, window)
    stdv = rolling_std(arr, window)
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (arr[i] - sma[i]) / (stdv[i] + 1e-9)
    return out

@njit(cache=True)
def rolling_sigmoid_zscore(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    z = rolling_zscore(arr, window)
    for i in range(n):
        out[i] = 2.0 * (1.0 / (1.0 + np.exp(-z[i]))) - 1.0
    return out

@njit(cache=True)
def rolling_minmax_normalize(arr: np.ndarray, window: int) -> np.ndarray:
    mn = rolling_min(arr, window)
    mx = rolling_max(arr, window)
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = 2.0 * (arr[i] - mn[i]) / (mx[i] - mn[i] + 1e-9) - 1.0
    return out

@njit(cache=True)
def rolling_skew(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        mean = 0.0
        for j in range(i - window + 1, i + 1):
            mean += arr[j]
        mean /= window
        var = 0.0
        for j in range(i - window + 1, i + 1):
            diff = arr[j] - mean
            var += diff * diff
        stdv = np.sqrt(var / window) if var > 0 else 0.0
        if stdv == 0.0:
            out[i] = 0.0
        else:
            sk = 0.0
            for j in range(i - window + 1, i + 1):
                sk += ((arr[j] - mean) / stdv) ** 3
            out[i] = (window / ((window - 1) * (window - 2))) * sk
    return out

@njit(cache=True)
def rolling_var(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        mean = 0.0
        for j in range(i - window + 1, i + 1):
            mean += arr[j]
        mean /= window
        var = 0.0
        for j in range(i - window + 1, i + 1):
            diff = arr[j] - mean
            var += diff * diff
        out[i] = var / (window - 1)
    return out

@njit(cache=True)
def rolling_kurt(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        mean = 0.0
        for j in range(i - window + 1, i + 1):
            mean += arr[j]
        mean /= window
        var = 0.0
        for j in range(i - window + 1, i + 1):
            diff = arr[j] - mean
            var += diff * diff
        stdv = np.sqrt(var / (window - 1)) if var > 0 else 0.0
        if stdv == 0.0:
            out[i] = -3.0
        else:
            m4 = 0.0
            for j in range(i - window + 1, i + 1):
                m4 += ((arr[j] - mean) / stdv) ** 4
            m4 /= window
            out[i] = m4 - 3.0
    return out

@njit(cache=True)
def rolling_tanh_estimator(arr: np.ndarray, window: int) -> np.ndarray:
    z = rolling_zscore(arr, window)
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = np.tanh(0.01 * z[i])
    return out

@njit(cache=True)
def sigmoid(x: float) -> float:
    return 2.0 * (1.0 / (1.0 + np.exp(x))) - 1.0

@njit(cache=True)
def rolling_softmax(arr: np.ndarray, window: int) -> np.ndarray:
    n = arr.shape[0]
    out = np.empty(n, np.float64)
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        # max‐stable softmax
        m = arr[i - window + 1]
        for j in range(i - window + 2, i + 1):
            if arr[j] > m:
                m = arr[j]
        denom = 0.0
        for j in range(i - window + 1, i + 1):
            denom += np.exp(arr[j] - m)
        out[i] = 2.0 * (np.exp(arr[i] - m) / denom) - 1.0
    return out

@njit(cache=True)
def rolling_l1_normalization(arr: np.ndarray, window: int) -> np.ndarray:
    abs_arr = np.empty_like(arr)
    n = arr.shape[0]
    for i in range(n):
        abs_arr[i] = abs(arr[i])
    abs_sum = rolling_sum(abs_arr, window)
    out = np.empty(n, np.float64)
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        out[i] = 2.0 * (arr[i] / (abs_sum[i] + 1e-9)) - 1.0
    return out
