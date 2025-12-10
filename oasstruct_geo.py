import numpy as np
import openmdao.api as om
from openaerostruct.meshing.mesh_generator import generate_mesh
from openaerostruct.structures.struct_groups import SpatialBeamAlone

class OASStructGroup(om.Group):
    """
    OpenAeroStruct structural model for the BWB wing.

    Options:
    - material: dict with E, G, yield, mrho
    - AR: aspect ratio to use for the structural mesh
    - taper: taper ratio to use for the structural mesh
    """

    def initialize(self):
        self.options.declare("material", types=dict)
        self.options.declare("AR", default=10.0)
        self.options.declare("taper", default=0.27444)
        self.options.declare("span_ft", default=118.0)
        self.options.declare("t_c_root", default=0.165)

    def setup(self):
        material = self.options["material"]
        AR = self.options["AR"]
        taper = self.options["taper"]
        span_ft = self.options["span_ft"]
        t_c_root = self.options["t_c_root"]

        span_m = span_ft * 0.3048

        # Wing area from AR = b^2 / S
        S = span_m**2 / AR

        # Root chord from S = (b * (cr + ct)) / 2, ct = taper * cr
        root_chord = 2.0 * S / ((1.0 + taper) * span_m)
        tip_chord = taper * root_chord

        print("span_m:", span_m, "root_chord:", root_chord)

        # ==== Mesh dict: rectangular planform with BWB numbers ====
        mesh_dict = {
            "num_y": 17,
            "num_x": 3,
            "wing_type": "rect",
            "symmetry": True,
            "span": span_m,
            "root_chord": root_chord,
        }

        res = generate_mesh(mesh_dict)
        if isinstance(res, (tuple, list)):
            mesh = res[0]
        else:
            mesh = res

        ny = mesh.shape[1]

        # ==== Surface definition for tube FEM ====
        surf_dict = {
            "name": "wing",
            "symmetry": True,
            "fem_model_type": "tube",
            "mesh": mesh,

            # Material
            "E": material["E"],
            "G": material["G"],
            "yield": material["yield"],
            "mrho": material["mrho"],

            "safety_factor": 2.5,
            "fem_origin": 0.35,

            # Use your BWB-ish t/c at the root
            "t_over_c_cp": np.array([t_c_root]),

            # Initial thickness distribution (starting guess)
            "thickness_cp": np.ones(3) * 0.10,   # meters

            "wing_weight_ratio": 2.0,
            "struct_weight_relief": False,
            "distributed_fuel_weight": False,
            "exact_failure_constraint": False,
        }

        # ==== Indep vars inside this group ====
        ivc = om.IndepVarComp()
        ivc.add_output("loads", val=np.ones((ny, 6)) * 2e3, units="N")
        ivc.add_output("thickness_cp", val=np.ones(3) * 0.10, units="m")

        # Promote loads + thickness_cp to the group interface
        self.add_subsystem("ivc", ivc, promotes=["loads", "thickness_cp"])

        # ==== Structural model ====
        struct_group = SpatialBeamAlone(surface=surf_dict)
        self.add_subsystem(
            "struct",
            struct_group,
            promotes_inputs=["loads", "thickness_cp"],
            promotes_outputs=["structural_mass", "failure"],
        )
