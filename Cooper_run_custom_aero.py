"""Run the a mission with a simple external component that computes aircraft lift and drag."""

from copy import deepcopy

import aviary.api as av
from PAT_aero_builder import PATAeroBuilder
from aviary.models.missions.two_dof_default import phase_info


# Add custom aero.
# TODO: This API for replacing aero will be changed an upcoming release.
phase_info['cruise']['external_subsystems'] = [PATAeroBuilder()]

# Disable internal aero
# TODO: This API for replacing aero will be changed an upcoming release.
phase_info['cruise']['subsystem_options']['core_aerodynamics'] = {
    'method': 'external',
}


if __name__ == '__main__':
    prob = av.AviaryProblem()

    # Load aircraft and options data from user
    # Allow for user overrides here
    prob.load_inputs('models/aircraft/blended_wing_body/generic_BWB_GASP.csv', phase_info)

    prob.check_and_preprocess_inputs()

    prob.build_model()

    # Note, SLSQP has trouble here.
    prob.add_driver('IPOPT', max_iter=100)

    prob.add_design_variables()

    prob.add_objective()

    prob.setup()

    prob.run_aviary_problem(suppress_solver_print=True)

    print('done')
