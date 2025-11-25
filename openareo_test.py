from openaerostruct.meshing.mesh_generator import generate_mesh
from openaerostruct.geometry.geometry_group import Geometry
from openaerostruct.aerodynamics.aero_groups import AeroPoint
from openaerostruct.structures.struct_groups import SpatialBeamAlone
from aviary.variable_info.variables import Mission

import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt

import aviary.api as av
import openmdao.api as om

from dof_geometry import phase_info
from oasstruct_geo import OASStructGroup

def build_coupled_problem():
    avi_prob = av.AviaryProblem()

    avi_prob.load_inputs("GASP_Geometry.csv", phase_info)
    avi_prob.check_and_preprocess_inputs()
    avi_prob.build_model()

    avi_prob.add_driver("IPOPT", max_iter=100)

    avi_prob.add_design_variables()
    avi_prob.model.add_design_var("aircraft:wing:aspect_ratio", lower=7.0, upper=14.0)
    avi_prob.model.add_design_var("aircraft:wing:taper_ratio", lower=0.25, upper=0.45)

    aluminum = {
        "E": 70e9,
        "G": 27e9,
        "yield": 300e6,
        "mrho": 2800.0,
    }

    avi_prob.model.add_subsystem(
        "oas_struct",
        OASStructGroup(material=aluminum),
        promotes_outputs=["structural_mass", "failure"],
    )

    # ---- Structural DV is now thickness_cp (vector of length 3) ----
    avi_prob.model.add_design_var("oas_struct.thickness_cp", lower=0.01, upper=0.5)

    avi_prob.model.add_constraint("failure", upper=0.0)
    avi_prob.model.add_objective("structural_mass", scaler=1e-5)

    avi_prob.setup()
    return avi_prob

if __name__ == "__main__":
    prob = build_coupled_problem()
    prob.run_aviary_problem()

    print("Structural mass (OAS):", prob.get_val("structural_mass"))
    print("Max failure:", prob.get_val("failure").max())
    print("Optimized thickness_cp:", prob.get_val("oas_struct.thickness_cp"))

    
    ar = prob.get_val("aircraft:wing:aspect_ratio")
    taper = prob.get_val("aircraft:wing:taper_ratio")
    fuel_burned = prob.get_val(av.Mission.Summary.FUEL_BURNED)
    print("Final aspect ratio:", ar)
    print("Final taper ratio:", taper)
    print("Fuel burned", fuel_burned)


import numpy as np
import openmdao.api as om
from oasstruct_geo import OASStructGroup  # the version with AR/taper options

aluminum = {"E": 70e9, "G": 27e9, "yield": 300e6, "mrho": 2800.0}

def run_struct_sizing(AR, taper):
    """Run OAS structural optimization for a single (AR, taper)."""
    prob = om.Problem()
    prob.model = OASStructGroup(material=aluminum, AR=AR, taper=taper)

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["disp"] = False

    prob.model.add_design_var("thickness_cp", lower=0.01, upper=0.5)
    prob.model.add_constraint("failure", upper=0.0)
    prob.model.add_objective("structural_mass", scaler=1e-5)

    prob.setup()
    prob.run_driver()

    struct_mass = float(prob.get_val("structural_mass"))
    max_failure = float(prob.get_val("failure").max())
    th_cp = prob.get_val("thickness_cp").copy()
    return struct_mass, max_failure, th_cp



