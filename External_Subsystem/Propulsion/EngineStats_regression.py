import numpy as np
import pandas as pd
import json

def Engine_loglog_regression(X, y):
    """
    Fit a log regression fit: log(y) = beta0 + beta1*log(x1) + beta2*log(x2) + ...
    Returns beta, r2, and a predictor function.
    """
    X = np.asarray(X)
    y = np.asarray(y)

    logX = np.log(X)
    logy = np.log(y)

    # Constant intercept
    A = np.column_stack([np.ones(len(logy)), logX])

    beta, *_ = np.linalg.lstsq(A, logy, rcond=None)
    pred = A @ beta

    ss_res = np.sum((logy - pred)**2)
    ss_tot = np.sum((logy - np.mean(logy))**2)
    r2 = 1.0 - ss_res/ss_tot

    def predictor(*x_cols):
        x_stack = np.column_stack(x_cols)
        logx_stack = np.log(x_stack)
        Anew = np.column_stack([np.ones(len(logx_stack)), logx_stack])
        return np.exp(Anew @ beta)

    return beta, r2, predictor


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

    beta, r2, pred = Engine_loglog_regression(Thrust.reshape(-1,1), mass.reshape(-1,1))

    a = float(np.exp(beta[0]))
    b = float(beta[1])

    info = {
        'a': a, 'b': b, 'r2': r2,
        'formula': f"m = {a:.4g} * T^{b:.4g}"
    }
    return info, pred


def fit_tsfc_regression(df,
                        thrust_col='Takeoff Thrust [lbf]',
                        tsfc_col='SFC (Cruise) [lb/lbf hr]',
                        bpr_col='BPR', # Baypass ratio Higher means more efficient
                        opr_col='OPR_ Sea lvl', # P_exit / P_0 Higher means more compression which is more efficient
                        mach_col='Mach Number',
                        h_col='Cruise Altitude (h) [ft]',
                        filters=None):
    """
    TSFC regression (better):
      TSFC = a * Thrust ^ b * BPR ^ c * OPR ^ d * Mach_number ^ e * Cruise_height ^ f
    filters: dict like {'BPR_min':3, 'T_min':15000, 'T_max':40000}
    """
    df = df.copy()

    if filters:
        if 'BPR_min' in filters:
            df = df[df[bpr_col] >= filters['BPR_min']]
        if 'T_min' in filters:
            df = df[df[thrust_col] >= filters['T_min']]
        if 'T_max' in filters:
            df = df[df[thrust_col] <= filters['T_max']]

    cols = [thrust_col, tsfc_col, bpr_col, opr_col, mach_col, h_col]
    df = df[cols].dropna()
    df = df[(df[thrust_col] > 0) & (df[tsfc_col] > 0) &
            (df[bpr_col] > 0) & (df[opr_col] > 0) &
            (df[mach_col] > 0) & (df[h_col] > 0)]

    T    = df[thrust_col].values
    TSFC = df[tsfc_col].values
    BPR  = df[bpr_col].values
    OPR  = df[opr_col].values
    M    = df[mach_col].values
    h    = df[h_col].values

    X = np.column_stack([T, BPR, OPR, M, h])
    beta, r2, pred = Engine_loglog_regression(X, TSFC)

    a = float(np.exp(beta[0]))
    b, c, dcoef, ecoef, fcoef = map(float, beta[1:])

    formula = (f"TSFC = {a:.4g} * T^{b:.4g} * BPR^{c:.4g} * "
               f"OPR^{dcoef:.4g} * Mach^{ecoef:.4g} * h^{fcoef:.4g}")

    info = {'a': a, 'b': b, 'c': c, 'd': dcoef, 'e': ecoef, 'f': fcoef,
            'r2': r2, 'formula': formula}

    return info, pred

def plot_thrust_vs_mass_actual_vs_predicted(df, mass_predictor,
                                         thrust_col='Takeoff Thrust [lbf]',
                                         mass_col='Dry Mass [lb]'):
    import matplotlib.pyplot as plt

    df = df[[thrust_col, mass_col]].dropna()
    df = df[(df[thrust_col] > 0) & (df[mass_col] > 0)]

    Thrust = df[thrust_col].values
    actual_mass = df[mass_col].values
    predicted_mass = mass_predictor(Thrust)

    plt.figure(figsize=(10,6))
    plt.scatter(Thrust, actual_mass, label='Actual Mass', color='blue', alpha=0.6)
    plt.scatter(Thrust, predicted_mass, label='Predicted Mass', color='red', alpha=0.6)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Takeoff Thrust [lbf]')
    plt.ylabel('Dry Mass [lb]')
    plt.title('Thrust vs Dry Mass: Actual vs Predicted')
    plt.legend()
    plt.grid(True, which="both", ls="-")
    plt.show()

if __name__ == "__main__":
    folder_path = "Subsystem\Propulsion\\"
    df = pd.read_csv(folder_path + "TurboFans_Performance_database.csv", encoding="latin1")

    # 1. Mass regression
    mass_info, mass_predictor = fit_mass_regression(df)
    print(mass_info)
    # plot_thrust_vs_mass_actual_vs_predicted(df, mass_predictor)

    # 2. TSFC regression
    tsfc_info, tsfc_pred = fit_tsfc_regression(
        df,
        filters = None
        # filters={'T_min': 15000, 'T_max': 40000} 
    )
    print(tsfc_info)

    coeffs = {"mass": mass_info, "tsfc": tsfc_info}

    with open(folder_path + "engine_regression_coeffs.json", "w") as f:
        json.dump(coeffs, f, indent=2)


    print(coeffs)