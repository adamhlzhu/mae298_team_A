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

from two_dof_default_to_mission import phase_info
from oasstruct_geo import OASStructGroup

def build_coupled_problem():
    avi_prob = av.AviaryProblem()

    avi_prob.load_inputs("GASP_Geometry.csv", phase_info)
    avi_prob.check_and_preprocess_inputs()
    avi_prob.build_model()

    avi_prob.add_driver("IPOPT", max_iter=200)

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
    avi_prob.model.add_design_var("oas_struct.thickness_cp", lower=0.003, upper=0.5)

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


    #This optimizes the chord thickness to keep mass as low as possible while staying under the failure limit (>0)
    #Additionally, I have two wing design variables (aspect and taper ratio)