import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from PAT.geometry import Point, HybridLoop, SplineSurface, Model
from PAT.utils import Airfoil


def define_and_generate_BWB(
    junk_dir,
    nose_length = 15, # (feet)
    fuselage_length = 100, # front to back length of BWB (feet)
    fuselage_width = 20, # (feet)
    height_to_width = 1, #TODO
    tail_height = 8, # (feet)
    wing_span = 120, # (feet)
    wing_length = 40, # (feet)
    wing_sweep = 25, # (degrees)
    wing_dihedral = 1, # (degrees)
    wing_croot = 25, # (feet)
    wing_taper = 0.6, # (unitless)
    wing_twist = -1, # (degrees/foot)
    wing_alpha = 2, # root incidence (degrees)
    wing_height = 10, # (feet)
    wing_x = 45, # (feet)
):
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

    deg2rad = np.pi/180

    fuselage_height = fuselage_width*height_to_width

    wing_sweep *= deg2rad
    wing_dihedral *= deg2rad
    wing_alpha *= deg2rad
    wing_twist *= deg2rad/wing_length
    

    pt_tip = Point(0, 0, 0, "tip")
    pt_flank = Point(nose_length, fuselage_width/2 + 2, 0, "flank")
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

    # pt_vstab = Point(
    #     pt_tip.x - 5,
    #     pt_tip.y,
    #     pt_tip.z + tail_height - 1,
    #     "vstab"
    # )

    points = [
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

    loop = HybridLoop(points)

    loop.set_smooth("tip", [0, 17, 0])
    # loop.set_smooth("flank", [20, 5, 0])
    # loop.set_smooth("flank (reflected)", [-20, 5, 0])
    loop.set_smooth("wingtip_le", [0, 0, 0])
    loop.set_smooth("wingtip_le (reflected)", [0, 0, 0])
    loop.set_smooth("wingtip_te", [0, 0, 0])
    loop.set_smooth("wingtip_te (reflected)", [0, 0, 0])
    loop.set_smooth("tail", [0, -50, 0])

    # Get slices of the loop
    slices = loop.get_slices(slice_density=2.0)

    # Generate and plot the 3D loop
    ax = loop.plot(show_tangents=True)
    ax.set_title("BWB Planform")
    ax.axis('equal')
    ax.legend()

    # Create the main wing.
    wing_surface = SplineSurface(name="Wing", loop=loop, default_section_density=0.35)
    chord = np.sqrt(fuselage_length**2 + tail_height**2)
    naca2412 = Path('airfoils/NACA2412.dat')
    body_af = Airfoil(naca2412, thickness_scale=fuselage_width*height_to_width/(0.12*chord)).invert()
    wall_af = Airfoil(naca2412, thickness_scale=fuselage_width*height_to_width/(0.12*chord)).invert()
    wing_af = Airfoil(naca2412, thickness_scale=0.9)
    wing_surface.set_airfoil_at_control_point(0, body_af)
    wing_surface.set_airfoil_at_control_point(2, wing_af)
    wing_surface.set_airfoil_at_control_point(10, wing_af)
    wing_surface.set_airfoil_at_control_point(1, wall_af)
    wing_surface.set_airfoil_at_control_point(11, wall_af)
    wing_surface.calc_sectioned_geometry()

    # Calculate the points for plotting.
    le_pts, _, te_pts = wing_surface.calc_plot_points()

    # Plot the resulting surface.
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot LE and TE
    ax.plot(le_pts[0], le_pts[1], le_pts[2], 'r-', label='Leading Edge')
    ax.plot(te_pts[0], te_pts[1], te_pts[2], 'b-', label='Trailing Edge')

    # Plot chord lines
    for i in range(len(le_pts[0])):
        ax.plot(
            [le_pts[0][i], te_pts[0][i]], 
            [le_pts[1][i], te_pts[1][i]],
            [le_pts[2][i], te_pts[2][i]],
            'g--',
            alpha=0.5
            )

    ax.set_xlabel('X')
    ax.set_ylabel('Y (Span)')
    ax.set_zlabel('Z')
    ax.set_title("SplineSurface Visualization")
    ax.legend()
    ax.axis('equal')
    # plt.show()

    # Plot the 2D slices
    plt.figure(figsize=(8, 6))
    for y_coord, points_2d in slices.items():
        if points_2d:
            x_coords, z_coords = zip(*points_2d)
            plt.scatter(x_coords, z_coords, label=f'y = {y_coord:.2f}')
    plt.title("2D Slices of the Hybrid Loop (X-Z Plane)")
    plt.xlabel("X coordinate")
    plt.ylabel("Z coordinate")
    plt.axis('equal')
    plt.legend()
    plt.grid(True)
    # plt.show()

    the_plane = Model([wing_surface], 'FEET', 0)

    avl_file = the_plane.get_AvlFile()
    # avl_file.save_to_file(Path("PAT_aero/data/test.avl"))

    vsp_file = the_plane.get_VspFile(Path(junk_dir), 0.8)
    vsp_file.save_to_file(Path("temp/test.vsp3"))

    return the_plane, avl_file, vsp_file
    

def run_avl(avl_file, alphas, betas, mach):
    avl_out = avl_file.run_avl(alphas, betas, Path("software/avl.exe"), Path("temp/temp.txt"), mach)
    print(avl_out)

def run_vsp(
        vsp_file, 
        alpha_start, 
        alpha_end, 
        alpha_npts, 
        junk_loc, 
        Xref, 
        Yref, 
        Zref, 
        mach_start, 
        mach_end, 
        mach_npts, 
        Re_start, 
        Re_end, 
        Re_npts,
        debug,
        Sref = None,
        Bref = None,
        Cref = None,
        ):
    
    vsp_out = []
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

    CLtot = []
    CDtot = []
    for result in vsp_out:
        CLtot.append(result["CLwtot"])
        CDtot.append(result["CDwtot"])

    return CLtot, CDtot



if __name__ == "__main__":
    define_and_generate_BWB(
        "temp/temp.txt",
    )
    # run_vsp()
    # print(CLtot, CDtot)