from numba import njit
import numpy as np
from rexilion.backtest.formula_numba import (
    rolling_mean,
    rolling_ema,
    rolling_wma,
    rolling_std,
    rolling_min,
    rolling_max
)

# Mode IDs
MODE_MR = 0
MODE_MR_0 = 1
MODE_0_SIDELINE = 2
MODE_MOMENTUM = 3
MODE_MOMENTUM_SIDELINE = 4
MODE_MOMENTUM_0 = 5
MODE_MR_SMAMA = 6
MODE_MR_EMAMA = 7
MODE_MR_WMAMA = 8
MODE_MOMENTUM_SMAMA = 9
MODE_MOMENTUM_EMAMA = 10
MODE_MOMENTUM_WMAMA = 11
MODE_MR_SMA = 12
MODE_MR_EMA = 13
MODE_MR_WMA = 14
MODE_MOMENTUM_SMA = 15
MODE_MOMENTUM_EMA = 16
MODE_MOMENTUM_WMA = 17
MODE_MOM_SMA_SIDELINE = 18
MODE_MOM_EMA_SIDELINE = 19
MODE_MOM_WMA_SIDELINE = 20
MODE_MM_MR = 21
MODE_MM_MR_0 = 22
MODE_MM_MOMENTUM = 23
MODE_MM_MOMENTUM_0 = 24
MODE_MM_MR_SMA = 25
MODE_MM_MR_EMA = 26
MODE_MM_MR_WMA = 27
MODE_MM_MOMENTUM_SMA = 28
MODE_MM_MOMENTUM_EMA = 29
MODE_MM_MOMENTUM_WMA = 30

