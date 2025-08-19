import numpy as np
import pandas as pd
from scipy.stats import yeojohnson
from numpy.lib.stride_tricks import sliding_window_view

def diff(arr, periods=1):
    a = np.asarray(arr, dtype=float)
    if periods < 1:
        raise ValueError("`periods` must be a positive integer")
    out = np.empty_like(a)
    out[:periods] = np.nan
    out[periods:] = a[periods:] - a[:-periods]
    return out

def diff_n(arr, n_diffs=1) -> np.ndarray:
    """
    Take n_diffs successive first-differences of the input array,
    without any log transform.
    """
    d = np.asarray(arr, dtype=float)
    for _ in range(n_diffs):
        d = diff(d, periods=1)
    return d

def rolling_sum(
    x: np.ndarray,
    window: int,
    min_periods: int | None = None,
    fill_value: float = np.nan
) -> np.ndarray:
    """
    Compute a left-aligned rolling sum over a 1D numeric array, handling NaNs.

    Parameters
    ----------
    x : array-like
        1D array of floats (may contain NaNs).
    window : int
        Size of the rolling window (must be ≥ 1).
    min_periods : int, optional
        Minimum number of non-NaN observations in the window before
        producing a valid sum.  Defaults to `window` (i.e. require a full window).
    fill_value : float, default np.nan
        Value to use when the non-NaN count in the window is below `min_periods`.

    Returns
    -------
    out : np.ndarray, shape (len(x),)
        out[i] = sum(x[i−window+1 : i+1]) if that slice has ≥ min_periods non-NaNs;
        otherwise `fill_value`.
    """
    # ——— Input checks ———
    x = np.asarray(x, dtype=float)
    n = x.size
    if not isinstance(window, int) or window < 1:
        raise ValueError("`window` must be an integer ≥ 1")
    if min_periods is None:
        min_periods = window
    if not isinstance(min_periods, int) or min_periods < 1:
        raise ValueError("`min_periods` must be an integer ≥ 1")

    # ——— Build cumulative sums & counts ———
    # replace NaN with 0 for summation
    x0 = np.nan_to_num(x, 0.0)
    cs  = np.concatenate(([0.0], np.cumsum(x0)))           # length = n+1

    # count up how many non-NaN values we’ve seen
    valid = (~np.isnan(x)).astype(int)
    cc  = np.concatenate(([0], np.cumsum(valid)))          # length = n+1

    # ——— Compute rolling sums & counts in one vectorized pass ———
    idx = np.arange(n)
    start = idx - window + 1
    start_clipped = np.where(start > 0, start, 0)

    sums   = cs[idx + 1] - cs[start_clipped]
    counts = cc[idx + 1] - cc[start_clipped]

    # ——— Mask out any positions with too few valid observations ———
    out = np.where(counts >= min_periods, sums, fill_value)
    return out

def rolling_mean(array, rolling_window):
    array = np.nan_to_num(array, nan=0)  # Replace NaNs with zero
    if rolling_window > len(array):
        return np.full_like(array, np.nan)

    cumsum = np.zeros(len(array) + 1)
    cumsum[1:] = np.cumsum(array)  # Avoid inserting 0 manually
    rolling_sum = cumsum[rolling_window:] - cumsum[:-rolling_window]
    rolling_mean = rolling_sum / rolling_window

    # Prepend NaNs for first (window - 1) values
    rolling_mean = np.concatenate((np.full(rolling_window - 1, np.nan), rolling_mean))
    return rolling_mean

def rolling_ema(data, window):
    if window > len(data):
        return np.full_like(data, np.nan)

    multiplier = 2 / (window + 1)
    ema_values = np.zeros_like(data, dtype=np.float64)

    # Compute the initial SMA for first 'window' values
    ema_values[window - 1] = np.mean(data[:window])

    # Compute the EMA for remaining values
    for i in range(window, len(data)):
        ema_values[i] = (data[i] - ema_values[i - 1]) * multiplier + ema_values[i - 1]

    # Set first `window-1` values to NaN since they can't be computed
    ema_values[:window - 1] = np.nan
    return ema_values

