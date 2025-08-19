from math import inf
from dlubal.api import rfem

# Connect to the RFEM application
rfem_app = rfem.Application()

# Close all models and prevent overiding them
rfem_app.close_all_models(save_changes=False)

# Create new model named 'steel_hall'
rfem_app.create_model(name='steel_hall')

# Cleanup the model
rfem_app.delete_all_objects()

hall_width_L = 15
hall_height_h_o = 5
hall_height_h_m = 8
frame_spacing = 5
number_frames = 5

# Define list of model objects to be created
lst_1 = [
    # Material
    rfem.structure_core.Material(
        no=1,
        name="S235 | EN 1993-1-1:2005-05"),

    # Sections
    rfem.structure_core.Section(
        no=1,
        material=1,
        name="HEB 220"),

    rfem.structure_core.Section(
        no=2,
        material=1,
        name="IPE 240"),
    rfem.structure_core.Section(
        no=3,
        material=1,
        name="IPE 100 | -- | British Steel"),
    rfem.structure_core.Section(
        no=4,
        material=1,
        name="L 20x20x3 | ČSN EN 10056-1:2003 | Ferona"),

    # Thickness
    rfem.structure_core.Thickness(
        no=1,
        name="Slab",
        material=1,
        uniform_thickness=0.24,
        comment="Test"),
]
# Nodes
for i in range(number_frames):

    j = i * 5

    lst_1.append(rfem.structure_core.Node(
        no=j+1,
        coordinate_1=0,
        coordinate_2=-i*frame_spacing,
        coordinate_3=0))
    lst_1.append(rfem.structure_core.Node(
        no=j+2,
        coordinate_1=0,
        coordinate_2=-i*frame_spacing,
        coordinate_3=-hall_height_h_o))
    lst_1.append(rfem.structure_core.Node(
        no=j+3,
        coordinate_1=hall_width_L/2,
        coordinate_2=-i*frame_spacing,
        coordinate_3=-hall_height_h_m))
    lst_1.append(rfem.structure_core.Node(
        no=j+4,
        coordinate_1=hall_width_L,
        coordinate_2=-i*frame_spacing,
        coordinate_3=-hall_height_h_o))
    lst_1.append(rfem.structure_core.Node(
        no=j+5,
        coordinate_1=hall_width_L,
        coordinate_2=-i*frame_spacing,
        coordinate_3=0))

# Nodes for openings
k = number_frames*5
open_dim_x = hall_width_L/10
open_dim_y = -(number_frames*frame_spacing)/15
solid_support = [k+5, k+6, k+7, k+8]

lst_2 = [
    rfem.structure_core.Node(
        no=k+1,
        coordinate_1=hall_width_L-open_dim_x,
        coordinate_2=open_dim_y,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+2,
        coordinate_1=hall_width_L-open_dim_x,
        coordinate_2=2*open_dim_y,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+3,
        coordinate_1=hall_width_L-2*open_dim_x,
        coordinate_2=2*open_dim_y,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+4,
        coordinate_1=hall_width_L-2*open_dim_x,
        coordinate_2=open_dim_y,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+5,
        coordinate_1=1,
        coordinate_2=1,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+6,
        coordinate_1=2,
        coordinate_2=1,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+7,
        coordinate_1=2,
        coordinate_2=2,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+8,
        coordinate_1=1,
        coordinate_2=2,
        coordinate_3=0),
    rfem.structure_core.Node(
        no=k+9,
        coordinate_1=1,
        coordinate_2=1,
        coordinate_3=-1),
    rfem.structure_core.Node(
        no=k+10,
        coordinate_1=2,
        coordinate_2=1,
        coordinate_3=-1),
    rfem.structure_core.Node(
        no=k+11,
        coordinate_1=2,
        coordinate_2=2,
        coordinate_3=-1),
    rfem.structure_core.Node(
        no=k+12,
        coordinate_1=1,
        coordinate_2=2,
        coordinate_3=-1)
]
# -------------------------------------------------------------
# Lines

# List (str) of line nodes
nodes_no = []
for i in range(number_frames):
    nodes_no.append(i*5+1)

for i in range(number_frames, 0, -1):
    nodes_no.append((i-1)*5+5)
nodes_no.append(1)

