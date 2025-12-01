# Unspecified Hierarchy Variables
These aviary inputs are unspecified in aviary_inputs, and may be using default values defined in the Aviary metadata.

| Name | Value | Units | Description | Absolute Paths
| :- |  :- |  :- | :- | :- |
| **aircraft:design:external_subsystems_mass** | [0.] | lbm | total mass of all user-defined external subsystems | ['pre_mission.core_subsystems.core_mass.equip_and_useful_mass.equip.equip_partial.aircraft:design:external_subsystems_mass']|
| **aircraft:design:lift_dependent_drag_coeff_factor** | [1.] | unitless | Scaling factor for lift-dependent drag coefficient | ['traj.param_comp.parameters:aircraft:design:lift_dependent_drag_coeff_factor']|
| **aircraft:design:subsonic_drag_coeff_factor** | [1.] | unitless | Scaling factor for subsonic drag | ['traj.param_comp.parameters:aircraft:design:subsonic_drag_coeff_factor']|
| **aircraft:design:supersonic_drag_coeff_factor** | [1.] | unitless | Scaling factor for supersonic drag | ['traj.param_comp.parameters:aircraft:design:supersonic_drag_coeff_factor']|
| **aircraft:design:zero_lift_drag_coeff_factor** | [1.] | unitless | Scaling factor for zero-lift drag coefficient | ['traj.param_comp.parameters:aircraft:design:zero_lift_drag_coeff_factor']|
| **aircraft:fuel:unusable_fuel_mass** | [0.] | lbm | unusable fuel mass | ['post_mission.excess_fuel_constraint.unusable_fuel']|
| **aircraft:fuselage:mass_scaler** | [1.] | unitless | mass scaler of the fuselage structure | ['pre_mission.core_subsystems.core_mass.fuel_mass.struct.aircraft:fuselage:mass_scaler']|
| **aircraft:horizontal_tail:mass_scaler** | [1.] | unitless | mass scaler of the horizontal tail structure | ['pre_mission.core_subsystems.core_mass.fuel_mass.struct.aircraft:horizontal_tail:mass_scaler']|
| **aircraft:propulsion:misc_mass_scaler** | [1.] | unitless | scaler applied to miscellaneous engine mass (sum of engine control, starter, and additional mass) | ['pre_mission.core_subsystems.core_mass.fixed_mass.engine.aircraft:propulsion:misc_mass_scaler']|
| **aircraft:strut:chord** | [0.] | ft | chord of the strut | ['landing.aero_td.aero_setup.geom.aircraft:strut:chord', 'landing.core_aerodynamics.aero_setup.geom.aircraft:strut:chord', 'traj.param_comp.parameters:aircraft:strut:chord']|
| **aircraft:vertical_tail:mass_scaler** | [1.] | unitless | mass scaler of the vertical tail structure | ['pre_mission.core_subsystems.core_mass.fuel_mass.struct.aircraft:vertical_tail:mass_scaler']|
| **aircraft:wing:folded_span_dimensionless** | [1.] | unitless | folded wingspan | ['pre_mission.core_subsystems.core_geometry.wing.dimensionless_calcs.fold_calcs.aircraft:wing:folded_span_dimensionless']|
| **aircraft:wing:mass_scaler** | [1.] | unitless | mass scaler of the overall wing | ['pre_mission.core_subsystems.core_mass.fuel_mass.struct.aircraft:wing:mass_scaler']|
| **aircraft:wing:slat_span_ratio** | [0.] | unitless | fraction of wing leading edge with slats | ['pre_mission.core_subsystems.core_aerodynamics.flaps_landing.LookupTables.VLAM11_interp.aircraft:wing:slat_span_ratio', 'pre_mission.core_subsystems.core_aerodynamics.flaps_takeoff.LookupTables.VLAM11_interp.aircraft:wing:slat_span_ratio', 'pre_mission.core_subsystems.core_aerodynamics.flaps_up.LookupTables.VLAM11_interp.aircraft:wing:slat_span_ratio', 'pre_mission.core_subsystems.core_mass.fixed_mass.HL.aircraft:wing:slat_span_ratio']|
| **aircraft:wing:surface_ctrl_mass_scaler** | [1.] | unitless | Surface controls mass scaler | ['pre_mission.core_subsystems.core_mass.fixed_mass.controls.aircraft:wing:surface_ctrl_mass_scaler']|
| **mission:landing:initial_mach** | [0.1] | unitless | approach Mach number | ['landing.atmosphere.flight_conditions.mach', 'landing.core_aerodynamics.aero_setup.geom.mach', 'landing.core_aerodynamics.aero_setup.xlifts.mach', 'landing.core_aerodynamics.body_lift_curve.mach', 'landing.core_propulsion.turbofan_gasp_bwb.engine_scaling.mach', 'landing.core_propulsion.turbofan_gasp_bwb.interpolation.mach', 'landing.core_propulsion.turbofan_gasp_bwb.max_interpolation.mach']|
| **mission:summary:reserve_fuel_burned** | [0.] | lbm | fuel burned during reserve phases, this does not include fuel burned in regular phases | ['post_mission.reserve_fuel.reserve_fuel_burned']|
| **mission:takeoff:airport_altitude** | [0.] | ft | altitude of airport where aircraft takes off | ['taxi.alias_taxi_phase.airport_alt', 'taxi.core_propulsion.turbofan_gasp_bwb.interpolation.altitude', 'taxi.core_propulsion.turbofan_gasp_bwb.max_interpolation.altitude']|
| **mission:takeoff:ascent_duration** | [25.] | s | duration of the ascent phase of takeoff | ['event_xform.m', 'fuel_obj.ascent_duration', 'range_obj.ascent_duration', 'traj.phases.ascent.param_comp.t_duration', 'traj.phases.ascent.time.t_duration']|
| **mission:takeoff:ascent_t_initial** | [45.] | s | time that the ascent phase of takeoff starts at | ['event_xform.b', 'traj.phases.ascent.param_comp.t_initial', 'traj.phases.ascent.time.t_initial']|
| **mission:taxi:mach** | [0.] | unitless | speed during taxi, must be nonzero if pycycle is enabled | ['taxi.alias_taxi_phase.taxi_mach', 'taxi.core_propulsion.turbofan_gasp_bwb.engine_scaling.mach', 'taxi.core_propulsion.turbofan_gasp_bwb.interpolation.mach', 'taxi.core_propulsion.turbofan_gasp_bwb.max_interpolation.mach']|
| **traj.ascent.rhs_all.mission:takeoff:airport_altitude** | [0.] | ft | altitude of airport where aircraft takes off | ['traj.phases.ascent.rhs_all.core_aerodynamics.drag_coef.airport_alt', 'traj.phases.ascent.rhs_all.core_aerodynamics.kclge.airport_alt']|
| **traj.groundroll.rhs_all.mission:takeoff:airport_altitude** | [0.] | ft | altitude of airport where aircraft takes off | ['traj.phases.groundroll.rhs_all.core_aerodynamics.drag_coef.airport_alt', 'traj.phases.groundroll.rhs_all.core_aerodynamics.kclge.airport_alt']|
| **traj.rotation.rhs_all.mission:takeoff:airport_altitude** | [0.] | ft | altitude of airport where aircraft takes off | ['traj.phases.rotation.rhs_all.core_aerodynamics.drag_coef.airport_alt', 'traj.phases.rotation.rhs_all.core_aerodynamics.kclge.airport_alt']|

