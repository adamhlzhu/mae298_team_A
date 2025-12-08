import numpy as np
import pandas as pd
import json

def Engine_loglog_regression(X, y):
    """
    Fit a log regression fit: log(y) = beta0 + beta1*log(x1) + beta2*log(x2) + ...
    Returns beta, r2, rmse, rmse_log, mape, predictor, and std_err for confidence intervals.
    """
    X = np.asarray(X)
    y = np.asarray(y)

    logX = np.log(X)
    logy = np.log(y)

    # Constant intercept
    A = np.column_stack([np.ones(len(logy)), logX])

    beta, residuals, rank, s = np.linalg.lstsq(A, logy, rcond=None)
    pred = A @ beta

    ss_res = np.sum((logy - pred)**2)
    ss_tot = np.sum((logy - np.mean(logy))**2)
    r2 = 1.0 - ss_res/ss_tot
    
    # Calculate RMSE in log-space
    rmse_log = np.sqrt(np.mean((logy - pred)**2))
    
    # Calculate standard error in log space for confidence intervals
    n = len(logy)
    p = A.shape[1]  # number of parameters
    mse_log = ss_res / (n - p)
    std_err_log = np.sqrt(mse_log)
    
    # Calculate RMSE in original scale
    y_pred_original = np.exp(pred)
    
    # Manual verification of RMSE calculation
    residuals_original = y.flatten() - y_pred_original.flatten()
    rmse = np.sqrt(np.mean(residuals_original**2))
    
    # Calculate MAPE
    mape = np.mean(np.abs(residuals_original / y.flatten())) * 100

    def predictor(*x_cols):
        x_stack = np.column_stack(x_cols)
        logx_stack = np.log(x_stack)
        Anew = np.column_stack([np.ones(len(logx_stack)), logx_stack])
        return np.exp(Anew @ beta)

    return beta, r2, rmse, rmse_log, mape, std_err_log, predictor

    return beta, r2, rmse, rmse_log, mape, predictor


def fit_mass_regression(df, thrust_col='Takeoff Thrust [lbf]', mass_col='Dry Mass [lb]',
                        filters=None):
    """
    Mass regression: mass_eng = a * Thrust^b 

    filters: dict like {'BPR_min':3, 'T_min':15000, 'T_max':40000}
    """
    df = df.copy()

    if filters:
        if 'BPR_min' in filters:
            df = df[df['BPR'] >= filters['BPR_min']]
        if 'T_min' in filters:
            df = df[df[thrust_col] >= filters['T_min']]
        if 'T_max' in filters:
            df = df[df[thrust_col] <= filters['T_max']]
    df = df[[thrust_col, mass_col]].dropna()
    df = df[(df[thrust_col] > 0) & (df[mass_col] > 0)]

    Thrust = df[thrust_col].values
    mass = df[mass_col].values

    beta, r2, rmse, rmse_log, mape, std_err_log, pred = Engine_loglog_regression(Thrust.reshape(-1,1), mass.reshape(-1,1))

    a = float(np.exp(beta[0]))
    b = float(beta[1])

    info = {
        'a': a, 'b': b, 'r2': r2, 'rmse': rmse, 'rmse_log': rmse_log, 'mape': mape,
        'std_err_log': std_err_log,
        'formula': f"m = {a:.4g} * T^{b:.4g}"
    }
    return info, pred, r2, rmse, rmse_log, mape, std_err_log


def fit_tsfc_regression(df,
                        thrust_col='Takeoff Thrust [lbf]',
                        tsfc_col='SFC (h=0,M=0) [lb/lbf hr]',  # Sea level SFC
                        filters=None):
    """
    TSFC regression for sea level conditions:
      TSFC = a * Thrust ^ b
    filters: dict like {'BPR_min':3, 'T_min':15000, 'T_max':40000}
    """
    df = df.copy()

    if filters:
        if 'T_min' in filters:
            df = df[df[thrust_col] >= filters['T_min']]
        if 'T_max' in filters:
            df = df[df[thrust_col] <= filters['T_max']]

    cols = [thrust_col, tsfc_col]
    df = df[cols].dropna()
    df = df[(df[thrust_col] > 0) & (df[tsfc_col] > 0)]

    T    = df[thrust_col].values
    TSFC = df[tsfc_col].values

    beta, r2, rmse, rmse_log, mape, std_err_log, pred = Engine_loglog_regression(T.reshape(-1,1), TSFC)

    a = float(np.exp(beta[0]))
    b = float(beta[1])

    formula = (f"TSFC_SL = {a:.4g} * T^{b:.4g}")

    info = {'a': a, 'b': b,
            'r2': r2, 'rmse': rmse, 'rmse_log': rmse_log, 'mape': mape, 
            'std_err_log': std_err_log, 'formula': formula}

    return info, pred, r2, rmse, rmse_log, mape, std_err_log

