from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from matplotlib.ticker import MaxNLocator
from scipy import stats


def plot_single_diagram(df, report_df, file_path: str=None):
    plot_heatmap(report_df)

    # Plot Cumulative Return and Close Price
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Cumulative Return on the left y-axis
    line1, = ax1.plot(df['datetime'], df['cumu'], label='Cumulative Return (Buy and Hold)', color='red')
    ax1.set_ylabel('Cumulative Return', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.legend(loc="upper left")
    ax1.grid(True)

    # Create a secondary y-axis for Close Price
    ax2 = ax1.twinx()
    line2, = ax2.plot(df['datetime'], df['close'], label='Close Price', color='blue')
    ax2.set_ylabel('Close Price', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.legend(loc="lower right")

    # Set the title and x-axis labels
    plt.title('Cumulative Return and Close Price Over Time')
    ax1.set_xlabel('Date')

    # Manually set the major locator and formatter for the x-axis
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True, prune='lower', nbins=12))  # Adjust number of ticks

    # Rotate the x-axis labels and apply auto format to prevent overlapping
    fig.autofmt_xdate(rotation=45)

    # Identify MDD points: peak and trough
    trough_index = df["drawdown"].idxmin()  # Index of the trough (lowest drawdown point)
    trough_value = df["cumu"].iloc[trough_index]
    trough_date = df["datetime"].iloc[trough_index]

    peak_index = df["cumu"][:trough_index].idxmax()  # Peak before the trough
    peak_value = df["cumu"].iloc[peak_index]
    peak_date = df["datetime"].iloc[peak_index]

    # Plot the peak and trough
    ax1.scatter(peak_date, peak_value, color='orange', zorder=5, label="Peak (Before MDD)")
    ax1.scatter(trough_date, trough_value, color='green', zorder=5, label="Trough (MDD)")

    # Add vertical lines to mark the MDD period
    ax1.axvline(peak_date, color='orange', linestyle='--', linewidth=1, label="Peak Date")
    ax1.axvline(trough_date, color='green', linestyle='--', linewidth=1, label="Trough Date")

    # Add a legend for the MDD points
    ax1.legend(loc="upper left")

    # Adjust layout to avoid overlap
    plt.tight_layout()

    if file_path:
        base = Path(file_path).with_suffix("")  
        chart_path = base.parent / f"{base.name}_equitycurve.png"
        fig.savefig(str(chart_path), bbox_inches="tight")
        
    # Show the plot
    plt.show()
    
def plot_heatmap(report_df, file_path: str=None):
    pivot_table = report_df.pivot(index="param1", columns="param2", values="SR")

    # Dynamically adjust figure size based on data dimensions
    rows, cols = pivot_table.shape
    fig_size = (max(10, cols * 1.2), max(5, rows * 0.7))

    # Create figure and axis with dynamic size
    fig, ax1 = plt.subplots(figsize=fig_size)

    # Compute font size dynamically
    font_size = max(8, min(20, 250 / max(rows, cols)))  

    # Define custom colormap
    cmap = sns.color_palette(["white"] + sns.color_palette("YlGn", as_cmap=True)(np.linspace(0, 1, 256)).tolist())

    # Main heatmap with dynamic font size
    sns.heatmap(
        pivot_table, 
        annot=True, 
        fmt=".2f",
        cmap=cmap, 
        vmin=1, 
        vmax=pivot_table.max().max(), 
        ax=ax1,
        annot_kws={"size": font_size}  # Adjust annotation size dynamically
    )

    # Create a secondary y-axis on the right
    ax2 = ax1.twinx()
    ax2.set_ylim(ax1.get_ylim())

    # Set the same y-ticks and labels on the second axis
    ax2.set_yticks(ax1.get_yticks())
    ax2.set_yticklabels(ax1.get_yticklabels())

    # Set labels for both y-axes
    ax1.set_ylabel("param1 (Left Axis)")
    ax2.set_ylabel("param1 (Right Axis)")

    plt.title("Sharpe Ratio Heatmap", fontsize=font_size + 5)

    if file_path:
        fig.savefig(file_path, bbox_inches="tight")
    plt.show()
    
