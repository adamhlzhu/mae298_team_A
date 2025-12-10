import openmdao.api as om
import aviary.api as av

from Subsystem.Mass.BWB_fuel_tank import BWBFuelTankComp

BWB_TANK_SPAN_FRACTION = 'bwb_fuel:tank_span_fraction'
BWB_TANK_T_OVER_C_EFF  = 'bwb_fuel:t_over_c_eff'
BWB_TANK_FUEL_DENSITY  = 'bwb_fuel:fuel_density'
BWB_TANK_CAPACITY_MASS = 'bwb_fuel:capacity_mass'
BWB_TANK_CAPACITY_VOL  = 'bwb_fuel:capacity_volume'
BWB_TANK_STRUCT_MASS   = 'bwb_fuel:tank_struct_mass'


class BWBFuelTankBuilder(av.SubsystemBuilderBase):
    """
    External subsystem builder for BWB fuel-tank sizing.
    - Runs in pre-mission (sizing) to compute capacity and tank structural mass.
    - Uses core Aviary wing area + mission fuel as inputs.
    - Provides capacity mass as an output you can constrain against.
    """

    def __init__(self, name='bwb_fuel_tank'):
        super().__init__(name=name)

    def build_pre_mission(self, aviary_inputs):
        g = om.Group()

        g.add_subsystem(
            'bwb_fuel_tank',
            BWBFuelTankComp(),
            promotes_inputs=[
                # From Aviary:
                # Wing area S_ref (you might change to the exact tag you use)
                ('ref_wing_area', av.Aircraft.Wing.AREA),
                ('fuel_required', av.Mission.Design.FUEL_MASS),

                # Variables to set for BWB fuel tank sizing:
                ('thickness_to_chord_eff', BWB_TANK_T_OVER_C_EFF),
                ('tank_span_fraction', BWB_TANK_SPAN_FRACTION),
                ('fuel_density', BWB_TANK_FUEL_DENSITY),
            ],
            promotes_outputs=[
                ('fuel_capacity_mass',   BWB_TANK_CAPACITY_MASS),
                ('fuel_capacity_volume', BWB_TANK_CAPACITY_VOL),
                ('tank_structure_mass',  BWB_TANK_STRUCT_MASS),
            ],
        )

        return g