@njit(cache=True)
def entry_exit_threshold(
    processed: np.ndarray,
    rolling_window: int,
    threshold: float,
    mode_id: int
) -> np.ndarray:
    n = processed.shape[0]
    pos = np.empty(n, np.int8)
    # initialize
    for i in range(rolling_window):
        pos[i] = 0

    # --- precompute flags once ---
    use_sma = (mode_id == MODE_MR_SMAMA or mode_id == MODE_MOMENTUM_SMAMA
               or mode_id == MODE_MR_SMA or mode_id == MODE_MOMENTUM_SMA
               or mode_id == MODE_MM_MOMENTUM_SMA or mode_id == MODE_MM_MR_SMA)
    use_ema = (mode_id == MODE_MR_EMAMA or mode_id == MODE_MOMENTUM_EMAMA
               or mode_id == MODE_MR_EMA or mode_id == MODE_MOMENTUM_EMA
               or mode_id == MODE_MM_MOMENTUM_EMA or mode_id == MODE_MM_MR_EMA)
    use_wma = (mode_id == MODE_MR_WMAMA or mode_id == MODE_MOMENTUM_WMAMA
               or mode_id == MODE_MR_WMA or mode_id == MODE_MOMENTUM_WMA
               or mode_id == MODE_MM_MOMENTUM_WMA or mode_id == MODE_MM_MR_WMA)
    use_minmax = (mode_id == MODE_MM_MOMENTUM or mode_id == MODE_MM_MOMENTUM_0
                  or mode_id == MODE_MM_MOMENTUM_EMA or mode_id == MODE_MM_MOMENTUM_SMA
                  or mode_id == MODE_MM_MOMENTUM_WMA or mode_id == MODE_MM_MR
                  or mode_id == MODE_MM_MR_EMA or mode_id == MODE_MM_MR_SMA
                  or mode_id == MODE_MM_MR_WMA)

    # --- compute only what’s needed ---
    sma = rolling_mean(processed, rolling_window) if use_sma else np.empty(1, np.float64)
    ema = rolling_ema(processed, rolling_window) if use_ema else np.empty(1, np.float64)
    wma = rolling_wma(processed, rolling_window) if use_wma else np.empty(1, np.float64)
    mn  = rolling_min(processed, rolling_window) if use_minmax else np.empty(1, np.float64)
    mx  = rolling_max(processed, rolling_window) if use_minmax else np.empty(1, np.float64)

    # main loop
    for i in range(rolling_window, n):
        x = processed[i]
        prev = pos[i-1]
        # mean-reversion
        if mode_id == MODE_MR:
            if x < -threshold:
                pos[i] = 1
            elif x > threshold:
                pos[i] = -1
            else:
                pos[i] = prev
        # mr_0
        elif mode_id == MODE_MR_0:
            if x < -threshold:
                pos[i] = 1
            elif x > threshold:
                pos[i] = -1
            elif (x >= 0 and prev == 1) or (x <= 0 and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # mr_sma
        elif mode_id == MODE_MR_SMA:
            if x < -threshold:
                pos[i] = 1
            elif x > threshold:
                pos[i] = -1
            elif (x >= sma[i] and prev == 1) or (x <= sma[i] and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # mr_ema
        elif mode_id == MODE_MR_EMA:
            if x < -threshold:
                pos[i] = 1
            elif x > threshold:
                pos[i] = -1
            elif (x >= ema[i] and prev == 1) or (x <= ema[i] and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # mr_wma
        elif mode_id == MODE_MR_WMA:
            if x < -threshold:
                pos[i] = 1
            elif x > threshold:
                pos[i] = -1
            elif (x >= wma[i] and prev == 1) or (x <= wma[i] and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # 0_sideline
        elif mode_id == MODE_0_SIDELINE:
            if 0 < x < threshold:
                pos[i] = 1
            elif 0 > x > -threshold:
                pos[i] = -1
            elif ((x >= threshold and prev == 1) or
                  (x <= -threshold and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev
        # momentum
        elif mode_id == MODE_MOMENTUM:
            if x < -threshold:
                pos[i] = -1
            elif x > threshold:
                pos[i] = 1
            else:
                pos[i] = prev
        # momentum_0
        elif mode_id == MODE_MOMENTUM_0:
            if x < -threshold:
                pos[i] = -1
            elif x > threshold:
                pos[i] = 1
            elif (x <= 0 and prev == 1) or (x >= 0 and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # momentum_sma
        elif mode_id == MODE_MOMENTUM_SMA:
            if x < -threshold:
                pos[i] = -1
            elif x > threshold:
                pos[i] = 1
            elif (x <= sma[i] and prev == 1) or (x >= sma[i] and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # momentum_ema
        elif mode_id == MODE_MOMENTUM_EMA:
            if x < -threshold:
                pos[i] = -1
            elif x > threshold:
                pos[i] = 1
            elif (x <= ema[i] and prev == 1) or (x >= ema[i] and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # momentum_wma
        elif mode_id == MODE_MOMENTUM_WMA:
            if x < -threshold:
                pos[i] = -1
            elif x > threshold:
                pos[i] = 1
            elif (x <= wma[i] and prev == 1) or (x >= wma[i] and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev
        # mr(sma)
        elif mode_id == MODE_MR_SMAMA:
            m = sma[i]
            if m > 0:
                up = m * (1 + threshold)
                lo = m * (1 - threshold)
            else:
                up = m * (1 - threshold)
                lo = m * (1 + threshold)
            if x > up:
                pos[i] = -1
            elif x < lo:
                pos[i] = 1
            else:
                pos[i] = prev
        # momentum(sma)
        elif mode_id == MODE_MOMENTUM_SMAMA:
            m = sma[i]
            if m > 0:
                up = m * (1 + threshold)
                lo = m * (1 - threshold)
            else:
                up = m * (1 - threshold)
                lo = m * (1 + threshold)
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            else:
                pos[i] = prev
        # mr(ema)
        elif mode_id == MODE_MR_EMAMA:
            m = ema[i]
            if m > 0:
                up = m * (1 + threshold)
                lo = m * (1 - threshold)
            else:
                up = m * (1 - threshold)
                lo = m * (1 + threshold)
            if x > up:
                pos[i] = -1
            elif x < lo:
                pos[i] = 1
            else:
                pos[i] = prev
        # momentum(ema)
        elif mode_id == MODE_MOMENTUM_EMAMA:
            m = ema[i]
            if m > 0:
                up = m * (1 + threshold)
                lo = m * (1 - threshold)
            else:
                up = m * (1 - threshold)
                lo = m * (1 + threshold)
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            else:
                pos[i] = prev
        # mr(wma)
        elif mode_id == MODE_MR_WMAMA:
            m = wma[i]
            if m > 0:
                up = m * (1 + threshold)
                lo = m * (1 - threshold)
            else:
                up = m * (1 - threshold)
                lo = m * (1 + threshold)
            if x > up:
                pos[i] = -1
            elif x < lo:
                pos[i] = 1
            else:
                pos[i] = prev
        # momentum(wma)
        elif mode_id == MODE_MOMENTUM_WMAMA:
            m = wma[i]
            if m > 0:
                up = m * (1 + threshold)
                lo = m * (1 - threshold)
            else:
                up = m * (1 - threshold)
                lo = m * (1 + threshold)
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            else:
                pos[i] = prev
        elif mode_id == MODE_MM_MR:
            if x < mn[i] * threshold:
                pos[i] = 1
            elif x > mx[i] * threshold:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_0:
            if x < mn[i] * threshold:
                pos[i] = 1
            elif x > mx[i] * threshold:
                pos[i] = -1
            elif (x >= 0.0 and prev == 1) or (x <= 0.0 and prev == -1):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_SMA:
            m = sma[i]
            if x < mn[i] * threshold:
                pos[i] = 1
            elif x > mx[i] * threshold:
                pos[i] = -1
            elif ((x >= m and prev == 1) or (x <= m and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_EMA:
            m = ema[i]
            if x < mn[i] * threshold:
                pos[i] = 1
            elif x > mx[i] * threshold:
                pos[i] = -1
            elif ((x >= m and prev == 1) or (x <= m and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_WMA:
            m = wma[i]
            if x < mn[i] * threshold:
                pos[i] = 1
            elif x > mx[i] * threshold:
                pos[i] = -1
            elif ((x >= m and prev == 1) or (x <= m and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM:
            if x < mn[i] * threshold:
                pos[i] = -1
            elif x > mx[i] * threshold:
                pos[i] = 1
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_0:
            if x < mn[i] * threshold:
                pos[i] = -1
            elif x > mx[i] * threshold:
                pos[i] = 1
            elif ((x <= 0.0 and prev == 1) or (x >= 0.0 and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_SMA:
            m = sma[i]
            if x < mn[i] * threshold:
                pos[i] = -1
            elif x > mx[i] * threshold:
                pos[i] = 1
            elif ((x <= m and prev == 1) or (x >= m and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_EMA:
            m = ema[i]
            if x < mn[i] * threshold:
                pos[i] = -1
            elif x > mx[i] * threshold:
                pos[i] = 1
            elif ((x <= m and prev == 1) or (x >= m and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_WMA:
            m = wma[i]
            if x < mn[i] * threshold:
                pos[i] = -1
            elif x > mx[i] * threshold:
                pos[i] = 1
            elif ((x <= m and prev == 1) or (x >= m and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        else:
            pos[i] = prev  # carry
    return pos


@njit(cache=True)
def entry_exit_band(
    data: np.ndarray,
    rolling_window: int,
    multiplier: float,
    mode_id: int
) -> np.ndarray:
    """
    Numba‐compiled entry/exit logic that mirrors the pure‐Python `entry_exit_band` with all backtest_mode branches.
    The caller must pass in `mode_id` corresponding to one of the MODE_* constants described below.
    """
    n = data.shape[0]

    # Preallocate arrays
    sma = rolling_mean(data, rolling_window)
    ema = np.empty(n, np.float64)
    wma = np.empty(n, np.float64)

    # Precompute EMA/WMA only if needed
    if (mode_id == MODE_MR_EMAMA
        or mode_id == MODE_MR_EMA
        or mode_id == MODE_MOMENTUM_EMA
        or mode_id == MODE_MOM_EMA_SIDELINE):
        ema = rolling_ema(data, rolling_window)

    if (mode_id == MODE_MR_WMAMA
        or mode_id == MODE_MR_WMA
        or mode_id == MODE_MOMENTUM_WMA
        or mode_id == MODE_MOM_WMA_SIDELINE):
        wma = rolling_wma(data, rolling_window)

    # Upper and lower bands (based on SMA + multiplier * STD)
    std = rolling_std(data, rolling_window)
    upper = np.empty(n, np.float64)
    lower = np.empty(n, np.float64)
    for i in range(n):
        upper[i] = sma[i] + multiplier * std[i]
        lower[i] = sma[i] - multiplier * std[i]

    # Output positions (0 = flat, 1 = long, -1 = short)
    pos = np.empty(n, np.int8)
    for i in range(rolling_window):
        pos[i] = 0  # no position before we have a full window

    # Main loop
    for i in range(rolling_window, n):
        x = data[i]
        prev = pos[i - 1]
        up = upper[i]
        lo = lower[i]
        m_sma = sma[i]
        m_ema = ema[i]
        m_wma = wma[i]

        # ---- MODE_MR: mean‐reversion on bands, carry last if no signal ----
        if mode_id == MODE_MR:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            else:
                pos[i] = prev

        # ---- MODE_MR_SMAMA: MR + exit when price crosses SMA ----
        elif mode_id == MODE_MR_SMA:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= m_sma and prev == 1) or (x <= m_sma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MR_EMAMA: MR + exit when price crosses EMA ----
        elif mode_id == MODE_MR_EMA:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= m_ema and prev == 1) or (x <= m_ema and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MR_WMAMA: MR + exit when price crosses WMA ----
        elif mode_id == MODE_MR_WMA:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= m_wma and prev == 1) or (x <= m_wma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MR_0: MR + exit when price crosses zero ----
        elif mode_id == MODE_MR_0:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= 0.0 and prev == 1) or (x <= 0.0 and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_0_SIDELINE: "0_sideline" logic ----
        elif mode_id == MODE_0_SIDELINE:
            if x > 0.0 and x < up:
                pos[i] = 1
            elif x < 0.0 and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOM_SMA_SIDELINE: "momentum(sma)_sideline" ----
        elif mode_id == MODE_MOM_SMA_SIDELINE:
            if x > m_sma and x < up:
                pos[i] = 1
            elif x < m_sma and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOM_EMA_SIDELINE: "momentum(ema)_sideline" ----
        elif mode_id == MODE_MOM_EMA_SIDELINE:
            if x > m_ema and x < up:
                pos[i] = 1
            elif x < m_ema and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOM_WMA_SIDELINE: "momentum(wma)_sideline" ----
        elif mode_id == MODE_MOM_WMA_SIDELINE:
            if x > m_wma and x < up:
                pos[i] = 1
            elif x < m_wma and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOMENTUM: purely momentum on bands (flip signs from MR) ----
        elif mode_id == MODE_MOMENTUM:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            else:
                pos[i] = prev

        # ---- MODE_MOMENTUM_SIDELINE: exit when crossing back inside bands ----
        elif mode_id == MODE_MOMENTUM_SIDELINE:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= up and prev == 1) or (x >= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOMENTUM_0: momentum + exit when crossing zero ----
        elif mode_id == MODE_MOMENTUM_0:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= 0.0 and prev == 1) or (x >= 0.0 and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOMENTUM_SMA: momentum + exit on crossing SMA ----
        elif mode_id == MODE_MOMENTUM_SMA:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= m_sma and prev == 1) or (x >= m_sma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOMENTUM_EMA: momentum + exit on crossing EMA ----
        elif mode_id == MODE_MOMENTUM_EMA:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= m_ema and prev == 1) or (x >= m_ema and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- MODE_MOMENTUM_WMA: momentum + exit on crossing WMA ----
        elif mode_id == MODE_MOMENTUM_WMA:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= m_wma and prev == 1) or (x >= m_wma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        # ---- Fallback: unsupported mode → carry last position ----
        else:
            continue

    return pos

@njit(cache=True)
def entry_exit_macd(
    macd: np.ndarray,
    signal: np.ndarray,
    rolling_window: int
) -> np.ndarray:
    n = macd.shape[0]
    pos = np.empty(n, np.int8)
    for i in range(rolling_window):
        pos[i] = 0
    for i in range(rolling_window, n):
        if macd[i] >= signal[i]:
            pos[i] = 1
        elif macd[i] <= signal[i]:
            pos[i] = -1
        else:
            pos[i] = pos[i-1]
    return pos