def rolling_wma(data, window):
    if window > len(data):
        return np.full_like(data, np.nan)

    weights = np.arange(1, window + 1)
    wma = np.convolve(data, weights[::-1], mode='valid') / weights.sum()

    # Pad with NaN to match original array length
    wma = np.concatenate((np.full(window - 1, np.nan), wma))
    return wma

def rolling_std(array, window):
    s = pd.Series(array, dtype=float)
    return s.rolling(window=window).std().to_numpy()

def rolling_min(array, rolling_window):
    return pd.Series(array).rolling(rolling_window).min().to_numpy()

def rolling_max(array, rolling_window):
    return pd.Series(array).rolling(rolling_window).max().to_numpy()

def rolling_mean_normalize(array, rolling_window):
    sma = rolling_mean(array, rolling_window)
    min_val = rolling_min(array, rolling_window)
    max_val = rolling_max(array, rolling_window)
    return (array - sma) / (max_val - min_val + 1e-9)

def rolling_zscore_mean(array, rolling_window):
    sma = rolling_mean(array, rolling_window)
    stddev = rolling_std(array, rolling_window)
    zscore = (array - sma) / (stddev + 1e-9)
    return zscore - rolling_mean(zscore, rolling_window)

def rolling_sigmoid_zscore(arr: np.ndarray, window: int) -> np.ndarray:
    # 1) get the exact z‐scores (unaltered)
    z = rolling_zscore(arr, window)

    # 2) apply the mathematically equivalent tanh form
    return np.tanh(z / 2.0)

def rolling_minmax_original(array, rolling_window):
    min_val = rolling_min(array, rolling_window)
    max_val = rolling_max(array, rolling_window)
    return (array - min_val) / (max_val - min_val)

def rolling_minmax_normalize(array, rolling_window):
    min_val = rolling_min(array, rolling_window)
    max_val = rolling_max(array, rolling_window)
    return 2 * (array - min_val) / (max_val - min_val + 1e-9) - 1

def rolling_skew(arr, window):
    n = arr.shape[0]
    if n < window:
        return np.full(n, np.nan)  # Return all NaNs if not enough data

    rolling_skew = np.full(n, np.nan)  # Full-length array, pre-filled with NaNs

    for i in range(n - window + 1):
        window_data = arr[i:i + window]  # Extract rolling window
        mean = np.mean(window_data)
        std = np.std(window_data, ddof=1)  # Sample std (ddof=1)
        
        if std != 0:  # Avoid division by zero
            rolling_skew[i + window - 1] = (window / ((window - 1) * (window - 2))) * np.sum(
                ((window_data - mean) / std) ** 3
            )

    return rolling_skew

def rolling_var(arr, window):
    n = arr.shape[0]
    if n < window:
        return np.full(n, np.nan)

    rolling_var = np.full(n, np.nan)

    for i in range(n - window + 1):
        window_data = arr[i:i + window]
        rolling_var[i + window - 1] = np.var(window_data, ddof=1)  # Sample variance

    return rolling_var

def rolling_kurt(arr, window):
    n = arr.shape[0]
    if n < window:
        return np.full(n, np.nan)

    rolling_kurt = np.full(n, np.nan)

    for i in range(n - window + 1):
        window_data = arr[i:i + window]
        mean = np.mean(window_data)
        std = np.std(window_data, ddof=1)

        if std != 0:
            m4 = np.mean(((window_data - mean) / std) ** 4)
            # Excess kurtosis: subtract 3 (optional, comment out if you want regular kurtosis)
            rolling_kurt[i + window - 1] = m4 - 3

    return rolling_kurt

def rolling_zscore(array, rolling_window):
    sma    = rolling_mean(array, rolling_window)
    stddev = rolling_std(array, rolling_window)
    # plain z-score:
    return (array - sma) / (stddev + 1e-9)

def rolling_tanh_estimator(arr, rolling_window):
    sma    = rolling_mean(arr, rolling_window)
    stddev = rolling_std(arr, rolling_window)
    return np.tanh(0.01 * (arr - sma) / (stddev + 1e-9))

