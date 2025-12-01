import openmdao.api as om

class BWBFuelTankComp(om.ExplicitComponent):
    """
    Inputs:
    - ref_wing_area               : Wing reference area [m**2]
    - thickness_to_chord_eff      : Effective thickness-to-chord ratio [-]
    - tank_span_fraction          : Fraction of span that is "wet" [-]
    - fuel_density                : Fuel density [kg/m**3]
    - fuel_required               : Mission fuel mass required [kg] 

    Outputs:
    - fuel_capacity_mass   : Max fuel mass tank can hold [kg]
    - fuel_capacity_volume : Corresponding tank volume [m**3]
    - tank_struct_mass     : Simple structural mass estimate [kg]
    """

    def setup(self):
        # Inputs
        self.add_input('ref_wing_area', units='m**2')
        self.add_input('thickness_to_chord_eff', val=0.5)  # Placeholder Val
        self.add_input('tank_span_fraction', val=0.6)       
        self.add_input('fuel_density', units='kg/m**3', val=49.94) # Jet fuel density (775-840 kg/m^3 = 48.38-52.43 lb/ft^3)
        self.add_input('fuel_required', units='kg', val=0.0)       

        # Outputs
        self.add_output('fuel_capacity_mass', units='kg')
        self.add_output('fuel_capacity_volume', units='m**3')
        self.add_output('tank_structure_mass', units='kg')

    def compute(self, inputs, outputs):
        S_ref_wing = inputs['ref_wing_area']
        t_over_c = inputs['thickness_to_chord_eff']
        span_frac = inputs['tank_span_fraction']
        rho_fuel = inputs['fuel_density']

        # Equation: volume = (t/c * mean chord) * (span fraction * span) * thickness factor of the wing
        # Assume: mean chord * span = reference wing area
        # Therefore, tank volume = S_ref_wing * (t/c) * (span fraction) * thickness factor
        effective_thickness_factor = 0.4  # placeholder for factor accounting for chord and shape
        tank_volume = S_ref_wing * t_over_c * span_frac * effective_thickness_factor

        fuel_capacity_mass = tank_volume * rho_fuel

        # Estimating structural mass as a fraction of fuel capacity mass
        struct_mass_factor = 0.1  # Placeholder for X% of fuel capacity mass
        tank_structure_mass = struct_mass_factor * fuel_capacity_mass

        outputs['fuel_capacity_volume'] = tank_volume
        outputs['fuel_capacity_mass'] = fuel_capacity_mass
        outputs['tank_structure_mass'] = tank_structure_mass