def plot_data_spread(df):
    # Create the figure and primary axis
    fig, ax1 = plt.subplots(figsize=(20, 9))

    # Scatter plot for 'data' on the left y-axis
    ax1.scatter(df['datetime'], df['data'], label='Data Spread', color='red', marker='o', s=3)
    ax1.set_ylabel('Raw Data', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.legend(loc="upper left")
    ax1.grid(True)

    # Create a secondary y-axis for Close Price
    ax2 = ax1.twinx()
    ax2.plot(df['datetime'], df['close'], label='Close Price', color='blue')
    ax2.set_ylabel('Close Price', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.legend(loc="lower right")

    # Set the title and x-axis labels
    plt.title('Data Spread and Close Price over Time')
    ax1.set_xlabel('Date')

    # Manually set the major locator and formatter (use 'nbins' instead of 'nticks')
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True, prune='lower', nbins=12))  # Adjust number of ticks

    # Rotate the x-axis labels to avoid overlap
    fig.autofmt_xdate(rotation=45)

    # Adjust layout to avoid overlap
    plt.tight_layout()

    # Show the plot
    plt.show()

def plot_correlation(file_paths, start_time, end_time):
    returns_list = []
    pnl_list = []
    
    # Load each CSV, calculate periodic returns and PnL, and store them in the lists
    for strategy_name, (file_path, leverage) in file_paths.items():
        try:
            strategy_data = process_file(file_path, leverage, start_time, end_time)
            
            if 'new_cumu' not in strategy_data.columns or 'datetime' not in strategy_data.columns:
                raise ValueError(f"'new_cumu' or 'datetime' column not found in {file_path}")
            if 'new_pnl' not in strategy_data.columns:
                raise ValueError(f"'new_pnl' column not found in {file_path}")
                        
            # Extract cumulative returns and time
            cumulative_returns = strategy_data['new_cumu'].values
            time = strategy_data['datetime'].values[1:]  # Adjust for periodic returns
            
            # Calculate periodic returns
            periodic_returns = cumulative_returns[1:] / cumulative_returns[:-1] - 1
            
            # Create a DataFrame for periodic returns
            strategy_returns = pd.DataFrame({
                'datetime': time,
                strategy_name: periodic_returns
            })
            
            returns_list.append(strategy_returns)

            # Extract PnL and time
            pnl = strategy_data['new_pnl'].values
            time_pnl = strategy_data['datetime'].values
            
            # Create a DataFrame for PnL
            strategy_pnl = pd.DataFrame({
                'datetime': time_pnl,
                strategy_name: pnl
            })
            
            pnl_list.append(strategy_pnl)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    # Plot correlation for cumulative returns
    plot_correlation_helper(returns_list, "Cumulative Returns Correlation Matrix Heatmap")

    # Plot correlation for PnL
    plot_correlation_helper(pnl_list, "PnL Correlation Matrix Heatmap")

def plot_correlation_helper(data_list, title):
    """Helper function to plot correlation matrix."""
    merged_data = data_list[0]
    for other in data_list[1:]:
        merged_data = pd.merge(merged_data, other, on='datetime', how='inner')

    # Drop the 'datetime' column for correlation computation
    merged_data.drop(columns=['datetime'], inplace=True)

    # Compute the correlation matrix
    correlation_matrix = merged_data.corr()

    # Adjust figure size dynamically
    size = max(10, len(correlation_matrix) * 1.2)  # Adjust size based on number of variables
    plt.figure(figsize=(size, size))

    # Plot the correlation matrix heatmap with adjusted font size
    sns.heatmap(
        correlation_matrix, 
        annot=True, 
        fmt=".2f", 
        cmap="coolwarm", 
        cbar=True, 
        square=True,
        annot_kws={"size": size / len(correlation_matrix) * 15}  # Dynamically adjust font size
    )

    plt.title(title, fontsize=20)
    plt.show()

def process_file(file_path, leverage, start_time, end_time):
    """Process a single file to calculate PnL and cumulative returns."""
    df = pd.read_csv(file_path)
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)

    if start_time_ms is not None:
        df = df[df["start_time"] >= start_time_ms]
    if end_time_ms is not None:
        df = df[df["start_time"] < end_time_ms]
        
    df = df.reset_index(drop=True)
    
    # Calculate new_pos using df.loc for consistency
    df.loc[:, 'new_pos'] = df['pos'] * leverage

    # Calculate new_trades using df.loc for alignment
    df.loc[:, 'new_trades'] = 0.0  # Initialize with float dtype
    df.loc[1:, 'new_trades'] = abs(
        df['new_pos'].iloc[1:].values - df['new_pos'].iloc[:-1].values
    )

    # Calculate new_pnl using df.loc for alignment
    df.loc[:, 'new_pnl'] = 0.0  # Initialize with float dtype
    df.loc[1:, 'new_pnl'] = (
        df['price_chg'].iloc[1:].values * df['new_pos'].iloc[:-1].values
        - df['new_trades'].iloc[1:].values * 0.06 / 100.0
    )

    # Calculate cumulative returns
    df.loc[:, 'new_cumu'] = df['new_pnl'].cumsum()

    return df[['datetime', 'new_pnl', 'new_cumu', 'close']]  # Include only relevant columns