def sigmoid(arr):
    return 2 * (1 / (1 + np.exp(arr))) - 1

def rolling_softmax(arr, window):
    n = arr.size
    if window > n:
        return np.full(n, np.nan)

    # build a (n–window+1)×window view
    shape   = (n - window + 1, window)
    strides = (arr.strides[0], arr.strides[0])
    wins    = np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)

    # 1) subtract per-window max for numerical stability
    m      = wins.max(axis=1)               # shape (n-window+1,)
    exps   = np.exp(wins - m[:, None])      # shape (n-window+1, window)

    # 2) get softmax of the *last* element in each window
    sm_last = exps[:, -1] / exps.sum(axis=1)

    # 3) pad the front with NaNs to keep length = n
    return np.concatenate((np.full(window - 1, np.nan), 2*sm_last - 1))

def rolling_l1_normalization(arr, rolling_window):
    abs_sum = rolling_sum(np.abs(arr), rolling_window)
    return 2 * (arr / (abs_sum + 1e-9)) - 1

def rolling_rsi(df, rolling_window):
    def calculate_rsi(series):
        delta = series.diff()
        gain = rolling_mean(delta.where(delta > 0, 0), rolling_window)
        loss = rolling_mean(-delta.where(delta < 0, 0), rolling_window)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    df["rsi"] = calculate_rsi(df["data"])
    df["sma"] = rolling_mean(df["rsi"], rolling_window)
    df["ema"] = rolling_ema(df["rsi"], rolling_window)
    df["wma"] = rolling_wma(df["rsi"], rolling_window)
    df["processed_data"] = (df["rsi"] - 50) / 50 
    return df

def calculate_macd(df, short_window, long_window, signal_window=9):
    # Calculate the short-term and long-term EMA
    df["EMA_short"] = rolling_ema(df["data"], short_window)
    df["EMA_long"] = rolling_ema(df["data"], long_window)
    # Calculate MACD line
    df["MACD"] = df["EMA_short"] - df["EMA_long"]
    # Calculate Signal line
    df["Signal"] = rolling_ema(df["MACD"], signal_window)
    # Calculate Histogram
    df["Histogram"] = df["MACD"] - df["Signal"]
    return df

def rolling_median(array, rolling_window):
    # Replace NaNs with zero
    arr = np.nan_to_num(array, nan=0)
    n = len(arr)
    # If window larger than array, all NaN
    if rolling_window > n:
        return np.full(n, np.nan)

    medians = np.empty(n, dtype=float)
    # First (window–1) entries are NaN
    medians[:rolling_window-1] = np.nan

    # Compute median for each full window
    for i in range(rolling_window-1, n):
        window = arr[i - rolling_window + 1 : i + 1]
        medians[i] = np.median(window)

    return medians

