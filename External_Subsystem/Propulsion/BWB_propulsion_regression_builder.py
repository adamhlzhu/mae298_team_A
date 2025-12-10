import json
import numpy as np
import openmdao.api as om
import aviary.api as av

class RegressionPropulsionBuilder(av.SubsystemBuilderBase):
    """
    Aviary external subsystem builder.
    - Pre-mission subsystem.
    - Uses offline regressions to scale an existing turbofan deck.
    - Outputs scaling factors + total engine mass.

    You MUST provide a baseline turbofan deck in your aircraft CSV.
    """

    def __init__(
        self,
        coeffs_json_path,
        T_deck_ref,
        TSFC_deck_ref,
        num_engines,
        cruise_refs=None,
        name="regression_propulsion",
    ):
        """
        coeffs_json_path: path to your saved regression json
        T_deck_ref: rated thrust of the baseline deck (lbf), og file is Aviary\aviary\models\engines\turbofan_gasp_bwb.csv
        TSFC_deck_ref: representative cruise TSFC for that baseline deck, og file is Aviary\aviary\models\engines\turbofan_gasp_bwb.csv
        num_engines: scenario engine count (2/3/4)
        cruise_refs: dict with fixed cruise values for BPR/OPR/Mach/h
                     e.g. {"BPR": 8.5, "OPR": 40, "Mach": 0.78, "h_ft": 35000}
        name: subsystem instance name inside pre_mission
        """
        super().__init__()
        self.coeffs_json_path = coeffs_json_path
        self.T_deck_ref = float(T_deck_ref)
        self.TSFC_deck_ref = float(TSFC_deck_ref)
        self.num_engines = int(num_engines)
        self.name = name

        if cruise_refs is None:
            cruise_refs = {"BPR": 8.5, "OPR": 40.0, "Mach": 0.78, "h_ft": 35000.0} # some defaults, placeholder here
        self.cruise_refs = cruise_refs
    
    def build_pre_mission(self, aviary_inputs):
        g = om.Group()

        g.add_subsystem(
            "eng_ivc",
            om.IndepVarComp("propulsion:T_rated", val=self.T_deck_ref, units="lbf"),
            promotes=["*"],
        )

        g.add_subsystem(
            "regression_scaler",
            EngineRegressionScalerComp(
                coeffs_json_path=self.coeffs_json_path,
                T_deck_ref=self.T_deck_ref,
                TSFC_deck_ref=self.TSFC_deck_ref,
                num_engines=self.num_engines,
                cruise_refs=self.cruise_refs
            ),
            promotes=["*"],
        )

        return g
    

class EngineRegressionScalerComp(om.ExplicitComponent):
    """
    OpenMDAO component:
      inputs:  propulsion:T_rated
      outputs: propulsion:thrust_scale
               propulsion:fuelflow_scale
               propulsion:engine_mass_total
    """

    def initialize(self):
        self.options.declare("coeffs_json_path", types=str)
        self.options.declare("T_deck_ref", types=float)
        self.options.declare("TSFC_deck_ref", types=float)
        self.options.declare("num_engines", types=int)
        self.options.declare("cruise_refs", types=dict)

    def setup(self):
        self.add_input("propulsion:T_rated", units="lbf")
        
        self.add_output("propulsion:engine_mass", units="lbm")
        self.add_output("propulsion:mass_scaler_out")
        self.add_output("propulsion:tsfc_scale")
        self.add_output("propulsion:thrust_scale")
        self.add_output("propulsion:fuelflow_scale")
        self.add_output("propulsion:engine_mass_total", units="lbm")

        # load coeffs
        coeff_path = self.options["coeffs_json_path"]
        with open(coeff_path, "r") as f:
            self.coeffs = json.load(f)

        self.mass_c = self.coeffs["mass"]   # a,b
        self.tsfc_c = self.coeffs["tsfc"]   # a,b,c,d,e,f,...

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    # Mass regression prediction model
    def mass_regression(self, T):
        a = self.mass_c["a"]; b = self.mass_c["b"]
        return a * T**b
    
    # TSFC regression prediction model
    def tsfc_regression(self, T, BPR, OPR, Mach, h_ft):
        c = self.tsfc_c
        
        if "c" not in c:
            return c["a"] * T**c["b"]

        if not all(k in c for k in ["d", "e", "f"]):
            return c["a"] * T**c["b"] * BPR**c["c"]

        return (c["a"] * T**c["b"] * BPR**c["c"] *
                OPR**c["d"] * Mach**c["e"] * h_ft**c["f"])

    def compute(self, inputs, outputs):
        T_rated = float(inputs["propulsion:T_rated"])

        T_deck_ref = self.options["T_deck_ref"]
        TSFC_deck_ref = self.options["TSFC_deck_ref"]
        N = self.options["num_engines"]
        refs = self.options["cruise_refs"]

        # fixed cruise refs for TSFC prediction
        BPR_ref = refs["BPR"]
        OPR_ref = refs["OPR"]
        Mach_ref = refs["Mach"]
        h_ref = refs["h_ft"]

        m_per_eng = self.mass_regression(T_rated)
        tsfc_cruise = self.tsfc_regression(T_rated, BPR_ref, OPR_ref, Mach_ref, h_ref)

        thrust_scale = T_rated / T_deck_ref
        fuelflow_scale = (tsfc_cruise / TSFC_deck_ref) * thrust_scale


        baseline_mass_per_eng = 6130.0  # from INGASP.WENG, per-engine
        mass_scaler_out = m_per_eng / baseline_mass_per_eng

        # mass_specific = 0.178884  # from CSV
        # mass_scaler_out = m_per_eng / (mass_specific * T_rated)

        outputs["propulsion:engine_mass"] = m_per_eng
        outputs["propulsion:mass_scaler_out"] = mass_scaler_out
        outputs["propulsion:thrust_scale"] = thrust_scale
        outputs["propulsion:fuelflow_scale"] = fuelflow_scale
        outputs["propulsion:engine_mass_total"] = N * m_per_eng
        outputs["propulsion:tsfc_scale"] = tsfc_cruise / TSFC_deck_ref