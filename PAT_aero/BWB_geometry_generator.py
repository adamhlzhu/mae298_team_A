import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from PAT.geometry import Point, HybridLoop, SplineSurface, Model
from PAT.utils import Airfoil, VspFile
from itertools import product
import pandas as pd


def define_and_generate_BWB(
    junk_dir: Path | str,
    nose_length: float = 15, # (feet)
    fuselage_length: float = 100, # front to back length of BWB (feet)
    fuselage_width: float = 20, # (feet)
    height_to_width: float = 1, # (unitless)
    tail_height: float = 8, # (feet)
    wing_span: float = 120, # (feet)
    wing_length: float = 40, # (feet)
    wing_sweep: float = 25, # (degrees)
    wing_dihedral: float = 1, # (degrees)
    wing_croot: float = 25, # (feet)
    wing_taper: float = 0.6, # (unitless)
    wing_twist: float = -1, # (degrees/foot)
    wing_alpha: float = 2, # root incidence (degrees)
    wing_height: float = 6, # (feet)
    wing_x: float = 45, # (feet)
    stabilizer_cant: float = 45, # (degrees)
    stabilizer_croot: float = 10, # (feet)
    stabilizer_taper: float = 0.6, # (unitless)
    stabilizer_length: float = 12, # (feet)
    stabilizer_sweep: float = 15, # (degrees)
):
    """Generate a BWB aircraft geometry based on given parameters."""

    print("Generating model with the following parameters:")
    print(f"  Nose length: {nose_length} ft")
    print(f"  Fuselage length: {fuselage_length} ft")
    print(f"  Fuselage width: {fuselage_width} ft")
    print(f"  Height to width ratio: {height_to_width}")
    print(f"  Tail height: {tail_height} ft")
    print(f"  Wing span: {wing_span} ft")
    print(f"  Wing length: {wing_length} ft")
    print(f"  Wing sweep: {wing_sweep} deg")
    print(f"  Wing dihedral: {wing_dihedral} deg")
    print(f"  Wing croot: {wing_croot} ft")
    print(f"  Wing taper: {wing_taper}")
    print(f"  Wing twist: {wing_twist} deg/ft")
    print(f"  Wing alpha: {wing_alpha} deg")
    print(f"  Wing height: {wing_height} ft")
    print(f"  Wing x: {wing_x} ft")
    print(f"  Stabilizer cant: {stabilizer_cant} deg")
    print(f"  Stabilizer croot: {stabilizer_croot} ft")
    print(f"  Stabilizer taper: {stabilizer_taper}")
    print(f"  Stabilizer span: {stabilizer_length} ft")
    print(f"  Stabilizer sweep: {stabilizer_sweep} deg")

    deg2rad = np.pi/180

    fuselage_height = fuselage_width*height_to_width

    wing_sweep *= deg2rad
    wing_dihedral *= deg2rad
    wing_alpha *= deg2rad
    wing_twist *= deg2rad/wing_length
    stabilizer_cant *= deg2rad
    stabilizer_sweep *= deg2rad
    
    pt_tip = Point(
        0,
        0,
        0,
        "tip")
    pt_flank = Point(
        nose_length,
        fuselage_width/2 + 2,
        0,
        "flank")
    pt_wingroot_le = Point(
        wing_x,
        max(fuselage_width/2 + 15, wing_span/2-wing_length),
        wing_height,
        "wing")
    pt_wingtip_le = Point(
        pt_wingroot_le.x + wing_length*np.sin(wing_sweep),
        pt_wingroot_le.y + wing_length,
        pt_wingroot_le.z + wing_length*np.sin(wing_dihedral),
        "wingtip_le")
    pt_wingtip_te = Point(
        pt_wingroot_le.x + wing_length*np.sin(wing_sweep) + wing_croot*wing_taper*np.cos(wing_alpha+wing_length*wing_twist),
        pt_wingroot_le.y + wing_length,
        pt_wingroot_le.z + wing_length*np.sin(wing_dihedral) + wing_croot*wing_taper*np.sin(wing_alpha+wing_length*wing_twist),
        "wingtip_te")
    pt_wingroot_te = Point(
        pt_wingroot_le.x + wing_croot*np.cos(wing_alpha), 
        pt_wingroot_le.y, 
        pt_wingroot_le.z + wing_croot*np.sin(wing_alpha), 
        "wingroot_te")
    pt_tail = Point(
        pt_tip.x + fuselage_length,
        pt_tip.y,
        pt_tip.z + tail_height,
        "tail")

    pt_stabroot_le = Point(
        pt_tail.x - 15,
        pt_tail.y + 10,
        pt_tail.z,
        "stabroot_le")
    pt_stabtip_le = Point(
        pt_stabroot_le.x + stabilizer_length*np.sin(stabilizer_sweep),
        pt_stabroot_le.y + stabilizer_length*np.sin(stabilizer_cant),
        pt_stabroot_le.z + stabilizer_length*np.cos(stabilizer_cant),
        "stabtip_le")
    pt_stabtip_te = Point(
        pt_stabtip_le.x + stabilizer_croot*stabilizer_taper,
        pt_stabtip_le.y,
        pt_stabtip_le.z,
        "stabtip_te")
    pt_stabroot_te = Point(
        pt_stabroot_le.x + stabilizer_croot,
        pt_stabroot_le.y,
        pt_stabroot_le.z,
        "stabroot_te")


    wing_points = [
        pt_tip,
        pt_flank,
        pt_wingroot_le,
        pt_wingtip_le,
        pt_wingtip_te,
        pt_wingroot_te, 
        pt_tail,
        pt_wingroot_te.reflect_y(),
        pt_wingtip_te.reflect_y(),
        pt_wingtip_le.reflect_y(),
        pt_wingroot_le.reflect_y(),
        pt_flank.reflect_y(),
        ]
    rstab_points = [
        pt_stabroot_le,
        pt_stabtip_le,
        pt_stabtip_te,
        pt_stabroot_te,
    ]
    lstab_points = [
        pt_stabroot_le.reflect_y(),
        pt_stabroot_te.reflect_y(),
        pt_stabtip_te.reflect_y(),
        pt_stabtip_le.reflect_y(),
    ]

    wing_loop = HybridLoop(wing_points)
    rstab_loop = HybridLoop(rstab_points)
    lstab_loop = HybridLoop(lstab_points)

    wing_loop.set_smooth("tip", [0, 17, 0])
    # loop.set_smooth("flank", [20, 5, 0])
    # loop.set_smooth("flank (reflected)", [-20, 5, 0])
    wing_loop.set_smooth("wingtip_le", [0, 0, 0])
    wing_loop.set_smooth("wingtip_le (reflected)", [0, 0, 0])
    wing_loop.set_smooth("wingtip_te", [0, 0, 0])
    wing_loop.set_smooth("wingtip_te (reflected)", [0, 0, 0])
    wing_loop.set_smooth("tail", [0, -50, 0])

    rstab_loop.set_smooth("stabroot_le", [0, 0, 0])
    rstab_loop.set_smooth("stabroot_te", [0, 0, 0])
    rstab_loop.set_smooth("stabtip_le", [0, 0, 0])
    rstab_loop.set_smooth("stabtip_te", [0, 0, 0])

    lstab_loop.set_smooth("stabroot_le (reflected)", [0, 0, 0])
    lstab_loop.set_smooth("stabroot_te (reflected)", [0, 0, 0])
    lstab_loop.set_smooth("stabtip_le (reflected)", [0, 0, 0])
    lstab_loop.set_smooth("stabtip_te (reflected)", [0, 0, 0])

    # Generate and plot the 3D loop
    ax = wing_loop.plot(show_tangents=True)
    ax = rstab_loop.plot(show_tangents=True)
    ax = lstab_loop.plot(show_tangents=True)
    ax.set_title("BWB Planform")
    ax.axis('equal')
    ax.legend()

    # Create the wings
    wing_surface = SplineSurface(name="Wing", loop=wing_loop, default_section_density=0.35)
    rstab_surface = SplineSurface(name="R_Stab", loop=rstab_loop, default_section_density=0.55)
    lstab_surface = SplineSurface(name="L_Stab", loop=lstab_loop, default_section_density=0.55)
    chord = np.sqrt(fuselage_length**2 + tail_height**2)
    naca2412 = Path('airfoils/NACA2412.dat')
    naca0012 = Path('airfoils/NACA0012.dat')
    body_af = Airfoil(naca2412, thickness_scale=fuselage_height/(0.12*chord)).invert()
    wall_af = Airfoil(naca2412, thickness_scale=fuselage_height/(0.12*chord)).invert()
    wing_af = Airfoil(naca2412, thickness_scale=0.9)
    symm_af = Airfoil(naca0012)
    wing_surface.set_airfoil_at_control_point(0, body_af)
    wing_surface.set_airfoil_at_control_point(2, wing_af)
    wing_surface.set_airfoil_at_control_point(10, wing_af)
    wing_surface.set_airfoil_at_control_point(1, wall_af)
    wing_surface.set_airfoil_at_control_point(11, wall_af)
    wing_surface.calc_sectioned_geometry()
    rstab_surface.set_airfoil_at_control_point(0, symm_af)
    rstab_surface.calc_sectioned_geometry()
    lstab_surface.set_airfoil_at_control_point(0, symm_af)
    lstab_surface.calc_sectioned_geometry()

    # # Calculate the points for plotting.
    # le_pts, _, te_pts = wing_surface.calc_plot_points()
    # le_pts_rstab, _, te_pts_rstab = rstab_surface.calc_plot_points()
    # le_pts_lstab, _, te_pts_lstab = lstab_surface.calc_plot_points()

    # # Plot the resulting surface.
    # fig = plt.figure(figsize=(10, 8))
    # ax = fig.add_subplot(111, projection='3d')

    # # Plot LE and TE
    # ax.plot(le_pts[0], le_pts[1], le_pts[2], 'r-', label='Wing Leading Edge')
    # ax.plot(te_pts[0], te_pts[1], te_pts[2], 'b-', label='Wing Trailing Edge')
    # ax.plot(le_pts_rstab[0], le_pts_rstab[1], le_pts_rstab[2], 'r-', label='R_Stab Leading Edge')
    # ax.plot(te_pts_rstab[0], te_pts_rstab[1], te_pts_rstab[2], 'b-', label='R_Stab Trailing Edge')
    # ax.plot(le_pts_lstab[0], le_pts_lstab[1], le_pts_lstab[2], 'r-', label='L_Stab Leading Edge')
    # ax.plot(te_pts_lstab[0], te_pts_lstab[1], te_pts_lstab[2], 'b-', label='L_Stab Trailing Edge')

    # # Plot chord lines
    # for i in range(len(le_pts[0])):
    #     ax.plot(
    #         [le_pts[0][i], te_pts[0][i]], 
    #         [le_pts[1][i], te_pts[1][i]],
    #         [le_pts[2][i], te_pts[2][i]],
    #         'g--',
    #         alpha=0.5
    #         )
    # for i in range(len(le_pts_rstab[0])):
    #     ax.plot(
    #         [le_pts_rstab[0][i], te_pts_rstab[0][i]], 
    #         [le_pts_rstab[1][i], te_pts_rstab[1][i]],
    #         [le_pts_rstab[2][i], te_pts_rstab[2][i]],
    #         'g--',
    #         alpha=0.5
    #         )
    # for i in range(len(le_pts_lstab[0])):
    #     ax.plot(
    #         [le_pts_lstab[0][i], te_pts_lstab[0][i]], 
    #         [le_pts_lstab[1][i], te_pts_lstab[1][i]],
    #         [le_pts_lstab[2][i], te_pts_lstab[2][i]],
    #         'g--',
    #         alpha=0.5
    #         )

    # ax.set_xlabel('X')
    # ax.set_ylabel('Y (Span)')
    # ax.set_zlabel('Z')
    # ax.set_title("SplineSurface Visualization")
    # ax.legend()
    # ax.axis('equal')
    # plt.show()

    the_plane = Model([wing_surface, rstab_surface, lstab_surface], 'FEET', 0)

    avl_file = the_plane.get_AvlFile()
    # avl_file.save_to_file(Path("PAT_aero/data/test.avl"))

    vsp_file = the_plane.get_VspFile(Path(junk_dir), 0.8)
    vsp_file.save_to_file(Path("temp/test.vsp3"))

    return the_plane, avl_file, vsp_file
    