lst_3 = [
    rfem.structure_core.Line(
        no=1,
        definition_nodes=nodes_no),

    # Line for opening
    rfem.structure_core.Line(
        no=2,
        definition_nodes=[k+1, k+2, k+3, k+4, k+1]),

    # Lines for solid
    rfem.structure_core.Line(
        no=3,
        definition_nodes=[k+5, k+6, k+7, k+8, k+5]),
    rfem.structure_core.Line(
        no=4,
        definition_nodes=[k+9, k+10, k+11, k+12, k+9]),
    rfem.structure_core.Line(
        no=5,
        definition_nodes=[k+5, k+6, k+10, k+9, k+5]),
    rfem.structure_core.Line(
        no=6,
        definition_nodes=[k+6, k+7, k+11, k+10, k+6]),
    rfem.structure_core.Line(
        no=7,
        definition_nodes=[k+7, k+8, k+12, k+11, k+7]),
    rfem.structure_core.Line(
        no=8,
        definition_nodes=[k+8, k+5, k+9, k+12, k+8]),

    # -------------------------------------------------------------
    # Member Hinges
    rfem.types_for_members.MemberHinge(
        no=1,
        moment_release_mz=inf),
]
# -------------------------------------------------------------
# Members

# Frames
for i in range(number_frames):

    j = i * 5
    k = i * 4
    lst_3.append(
        rfem.structure_core.Member(
            no=k+1,
            node_start=j+1,
            node_end=j+2,
            section_start=1))
    lst_3.append(
        rfem.structure_core.Member(
            no=k+2,
            node_start=j+2,
            node_end=j+3,
            section_start=2))
    lst_3.append(
        rfem.structure_core.Member(
            no=k+3,
            node_start=j+3,
            node_end=j+4,
            section_start=2))
    lst_3.append(
        rfem.structure_core.Member(
            no=k+4,
            node_start=j+4,
            node_end=j+5,
            section_start=1))

# Purlins
for i in range(1, number_frames):

    j = (i-1) * 5
    lst_3.append(
        rfem.structure_core.Member(
            no=4*number_frames+i,
            node_start=j+2,
            node_end=j+7,
            section_start=3,
            member_hinge_start=1,
            member_hinge_end=1))
    lst_3.append(
        rfem.structure_core.Member(
            no=4*number_frames+i + number_frames-1,
            node_start=j+3,
            node_end=j+8,
            section_start=3))
    lst_3.append(
        rfem.structure_core.Member(
            no=4*number_frames+i + 2*number_frames-2,
            node_start=j+4,
            node_end=j+9,
            rotation_angle=180.0,
            section_start=3,
            member_hinge_start=1,
            member_hinge_end=1))

# Diagonals on the wall
j = 4*number_frames + 3*(number_frames-1)
for i in range(1, number_frames):

    k = j + (i-1)*4

    lst_3.append(
        rfem.structure_core.Member(
            no=k+1,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=(i-1)*5+1,
            node_end=(i-1)*5+7,
            section_start=4))
    lst_3.append(
        rfem.structure_core.Member(
            no=k+2,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=(i-1)*5+2,
            node_end=(i-1)*5+6,
            section_start=4))
    lst_3.append(
        rfem.structure_core.Member(
            no=k+3,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=(i-1)*5+5,
            node_end=(i-1)*5+9,
            section_start=4))
    lst_3.append(
        rfem.structure_core.Member(
            no=k+4,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=(i-1)*5+4,
            node_end=(i-1)*5+10,
            section_start=4))

# Diagonals on the roof
j += 4*(number_frames-1)
if number_frames > 1:
    lst_3.append(
        rfem.structure_core.Member(
            no=j+1,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=2,
            node_end=8,
            section_start=4))
    lst_3.append(
        rfem.structure_core.Member(
            no=j+2,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=7,
            node_end=3,
            section_start=4))
    lst_3.append(
        rfem.structure_core.Member(
            no=j+3,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=3,
            node_end=9,
            section_start=4))
    lst_3.append(
        rfem.structure_core.Member(
            no=j+4,
            type=rfem.structure_core.Member.TYPE_TENSION,
            node_start=4,
            node_end=8,
            section_start=4))

# -------------------------------------------------------------
# Surfaces
lst_3.append(
    rfem.structure_core.Surface(
        no=1,
        boundary_lines=[1],
        thickness=1))