def plot_thrust_vs_mass_actual_vs_predicted(df, mass_predictor, r2_value, rmse_value, rmse_log_value, mape_value, std_err_log,
                                         thrust_col='Takeoff Thrust [lbf]',
                                         mass_col='Dry Mass [lb]'):
    import matplotlib.pyplot as plt
    from scipy import stats

    df = df[[thrust_col, mass_col]].dropna()
    df = df[(df[thrust_col] > 0) & (df[mass_col] > 0)]

    Thrust = df[thrust_col].values
    actual_mass = df[mass_col].values
    
    # Sort thrust for smooth line plot
    sorted_indices = np.argsort(Thrust)
    Thrust_sorted = Thrust[sorted_indices]
    predicted_mass_sorted = mass_predictor(Thrust_sorted).flatten()
    
    # Calculate 95% confidence interval in log space
    # CI in log space: log(y) ± 1.96 * std_err
    # Then transform to original scale
    z_95 = 1.96
    log_lower = np.log(predicted_mass_sorted) - z_95 * std_err_log
    log_upper = np.log(predicted_mass_sorted) + z_95 * std_err_log
    ci_lower = np.exp(log_lower)
    ci_upper = np.exp(log_upper)

    plt.figure(figsize=(10,6))
    plt.scatter(Thrust, actual_mass, label='Actual Mass', color='blue', alpha=0.6)
    plt.plot(Thrust_sorted, predicted_mass_sorted, label='Predicted Mass', color='red', linewidth=2)
    plt.fill_between(Thrust_sorted, ci_lower, ci_upper, color='red', alpha=0.2, label='95% CI')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Takeoff Thrust [lbf]')
    plt.ylabel('Dry Mass [lb]')
    plt.title('Thrust vs Dry Mass: Actual vs Predicted')
    plt.legend(loc='lower right')
    plt.text(0.05, 0.95, f"$R^2$ = {r2_value:.3f}", 
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    plt.savefig(folder_path + 'thrust_vs_mass_regression.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_tsfc_actual_vs_predicted(df, tsfc_predictor, r2_value, rmse_value, rmse_log_value, mape_value, std_err_log,
                                   thrust_col='Takeoff Thrust [lbf]',
                                   tsfc_col='SFC (h=0,M=0) [lb/lbf hr]'):
    import matplotlib.pyplot as plt

    cols = [thrust_col, tsfc_col]
    df = df[cols].dropna()
    df = df[(df[thrust_col] > 0) & (df[tsfc_col] > 0)]

    Thrust = df[thrust_col].values
    actual_tsfc = df[tsfc_col].values
    predicted_tsfc = tsfc_predictor(Thrust).flatten()
    
    # Sort for smooth CI plot
    sorted_indices = np.argsort(Thrust)
    Thrust_sorted = Thrust[sorted_indices]
    predicted_tsfc_sorted = tsfc_predictor(Thrust_sorted).flatten()
    
    # Calculate 95% CI
    z_95 = 1.96
    log_lower = np.log(predicted_tsfc_sorted) - z_95 * std_err_log
    log_upper = np.log(predicted_tsfc_sorted) + z_95 * std_err_log
    ci_lower = np.exp(log_lower)
    ci_upper = np.exp(log_upper)

    plt.figure(figsize=(10,6))
    plt.scatter(actual_tsfc, predicted_tsfc, color='blue', alpha=0.6, label='Data Points')
    
    # Perfect prediction line
    min_val = min(actual_tsfc.min(), predicted_tsfc.min())
    max_val = max(actual_tsfc.max(), predicted_tsfc.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    
    plt.xlabel('Actual SFC at Sea Level [lb/lbf hr]')
    plt.ylabel('Predicted SFC at Sea Level [lb/lbf hr]')
    plt.title('SFC Regression: Actual vs Predicted')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.text(0.05, 0.95, f"$R^2$ = {r2_value:.3f}", 
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    plt.savefig(folder_path + 'sfc_regression.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    folder_path = "External_Subsystem/Propulsion/"
    df = pd.read_csv(folder_path + "TurboFans_Performance_database.csv", encoding="latin1")

    # 1. Mass regression
    mass_info, mass_predictor, mass_r2, mass_rmse, mass_rmse_log, mass_mape, mass_std_err_log = fit_mass_regression(df)
    print("\n" + "="*60)
    print("MASS REGRESSION RESULTS")
    print("="*60)
    print(mass_info)
    print(f"R² = {mass_r2:.4f}")
    print(f"RMSE = {mass_rmse:.2f} lb")
    print(f"RMSE (log scale) = {mass_rmse_log:.4f}")
    print(f"Std Error (log) = {mass_std_err_log:.4f}")
    print(f"MAPE = {mass_mape:.2f}%")
    print(f"\n95% CI width (approx): ±{mass_std_err_log*1.96:.4f} in log space")
    print(f"This translates to roughly ±{(np.exp(mass_std_err_log*1.96)-1)*100:.1f}% variation around prediction")
    plot_thrust_vs_mass_actual_vs_predicted(df, mass_predictor, mass_r2, mass_rmse, mass_rmse_log, mass_mape, mass_std_err_log)

    # 2. TSFC regression
    tsfc_info, tsfc_pred, tsfc_r2, tsfc_rmse, tsfc_rmse_log, tsfc_mape, tsfc_std_err_log = fit_tsfc_regression(
        df,
        filters = None
        # filters={'T_min': 15000, 'T_max': 40000} 
    )
    print("\n" + "="*60)
    print("SFC REGRESSION RESULTS (Sea Level)")
    print("="*60)
    print(tsfc_info)
    print(f"R² = {tsfc_r2:.4f}")
    print(f"RMSE = {tsfc_rmse:.4f} lb/lbf hr")
    print(f"RMSE (log scale) = {tsfc_rmse_log:.4f}")
    print(f"MAPE = {tsfc_mape:.2f}%")
    plot_tsfc_actual_vs_predicted(df, tsfc_pred, tsfc_r2, tsfc_rmse, tsfc_rmse_log, tsfc_mape, tsfc_std_err_log)

    coeffs = {"mass": mass_info, "tsfc": tsfc_info}

    with open(folder_path + "engine_regression_coeffs.json", "w") as f:
        json.dump(coeffs, f, indent=2)

    print("\n" + "="*60)
    print("Coefficients saved to engine_regression_coeffs.json")
    print("="*60)