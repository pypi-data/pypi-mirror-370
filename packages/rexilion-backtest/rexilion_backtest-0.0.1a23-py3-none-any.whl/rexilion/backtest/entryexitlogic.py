import numpy as np
from rexilion.backtest import formula

def entry_exit_threshold(df, rolling_window, threshold, backtest_mode):
    data = df["processed_data"].values
    position = [0.0] * rolling_window  
    # entry exit logic
    if backtest_mode == "mr": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_0":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= 0 and position[i - 1] == 1) or (
                data[i] <= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "0_sideline": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > 0 and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < 0 and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sideline": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= threshold and position[i - 1] == 1) or (
                data[i] >= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_0": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= 0 and position[i - 1] == 1) or (
                data[i] >= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position    
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(sma)_sma": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if sma[i] > 0.0:
                upper_threshold = sma[i] * (1 + threshold)
                lower_threshold = sma[i] * (1 - threshold)
            else:
                upper_threshold = sma[i] * (1 - threshold)
                lower_threshold = sma[i] * (1 + threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(ema)_ema": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if ema[i] > 0.0:
                upper_threshold = ema[i] * (1 + threshold)
                lower_threshold = ema[i] * (1 - threshold)
            else:
                upper_threshold = ema[i] * (1 - threshold)
                lower_threshold = ema[i] * (1 + threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(wma)_wma": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if wma[i] > 0.0:
                upper_threshold = wma[i] * (1 + threshold)
                lower_threshold = wma[i] * (1 - threshold)
            else:
                upper_threshold = wma[i] * (1 - threshold)
                lower_threshold = wma[i] * (1 + threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sma": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if sma[i] > 0.0:
                upper_threshold = sma[i] * (1 + threshold)
                lower_threshold = sma[i] * (1 - threshold)
            else:
                upper_threshold = sma[i] * (1 - threshold)
                lower_threshold = sma[i] * (1 + threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_ema": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if ema[i] > 0.0:
                upper_threshold = ema[i] * (1 + threshold)
                lower_threshold = ema[i] * (1 - threshold)
            else:
                upper_threshold = ema[i] * (1 - threshold)
                lower_threshold = ema[i] * (1 + threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_wma": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if wma[i] > 0.0:
                upper_threshold = wma[i] * (1 + threshold)
                lower_threshold = wma[i] * (1 - threshold)
            else:
                upper_threshold = wma[i] * (1 - threshold)
                lower_threshold = wma[i] * (1 + threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(sma)": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = sma[i] * (1 + threshold)
            lower_threshold = sma[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(ema)": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = ema[i] * (1 + threshold)
            lower_threshold = ema[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(wma)": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = wma[i] * (1 + threshold)
            lower_threshold = wma[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = sma[i] * (1 + threshold)
            lower_threshold = sma[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(1)
            # long
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = ema[i] * (1 + threshold)
            lower_threshold = ema[i] * (1 - threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window) 
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = wma[i] * (1 + threshold)
            lower_threshold = wma[i] * (1 - threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sma":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= sma[i] and position[i - 1] == 1) or (
                data[i] >= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_ema":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= ema[i] and position[i - 1] == 1) or (
                data[i] >= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_wma":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= wma[i] and position[i - 1] == 1) or (
                data[i] >= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sideline": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > sma[i] and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < sma[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_sideline": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > ema[i] and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < ema[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_sideline": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > wma[i] and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < wma[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_sma":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= sma[i] and position[i - 1] == 1) or (
                data[i] <= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_ema":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= ema[i] and position[i - 1] == 1) or (
                data[i] <= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_wma":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= wma[i] and position[i - 1] == 1) or (
                data[i] <= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "cross-sma":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > sma[i]:
                position.append(1)
            # short
            elif data[i] < sma[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "cross-ema":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > ema[i]:
                position.append(1)
            # short
            elif data[i] < ema[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "cross-wma":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > wma[i]:
                position.append(1)
            # short
            elif data[i] < wma[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr-l": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # exit
            elif data[i] > threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr-s": 
        for i in range(rolling_window, len(df)):
            # exit
            if data[i] < -threshold:
                position.append(0)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_0-l":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= 0 and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_0-s":
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= 0 and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "0_sideline-l": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > 0 and data[i] < threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "0_sideline-s": 
        for i in range(rolling_window, len(df)):
            if data[i] < 0 and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= -threshold and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum-l": 
        for i in range(rolling_window, len(df)):
            # exit
            if data[i] < -threshold:
                position.append(0)
            # long
            elif data[i] > threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum-s": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # exit
            elif data[i] > threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sideline-l": 
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= threshold and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sideline-s": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= -threshold and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_0-l": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= 0 and position[i - 1] == 1):
                position.append(0)
            # follow last position    
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_0-s": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= 0 and position[i - 1] == -1):
                position.append(0)
            # follow last position    
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(sma)_sma-l": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if sma[i] > 0.0:
                upper_threshold = sma[i] * (1 + threshold)
                lower_threshold = sma[i] * (1 - threshold)
            else:
                upper_threshold = sma[i] * (1 - threshold)
                lower_threshold = sma[i] * (1 + threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(sma)_sma-s": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if sma[i] > 0.0:
                upper_threshold = sma[i] * (1 + threshold)
                lower_threshold = sma[i] * (1 - threshold)
            else:
                upper_threshold = sma[i] * (1 - threshold)
                lower_threshold = sma[i] * (1 + threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(ema)_ema-l": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if ema[i] > 0.0:
                upper_threshold = ema[i] * (1 + threshold)
                lower_threshold = ema[i] * (1 - threshold)
            else:
                upper_threshold = ema[i] * (1 - threshold)
                lower_threshold = ema[i] * (1 + threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(ema)_ema-s": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if ema[i] > 0.0:
                upper_threshold = ema[i] * (1 + threshold)
                lower_threshold = ema[i] * (1 - threshold)
            else:
                upper_threshold = ema[i] * (1 - threshold)
                lower_threshold = ema[i] * (1 + threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(wma)_wma-l": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if wma[i] > 0.0:
                upper_threshold = wma[i] * (1 + threshold)
                lower_threshold = wma[i] * (1 - threshold)
            else:
                upper_threshold = wma[i] * (1 - threshold)
                lower_threshold = wma[i] * (1 + threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(wma)_wma-s": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if wma[i] > 0.0:
                upper_threshold = wma[i] * (1 + threshold)
                lower_threshold = wma[i] * (1 - threshold)
            else:
                upper_threshold = wma[i] * (1 - threshold)
                lower_threshold = wma[i] * (1 + threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sma-l": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if sma[i] > 0.0:
                upper_threshold = sma[i] * (1 + threshold)
                lower_threshold = sma[i] * (1 - threshold)
            else:
                upper_threshold = sma[i] * (1 - threshold)
                lower_threshold = sma[i] * (1 + threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sma-s": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if sma[i] > 0.0:
                upper_threshold = sma[i] * (1 + threshold)
                lower_threshold = sma[i] * (1 - threshold)
            else:
                upper_threshold = sma[i] * (1 - threshold)
                lower_threshold = sma[i] * (1 + threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_ema-l": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if ema[i] > 0.0:
                upper_threshold = ema[i] * (1 + threshold)
                lower_threshold = ema[i] * (1 - threshold)
            else:
                upper_threshold = ema[i] * (1 - threshold)
                lower_threshold = ema[i] * (1 + threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_ema-s": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if ema[i] > 0.0:
                upper_threshold = ema[i] * (1 + threshold)
                lower_threshold = ema[i] * (1 - threshold)
            else:
                upper_threshold = ema[i] * (1 - threshold)
                lower_threshold = ema[i] * (1 + threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_wma-l": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if wma[i] > 0.0:
                upper_threshold = wma[i] * (1 + threshold)
                lower_threshold = wma[i] * (1 - threshold)
            else:
                upper_threshold = wma[i] * (1 - threshold)
                lower_threshold = wma[i] * (1 + threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_wma-s": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if wma[i] > 0.0:
                upper_threshold = wma[i] * (1 + threshold)
                lower_threshold = wma[i] * (1 - threshold)
            else:
                upper_threshold = wma[i] * (1 - threshold)
                lower_threshold = wma[i] * (1 + threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])   
    elif backtest_mode == "mr(sma)-l": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = sma[i] * (1 + threshold)
            lower_threshold = sma[i] * (1 - threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(sma)-s": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = sma[i] * (1 + threshold)
            lower_threshold = sma[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(ema)-l": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = ema[i] * (1 + threshold)
            lower_threshold = ema[i] * (1 - threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(ema)-s": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = ema[i] * (1 + threshold)
            lower_threshold = ema[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(wma)-l": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = wma[i] * (1 + threshold)
            lower_threshold = wma[i] * (1 - threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # long
            elif data[i] < lower_threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr(wma)-s": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = wma[i] * (1 + threshold)
            lower_threshold = wma[i] * (1 - threshold)
            # short
            if data[i] > upper_threshold:
                position.append(-1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)-l": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = sma[i] * (1 + threshold)
            lower_threshold = sma[i] * (1 - threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)-s": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = sma[i] * (1 + threshold)
            lower_threshold = sma[i] * (1 - threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)-l": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = ema[i] * (1 + threshold)
            lower_threshold = ema[i] * (1 - threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)-s": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = ema[i] * (1 + threshold)
            lower_threshold = ema[i] * (1 - threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)-l":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window) 
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = wma[i] * (1 + threshold)
            lower_threshold = wma[i] * (1 - threshold)
            # long
            if data[i] > upper_threshold:
                position.append(1)
            # exit
            elif data[i] < lower_threshold:
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)-s":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window) 
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            upper_threshold = wma[i] * (1 + threshold)
            lower_threshold = wma[i] * (1 - threshold)
            # exit
            if data[i] > upper_threshold:
                position.append(0)
            # short
            elif data[i] < lower_threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sma-l":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= sma[i] and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sma-s":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= sma[i] and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_ema-l":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= ema[i] and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_ema-s":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= ema[i] and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])    
    elif backtest_mode == "momentum_wma-l":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= wma[i] and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_wma-s":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= wma[i] and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sideline-l": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > sma[i] and data[i] < threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sideline-s": 
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if data[i] < sma[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif(data[i] <= -threshold and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_sideline-l": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > ema[i] and data[i] < threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_sideline-s": 
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if data[i] < ema[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= -threshold and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_sideline-l": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > wma[i] and data[i] < threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_sideline-s": 
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if data[i] < wma[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= -threshold and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_sma-l":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= sma[i] and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_sma-s":
        df["processed_sma"] = formula.rolling_mean(df["processed_data"], rolling_window)
        sma = df["processed_sma"].values
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= sma[i] and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_ema-l":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= ema[i] and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_ema-s":
        df["processed_ema"] = formula.rolling_ema(df["processed_data"], rolling_window)
        ema = df["processed_ema"].values
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= ema[i] and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_wma-l":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # exit logic
            elif (data[i] >= wma[i] and position[i - 1] == 1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_wma-s":
        df["processed_wma"] = formula.rolling_wma(df["processed_data"], rolling_window)
        wma = df["processed_wma"].values
        for i in range(rolling_window, len(df)):
            if data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] <= wma[i] and position[i - 1] == -1):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    else:
        print(f"Warning: Unsupported backtest_mode '{backtest_mode}' - skipping this iteration.")
    return position

def entry_exit_band(df, rolling_window, multiplier, backtest_mode):
    data = df["data"].values
    sma = formula.rolling_mean(data, rolling_window)
    upper_band = sma + (multiplier * formula.rolling_std(data, rolling_window))
    lower_band = sma - (multiplier * formula.rolling_std(data, rolling_window))
    position = [np.nan] * rolling_window  

    if backtest_mode == "mr": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_sma":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= sma[i] and position[i - 1] == 1) or (
                data[i] <= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_ema":
        ema = formula.rolling_ema(data, rolling_window)
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= ema[i] and position[i - 1] == 1) or (
                data[i] <= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_wma":
        wma = formula.rolling_wma(data, rolling_window)
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= wma[i] and position[i - 1] == 1) or (
                data[i] <= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "mr_0":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= 0 and position[i - 1] == 1) or (
                data[i] <= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "0_sideline": 
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > 0 and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < 0 and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(sma)_sideline": 
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > sma[i] and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < sma[i] and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(ema)_sideline": 
        ema = formula.rolling_ema(data, rolling_window)
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > ema[i] and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < ema[i] and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum(wma)_sideline": 
        wma = formula.rolling_wma(data, rolling_window)
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > wma[i] and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < wma[i] and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sideline": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= upper_band[i] and position[i - 1] == 1) or (
                data[i] >= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_0": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= 0 and position[i - 1] == 1) or (
                data[i] >= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position    
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_sma":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= sma[i] and position[i - 1] == 1) or (
                data[i] >= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_ema":
        ema = formula.rolling_ema(data, rolling_window)
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= ema[i] and position[i - 1] == 1) or (
                data[i] >= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    elif backtest_mode == "momentum_wma":
        wma = formula.rolling_wma(data, rolling_window)
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= wma[i] and position[i - 1] == 1) or (
                data[i] >= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    else:
        print(f"Warning: Unsupported backtest_mode '{backtest_mode}' - skipping this iteration.")
    return position
   
def entry_exit_macd(df, rolling_window1, rolling_window2):
    rolling_window = rolling_window1 if rolling_window1 > rolling_window2 else rolling_window2
    position = [np.nan] * rolling_window  
    macd = df["MACD"].values
    signal = df["Signal"].values
    for i in range(rolling_window, len(df)):
            # long
            if macd[i] >= signal[i]:
                position.append(1)
            # short
            elif macd[i] <= signal[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    return position

