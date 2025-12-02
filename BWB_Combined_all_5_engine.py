"""
This is an example of running a coupled aircraft design-mission optimization in Aviary using the
"level 2" API. It runs the same aircraft and mission as the `level1_example.py` script, but it uses
the AviaryProblem class to set up the problem. This exposes more options and flexibility to the user.

The same ".csv" file is used to define the aircraft, but now the phase_info dictionary is directly
imported from the file and passed as an argument. It is common for level 2 scripts to modify
existing phase_info, but here it is used as-is here to match the level 1 example.

We then call the correct methods in order to set up and run an Aviary optimization problem. Most
methods have optional arguments, but none are necessary here. The selection of the SLSQP optimizer
limited to 50 iterations are included to demonstrate of how those common settings are set.
"""
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

from two_dof_default_altitude_opt import phase_info
from oasstruct_geo import OASStructGroup
from External_Subsystem.Propulsion.BWB_propulsion_regression_builder import RegressionPropulsionBuilder


def build_coupled_problem():
    # Propulsion builder setup: -- From AZ
    # Begin:
    N_ENG = 5 # Try 3 or 4 for other BWB configurations, make sure to also change the corresponding values in the CSV file

    prop_builder = RegressionPropulsionBuilder(
        coeffs_json_path="External_Subsystem/Propulsion/engine_regression_coeffs.json",
        T_deck_ref=23928.17,      # SLS static max thrust from turbofan_gasp_bwb.csv

        # This following parameter only involved for caculating the TSFC scaling, but not for thrust or mass scaling
        # I created the caluclation model in the builder but you can ignore it if you don't need TSFC scaling
        # It's been ignored because in Aviary the fuel flow scaling is not a design variable that can be simply added unless you modify the engine model.
        TSFC_deck_ref=0.50,       # pick a representative cruise TSFC from the deck 5783.02
        num_engines=N_ENG,
        cruise_refs={"BPR": 8.5, "OPR": 40.0, "Mach": 0.78, "h_ft": 35000.0}, # For calucting fuel flow from TSFC regression
        name="regression_propulsion",
    )

    # Add builder to pre_mission before load inputs:
    phase_info.setdefault("pre_mission", {})
    phase_info["pre_mission"].setdefault("external_subsystems", [])
    phase_info["pre_mission"]["external_subsystems"].append(prop_builder)
    # End

    avi_prob = av.AviaryProblem()

    avi_prob.load_inputs("GASP_Geometry_5_engine.csv", phase_info)
    avi_prob.check_and_preprocess_inputs()
    avi_prob.build_model()

    avi_prob.add_driver("IPOPT", max_iter=300)

    avi_prob.add_design_variables()
    avi_prob.model.add_design_var("aircraft:wing:aspect_ratio", lower=7.0, upper=14.0)
    avi_prob.model.add_design_var("aircraft:wing:taper_ratio", lower=0.25, upper=0.45)

    avi_prob.add_design_var_default(
        name='traj.cruise.parameters:altitude',  # phase-level altitude
        lower=10000.0,
        upper=42000.0,
        units='ft',
        default_val=25000.0,
        ref=25000.0
    )

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

    # Add propulsion design variable and connections: -- From AZ
    # Begin:
    avi_prob.model.add_design_var(
        "pre_mission.regression_propulsion.eng_ivc.propulsion:T_rated",
        lower=5000.0,
        upper=40000.0,
    )

    avi_prob.model.connect(
        "pre_mission.regression_propulsion.propulsion:thrust_scale",
        "aircraft:engine:scale_factor",
    )

    avi_prob.model.connect(
        "pre_mission.regression_propulsion.propulsion:mass_scaler_out",
        "aircraft:engine:mass_scaler"
    )
    # End


    
    # ---- Structural DV is now thickness_cp (vector of length 3) ----
    avi_prob.model.add_design_var("oas_struct.thickness_cp", lower=0.003, upper=0.5)

    avi_prob.model.add_constraint("failure", upper=0.0)
    #avi_prob.model.add_objective("structural_mass", scaler=1e-5)
    avi_prob.add_objective("fuel_burned")

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

    # Print out relevant results: -- From AZ
    # Begin:
    print("T_rated =", prob.get_val("pre_mission.regression_propulsion.eng_ivc.propulsion:T_rated"))
    print("scale_factor =", prob.get_val("aircraft:engine:scale_factor"))
    print("fuel_burned =", prob.get_val(av.Mission.Summary.FUEL_BURNED))
    print("num_engines (inputs) =", prob.aviary_inputs.get_val(av.Aircraft.Engine.NUM_ENGINES))
    print("num_fuselage_engines (inputs) =", prob.aviary_inputs.get_val(av.Aircraft.Engine.NUM_FUSELAGE_ENGINES))
    print("engine_mass", prob.get_val("pre_mission.regression_propulsion.propulsion:engine_mass"))
    print("engine_mass_scale_out =", prob.get_val("pre_mission.regression_propulsion.propulsion:mass_scaler_out"))
    print("engine_mass_total =", prob.get_val("pre_mission.regression_propulsion.propulsion:engine_mass_total"))
    # End


    #This optimizes the chord thickness to keep mass as low as possible while staying under the failure limit (>0)
    #Additionally, I have two wing design variables (aspect and taper ratio)