lst_3.append(
    rfem.structure_core.Surface(
        no=2,
        boundary_lines=[3],
        thickness=1))
lst_3.append(
    rfem.structure_core.Surface(
        no=3,
        boundary_lines=[4],
        thickness=1))
lst_3.append(
    rfem.structure_core.Surface(
        no=4,
        boundary_lines=[5],
        thickness=1))
lst_3.append(
    rfem.structure_core.Surface(
        no=5,
        boundary_lines=[6],
        thickness=1))
lst_3.append(
    rfem.structure_core.Surface(
        no=6,
        boundary_lines=[7],
        thickness=1))
lst_3.append(
    rfem.structure_core.Surface(
        no=7,
        boundary_lines=[8],
        thickness=1))

# -------------------------------------------------------------
# Openings
lst_3.append(
    rfem.structure_core.Opening(
        no=1,
        boundary_lines=[2],
        comment="waste passage"))

# -------------------------------------------------------------
# Nodal Supports

# List (str) of supported nodes
nodes_no = []
for i in range(number_frames):

    j = i * 5
    nodes_no.append(j+1)
    nodes_no.append(j+5)

lst_3.append(
    rfem.types_for_nodes.NodalSupport(
        no=1,
        nodes=nodes_no,
        spring_x=inf,
        spring_y=inf,
        spring_z=inf,
        rotational_restraint_x=0,
        rotational_restraint_y=0,
        rotational_restraint_z=0))

# Support of solid
lst_3.append(
    rfem.types_for_nodes.NodalSupport(
        no=2,
        nodes=solid_support,
        spring_x=inf,
        spring_y=inf,
        spring_z=inf,
        rotational_restraint_x=0,
        rotational_restraint_y=0,
        rotational_restraint_z=0))

# -------------------------------------------------------------
# Solid
lst_3.append(
    rfem.structure_core.Solid(
        no=1,
        boundary_surfaces=[2, 3, 4, 5, 6, 7],
        material=1))

# -------------------------------------------------------------
# Static Analysis Settings
lst_3.append(
    rfem.loading.StaticAnalysisSettings(
        no=1,
        analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_GEOMETRICALLY_LINEAR,
    )
)

# -------------------------------------------------------------
# Load Cases
lst_3.append(
    rfem.loading.LoadCase(
        no=1,
        name="Self-weight",
        self_weight_active=True,
        self_weight_factor_x=0.0,
        self_weight_factor_y=0.0,
        self_weight_factor_z=10.0))

lst_3.append(
    rfem.loading.LoadCase(
        no=2,
        name="Live loads"))
lst_3.append(
    rfem.loading.LoadCase(
        no=3,
        name="Test 1"))
lst_3.append(
    rfem.loading.LoadCase(
        no=4,
        name="Test 2"))
lst_3.append(
    rfem.loading.LoadCase(
        no=5,
        name="Test 3"))
lst_3.append(
    rfem.loading.LoadCase(
        no=6,
        name="Test 4"))
lst_3.append(
    rfem.loading.LoadCase(
        no=7,
        name="Test 5"))
lst_3.append(
    rfem.loading.LoadCase(
        no=8,
        name="Test 6"))
lst_3.append(
    rfem.loading.LoadCase(
        no=9,
        name="Test 7"))
lst_3.append(
    rfem.loading.LoadCase(
        no=10,
        name="Test 8"))
lst_3.append(
    rfem.loading.LoadCase(
        no=11,
        name="Test 9"))
lst_3.append(
    rfem.loading.LoadCase(
        no=12,
        name="Test 10"))
lst_3.append(
    rfem.loading.LoadCase(
        no=13,
        name="Test 11"))
lst_3.append(
    rfem.loading.LoadCase(
        no=14,
        name="Test 12"))

# -------------------------------------------------------------
# Nodal Forces
lst_3.append(
    rfem.loads.NodalLoad(
        no=1,
        load_case=3,
        nodes=[9, 4, 7, 2],
        load_direction=rfem.loads.NodalLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        force_magnitude=2000.0))

# -------------------------------------------------------------
# Member Loads
lst_3.append(
    rfem.loads.MemberLoad(
        no=1,
        load_case=1,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_UNIFORM,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        magnitude=5000))
