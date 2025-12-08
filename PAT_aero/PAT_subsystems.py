import numpy as np
import openmdao.api as om

from aviary.variable_info.functions import add_aviary_input, add_aviary_output
from aviary.variable_info.variables import Aircraft, Dynamic

from BWB_geometry_generator import define_and_generate_BWB, run_avl, run_vsp


class Coefficients(om.ExplicitComponent):
    """
    Calculates the lift and drag coefficients of the aircraft based on a VSPAERO analysis.
    """

    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('temp_dir', default='data/temp', types=str)

    def setup(self):
        nn = self.options['num_nodes']

        # Inputs from the aircraft geometry and flight conditions
        # add_aviary_input(self, Aircraft.Wing.AREA, shape=nn, units='ft**2')
        add_aviary_input(self, Aircraft.Wing.SPAN, units='ft')
        add_aviary_input(self, Aircraft.Wing.SWEEP, units='deg')
        add_aviary_input(self, Aircraft.Wing.DIHEDRAL, units='deg')
        add_aviary_input(self, Aircraft.Wing.ROOT_CHORD, units='ft')
        add_aviary_input(self, Aircraft.Wing.TAPER_RATIO, units='unitless')
        add_aviary_input(self, Aircraft.Wing.INCIDENCE, units='deg')
        add_aviary_input(self, Aircraft.Wing.TWIST, units='deg')
        # add_aviary_input(self, Aircraft.Wing.VERTICAL_MOUNT_LOCATION, units='unitless')

        add_aviary_input(self, Aircraft.Fuselage.AVG_DIAMETER, units='ft')
        add_aviary_input(self, Aircraft.Fuselage.LENGTH, units='ft')
        add_aviary_input(self, Aircraft.Fuselage.HEIGHT_TO_WIDTH_RATIO, units='unitless')

        add_aviary_input(self, Dynamic.Atmosphere.MACH, shape=nn, units='unitless')
        add_aviary_input(self, Dynamic.Vehicle.ANGLE_OF_ATTACK, shape=nn, units='deg')
        add_aviary_input(self, Dynamic.Atmosphere.REYNOLDS_NUMBER, shape=nn, units='unitless')
        
        self.add_output('CL', shape=nn, units='unitless')
        self.add_output('CD', shape=nn, units='unitless')

    def compute(self, inputs, outputs):
        junk_dir = self.options['temp_dir']
        nn = self.options['num_nodes']

        model, avl_file, vsp_file = define_and_generate_BWB(
            junk_dir,
            nose_length = 15, # (feet)
            fuselage_length = inputs[Aircraft.Fuselage.LENGTH], # front to back length of BWB (feet)
            fuselage_width = inputs[Aircraft.Fuselage.AVG_DIAMETER], # (feet)
            height_to_width = inputs[Aircraft.Fuselage.HEIGHT_TO_WIDTH_RATIO], # (unitless)
            tail_height = 8, # (feet)
            wing_span = inputs[Aircraft.Wing.SPAN], # (feet)
            wing_length = 40, # (feet)
            wing_sweep = inputs[Aircraft.Wing.SWEEP], # (degrees)
            wing_dihedral = inputs[Aircraft.Wing.DIHEDRAL], # (degrees)
            wing_croot = inputs[Aircraft.Wing.ROOT_CHORD], # (feet)
            wing_taper = inputs[Aircraft.Wing.TAPER_RATIO], # (unitless)
            wing_twist = inputs[Aircraft.Wing.TWIST], # (degrees/foot)
            wing_alpha = inputs[Aircraft.Wing.INCIDENCE], # root incidence (degrees)
            wing_height = 8, # inputs[Aircraft.Wing.VERTICAL_MOUNT_LOCATION], # (feet)
            wing_x = 30, # (feet)
            )
        
        Xref, Yref, Zref = [0, 0, 0]

        alpha_start = inputs[Dynamic.Vehicle.ANGLE_OF_ATTACK]
        alpha_end = alpha_start
        alpha_npts = 1

        mach_start = inputs[Dynamic.Atmosphere.MACH]
        mach_end = mach_start
        mach_npts = 1

        Re_start = inputs['Re']
        Re_end = Re_start
        Re_npts = 1

        
        CLtot, CDtot = run_vsp(
            vsp_file,
            alpha_start,
            alpha_end,
            alpha_npts,
            junk_dir,
            Xref,
            Yref,
            Zref,
            mach_start,
            mach_end,
            mach_npts,
            Re_start,
            Re_end,
            Re_npts,
            False,
            Sref = inputs[Aircraft.Wing.AREA],
            )
        
        outputs['CL'] = CLtot[0]
        outputs['CD'] = CDtot[0]


class LiftAndDrag(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']
        add_aviary_input(self, Dynamic.Atmosphere.DYNAMIC_PRESSURE, shape=nn, units='psi')
        add_aviary_input(self, Aircraft.Wing.AREA, units='ft**2')

        self.add_input('CL', shape=nn, units='unitless')
        self.add_input('CD', shape=nn, units='unitless')

        add_aviary_output(self, Dynamic.Vehicle.LIFT, shape=nn, units='lbf')
        add_aviary_output(self, Dynamic.Vehicle.DRAG, shape=nn, units='lbf')

    def setup_partials(self):
        nn = self.options['num_nodes']
        
        rows_cols = np.arange(nn)

        self.declare_partials(
            Dynamic.Vehicle.LIFT,
            [Dynamic.Atmosphere.DYNAMIC_PRESSURE, Aircraft.Wing.AREA],
            rows=rows_cols,
            cols=rows_cols,
        )

        self.declare_partials(
            Dynamic.Vehicle.DRAG,
            [Dynamic.Atmosphere.DYNAMIC_PRESSURE, Aircraft.Wing.AREA],
            rows=rows_cols,
            cols=rows_cols,
        )

    def compute(self, inputs, outputs):
        cl = inputs['CL']
        cd = inputs['CD']
        q = inputs[Dynamic.Atmosphere.DYNAMIC_PRESSURE]
        s = inputs[Aircraft.Wing.AREA]

        outputs[Dynamic.Vehicle.LIFT] = cl*q*s
        outputs[Dynamic.Vehicle.DRAG] = cd*q*s

    def compute_partials(self, inputs, partials):
        cl = inputs['CL']
        cd = inputs['CD']
        q = inputs[Dynamic.Atmosphere.DYNAMIC_PRESSURE]
        s = inputs[Aircraft.Wing.AREA]

        partials[Dynamic.Vehicle.LIFT, Dynamic.Atmosphere.DYNAMIC_PRESSURE] = cl*s
        partials[Dynamic.Vehicle.LIFT, Aircraft.Wing.AREA] = cl*q

        partials[Dynamic.Vehicle.LIFT, Dynamic.Atmosphere.DYNAMIC_PRESSURE] = cd*s
        partials[Dynamic.Vehicle.LIFT, Aircraft.Wing.AREA] = cd*q