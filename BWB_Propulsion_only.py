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
from aviary.api import Aircraft
from two_dof_default_to_mission import phase_info
from External_Subsystem.Propulsion.BWB_propulsion_regression_builder import RegressionPropulsionBuilder

import aviary.api as av

# Propulsion builder setup: -- From AZ
# Begin:
N_ENG = 2 # Try 3 or 4 for other BWB configurations, make sure to also change the corresponding values in the CSV file

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

# Set up and run Aviary problem:
prob = av.AviaryProblem()

# Load aircraft and options data from provided sources
prob.load_inputs(
    'GASP_Geometry.csv', phase_info
)

prob.check_and_preprocess_inputs()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver('IPOPT', max_iter=200)

prob.add_design_variables()

# Add propulsion design variable and connections: -- From AZ
# Begin:
prob.model.add_design_var(
    "pre_mission.regression_propulsion.eng_ivc.propulsion:T_rated",
    lower=5000.0,
    upper=40000.0,
    ref=18000.0,
)

prob.model.connect(
    "pre_mission.regression_propulsion.propulsion:thrust_scale",
    "aircraft:engine:scale_factor",
)

prob.model.connect(
    "pre_mission.regression_propulsion.propulsion:mass_scaler_out",
    "aircraft:engine:mass_scaler"
)
# End


prob.add_objective("fuel_burned")

prob.setup()

prob.run_aviary_problem()

# Print out relevant results: -- From AZ
# Begin:
print("T_rated =", prob.get_val("pre_mission.regression_propulsion.eng_ivc.propulsion:T_rated"))
print("scale_factor =", prob.get_val("aircraft:engine:scale_factor"))
print("fuel_burned =", prob.get_val(av.Mission.Summary.FUEL_BURNED))
print("num_engines (inputs) =", prob.aviary_inputs.get_val(Aircraft.Engine.NUM_ENGINES))
print("num_fuselage_engines (inputs) =", prob.aviary_inputs.get_val(Aircraft.Engine.NUM_FUSELAGE_ENGINES))
print("engine_mass", prob.get_val("pre_mission.regression_propulsion.propulsion:engine_mass"))
print("engine_mass_scale_out =", prob.get_val("pre_mission.regression_propulsion.propulsion:mass_scaler_out"))
print("engine_mass_total =", prob.get_val("pre_mission.regression_propulsion.propulsion:engine_mass_total"))
# End

