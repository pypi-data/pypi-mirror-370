from pathlib import Path
import pandas as pd
import os
import numpy as np
from rexilion.backtest import diagram, util, entryexitlogic, formula

def mean_normalize_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_mean_normalize(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def mean_normalize(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"mean_normalize-backtest mode: {backtest_mode}")
            try:
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = mean_normalize_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"mean_normalize-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"mean_normalize-backtest mode: {backtest_mode_list}")
        report,df = mean_normalize_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"mean_normalize-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"mean_normalize-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))

def bollinger_bands_backtesting(df, rolling_window, multiplier, fees, sr_multiplier, backtest_mode, start_time, end_time):
    # models
    df["pos"] = entryexitlogic.entry_exit_band(df, rolling_window, multiplier, backtest_mode)
    return util.generate_report(df, rolling_window, multiplier, fees, sr_multiplier, start_time, end_time)

def bollinger_bands(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"bollinger_bands-backtest mode: {backtest_mode}")
            try:
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = bollinger_bands_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            multiplier=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"bollinger_bands-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"bollinger_bands-backtest mode: {backtest_mode_list}")
        report,df = bollinger_bands_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            multiplier=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"bollinger_bands-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"bollinger_bands-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def rsi_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    formula.rolling_rsi(df, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def rsi(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"rsi-backtest mode: {backtest_mode}")
            try:
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = rsi_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"rsi-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"rsi-backtest mode: {backtest_mode_list}")
        report, df = rsi_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"rsi-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"rsi-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def zscore_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_zscore(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def zscore(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"zscore-backtest mode: {backtest_mode}")
            try: 
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = zscore_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"zscore-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"zscore-backtest mode: {backtest_mode_list}")
        report, df = zscore_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"zscore-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"zscore-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def macd_backtesting(df, rolling_window1, rolling_window2, fees, sr_multiplier):
    formula.calculate_macd(df, rolling_window1, rolling_window2)
    df["pos"] = entryexitlogic.entry_exit_macd(df, rolling_window1, rolling_window2)
    report = util.generate_report(df, rolling_window1, rolling_window2, fees, sr_multiplier)
    return report

def macd(df, rolling_window1, rolling_window2, fees, sr_multiplier):
    if (isinstance(rolling_window1,(np.generic, np.ndarray)) and isinstance(rolling_window2,(np.generic, np.ndarray))):
        all_report = []
        print(f"MACD-backtest")
        for rolling1 in rolling_window1:
            for rolling2 in rolling_window2:                
                report = macd_backtesting(
                    df=df,
                    rolling_window1=rolling1,
                    rolling_window2=rolling2,
                    fees=fees,
                    sr_multiplier=sr_multiplier,
                )
                all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"MACD.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\MACD", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path) 
        diagram.plot_heatmap(report_df)
    else:
        all_report = []
        print(f"MACD-backtest")
        report = macd_backtesting(
            df=df,
            rolling_window1=rolling_window1,
            rolling_window2=rolling_window2,
            fees=fees,
            sr_multiplier=sr_multiplier,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"MACD.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\MACD", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path)
        file_name1 = f"MACD-Position.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\MACD", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)
        diagram.plot_single_diagram(df, report_df)
        
def minmax_normalize_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_minmax_normalize(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def minmax_normalize(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"minmax-backtest mode: {backtest_mode}")
            try:
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = minmax_normalize_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"minmax-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"minmax-backtest mode: {backtest_mode_list}")
        report, df = minmax_normalize_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"minmax-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"minmax-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def zscore_mean_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_zscore_mean(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def zscore_mean(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"zscore_mean-backtest mode: {backtest_mode}")
            try: 
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = zscore_mean_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"zscore_mean-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"zscore_mean-backtest mode: {backtest_mode_list}")
        report, df = zscore_mean_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"zscore_mean-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"zscore_mean-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def tanh_estimator_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_tanh_estimator(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def tanh_estimator(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"tanh_estimator-backtest mode: {backtest_mode}")
            try: 
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = tanh_estimator_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"tanh_estimator-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"tanh_estimator-backtest mode: {backtest_mode_list}")
        report, df = tanh_estimator_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"tanh_estimator-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"tanh_estimator-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def sigmoid_zscore_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_sigmoid_zscore(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def sigmoid_zscore(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"sigmoid_zscore-backtest mode: {backtest_mode}")
            try: 
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = sigmoid_zscore_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"sigmoid_zscore-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"sigmoid_zscore-backtest mode: {backtest_mode_list}")
        report, df = sigmoid_zscore_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"sigmoid_zscore-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"sigmoid_zscore-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def softmax_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_softmax(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def softmax(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"softmax-backtest mode: {backtest_mode}")
            try: 
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = softmax_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"softmax-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"softmax-backtest mode: {backtest_mode_list}")
        report, df = softmax_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"softmax-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"softmax-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))
        
def l1_normalization_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode, start_time, end_time):
    df["processed_data"] = formula.rolling_l1_normalization(df["data"].values, rolling_window)
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    return util.generate_report(df, rolling_window, threshold, fees, sr_multiplier, start_time, end_time)

def l1_normalization(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier, start_time, end_time, naming: str=None):
    base = Path("result")
    if naming:
        base = base / naming

    base.mkdir(parents=True, exist_ok=True)
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"l1_normalization-backtest mode: {backtest_mode}")
            try: 
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report, _ = l1_normalization_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                            start_time=start_time,
                            end_time=end_time
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            if naming:
                file_name = f"{naming}.csv"
                img_name = f"{naming}_heatmap.png"
                diagram.plot_heatmap(report_df, str(base / img_name))
            else:
                file_name = f"l1_normalization-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
                diagram.plot_heatmap(report_df)
            report_df.to_csv(str(base / file_name)) 
    else:
        all_report = []
        print(f"l1_normalization-backtest mode: {backtest_mode_list}")
        report, df = l1_normalization_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
            start_time=start_time,
            end_time=end_time
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        if naming:
            file_name = f"{naming}.csv"
            img_name = f"{naming}.png"
            file_name1 = f"{naming}_position.csv"
            diagram.plot_single_diagram(df, report_df, str(base / img_name))
        else:
            file_name = f"l1_normalization-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_name1 = f"l1_normalization-{backtest_mode_list}_position.csv"
            diagram.plot_single_diagram(df, report_df)
        report_df.to_csv(str(base / file_name)) 
        df.to_csv(str(base / file_name1))

def Michael_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode):
    df["processed_data"] = df["data"]
    df["pos"] = entryexitlogic.entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    report = util.generate_report(df, rolling_window, threshold, fees, sr_multiplier)
    return report

def Michael(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier):
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"Michael-backtest mode: {backtest_mode}")
            try:
                for rolling_window in rolling_window_range:
                    for threshold in threshold_range:
                        report = Michael_backtesting(
                            df=df,
                            rolling_window=rolling_window,
                            threshold=threshold,
                            fees=fees,
                            sr_multiplier=sr_multiplier,
                            backtest_mode=backtest_mode,
                        )
                        all_report.append(report)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            report_df = pd.DataFrame(all_report)
            file_name = f"Michael-{backtest_mode}.csv"
            file_path = Path(os.path.join(r"result\Michael", file_name))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            report_df.to_csv(file_path) 
            diagram.plot_heatmap(report_df)
    else:
        all_report = []
        print(f"Michael-backtest mode: {backtest_mode_list}")
        report = Michael_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"Michael-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\Michael", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path) 
        file_name1 = f"Michael-Position-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\Michael", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)
        diagram.plot_single_diagram(df, report_df)