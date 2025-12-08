import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import os
import json
import re

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

def mission_plotter_multi(dfs, labels=None, styles=None, save_folder_path=None, save_filename=None):
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
    save_filename : str, optional
        Custom filename for saving. If None, auto-generates name.
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
    axes[0].set_xlim(0, 3500)  # Time range based on typical mission duration
    axes[0].set_ylim(0, 550)   # Velocity range in knots

    # Altitude subplot
    _plot_on_axis(axes[1], 'altitude (ft)', 'Altitude (ft)')
    axes[1].set_xlim(0, 3500)
    axes[1].set_ylim(0, 45000)  # Altitude range in feet

    # Fuel burned subplot
    _plot_on_axis(axes[2], 'fuel_burned (lbm)', 'Fuel Burned (lbm)')
    axes[2].set_xlabel('Time (s)')
    axes[2].set_xlim(0, 3500)
    axes[2].set_ylim(0, 3500)  # Fuel burn range in lbm

    # One legend (they're identical across subplots)
    # Move legend outside to the right
    axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), framealpha=0.9)

    fig.tight_layout(rect=[0, 0, 0.85, 1])  # Make room for legend

    # Determine filename
    if save_filename:
        filename = save_filename
    else:
        n_cases = len(labels)
        filename = f'mission_profile_comparison_{n_cases}_cases.png'
    
    if save_folder_path is not None:
        save_path = os.path.join(save_folder_path, filename)
        fig.savefig(save_path, dpi=600, transparent=True, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close(fig)


def extract_configuration_summary(config_paths, config_names, save_path=None):
    """
    Extract summary information from multiple configuration reports.
    
    Parameters
    ----------
    config_paths : list of str
        List of paths to the output directories (e.g., 'BWB_Baseline_out/reports/')
    config_names : list of str
        Names for each configuration (e.g., 'Baseline', '2 engines', etc.)
    save_path : str, optional
        Path to save the summary CSV. If None, returns DataFrame without saving.
        
    Returns
    -------
    pd.DataFrame
        Summary dataframe with configuration information
    """
    summary_data = []
    
    for config_path, config_name in zip(config_paths, config_names):
        try:
            config_info = {'Configuration': config_name}
            
            # Read status.json for iteration and optimization info
            status_file = os.path.join(config_path, 'status.json')
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    config_info['Iterations'] = status.get('Number of driver iterations', 'N/A')
                    config_info['Model Evals'] = status.get('Number of model evals', 'N/A')
                    config_info['Exit Status'] = status.get('Exit status', 'N/A')
                    config_info['Runtime'] = status.get('Wall clock run time', 'N/A')
            
            # Read mission_summary.md for fuel burn and other mission metrics
            summary_file = os.path.join(config_path, 'mission_summary.md')
            if os.path.exists(summary_file):
                with open(summary_file, 'r') as f:
                    content = f.read()
                    
                    # Extract Total Fuel Burn
                    fuel_match = re.search(r'\| Total Fuel Burn \| ([\d.]+(?:e[+-]?\d+)?)', content)
                    if fuel_match:
                        config_info['Fuel Burn (lbm)'] = float(fuel_match.group(1))
                    
                    # Extract Total Time
                    time_match = re.search(r'\| Total Time \| ([\d.]+(?:e[+-]?\d+)?)', content)
                    if time_match:
                        config_info['Total Time (min)'] = float(time_match.group(1))
                    
                    # Extract Total Ground Distance
                    dist_match = re.search(r'\| Total Ground Distance \| ([\d.]+(?:e[+-]?\d+)?)', content)
                    if dist_match:
                        config_info['Distance (nmi)'] = float(dist_match.group(1))
            
            # Read mission_timeseries_data.csv for cruise conditions and MTOW
            timeseries_file = os.path.join(config_path, 'mission_timeseries_data.csv')
            if os.path.exists(timeseries_file):
                df = pd.read_csv(timeseries_file)
                
                # MTOW (initial mass)
                if 'mass (lbm)' in df.columns:
                    mtow = df['mass (lbm)'].iloc[0]
                    config_info['MTOW (lbm)'] = mtow
                    
                    # Final mass (landing weight = MTOW - Fuel Burned)
                    final_mass = df['mass (lbm)'].iloc[-1]
                    config_info['Landing Weight (lbm)'] = final_mass
                
                # Cruise Mach (find max mach during cruise)
                if 'mach (unitless)' in df.columns:
                    cruise_mach = df['mach (unitless)'].max()
                    config_info['Cruise Mach'] = cruise_mach
                    # Average cruise mach (where altitude is near max)
                    if 'altitude (ft)' in df.columns:
                        max_alt = df['altitude (ft)'].max()
                        cruise_data = df[df['altitude (ft)'] > max_alt * 0.95]
                        if len(cruise_data) > 0 and 'mach (unitless)' in cruise_data.columns:
                            config_info['Avg Cruise Mach'] = cruise_data['mach (unitless)'].mean()
                
                # Cruise Altitude
                if 'altitude (ft)' in df.columns:
                    cruise_alt = df['altitude (ft)'].max()
                    config_info['Cruise Altitude (ft)'] = cruise_alt
                
                # Max thrust (total)
                if 'thrust_net_total (lbf)' in df.columns:
                    max_thrust = df['thrust_net_total (lbf)'].max()
                    config_info['Max Total Thrust (lbf)'] = max_thrust
                    # Average cruise thrust
                    if 'altitude (ft)' in df.columns:
                        max_alt = df['altitude (ft)'].max()
                        cruise_data = df[df['altitude (ft)'] > max_alt * 0.95]
                        if len(cruise_data) > 0:
                            config_info['Avg Cruise Thrust (lbf)'] = cruise_data['thrust_net_total (lbf)'].mean()
                
                # Aerodynamic efficiency metrics
                if 'CL (unitless)' in df.columns and 'CD (unitless)' in df.columns:
                    # Filter out zeros to avoid division errors
                    valid_data = df[(df['CD (unitless)'] > 0) & (df['CL (unitless)'] > 0)]
                    if len(valid_data) > 0:
                        ld_ratio = valid_data['CL (unitless)'] / valid_data['CD (unitless)']
                        config_info['Max L/D'] = ld_ratio.max()
                        # Cruise L/D
                        if 'altitude (ft)' in df.columns:
                            max_alt = df['altitude (ft)'].max()
                            cruise_data = valid_data[valid_data['altitude (ft)'] > max_alt * 0.95]
                            if len(cruise_data) > 0:
                                cruise_ld = cruise_data['CL (unitless)'] / cruise_data['CD (unitless)']
                                config_info['Cruise L/D'] = cruise_ld.mean()
                
                # Fuel efficiency metrics
                if 'Fuel Burn (lbm)' in config_info and 'Distance (nmi)' in config_info:
                    if config_info['Distance (nmi)'] > 0:
                        config_info['Fuel Efficiency (lbm/nmi)'] = config_info['Fuel Burn (lbm)'] / config_info['Distance (nmi)']
                
                # Specific range (nmi/lbm of fuel)
                if 'Distance (nmi)' in config_info and 'Fuel Burn (lbm)' in config_info:
                    if config_info['Fuel Burn (lbm)'] > 0:
                        config_info['Specific Range (nmi/lbm)'] = config_info['Distance (nmi)'] / config_info['Fuel Burn (lbm)']
                
                # Fuel flow rate
                if 'fuel_flow_rate_negative_total (lbm/s)' in df.columns:
                    # Get cruise fuel flow
                    if 'altitude (ft)' in df.columns:
                        max_alt = df['altitude (ft)'].max()
                        cruise_data = df[df['altitude (ft)'] > max_alt * 0.95]
                        if len(cruise_data) > 0:
                            config_info['Cruise Fuel Flow (lbm/s)'] = abs(cruise_data['fuel_flow_rate_negative_total (lbm/s)'].mean())
            
            # Try to extract engine count from configuration name or path
            engine_count = None
            engine_match = re.search(r'(\d+)\s*engine', config_name, re.IGNORECASE)
            if engine_match:
                engine_count = int(engine_match.group(1))
            else:
                # Default to 2 engines for all subsystem configurations
                engine_count = 2
            
            if engine_count:
                config_info['Number of Engines'] = engine_count
                if 'Max Total Thrust (lbf)' in config_info:
                    thrust_per_engine = config_info['Max Total Thrust (lbf)'] / engine_count
                    config_info['Thrust per Engine (lbf)'] = thrust_per_engine
                    
                    # Determine if this uses regression-based or fixed engine mass
                    # Regression: Combined, Mission+Structure+Propulsion, Propulsion only use m = 0.2949 * T^0.9577
                    # Fixed: Baseline, Mission only, Structure only use INGASP.WENG = 6130 lbm (per engine)
                    uses_regression = (
                        'Combined' in config_name or 
                        ('Propulsion' in config_name and 'Structure' in config_name) or
                        config_name == 'Propulsion only'
                    )
                    
                    if uses_regression:
                        # Regression-based engine mass (varies with thrust)
                        estimated_engine_mass = 0.2949 * (thrust_per_engine ** 0.9577)
                        config_info['Engine Dry Mass (lb)'] = estimated_engine_mass
                        config_info['Total Engine Mass (lb)'] = estimated_engine_mass * engine_count
                    else:
                        # Fixed engine mass from GASP input: INGASP.WENG = 6130 lbm per single engine
                        config_info['Engine Dry Mass (lb)'] = 6130.0
                        config_info['Total Engine Mass (lb)'] = 6130.0 * engine_count
            
            summary_data.append(config_info)
            
        except Exception as e:
            print(f"Error processing {config_name}: {e}")
            summary_data.append({'Configuration': config_name, 'Error': str(e)})
    
    # Create DataFrame
    df_summary = pd.DataFrame(summary_data)
    
    # Reorder columns for better readability
    preferred_order = [
        'Configuration', 'Exit Status', 'Iterations', 'Runtime', 'Model Evals',
        # Engine/Propulsion
        'Number of Engines', 'Thrust per Engine (lbf)', 'Engine Dry Mass (lb)', 'Total Engine Mass (lb)', 
        'Max Total Thrust (lbf)', 'Avg Cruise Thrust (lbf)',
        # Weight
        'MTOW (lbm)', 'Landing Weight (lbm)', 'Fuel Burn (lbm)',
        # Performance
        'Distance (nmi)', 'Total Time (min)', 'Cruise Mach', 'Avg Cruise Mach', 'Cruise Altitude (ft)',
        # Efficiency
        'Max L/D', 'Cruise L/D', 'Fuel Efficiency (lbm/nmi)', 'Specific Range (nmi/lbm)', 'Cruise Fuel Flow (lbm/s)'
    ]
    
    # Reorder columns that exist
    existing_cols = [col for col in preferred_order if col in df_summary.columns]
    other_cols = [col for col in df_summary.columns if col not in existing_cols]
    df_summary = df_summary[existing_cols + other_cols]
    
    # Save if path provided
    if save_path:
        df_summary.to_csv(save_path, index=False)
        print(f"Configuration summary saved to {save_path}")
    
    return df_summary


if __name__ == "__main__":
    baseline_file_path = 'BWB_Baseline_out/reports/mission_timeseries_data.csv'
    # Mission_Propulsion_file_path = 'BWB_Propulsion_Mission_only_out/reports/mission_timeseries_data.csv' 
    Mission_only_file_path = 'BWB_Mission_only_out/reports/mission_timeseries_data.csv'
    # Mission_Structure_file_path = 'BWB_Mission_Structure_out/reports/mission_timeseries_data.csv'
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
        print("\n" + "="*60)
        print("Loading all configuration data...")
        print("="*60)
        
        # Load all data files
        baseline_df = file_loader(baseline_file_path)
        Mission_only_df = file_loader(Mission_only_file_path)
        Structure_only_df = file_loader(Structure_only_file_path)
        Propulsion_only_df = file_loader(Propulsion_only_file_path)
        Mission_Structure_Propulsion_df = file_loader(Mission_Structure_Propulsion_file_path)
        
        Combined_all_with_2_engine_df = file_loader(Combined_all_with_2_engine_file_path)
        Combined_all_with_3_engine_df = file_loader(Combined_all_with_3_engine_file_path)
        Combined_all_with_4_engine_df = file_loader(Combined_all_with_4_engine_file_path)
        Combined_all_with_5_engine_df = file_loader(Combined_all_with_5_engine_file_path)
        Combined_all_with_6_engine_df = file_loader(Combined_all_with_6_engine_file_path)
        
        print("\n" + "="*60)
        print("Generating mission profile plots...")
        print("="*60)
        
        # Plot 1: Propulsion only
        print("\n1. Plotting Propulsion only...")
        mission_plotter_multi(
            [baseline_df, Propulsion_only_df],
            labels=["Baseline", "Propulsion only"],
            styles=[{"color": "#7570b3", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85}],
            save_folder_path=plot_save_folder,
            save_filename="propulsion_only_comparison.png"
        )
        
        # Plot 2: Structure only
        print("2. Plotting Structure only...")
        mission_plotter_multi(
            [baseline_df, Structure_only_df],
            labels=["Baseline", "Structure only"],
            styles=[{"color": "#e6ab02", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85}],
            save_folder_path=plot_save_folder,
            save_filename="structure_only_comparison.png"
        )
        
        # Plot 3: Mission only
        print("3. Plotting Mission only...")
        mission_plotter_multi(
            [baseline_df, Mission_only_df],
            labels=["Baseline", "Mission only"],
            styles=[{"color": "#1b9e77", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85}],
            save_folder_path=plot_save_folder,
            save_filename="mission_only_comparison.png"
        )
        
        # Plot 4: Everything together (all subsystems)
        print("4. Plotting Everything together...")
        mission_plotter_multi(
            [baseline_df, Mission_Structure_Propulsion_df],
            labels=["Baseline", "Mission + Structure + Propulsion"],
            styles=[{"color": "#e7298a", "linestyle": "-", "linewidth": 2.0, "alpha": 1}],
            save_folder_path=plot_save_folder,
            save_filename="combined_all_subsystems.png"
        )
        
        # Plot 5: Engine count sweep
        print("5. Plotting Engine count sweep...")
        mission_plotter_multi(
            [baseline_df, Combined_all_with_2_engine_df, Combined_all_with_3_engine_df, 
             Combined_all_with_4_engine_df, Combined_all_with_5_engine_df, Combined_all_with_6_engine_df],
            labels=["Baseline (2 engines)", "Combined (2 engines)", "Combined (3 engines)", 
                   "Combined (4 engines)", "Combined (5 engines)", "Combined (6 engines)"],
            styles=[
                {"color": "#1b9e77", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},
                {"color": "#d95f02", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},
                {"color": "#7570b3", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},
                {"color": "#e7298a", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},
                {"color": "#66a61e", "linestyle": "--", "linewidth": 2.0, "alpha": 0.85},
            ],
            save_folder_path=plot_save_folder,
            save_filename="engine_count_sweep.png"
        )
        
        # Generate configuration summary
        print("\n" + "="*60)
        print("Generating Configuration Summary...")
        print("="*60)
        
        # Configuration paths for subsystem comparison
        config_paths_subsys = [
            'BWB_Baseline_out/reports/',
            'BWB_Mission_only_out/reports/',
            'BWB_Propulsion_only_out/reports/',
            'BWB_Structure_only_out/reports/',
            'BWB_Mission_Structure_Propulsion_out/reports/'
        ]
        
        config_names_subsys = [
            "Baseline",
            "Mission only",
            "Propulsion only",
            "Structure only",
            "Mission + Structure + Propulsion"
        ]
        
        summary_subsys = extract_configuration_summary(
            config_paths_subsys, 
            config_names_subsys,
            save_path=os.path.join(plot_save_folder, 'subsystem_configuration_summary.csv')
        )
        print("\nSubsystem Configuration Summary:")
        print(summary_subsys.to_string(index=False))
        
        # Configuration paths for engine count comparison
        config_paths_engine = [
            'BWB_Baseline_out/reports/',
            'BWB_Mission_Structure_Propulsion_out/reports/',
            'BWB_Combined_all_3_engine_out/reports/',
            'BWB_Combined_all_4_engine_out/reports/',
            'BWB_Combined_all_5_engine_out/reports/',
            'BWB_Combined_all_6_engine_out/reports/'
        ]
        
        config_names_engine = [
            "Combined (2 engines)",
            "Combined (2 engines)",
            "Combined (3 engines)",
            "Combined (4 engines)",
            "Combined (5 engines)",
            "Combined (6 engines)"
        ]
        
        summary_engine = extract_configuration_summary(
            config_paths_engine,
            config_names_engine,
            save_path=os.path.join(plot_save_folder, 'engine_configuration_summary.csv')
        )
        print("\n\nEngine Configuration Summary:")
        print(summary_engine.to_string(index=False))
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