def run_avl(avl_file, alphas, betas, mach):
    avl_out = avl_file.run_avl(alphas, betas, Path("software/avl.exe"), Path("temp/temp.txt"), mach)
    print(avl_out)

def run_vsp(
        vsp_file: VspFile, 
        alpha_start: float, 
        alpha_end: float, 
        alpha_npts: int, 
        junk_loc: Path | str, 
        Xref: float, 
        Yref: float, 
        Zref: float, 
        mach_start: float, 
        mach_end: float, 
        mach_npts: int, 
        Re_start: float, 
        Re_end: float, 
        Re_npts: int,
        debug: bool,
        Sref: float = None,
        Bref: float = None,
        Cref: float = None,
        ):
    
    vsp_out: list[dict[str, float | str]] = []
    vsp_out = vsp_file.run_vspaero(
        alpha_start,
        alpha_end,
        alpha_npts,
        junk_loc,
        Xref=Xref,
        Yref=Yref,
        Zref=Zref,
        mach_start=mach_start,
        mach_end=mach_end,
        mach_npts=mach_npts,
        Re_start=Re_start, 
        Re_end=Re_end,
        Re_npts=Re_npts,
        Sref=Sref,
        Bref=Bref,
        Cref=Cref,
        debug=debug
        )

    CLtot: list[float] = []
    CDtot: list[float] = []
    for result in vsp_out:
        CLtot.append(result["CLwtot"])
        CDtot.append(result["CDwtot"])

    return CLtot, CDtot