def signed_log1p(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.log1p(np.abs(x))

def rolling_cvs(array: np.ndarray, rolling_window: int) -> np.ndarray:
    std = rolling_std(array, rolling_window)
    mean = rolling_mean(array, rolling_window)
    return std / (mean + 1e-9)

def rolling_range(array, rolling_window):
    return rolling_max(array, rolling_window) - rolling_min(array, rolling_window)

def rolling_moment(array: np.ndarray, rolling_window: int, moment: int) -> np.ndarray:
    # 1) full-series rolling mean and std
    mu = rolling_mean(array, rolling_window)
    sigma = rolling_std(array, rolling_window)

    # 2) deviations
    deviations = array - mu

    # 3) numerator: rolling mean of deviations**moment
    num = rolling_mean(deviations ** moment, rolling_window)

    # 4) denominator: sigma**moment
    denom = (sigma ** moment) + 1e-9

    # 5) z-score
    return num / denom

def pct_change(arr):
    return pd.Series(arr, dtype=float).pct_change().to_numpy()

def log_diff_n(arr, n_diffs=1) -> np.ndarray:
    """
    1) compute n_diffs successive first-differences via your diff_n
    2) apply signed-log1p to that result
    """
    d = diff_n(arr, n_diffs)
    return signed_log1p(d)

def rolling_iqr(array: np.ndarray, rolling_window: int) -> np.ndarray:
    # replace NaNs with zero so percentile still works
    arr = np.nan_to_num(array, nan=0.0)
    n = len(arr)
    if rolling_window > n:
        return np.full(n, np.nan)

    out = np.empty(n, dtype=float)
    out[: rolling_window - 1] = np.nan

    for i in range(rolling_window - 1, n):
        window = arr[i - rolling_window + 1 : i + 1]
        q75 = np.percentile(window, 75)
        q25 = np.percentile(window, 25)
        out[i] = q75 - q25

    return out

def rolling_mad(array: np.ndarray, rolling_window: int) -> np.ndarray:
    arr = np.nan_to_num(array, nan=0.0)
    n = len(arr)
    if rolling_window > n:
        return np.full(n, np.nan)

    # first compute the rolling medians of the original array
    medians = rolling_median(arr, rolling_window)

    mad = np.empty(n, dtype=float)
    mad[:rolling_window-1] = np.nan

    # for each window, compute |vals - median| and take its median via rolling_median
    for i in range(rolling_window-1, n):
        window_vals = arr[i - rolling_window + 1 : i + 1]
        deviations = np.abs(window_vals - medians[i])
        # rolling_median(deviations, rolling_window) gives an array whose last element
        # is the median of the full `deviations` window
        mad[i] = rolling_median(deviations, rolling_window)[-1]

    return mad

def rolling_robust_z(array, rolling_window):
    # ensure NumPy array
    x = np.asarray(array, dtype=float)

    # 1) rolling median
    med = rolling_median(x, rolling_window)

    # 2) rolling MAD
    mad = rolling_mad(x, rolling_window)

    # 3) robust z
    return (x - med) / (mad + 1e-9)

def rolling_max_drawdown(array, rolling_window):
    # ensure float array
    x = np.asarray(array, dtype=float)
    # compute rolling maximum
    rm = rolling_max(x, rolling_window)
    # drawdown
    return (rm - x) / (rm + 1e-9)

def rolling_trend_slope(array: np.ndarray, window: int) -> np.ndarray:
    # ensure numpy array of floats
    y = np.asarray(array, dtype=float)
    n = y.shape[0]
    if window > n:
        return np.full(n, np.nan)

    # precompute X demean and denominator
    x = np.arange(window, dtype=float)
    x_mean = x.mean()
    x_demean = x - x_mean
    denom = np.sum(x_demean * x_demean)

    slopes = np.empty(n, dtype=float)
    slopes[: window - 1] = np.nan

    # slide the window
    for i in range(window - 1, n):
        y_win = y[i - window + 1 : i + 1]
        y_mean = y_win.mean()
        y_demean = y_win - y_mean
        slopes[i] = np.dot(y_demean, x_demean) / denom

    return slopes

def rolling_entropy(array, window):
    arr = np.asarray(array)
    n = arr.shape[0]
    if window > n:
        return np.full(n, np.nan)

    out = np.empty(n, dtype=float)
    out[: window-1] = np.nan

    for i in range(window-1, n):
        win = arr[i-window+1 : i+1]
        # get unique values and their frequencies
        vals, cnts = np.unique(win, return_counts=True)
        probs = cnts / cnts.sum()
        out[i] = -np.sum(probs * np.log(probs))

    return out

def rolling_positive_ratio(array, rolling_window):
    # 1) compute 1‐lag diff
    d = diff(array, periods=1)
    # 2) boolean mask of positive changes, cast to float for mean
    pos = (d > 0).astype(float)
    # 3) rolling mean of that mask
    return rolling_mean(pos, rolling_window)

def count_direction_changes(x):
    # first‐difference of x, then look at changes in its sign
    dx = np.diff(np.sign(np.diff(x)))
    # a non‐zero entry in dx means a flip in direction
    return np.sum(dx != 0)

def rolling_direction_changes(array, window):
    arr = np.asarray(array, dtype=float)
    n = arr.shape[0]
    if window > n:
        return np.full(n, np.nan)
    
    out = np.empty(n, dtype=float)
    out[:window-1] = np.nan
    
    for i in range(window-1, n):
        window_vals = arr[i-window+1 : i+1]
        out[i] = count_direction_changes(window_vals)
    
    return out

def rolling_autocorr(array, window, lag=1):
    x = np.asarray(array, dtype=float)
    n = x.shape[0]

    # if parameters are invalid, return all NaNs
    if window > n or lag < 1 or lag >= window:
        return np.full(n, np.nan, dtype=float)

    out = np.empty(n, dtype=float)
    out[: window - 1] = np.nan

    for t in range(window - 1, n):
        win = x[t - window + 1 : t + 1]
        y1 = win[:-lag]
        y2 = win[lag:]
        # de‐mean
        y1_dev = y1 - y1.mean()
        y2_dev = y2 - y2.mean()
        num = np.sum(y1_dev * y2_dev)
        den = np.sqrt(np.sum(y1_dev**2) * np.sum(y2_dev**2))
        out[t] = num / den if den != 0 else np.nan

    return out

def rolling_sharpe_like(array, rolling_window):
    x = np.asarray(array, dtype=float)
    mu = rolling_mean(x, rolling_window)
    sigma = rolling_std(x, rolling_window)
    return (mu / (sigma + 1e-9)) * np.sqrt(365)

def rolling_zscore_jump(array, window):
    x = np.asarray(array, dtype=float)
    n = x.size
    if window > n:
        return np.full(n, np.nan, dtype=float)

    out = np.empty(n, dtype=float)
    out[:window-1] = np.nan

    for i in range(window-1, n):
        win = x[i-window+1 : i+1]
        m = win.mean()
        s = win.std()  # population std (ddof=0)
        z = np.abs((win - m) / (s + 1e-9))
        out[i] = np.sum(z > 2)

    return out

def rolling_yeojohnson(array: np.ndarray, window: int) -> np.ndarray:
    x = np.asarray(array, dtype=float)
    n = x.size
    out = np.full(n, np.nan, dtype=float)

    for i in range(window - 1, n):
        win = x[i - window + 1 : i + 1]
        try:
            transformed, _ = yeojohnson(win)
            out[i] = transformed[-1]
        except Exception:
            out[i] = np.nan

    return out

def log_returns(arr) -> np.ndarray:
    a = np.asarray(arr, dtype=float)
    out = np.empty_like(a)
    out[0] = np.nan
    out[1:] = signed_log1p(a[1:] / (a[:-1] + 1e-9))
    return out

def rolling_trend_angle(arr: np.ndarray, window: int, to_degrees: bool = False) -> np.ndarray:
    a = np.asarray(arr, dtype=float)
    n = a.size
    if window < 2 or window > n:
        raise ValueError("`window` must be at least 2 and at most len(arr)")
    
    # Build a (n-window+1, window) view of all rolling windows
    windows = sliding_window_view(a, window_shape=window)
    x = np.arange(window)
    
    angles = np.empty(windows.shape[0], dtype=float)
    for i, y in enumerate(windows):
        slope = np.polyfit(x, y, 1)[0]
        angle = np.arctan(slope)
        angles[i] = np.degrees(angle) if to_degrees else angle

    # Prepend NaNs for indices where the window isn't full yet
    result = np.empty(n, dtype=float)
    result[: window - 1] = np.nan
    result[window - 1 :] = angles
    return result

def rolling_volatility_adjusted_return(arr: np.ndarray, window: int) -> np.ndarray:
    # 1) one-period returns
    ret = pct_change(arr)            # uses your helper, returns np.ndarray with NaN at [0]
    
    # 2) rolling volatility
    std = rolling_std(ret, window)   # uses your helper, NaNs for first window–1
    
    # 3) volatility-adjusted return
    return ret / (std + 1e-9)

def rolling_slope_acceleration(array: np.ndarray, window: int) -> np.ndarray:
    # 1) get your rolling slopes
    slopes = rolling_trend_slope(array, window)

    # 2) compute first‐difference of slopes
    accel = np.empty_like(slopes)
    accel[:] = np.nan

    # from index `window` onward, both slopes[t] and slopes[t-1] are defined
    accel[window:] = slopes[window:] - slopes[window - 1:-1]

    return accel