def calculate_drawdown_and_recovery(cumu_series):
        """Calculate max drawdown and recovery period."""
        cumu_max = cumu_series.cummax()
        drawdown = cumu_series - cumu_max
        mdd = drawdown.min()

        if mdd < 0:
            # Index of the maximum drawdown
            mdd_start_idx = drawdown.idxmin()

            # Find recovery index (if exists)
            recovery_idxs = cumu_series[
                (cumu_series.index > mdd_start_idx) & (cumu_series >= cumu_max[mdd_start_idx])
            ].index

            if len(recovery_idxs) > 0:
                recovery_period = recovery_idxs[0] - mdd_start_idx

                # Convert to days if using DatetimeIndex
                if isinstance(cumu_series.index, pd.DatetimeIndex):
                    recovery_period_days = recovery_period.total_seconds() / (3600 * 24)
                else:
                    recovery_period_days = recovery_period / 24  # Assume 1 step = 1 hour
            else:
                recovery_period_days = None
        else:
            recovery_period_days = None

        return mdd, recovery_period_days

def plot_combined_equity(file_paths, start_time, end_time):
    cumu_list, pnl_list = [], []
    close_list = []  # Store close data

    # Process each strategy
    for strategy_name, (file_path, leverage) in file_paths.items():
        try:
            df = process_file(file_path, leverage, start_time, end_time)
            cumu_list.append(df[['datetime', 'new_cumu']].rename(columns={'new_cumu': strategy_name}))
            pnl_list.append(df[['datetime', 'new_pnl']].rename(columns={'new_pnl': strategy_name}))
            close_list.append(df[['datetime', 'close']].rename(columns={'close': strategy_name}))  # Store close data
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    # Merge PnL data and calculate total PnL
    pnl_merge = pd.concat(pnl_list, axis=1).drop_duplicates(subset=['datetime'])
    total_pnl = pnl_merge.drop(columns=['datetime']).sum(axis=1)

    # Compute metrics
    sharp_ratio = total_pnl.mean() / total_pnl.std() * np.sqrt(365 * 24) if total_pnl.std() != 0 else 0
    ar = total_pnl.mean() * 365 * 24  # Annualized return
    total_cumu = total_pnl.cumsum()
    mdd, recovery_period = calculate_drawdown_and_recovery(total_cumu)
    cr = ar / abs(mdd) if mdd != 0 else float('inf')

    # Print report
    print({
        "SR": sharp_ratio,
        "CR": cr,
        "MDD": mdd,
        "Recovery Period (days)": recovery_period,
        "AR": ar,
    })

    # Merge cumulative returns and plot
    merged_cumu = cumu_list[0]
    for other in cumu_list[1:]:
        merged_cumu = pd.merge(merged_cumu, other, on=['datetime'], how='inner')
    merged_returns_without_datetime = merged_cumu.drop(columns=['datetime'])

    # Sum the cumulative returns across all strategies
    total_cumulative_returns = merged_returns_without_datetime.sum(axis=1)
    fig, ax1 = plt.subplots(figsize=(20, 8))

    # Plot total cumulative returns and individual strategies on left y-axis
    line1, = ax1.plot(merged_cumu['datetime'], total_cumulative_returns, label='Total Cumulative Returns', color='red', linewidth=2)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Cumulative Return")
    ax1.set_title("Total Cumulative Returns and Close Price")
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Create second y-axis for close data (from the first file)
    ax2 = ax1.twinx()
    # Use the 'close' data from the first file
    merged_close = close_list[0]

    # Plot close data on right y-axis
    line2, = ax2.plot(merged_close['datetime'], merged_close[list(file_paths.keys())[0]], label='Close', color='blue', linewidth=2)
    ax2.set_ylabel("Close Price")
    ax2.legend(loc='upper right')
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True, prune='lower', nbins=12))  # Adjust number of ticks
    fig.autofmt_xdate(rotation=45)

    fig1, axa = plt.subplots(figsize=(20, 8))

    for col in merged_cumu.columns:
        if col != 'datetime':
            axa.plot(merged_cumu['datetime'], merged_cumu[col], label=col, linestyle='--')
    axa.set_xlabel("Time")
    axa.set_ylabel("Cumulative Return")
    axa.set_title("Cumulative Returns of Each Strategy and BTC Close")
    axa.legend(loc='upper left')
    axa.grid(True)

    # Create second y-axis for close data
    axb = axa.twinx()
    # Use the 'close' data from the first file
    merged_close = close_list[0]

    # Plot close data on right y-axis
    axb.plot(merged_close['datetime'], merged_close[list(file_paths.keys())[0]], label='Close', color='blue', linewidth=2)
    axa.xaxis.set_major_locator(MaxNLocator(integer=True, prune='lower', nbins=12))  # Adjust number of ticks
    fig1.autofmt_xdate(rotation=45)
    
    axb.set_ylabel("Close Price")
    axb.legend(loc='upper right')

    plt.tight_layout()
    plt.show()