if __name__ == "__main__":
    fuselage_length_start = 80
    fuselage_length_end = 120
    fuselage_length_num = 5
    fuselage_htw_start = 0.5
    fuselage_htw_end = 1.3
    fuselage_htw_num = 5

    fuselage_lengths = np.linspace(fuselage_length_start, fuselage_length_end, num=fuselage_length_num)
    fuselage_htws = np.linspace(fuselage_htw_start, fuselage_htw_end, num=fuselage_htw_num)
    results = {}
    
    for combo in product(fuselage_lengths, fuselage_htws):
        the_model, avl_file, vsp_file = define_and_generate_BWB(
            "temp/temp.txt",
            nose_length=15, # (feet)
            fuselage_length=combo[0], # front to back length of BWB (feet)
            fuselage_width=20, # (feet)
            height_to_width=combo[1], #TODO
            tail_height=8, # (feet)
            wing_span=120, # (feet)
            wing_length=40, # (feet)
            wing_sweep=25, # (degrees)
            wing_dihedral=1, # (degrees)
            wing_croot=25, # (feet)
            wing_taper=0.6, # (unitless)
            wing_twist=-1, # (degrees/foot)
            wing_alpha=2, # root incidence (degrees)
            wing_height=4, # (feet)
            wing_x=45, # (feet)
        )

        CLtot, CDtot = run_vsp(
            vsp_file,
            0,
            10,
            5,
            "temp/",
            0,
            0,
            0,
            0.74,
            1,
            1,
            8e7,
            8e7,
            1,
            False
        )

        print(CLtot, CDtot)

        results[combo] = [CLtot, CDtot]

    df = pd.DataFrame(results)
    df.to_csv("temp/BWB_coefficients.CSV")