if __name__ == "__main__":



    # --- Sensitivity 1: mass vs taper ---
    ar_fixed = 10.0
    taper_vals = np.linspace(0.25, 0.45, 7)

    masses2 = []
    failures2 = []

    for taper in taper_vals:
        print(f"Running taper={taper:.2f}, AR={ar_fixed:.2f}")
        m, f, th = run_struct_sizing(ar, taper)
        masses2.append(m)
        failures2.append(f)

    # --- Plot ---
    plt.figure()
    plt.plot(taper_vals, masses2, marker="o", color="green")
    plt.xlabel("Taper Ratio")
    plt.ylabel("Structural Mass [kg]")
    plt.title(f"Sensitivity: Structural Mass vs Taper (AR={ar_fixed})")
    plt.grid(True)
    plt.show()

    # --- Sensitivity 2: mass vs ar ---
    taper_fixed = 0.30
    ar_vals = np.linspace(8.0, 14.0, 7)  # 7 points

    masses = []
    failures = []

    for ar in ar_vals:
        print(f"Running AR={ar:.2f}, taper={taper_fixed:.2f}")
        m, f, th = run_struct_sizing(ar, taper_fixed)
        masses.append(m)
        failures.append(f)
        print(f"  -> mass={m:.1f}, max_failure={f:.3f}, th={th}")

    # Simple line plot
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(ar_vals, masses, marker="o")
    plt.xlabel("Aspect Ratio")
    plt.ylabel("Structural Mass [kg]")
    plt.title(f"Structural mass vs AR (taper={taper_fixed:.2f})")
    plt.grid(True)
    plt.show()


    #This optimizes the chord thickness to keep mass as low as possible while staying under the failure limit (>0)
    #Additionally, I have two wing design variables (aspect and taper ratio)

        # --- Sensitivity 1: mass & failure vs AR ---
    taper_fixed = 0.30
    ar_vals = np.linspace(8, 14, 7)

    masses = []
    failures = []

    for ar in ar_vals:
        print(f"Running AR={ar:.2f}, taper={taper_fixed:.2f}")
        m, f, th = run_struct_sizing(ar, taper_fixed)
        masses.append(m)
        failures.append(f)
        print(f"  -> mass={m:.2f}  failure={f:.3f}  t={th}")

    # --- Plot with secondary y-axis ---
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots()

    color_mass = "tab:blue"
    color_fail = "tab:red"

    # Structural Mass
    ax1.plot(ar_vals, masses, marker="o", color=color_mass, label="structural mass")
    ax1.set_xlabel("Aspect Ratio")
    ax1.set_ylabel("Structural Mass [kg]", color=color_mass)
    ax1.tick_params(axis="y", labelcolor=color_mass)

    # Failure line on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(ar_vals, failures, marker="s", linestyle="--", color=color_fail, label="max failure")
    ax2.set_ylabel("Max Failure", color=color_fail)
    ax2.tick_params(axis="y", labelcolor=color_fail)

    plt.title(f"Sensitivity: AR sweep (taper={taper_fixed})")
    fig.tight_layout()
    plt.grid(True)
    plt.show()



        # --- Sensitivity 2: mass & failure vs taper ---
    ar_fixed = 10.0
    taper_vals = np.linspace(0.25, 0.45, 7)

    masses2 = []
    failures2 = []

    for taper in taper_vals:
        print(f"Running taper={taper:.2f}, AR={ar_fixed:.2f}")
        m, f, th = run_struct_sizing(ar_fixed, taper)
        masses2.append(m)
        failures2.append(f)
        print(f"  -> mass={m:.2f}  failure={f:.3f}  t={th}")

    # --- Plot with secondary y-axis ---
    fig, ax1 = plt.subplots()

    color_mass = "tab:green"
    color_fail = "tab:red"

    # Structural Mass
    ax1.plot(taper_vals, masses2, marker="o", color=color_mass, label="structural mass")
    ax1.set_xlabel("Taper Ratio")
    ax1.set_ylabel("Structural Mass [kg]", color=color_mass)
    ax1.tick_params(axis="y", labelcolor=color_mass)

    # Failure curve
    ax2 = ax1.twinx()
    ax2.plot(taper_vals, failures2, marker="s", linestyle="--", color=color_fail, label="max failure")
    ax2.set_ylabel("Max Failure", color=color_fail)
    ax2.tick_params(axis="y", labelcolor=color_fail)

    plt.title(f"Sensitivity: taper sweep (AR={ar_fixed})")
    fig.tight_layout()
    plt.grid(True)
    plt.show()