lst_3.append(
    rfem.loads.MemberLoad(
        no=2,
        load_case=2,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_UNIFORM,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        magnitude=5000,
        has_force_eccentricity=True,
        eccentricity_y_at_start=0.01,
        eccentricity_z_at_start=0.02))
lst_3.append(
    rfem.loads.MemberLoad(
        no=3,
        load_case=3,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_UNIFORM_TOTAL,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        magnitude=5000))
lst_3.append(
    rfem.loads.MemberLoad(
        no=4,
        load_case=4,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_CONCENTRATED_1,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        distance_a_is_defined_as_relative=False,
        magnitude=5000,
        distance_a_absolute=1.2))
lst_3.append(
    rfem.loads.MemberLoad(
        no=5,
        load_case=5,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_CONCENTRATED_N,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        distance_a_is_defined_as_relative=False,
        distance_b_is_defined_as_relative=False,
        magnitude=5000,
        count_n=2,
        distance_a_absolute=1,
        distance_b_absolute=2))
lst_3.append(
    rfem.loads.MemberLoad(
        no=6,
        load_case=6,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_CONCENTRATED_2_2,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        distance_a_is_defined_as_relative=False,
        distance_b_is_defined_as_relative=False,
        distance_c_is_defined_as_relative=False,
        magnitude=5000,
        distance_a_absolute=1,
        distance_b_absolute=2,
        distance_c_absolute=3))
lst_3.append(
    rfem.loads.MemberLoad(
        no=7,
        load_case=7,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_CONCENTRATED_2,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        distance_a_is_defined_as_relative=False,
        distance_b_is_defined_as_relative=False,
        magnitude_1=5000,
        magnitude_2=6000,
        distance_a_absolute=1,
        distance_b_absolute=2))

# Parameter 'varying_load_parameters' can't be set yet
"""
lst_3.append(
    rfem.loads.MemberLoad(
        no=8,
        load_case=8,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_CONCENTRATED_VARYING,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        varying_load_parameters=[[1, 4000], [2, 5000]])
"""
lst_3.append(
    rfem.loads.MemberLoad(
        no=9,
        load_case=9,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_TRAPEZOIDAL,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        distance_a_is_defined_as_relative=False,
        distance_b_is_defined_as_relative=False,
        magnitude_1=4000,
        magnitude_2=8000,
        distance_a_absolute=1,
        distance_b_absolute=2))
lst_3.append(
    rfem.loads.MemberLoad(
        no=10,
        load_case=10,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_TAPERED,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        distance_a_is_defined_as_relative=False,
        distance_b_is_defined_as_relative=False,
        magnitude_1=4000,
        magnitude_2=8000,
        distance_a_absolute=1,
        distance_b_absolute=2))
lst_3.append(
    rfem.loads.MemberLoad(
        no=11,
        load_case=11,
        members=[2, 3, 6, 7],
        load_distribution=rfem.loads.MemberLoad.LOAD_DISTRIBUTION_PARABOLIC,
        load_direction=rfem.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        magnitude_1=4000,
        magnitude_2=8000,
        magnitude_3=12000))

# Parameter 'varying_load_parameters' can't be set yet
"""
lst_3.append(
    rfem.loads.MemberLoad(
        no=13,
        load_case=12,
        members=[2, 3, 6, 7],
        load_distribution=MEMBER_LOAD_LOAD_DISTRIBUTION_VARYING,
        load_direction=rfem.loads.MEMBER_LOAD_LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        varying_load_parameters=[[1, 4000], [2, 5000]])
lst_3.append(
    rfem.loads.MemberLoad(
        no=14,
        load_case=13,
        members=[2, 3, 6, 7],
        load_distribution=MEMBER_LOAD_LOAD_DISTRIBUTION_VARYING_IN_Z,
        load_direction=rfem.loads.MEMBER_LOAD_LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        varying_load_parameters=[[1,
        4000],
        [2,
        5000]])
"""

# -------------------------------------------------------------
# Surface Loads
lst_3.append(rfem.loads.SurfaceLoad(
    no=1,
    load_case=3,
    surfaces=[3],
    uniform_magnitude=20000))

# Set the list of model objects to be created
rfem_app.create_object_list(lst_1)
rfem_app.create_object_list(lst_2)
rfem_app.create_object_list(lst_3)

# Calculate the model
rfem_app.calculate_all(skip_warnings=False)

# Close the connection
rfem_app.close_connection()
