import numpy as np
import openmdao.api as om

from aviary.subsystems.aerodynamics.aero_common import DynamicPressure, ReynoldsNumber
from aviary.variable_info.variables import Aircraft, Dynamic
from PAT_subsystems import Coefficients, LiftAndDrag


class PATAeroGroup(om.Group):
    def initialize(self):
        self.options.declare(
            'num_nodes', default=1, types=int, desc='Number of nodes along mission segment'
        )

    def setup(self):
        nn = self.options['num_nodes']

        self.add_subsystem(
            'DynamicPressure',
            DynamicPressure(num_nodes=nn),
            promotes_inputs=[
                Dynamic.Atmosphere.MACH,
                Dynamic.Atmosphere.STATIC_PRESSURE,
            ],
            promotes_outputs=[Dynamic.Atmosphere.DYNAMIC_PRESSURE],
        )

        self.add_subsystem(
            'ReynoldsNumber',
            ReynoldsNumber(num_nodes=nn),
            promotes_inputs=[
                Dynamic.Atmosphere.KINEMATIC_VISCOSITY,
                Dynamic.Mission.VELOCITY,
                Aircraft.Wing.CHARACTERISTIC_LENGTH,
            ],
            promotes_outputs=[Dynamic.Atmosphere.REYNOLDS_NUMBER],
        )

        self.add_subsystem(
            'LiftAndDrag',
            LiftAndDrag(num_nodes=nn),
            promotes_inputs=[
                'CL',
                'CD',
                Dynamic.Atmosphere.DYNAMIC_PRESSURE,
                Aircraft.Wing.AREA,
            ],
            promotes_outputs=[
                Dynamic.Vehicle.LIFT,
                Dynamic.Vehicle.DRAG
            ],
        )

        self.add_subsystem(
            'Coefficients',
            Coefficients(num_nodes=nn),
            promotes_inputs=[
                # Aircraft.Wing.AREA,
                Aircraft.Wing.SPAN,
                Aircraft.Wing.SWEEP,
                Aircraft.Wing.DIHEDRAL,
                Aircraft.Wing.ROOT_CHORD,
                Aircraft.Wing.TAPER_RATIO,
                Aircraft.Wing.INCIDENCE,
                Aircraft.Wing.TWIST,
                # Aircraft.Wing.VERTICAL_MOUNT_LOCATION,

                Aircraft.Fuselage.AVG_DIAMETER,
                Aircraft.Fuselage.LENGTH,
                Aircraft.Fuselage.HEIGHT_TO_WIDTH_RATIO,

                Dynamic.Atmosphere.MACH,
                Dynamic.Vehicle.ANGLE_OF_ATTACK,
                Dynamic.Atmosphere.REYNOLDS_NUMBER,
            ],
            promotes_outputs=['CL', 'CD'],
        )