# Unspecified Local Variables
These local subsystem inputs are unconnected, and may be using default values specified in the component.

| Name | Value | Units | Absolute Paths
| :- |  :- |  :- | :- |
| **landing.aero_ramps.flap_factor:final_val** | [1.] | unitless | ['landing.aero_td.aero_ramps.flap_factor:final_val', 'landing.core_aerodynamics.aero_ramps.flap_factor:final_val']|
| **landing.aero_ramps.flap_factor:initial_val** | [0.] | unitless | ['landing.aero_td.aero_ramps.flap_factor:initial_val', 'landing.core_aerodynamics.aero_ramps.flap_factor:initial_val']|
| **landing.aero_ramps.gear_factor:final_val** | [1.] | unitless | ['landing.aero_td.aero_ramps.gear_factor:final_val', 'landing.core_aerodynamics.aero_ramps.gear_factor:final_val']|
| **landing.aero_ramps.gear_factor:initial_val** | [0.] | unitless | ['landing.aero_td.aero_ramps.gear_factor:initial_val', 'landing.core_aerodynamics.aero_ramps.gear_factor:initial_val']|
| **landing.altitude** | [0.] | ft | ['landing.aero_td.drag_coef.altitude', 'landing.aero_td.kclge.altitude', 'landing.atmosphere_td.standard_atmosphere.h', 'landing.core_propulsion.turbofan_gasp_bwb.interpolation.altitude', 'landing.core_propulsion.turbofan_gasp_bwb.max_interpolation.altitude']|
| **landing.angle_of_attack** | [0.] | deg | ['landing.core_aerodynamics.kclge.angle_of_attack', 'landing.core_aerodynamics.lift_coef.angle_of_attack']|
| **landing.dt_flaps** | [3.] | s | ['landing.aero_td.aero_ramps.flap_factor:t_duration', 'landing.core_aerodynamics.aero_ramps.flap_factor:t_duration']|
| **landing.dt_gear** | [7.] | s | ['landing.aero_td.aero_ramps.gear_factor:t_duration', 'landing.core_aerodynamics.aero_ramps.gear_factor:t_duration']|
| **landing.t_curr** | [1.] | s | ['landing.aero_td.aero_ramps.time', 'landing.core_aerodynamics.aero_ramps.time']|
| **landing.t_init_flaps_app** | [1.e+10] | s | ['landing.core_aerodynamics.aero_ramps.flap_factor:t_init']|
| **landing.t_init_flaps_td** | [1.e+10] | s | ['landing.aero_td.aero_ramps.flap_factor:t_init']|
| **landing.t_init_gear_app** | [1.e+10] | s | ['landing.core_aerodynamics.aero_ramps.gear_factor:t_init']|
| **landing.t_init_gear_td** | [1.e+10] | s | ['landing.aero_td.aero_ramps.gear_factor:t_init']|
| **landing.throttle** | [[0.]] | unitless | ['landing.core_propulsion.turbofan_gasp_bwb.interpolation.throttle']|
| **landing.vectorize_performance.electric_power_in_0** | [0.] | kW | ['landing.core_propulsion.vectorize_performance.electric_power_in_0']|
| **landing.vectorize_performance.nox_rate_0** | [0.] | lbm/h | ['landing.core_propulsion.vectorize_performance.nox_rate_0']|
| **landing.vectorize_performance.shaft_power_0** | [0.] | hp | ['landing.core_propulsion.vectorize_performance.shaft_power_0']|
| **landing.vectorize_performance.shaft_power_max_0** | [0.] | hp | ['landing.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **landing.vectorize_performance.t4_0** | [0.] | degR | ['landing.core_propulsion.vectorize_performance.t4_0']|
| **pre_mission.alt_flaps** | [0.] | ft | ['pre_mission.core_subsystems.core_aerodynamics.atmosphere.standard_atmosphere.h']|
| **pre_mission.flap_defl_up** | [0.] | deg | ['pre_mission.core_subsystems.core_aerodynamics.flaps_up.BasicFlapsCalculations.flap_defl', 'pre_mission.core_subsystems.core_aerodynamics.flaps_up.LookupTables.VLAM6_interp.flap_defl']|
| **pre_mission.mach** | [0.] | unitless | ['pre_mission.core_subsystems.core_aerodynamics.atmosphere.flight_conditions.mach', 'pre_mission.core_subsystems.core_aerodynamics.flaps_landing.LookupTables.VLAM14_interp.mach', 'pre_mission.core_subsystems.core_aerodynamics.flaps_takeoff.LookupTables.VLAM14_interp.mach', 'pre_mission.core_subsystems.core_aerodynamics.flaps_up.LookupTables.VLAM14_interp.mach']|
| **pre_mission.prop_mass** | [0.] | lbm | ['pre_mission.core_subsystems.core_mass.fixed_mass.engine.prop_mass']|
| **pre_mission.slat_defl_up** | [0.] | deg | ['pre_mission.core_subsystems.core_aerodynamics.flaps_up.BasicFlapsCalculations.slat_defl']|
| **reserve_fuel_frac_mass** | [0.] | lbm | ['post_mission.reserve_fuel.reserve_fuel_frac_mass']|
| **target_range** | [3500.] | nmi | ['range_constraint.target_range']|
| **tau_flaps** | [0.9] | unitless | ['event_xform.tau_flaps']|
| **tau_gear** | [0.2] | unitless | ['event_xform.tau_gear']|
| **taxi.throttle** | [[0.]] | unitless | ['taxi.core_propulsion.turbofan_gasp_bwb.interpolation.throttle']|
| **taxi.vectorize_performance.electric_power_in_0** | [0.] | kW | ['taxi.core_propulsion.vectorize_performance.electric_power_in_0']|
| **taxi.vectorize_performance.nox_rate_0** | [0.] | lbm/h | ['taxi.core_propulsion.vectorize_performance.nox_rate_0']|
| **taxi.vectorize_performance.shaft_power_0** | [0.] | hp | ['taxi.core_propulsion.vectorize_performance.shaft_power_0']|
| **taxi.vectorize_performance.shaft_power_max_0** | [0.] | hp | ['taxi.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **taxi.vectorize_performance.t4_0** | [0.] | degR | ['taxi.core_propulsion.vectorize_performance.t4_0']|
| **traj.accel.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0.] | kW | ['traj.phases.accel.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.accel.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0.] | lbm/h | ['traj.phases.accel.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.accel.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0.] | hp | ['traj.phases.accel.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.accel.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0.] | hp | ['traj.phases.accel.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.accel.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0.] | degR | ['traj.phases.accel.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.ascent.rhs_all.aero_ramps.flap_factor:final_val** | [0.] | unitless | ['traj.phases.ascent.rhs_all.core_aerodynamics.aero_ramps.flap_factor:final_val']|
| **traj.ascent.rhs_all.aero_ramps.flap_factor:initial_val** | [1.] | unitless | ['traj.phases.ascent.rhs_all.core_aerodynamics.aero_ramps.flap_factor:initial_val']|
| **traj.ascent.rhs_all.aero_ramps.gear_factor:final_val** | [0.] | unitless | ['traj.phases.ascent.rhs_all.core_aerodynamics.aero_ramps.gear_factor:final_val']|
| **traj.ascent.rhs_all.aero_ramps.gear_factor:initial_val** | [1.] | unitless | ['traj.phases.ascent.rhs_all.core_aerodynamics.aero_ramps.gear_factor:initial_val']|
| **traj.ascent.rhs_all.dt_flaps** | [3.] | s | ['traj.phases.ascent.rhs_all.core_aerodynamics.aero_ramps.flap_factor:t_duration']|
| **traj.ascent.rhs_all.dt_gear** | [7.] | s | ['traj.phases.ascent.rhs_all.core_aerodynamics.aero_ramps.gear_factor:t_duration']|
| **traj.ascent.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.ascent.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.ascent.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | lbm/h | ['traj.phases.ascent.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.ascent.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.ascent.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.ascent.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.ascent.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.ascent.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.ascent.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.climb1.rhs_all.atmosphere.velocity** | [0. 0. 0. 0.] | ft/s | ['traj.phases.climb1.rhs_all.atmosphere.flight_conditions.velocity']|
| **traj.climb1.rhs_all.speed_bal.rhs:EAS** | [0. 0. 0. 0.] | unitless | ['traj.phases.climb1.rhs_all.mach_balance_group.speed_bal.rhs:EAS']|
| **traj.climb1.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0.] | kW | ['traj.phases.climb1.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.climb1.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0.] | lbm/h | ['traj.phases.climb1.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.climb1.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0.] | hp | ['traj.phases.climb1.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.climb1.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0.] | hp | ['traj.phases.climb1.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.climb1.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0.] | degR | ['traj.phases.climb1.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.climb1.rhs_all.velocity_rate** | [1. 1. 1. 1.] | m/s**2 | ['traj.phases.climb1.rhs_all.ALTITUDE_RATE_MAX.velocity_rate']|
| **traj.climb2.rhs_all.atmosphere.velocity** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | ft/s | ['traj.phases.climb2.rhs_all.atmosphere.flight_conditions.velocity']|
| **traj.climb2.rhs_all.speed_bal.rhs:EAS** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | unitless | ['traj.phases.climb2.rhs_all.mach_balance_group.speed_bal.rhs:EAS']|
| **traj.climb2.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.climb2.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.climb2.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | lbm/h | ['traj.phases.climb2.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.climb2.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.climb2.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.climb2.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.climb2.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.climb2.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.climb2.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.climb2.rhs_all.velocity_rate** | [1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.] | m/s**2 | ['traj.phases.climb2.rhs_all.ALTITUDE_RATE_MAX.velocity_rate']|
| **traj.desc1.rhs_all.atmosphere.velocity** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | ft/s | ['traj.phases.desc1.rhs_all.atmosphere.flight_conditions.velocity']|
| **traj.desc1.rhs_all.speed_bal.rhs:mach** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | unitless | ['traj.phases.desc1.rhs_all.mach_balance_group.speed_bal.rhs:mach']|
| **traj.desc1.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.desc1.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.desc1.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | lbm/h | ['traj.phases.desc1.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.desc1.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.desc1.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.desc1.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.desc1.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.desc1.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.desc1.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.desc1.rhs_all.velocity_rate** | [1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.] | m/s**2 | ['traj.phases.desc1.rhs_all.ALTITUDE_RATE_MAX.velocity_rate']|
| **traj.desc2.rhs_all.atmosphere.velocity** | [0. 0. 0. 0. 0. 0. 0. 0.] | ft/s | ['traj.phases.desc2.rhs_all.atmosphere.flight_conditions.velocity']|
| **traj.desc2.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.desc2.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.desc2.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0. 0. 0. 0. 0.] | lbm/h | ['traj.phases.desc2.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.desc2.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.desc2.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.desc2.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.desc2.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.desc2.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.desc2.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.desc2.rhs_all.velocity_rate** | [1. 1. 1. 1. 1. 1. 1. 1.] | m/s**2 | ['traj.phases.desc2.rhs_all.ALTITUDE_RATE_MAX.velocity_rate']|
| **traj.groundroll.rhs_all.aero_ramps.flap_factor:final_val** | [1.] | unitless | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.flap_factor:final_val']|
| **traj.groundroll.rhs_all.aero_ramps.flap_factor:initial_val** | [1.] | unitless | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.flap_factor:initial_val']|
| **traj.groundroll.rhs_all.aero_ramps.gear_factor:final_val** | [1.] | unitless | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.gear_factor:final_val']|
| **traj.groundroll.rhs_all.aero_ramps.gear_factor:initial_val** | [1.] | unitless | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.gear_factor:initial_val']|
| **traj.groundroll.rhs_all.altitude** | [0. 0. 0. 0.] | ft | ['traj.phases.groundroll.rhs_all.atmosphere.standard_atmosphere.h', 'traj.phases.groundroll.rhs_all.core_aerodynamics.drag_coef.altitude', 'traj.phases.groundroll.rhs_all.core_aerodynamics.kclge.altitude', 'traj.phases.groundroll.rhs_all.core_propulsion.turbofan_gasp_bwb.interpolation.altitude', 'traj.phases.groundroll.rhs_all.core_propulsion.turbofan_gasp_bwb.max_interpolation.altitude']|
| **traj.groundroll.rhs_all.dt_flaps** | [3.] | s | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.flap_factor:t_duration']|
| **traj.groundroll.rhs_all.dt_gear** | [7.] | s | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.gear_factor:t_duration']|
| **traj.groundroll.rhs_all.flight_path_angle** | [0. 0. 0. 0.] | rad | ['traj.phases.groundroll.rhs_all.groundroll_eom.flight_path_angle']|
| **traj.groundroll.rhs_all.t_curr** | [0. 0. 0. 0.] | s | ['traj.phases.groundroll.rhs_all.core_aerodynamics.aero_ramps.time']|
| **traj.groundroll.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0.] | kW | ['traj.phases.groundroll.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.groundroll.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0.] | lbm/h | ['traj.phases.groundroll.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.groundroll.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0.] | hp | ['traj.phases.groundroll.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.groundroll.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0.] | hp | ['traj.phases.groundroll.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.groundroll.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0.] | degR | ['traj.phases.groundroll.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **traj.rotation.rhs_all.aero_ramps.flap_factor:final_val** | [1.] | unitless | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.flap_factor:final_val']|
| **traj.rotation.rhs_all.aero_ramps.flap_factor:initial_val** | [1.] | unitless | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.flap_factor:initial_val']|
| **traj.rotation.rhs_all.aero_ramps.gear_factor:final_val** | [1.] | unitless | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.gear_factor:final_val']|
| **traj.rotation.rhs_all.aero_ramps.gear_factor:initial_val** | [1.] | unitless | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.gear_factor:initial_val']|
| **traj.rotation.rhs_all.altitude** | [0. 0. 0. 0.] | ft | ['traj.phases.rotation.rhs_all.atmosphere.standard_atmosphere.h', 'traj.phases.rotation.rhs_all.core_aerodynamics.drag_coef.altitude', 'traj.phases.rotation.rhs_all.core_aerodynamics.kclge.altitude', 'traj.phases.rotation.rhs_all.core_propulsion.turbofan_gasp_bwb.interpolation.altitude', 'traj.phases.rotation.rhs_all.core_propulsion.turbofan_gasp_bwb.max_interpolation.altitude']|
| **traj.rotation.rhs_all.dt_flaps** | [3.] | s | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.flap_factor:t_duration']|
| **traj.rotation.rhs_all.dt_gear** | [7.] | s | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.gear_factor:t_duration']|
| **traj.rotation.rhs_all.flight_path_angle** | [0. 0. 0. 0.] | rad | ['traj.phases.rotation.rhs_all.rotation_eom.flight_path_angle']|
| **traj.rotation.rhs_all.t_curr** | [0. 0. 0. 0.] | s | ['traj.phases.rotation.rhs_all.core_aerodynamics.aero_ramps.time']|
| **traj.rotation.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0.] | kW | ['traj.phases.rotation.rhs_all.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.rotation.rhs_all.vectorize_performance.nox_rate_0** | [0. 0. 0. 0.] | lbm/h | ['traj.phases.rotation.rhs_all.core_propulsion.vectorize_performance.nox_rate_0']|
| **traj.rotation.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0.] | hp | ['traj.phases.rotation.rhs_all.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.rotation.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0.] | hp | ['traj.phases.rotation.rhs_all.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.rotation.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0.] | degR | ['traj.phases.rotation.rhs_all.core_propulsion.vectorize_performance.t4_0']|
| **vrot.g** | [1.] | lbf/lbm | ['vrot.g']|
| **vrot.rho** | [0.0023769] | slug/ft**3 | ['vrot.rho']|