def plot_bell_curve(df):
    data = df["data"]
    data = data.dropna() 

    # Fit a normal distribution to the data
    mu, std = stats.norm.fit(data)

    # Plot the bell curve (normal distribution)
    xmin, xmax = min(data), max(data)
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mu, std)  # Probability density function
    plt.plot(x, p, 'k', linewidth=2, label=f'Fit Normal Distribution\nMean: {mu:.2f}, Std Dev: {std:.2f}')

    # Add legend and labels
    plt.legend()
    plt.title('Bell Curve (Normal Distribution)')
    plt.xlabel('Value')
    plt.ylabel('Density')

    # Show the plot
    plt.show()

def plot_custom_correlation(file_path, output_file_prefix, target_series_func, max_lag=24):
    """Plot/save correlation of all numeric columns against a custom target series, including lag analysis."""
    
    # Extract output directory
    output_dir = os.path.dirname(output_file_prefix)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Load CSV
    try:
        df = pd.read_csv(file_path, usecols=lambda col: col not in ['Unnamed: 0'])
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return
    
    # Generate target series
    try:
        target_series = target_series_func(df.copy())  # prevent in-place modification
    except Exception as e:
        print(f"Error applying target_series_func: {e}")
        return

    target_name = 'target_custom'
    df.loc[:, target_name] = target_series  # ✅ safe assignment
    
    if target_name not in df.columns or not pd.api.types.is_numeric_dtype(df[target_name]):
        print("Target series is missing or not numeric.")
        return
    
    # Filter numeric columns
    numeric_cols = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col]) and col not in ['start_time', 'end_time', target_name]
    ]
    
    if len(numeric_cols) == 0:
        print("No numeric columns found to correlate with.")
        return

    methods = ['pearson', 'spearman', 'kendall']

    # --- Non-lagged correlation ---
    correlation_data = df[numeric_cols + [target_name]].dropna()
    for method in methods:
        corr_matrix = correlation_data.corr(method=method)
        if target_name not in corr_matrix.columns:
            print(f"{method.capitalize()}: Target missing in correlation matrix.")
            continue
        
        target_corr = corr_matrix[[target_name]].T
        sorted_corr = corr_matrix[[target_name]].rename(
            columns={target_name: f'correlation_with_{target_name}_{method}'}
        ).sort_values(by=f'correlation_with_{target_name}_{method}', ascending=False)

        plt.figure(figsize=(max(8, len(numeric_cols) * 0.8), 4))
        sns.heatmap(target_corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, annot_kws={"size": 8})
        plt.title(f"{method.capitalize()} Correlation: Numeric Columns vs {target_name} (No Lag)", fontsize=16)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.tight_layout()
        plt.show()

        output_file = os.path.join(output_file_prefix + f"_{method}_no_lag.csv")
        sorted_corr.to_csv(output_file, index=True)
        print(f"{method.capitalize()} correlation with {target_name} (no lag) saved to {output_file}")
    
    # --- Lagged correlation ---
    for lag in range(1, max_lag + 1):
        lag_col = f"{target_name}_lag_{lag}"
        df.loc[:, lag_col] = df[target_name].shift(-lag)  # ✅ safe assignment
        lag_data = df[numeric_cols + [lag_col]].dropna()
        if len(lag_data) < 2:
            print(f"Not enough data for lag {lag}")
            continue
        
        for method in methods:
            corr_matrix = lag_data.corr(method=method)
            if lag_col not in corr_matrix.columns:
                print(f"{method.capitalize()}: {lag_col} missing in correlation matrix.")
                continue
            
            target_corr = corr_matrix[[lag_col]].T
            sorted_corr = corr_matrix[[lag_col]].rename(
                columns={lag_col: f'correlation_with_{lag_col}_{method}'}
            ).sort_values(by=f'correlation_with_{lag_col}_{method}', ascending=False)

            plt.figure(figsize=(max(8, len(numeric_cols) * 0.8), 4))
            sns.heatmap(target_corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, annot_kws={"size": 8})
            plt.title(f"{method.capitalize()} Correlation: Numeric Columns vs {lag_col}", fontsize=16)
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.tight_layout()
            plt.show()

            output_file = os.path.join(output_file_prefix + f"_{method}_lag_{lag}.csv")
            sorted_corr.to_csv(output_file, index=True)
            print(f"{method.capitalize()} correlation with {lag_col} saved to {output_file}")
