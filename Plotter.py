import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import os

def file_loader(file_path):
    """Load data from a CSV file into a pandas DataFrame."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    df = pd.read_csv(file_path)
    # Cleaning the data with forward fill for missing values
    # Velocity column forward fill
    if 'velocity (knot)' in df.columns:
        df['velocity (knot)'].fillna(method='ffill', inplace=True)

    # Mach column forward fill
    if 'mach (unitless)' in df.columns:
        df['mach (unitless)'].fillna(method='ffill', inplace=True)

    # Altitude column forward fill
    if 'altitude (ft)' in df.columns:
        df['altitude (ft)'].fillna(method='ffill', inplace=True)
    
    # Add calculated fuel flow column
    # In CSV only have mass column, so we calculate fuel flow as negative change in mass over time
    initial_weight = df['mass (lbm)'].iloc[0]
    final_weight = df['mass (lbm)'].iloc[-1]
    fuel_burned = initial_weight - final_weight
    print(f"file {file_path}Total Fuel Burned: {fuel_burned} lbm")
    fuel_burn_column = df['mass (lbm)'] - initial_weight
    df['fuel_burned (lbm)'] = -fuel_burn_column
    return df

def mission_plotter_multi(dfs, labels=None, styles=None, save_folder_path=None, engine_counts=None):
    """
    Plot velocity, altitude, and fuel burn vs time for one or more DataFrames.

    Parameters
    ----------
    dfs : list of pandas.DataFrame
        Each DataFrame must contain:
        'time (s)', 'velocity (knot)', 'altitude (ft)', 'fuel_burned (lbm)'.
        The first DF is treated as the baseline (black solid line).
    labels : list of str, optional
        Legend labels for each DataFrame. If None, generic labels are used.
    styles : list of dict, optional
    """
    if not isinstance(dfs, (list, tuple)):
        dfs = [dfs]

    n = len(dfs)
    if n == 0:
        raise ValueError("No DataFrames provided.")

    # Labels
    if labels is None:
        labels = [f"case {i+1}" for i in range(n)]
    elif len(labels) != n:
        raise ValueError("Length of labels must match number of DataFrames.")

    # Styles for non-baseline curves
    if styles is not None and len(styles) < n - 1:
        raise ValueError("styles must have length at least len(dfs) - 1.")

    required_cols = [
        'time (s)',
        'velocity (knot)',
        'altitude (ft)',
        'fuel_burned (lbm)',
    ]

    # Check columns in each df
    for i, df in enumerate(dfs):
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(
                f"DataFrame {i} is missing columns: {missing}"
            )

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 8))
    # Set transparent background
    fig.patch.set_alpha(0.0)


    def _plot_on_axis(ax, col, ylabel):
        baseline_df = dfs[0]
        ax.plot(
            baseline_df['time (s)'],
            baseline_df[col],
            label=labels[0],
            color="black",
            linestyle="-",
        )

        # Others
        for idx in range(1, n):
            df = dfs[idx]
            style = styles[idx - 1] if styles is not None else {}
            ax.plot(
                df['time (s)'],
                df[col],
                label=labels[idx],
                **style,
            )

        ax.set_ylabel(ylabel)
        ax.grid(False)
        ax.set_facecolor('none')  # Transparent axes background

    # Velocity subplot
    _plot_on_axis(axes[0], 'velocity (knot)', 'Velocity (knot)')
    axes[0].set_title('Mission Profile')

    # Altitude subplot
    _plot_on_axis(axes[1], 'altitude (ft)', 'Altitude (ft)')

    # Fuel burned subplot
    _plot_on_axis(axes[2], 'fuel_burned (lbm)', 'Fuel Burned (lbm)')
    axes[2].set_xlabel('Time (s)')

    # One legend (they're identical across subplots)
    # Move legend outside to the right
    axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), framealpha=0.9)

    fig.tight_layout(rect=[0, 0, 0.85, 1])  # Make room for legend

    n_cases = len(labels)
    if engine_counts is not None:
        filename = f'mission_profile_comparison_{n_cases}_cases_engine_{engine_counts}.png'
    else:
        filename = f'mission_profile_comparison_{n_cases}_cases.png'
    
    if save_folder_path is not None:
        save_path = os.path.join(save_folder_path, filename)
        fig.savefig(save_path, dpi=600, transparent=True, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()



if __name__ == "__main__":
    baseline_file_path = 'BWB_Baseline_out/reports/mission_timeseries_data.csv'
    Mission_Propulsion_file_path = 'BWB_Propulsion_Mission_only_out/reports/mission_timeseries_data.csv' 
    Mission_only_file_path = 'BWB_Mission_only_out/reports/mission_timeseries_data.csv'
    Mission_Structure_file_path = 'BWB_Mission_Structure_out/reports/mission_timeseries_data.csv'
    Mission_Structure_Propulsion_file_path = 'BWB_Mission_Structure_Propulsion_out/reports/mission_timeseries_data.csv'
    Structure_only_file_path = 'BWB_Structure_only_out/reports/mission_timeseries_data.csv'
    Propulsion_only_file_path = 'BWB_Propulsion_only_out/reports/mission_timeseries_data.csv'

    # Engine:
    Combined_all_with_2_engine_file_path = Mission_Structure_Propulsion_file_path
    Combined_all_with_3_engine_file_path = 'BWB_Combined_all_3_engine_out/reports/mission_timeseries_data.csv'
    Combined_all_with_4_engine_file_path = 'BWB_Combined_all_4_engine_out/reports/mission_timeseries_data.csv'
    Combined_all_with_5_engine_file_path = 'BWB_Combined_all_5_engine_out/reports/mission_timeseries_data.csv'
    Combined_all_with_6_engine_file_path = 'BWB_Combined_all_6_engine_out/reports/mission_timeseries_data.csv'

    plot_save_folder = 'Mission_results_plots'
    if not os.path.exists(plot_save_folder):
        os.makedirs(plot_save_folder)  
    try:
        # If you want each comparison plot separately, comment the following lines one by one:
        baseline_df = file_loader(baseline_file_path)
        Mission_only_df = file_loader(Mission_only_file_path)
        Structure_only_df = file_loader(Structure_only_file_path)
        Propulsion_only_df = file_loader(Propulsion_only_file_path)
        Mission_Propulsion_df = file_loader(Mission_Propulsion_file_path)
        Mission_Structure_df = file_loader(Mission_Structure_file_path)
        Mission_Structure_Propulsion_df = file_loader(Mission_Structure_Propulsion_file_path)


        dfs = [baseline_df, 
               Mission_only_df, 
               Structure_only_df,
               Propulsion_only_df, 
               # Mission_Propulsion_df, 
               # Mission_Structure_df, 
               Mission_Structure_Propulsion_df
               ]
        labels = ["Baseline", 
                  "Mission only", 
                  "Structure only", 
                  "Propulsion only",
                  # "Mission + Propulsion", 
                  # "Mission + Structure", 
                  "Mission + Structure + Propulsion"
                  ]
        # The first style is always for Baseline, which defined as black solid line in the function code, so we only need styles for the others but not the first one
        styles = [
                {"color": "#1b9e77", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # Mission only
                {"color": "#e6ab02", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # Structure only
                {"color": "#7570b3", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # Propulsion only
                # {"color": "#d95f02", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # Mission + Propulsion
                # {"color": "#7570b3", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # Mission + Structure
                {"color": "#e7298a", "linestyle": "-", "linewidth": 2.0, "alpha": 1},  # Mission + Structure + Propulsion
            ]
        mission_plotter_multi(dfs, labels=labels, styles=styles, save_folder_path=plot_save_folder, engine_counts=None)

        # Engine:
        engine_count = 6
        Combined_all_with_2_engine_df = file_loader(Combined_all_with_2_engine_file_path)
        Combined_all_with_3_engine_df = file_loader(Combined_all_with_3_engine_file_path)
        Combined_all_with_4_engine_df = file_loader(Combined_all_with_4_engine_file_path)
        Combined_all_with_5_engine_df = file_loader(Combined_all_with_5_engine_file_path)
        Combined_all_with_6_engine_df = file_loader(Combined_all_with_6_engine_file_path)
        
        dfs_engine = [baseline_df, Combined_all_with_2_engine_df, Combined_all_with_3_engine_df, Combined_all_with_4_engine_df,
                      Combined_all_with_5_engine_df, Combined_all_with_6_engine_df]
        labels_engine = ["Baseline", "2 engines", "3 engines", "4 engines", "5 engines", "6 engines"]
        styles_engine = [
                {"color": "#1b9e77", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # 2 engines
                {"color": "#d95f02", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # 3 engines
                {"color": "#7570b3", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # 4 engines
                {"color": "#e7298a", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # 5 engines
                {"color": "#66a61e", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},  # 6 engines
            ]
        mission_plotter_multi(dfs_engine, labels=labels_engine, styles=styles_engine, save_folder_path=plot_save_folder, engine_counts=engine_count)
    except Exception as e:
        print(f"An error occurred: {e}")
