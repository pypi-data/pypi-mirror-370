from math import inf, pi
from dlubal.api import rfem

# Basic Settings
n_u = 3
n = 18
n_s = 11

purlins_1 = True
purlins_2 = True

W = 8
d = 0.5

L = 30
H = 7
h_1 = 3
h_2 = 5
R_1 = None
R_2 = None

L_s = 12
H_1 = 4.5
H_2 = 6
h = 1

section_top_chord_center = 1
section_bottom_chord_center = 1
section_diagonals_center = 1
section_columns_center = 1
section_girders_center = 1
section_purlins_center = 1

section_top_chord_side = 1
section_bottom_chord_side = 1
section_diagonals_side = 1
section_columns_side = 1
section_girders_side = 1
section_purlins_side = 1

thickness_material = 1
thickness_roof_slab_center = 1
roof_slab_center_thick = 0.2
thickness_roof_slab_side = 2
roof_slab_side_thick = 0.2

R_1 = h_1 / 2 + (L ** 2) / (8 * h_1)
R_2 = h_2 / 2 + (L ** 2) / (8 * h_2)

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Close all models opened in application without saving
    rfem_app.close_all_models(save_changes=False)

    # Create new model named 'steel_station'
    rfem_app.create_model(name='steel_station')

    # Cleanup the model
    rfem_app.delete_all_objects()

    material_section_thickness = [
        rfem.structure_core.Material(
            no=1,
            name='S235 | CYS EN 1993-1-1:2009-03'),

        rfem.structure_core.Material(
            no=2,
            name='C12/15'),

        rfem.structure_core.Section(
            no=1,
            name='IPE 200 | -- | British Steel',
            material=1),

        rfem.structure_core.Thickness(
            no=thickness_roof_slab_center,
            user_defined_name_enabled=True, name='Roof',
            uniform_thickness=roof_slab_center_thick,
            material=thickness_material),

        rfem.structure_core.Thickness(
            no=thickness_roof_slab_side,
            user_defined_name_enabled=True,
            name='Roof',
            uniform_thickness=roof_slab_side_thick,
            material=thickness_material)
    ]
    rfem_app.create_object_list(material_section_thickness)

    supports = []
    L_1 = L / n
    node_count = 1
    nodes_list = []

    for j in range(n_u + 1):

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=0.0,
                coordinate_2=j * W,
                coordinate_3=-H))
        node_count += 1

        for i in range(1, n):

            x = i * L_1

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=x,
                    coordinate_2=j * W,
                    coordinate_3=-((R_1 ** 2 - (x - L / 2) ** 2) ** 0.5 + h_1 - R_1) - H))
            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L,
                coordinate_2=j * W,
                coordinate_3=-H))
        node_count += 1

        for i in range(n):

            x = L_1 / 2 + i * L_1

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=x,
                    coordinate_2=j * W,
                    coordinate_3=-((R_2 ** 2 - (x - L / 2) ** 2) ** 0.5 + h_2 - R_2) - H))
            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=0.0,
                coordinate_2=j * W,
                coordinate_3=0.0))

        supports.append(node_count)

        node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L,
                coordinate_2=j * W,
                coordinate_3=0.0))

        supports.append(node_count)
        node_count += 1

    member_hinge = rfem.types_for_members.MemberHinge(
        no=1,
        axial_release_n=inf,
        axial_release_vy=inf,
        axial_release_vz=inf,
        moment_release_mt=inf)
    rfem_app.create_object(member_hinge)

    mem_num = 1
    members_list = []
    lines_list = []
    nn = 2 * n + 3

    for j in range(n_u + 1):

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=1 + j * nn,
                node_end=j * nn + 2,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_bottom_chord_center,
                rotation_angle=pi, member_hinge_start=1))

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                type=rfem.structure_core.Line.TYPE_ARC,
                arc_first_node=1 + j * nn,
                arc_second_node=j * nn + 2,
                arc_control_point={'x': L_1 / 2,
                                   'y': j * W,
                                   'z': -((R_1 ** 2 - (L_1 / 2 - L / 2) ** 2) ** 0.5 + h_1 - R_1) - H}))
        mem_num += 1

        for i in range(n - 2):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num, node_start=i + 2 + j * nn,
                    node_end=i + 3 + j * nn,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_bottom_chord_center,
                    rotation_angle=pi))
            x = 1.5 * L_1 + i * L_1

            lines_list.append(
                rfem.structure_core.Line(
                    no=mem_num,
                    type=rfem.structure_core.Line.TYPE_ARC,
                    arc_first_node=i + 2 + j * nn,
                    arc_second_node=i + 3 + j * nn,
                    arc_control_point={'x': x,
                                       'y': j * W,
                                       'z': -((R_1 ** 2 - (x - L / 2) ** 2) ** 0.5 + h_1 - R_1) - H}))
            mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num, node_start=n + j * nn,
                node_end=n + 1 + j * nn,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_bottom_chord_center,
                rotation_angle=pi,
                member_hinge_end=1))

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                type=rfem.structure_core.Line.TYPE_ARC,
                arc_first_node=n + j * nn,
                arc_second_node=n + 1 + j * nn,
                arc_control_point={
                    'x': L - L_1 / 2,
                    'y': j * W,
                    'z': -((R_1 ** 2 - (L - L_1 / 2 - L / 2) ** 2) ** 0.5 + h_1 - R_1) - H}))
        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=1 + j * nn,
                node_end=n + 2 + j * nn,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_top_chord_center))

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                type=rfem.structure_core.Line.TYPE_ARC,
                arc_first_node=1 + j * nn,
                arc_second_node=n + 2 + j * nn,
                arc_control_point={
                    'x': L_1 / 4,
                    'y': j * W,
                    'z': -((R_2 ** 2 - (L_1 / 4 - L / 2) ** 2) ** 0.5 + h_2 - R_2) - H}))
        mem_num += 1

        for i in range(n - 1):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=n + i + 2 + j * nn,
                    node_end=n + i + 3 + j * nn,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_top_chord_center))

            x = (i + 1) * L_1
            lines_list.append(
                rfem.structure_core.Line(
                    no=mem_num,
                    type=rfem.structure_core.Line.TYPE_ARC,
                    arc_first_node=n + i + 2 + j * nn,
                    arc_second_node=n + i + 3 + j * nn,
                    arc_control_point={
                        'x': x,
                        'y': j * W,
                        'z': -((R_2 ** 2 - (x - L / 2) ** 2) ** 0.5 + h_2 - R_2) - H}))
            mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=2 * n + 1 + j * nn,
                node_end=n + 1 + j * nn,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_top_chord_center))

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                type=rfem.structure_core.Line.TYPE_ARC,
                arc_first_node=2 * n + 1 + j * nn,
                arc_second_node=n + 1 + j * nn,
                arc_control_point={
                    'x': L - L_1 / 4,
                    'y': j * W,
                    'z': -((R_2 ** 2 - (L / 2 - L_1 / 4) ** 2) ** 0.5 + h_2 - R_2) - H}))

        mem_num += 1

        for i in range(n - 1):
            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=i + 2 + j * nn,
                    node_end=n + i + 2 + j * nn,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_diagonals_center,
                    member_hinge_start=1,
                    member_hinge_end=1))
            mem_num += 1
            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=i + 2 + j * nn,
                    node_end=n + i + 3 + j * nn,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_diagonals_center,
                    member_hinge_start=1,
                    member_hinge_end=1))
            mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=2 * n + 2 + j * nn,
                node_end=1 + j * nn,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_center))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=2 * n + 3 + j * nn,
                node_end=n + 1 + j * nn,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_center))

        mem_num += 1

        if j < n_u:
            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=1 + j * nn,
                    node_end=1 + (j + 1) * nn,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_girders_center))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=n + 1 + j * nn,
                    node_end=n + 1 + (j + 1) * nn,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_girders_center))

            mem_num += 1

        if j < n_u:
            if purlins_1:
                for i in range(n):

                    members_list.append(
                        rfem.structure_core.Member(
                            no=mem_num,
                            node_start=n + 2 + i + j * nn,
                            node_end=n + 2 + i + (j + 1) * nn,
                            type=rfem.structure_core.Member.TYPE_BEAM,
                            section_start=section_purlins_center))

                    mem_num += 1

    purlin_count_1 = 0

    if purlins_1:
        purlin_count_1 = n

    surfaces_list = []

    for j in range(n_u):

        surface_members = []
        for i in range(n + 1):

            surface_members.append(j * (4 * n + 3 + purlin_count_1) + n + i + 1)
            surface_members.append((j + 1) * (4 * n + 3 + purlin_count_1) + n + i + 1)

        surface_members.append(4 * n + 2 + j * (4 * n + 3 + purlin_count_1))
        surface_members.append(4 * n + 3 + j * (4 * n + 3 + purlin_count_1))

        surfaces_list.append(
            rfem.structure_core.Surface(
                no=j + 1,
                boundary_lines=surface_members,
                type=rfem.structure_core.Surface.TYPE_STANDARD,
                geometry=rfem.structure_core.Surface.GEOMETRY_QUADRANGLE,
                thickness=thickness_roof_slab_center))

    node_ref = node_count
    mem_ref = mem_num

    for j in range(n_u + 1):

        for i in range(n_s + 1):

            nodes_list.append(rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L + d + i * L_s / n_s,
                coordinate_2=j * W,
                coordinate_3=-H_1 - i * (H_2 - H_1) / n_s))

            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L + d,
                coordinate_2=j * W,
                coordinate_3=-H_1 - h))

        node_count += 1

        for i in range(n_s):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L + d + i * L_s / n_s + L_s / (2 * n_s),
                    coordinate_2=j * W,
                    coordinate_3=-H_1 - h - i * (H_2 - H_1) / n_s - (H_2 - H_1) / (2 * n_s)))

            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L + d + L_s,
                coordinate_2=j * W,
                coordinate_3=-H_2 - h))

        node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L + d,
                coordinate_2=j * W,
                coordinate_3=0))

        supports.append(node_count)
        node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L + d + L_s,
                coordinate_2=j * W,
                coordinate_3=0))

        supports.append(node_count)
        node_count += 1

        for i in range(n_s + 1):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=-d - i * L_s / n_s,
                    coordinate_2=j * W,
                    coordinate_3=-H_1 - i * (H_2 - H_1) / n_s))

            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=-d,
                coordinate_2=j * W,
                coordinate_3=-H_1 - h))
        node_count += 1

        for i in range(n_s):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=-d - i * L_s / n_s - L_s / (2 * n_s),
                    coordinate_2=j * W,
                    coordinate_3=-H_1 - h - i * (H_2 - H_1) / n_s - (H_2 - H_1) / (2 * n_s)))

            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=-d - L_s,
                coordinate_2=j * W,
                coordinate_3=-H_2 - h))

        node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=-d,
                coordinate_2=j * W,
                coordinate_3=0))

        supports.append(node_count)
        node_count += 1

        nodes_list.append(rfem.structure_core.Node(
            no=node_count,
            coordinate_1=-d - L_s,
            coordinate_2=j * W,
            coordinate_3=0))

        supports.append(node_count)
        node_count += 1

    nns = 4 * n_s + 10

    for j in range(n_u + 1):

        for i in range(n_s):

            if i == 0:
                members_list.append(
                    rfem.structure_core.Member(
                        no=mem_num,
                        node_start=node_ref + i + j * nns,
                        node_end=node_ref + i + 1 + j * nns,
                        type=rfem.structure_core.Member.TYPE_BEAM,
                        section_start=section_bottom_chord_side,
                        rotation_angle=pi,
                        member_hinge_start=1))
            elif i == n_s - 1:
                members_list.append(
                    rfem.structure_core.Member(
                        no=mem_num,
                        node_start=node_ref + i + j * nns,
                        node_end=node_ref + i + 1 + j * nns,
                        type=rfem.structure_core.Member.TYPE_BEAM,
                        section_start=section_bottom_chord_side,
                        rotation_angle=pi,
                        member_hinge_end=1))
            else:
                members_list.append(
                    rfem.structure_core.Member(
                        no=mem_num,
                        node_start=node_ref + i + j * nns,
                        node_end=node_ref + i + 1 + j * nns,
                        type=rfem.structure_core.Member.TYPE_BEAM,
                        section_start=section_bottom_chord_side,
                        rotation_angle=pi))

            mem_num += 1

            if i == 0:
                members_list.append(
                    rfem.structure_core.Member(
                        no=mem_num,
                        node_start=node_ref + i + 2 * n_s + 5 + j * nns,
                        node_end=node_ref + i + 1 + 2 * n_s + 5 + j * nns,
                        type=rfem.structure_core.Member.TYPE_BEAM,
                        section_start=section_bottom_chord_side,
                        rotation_angle=pi,
                        member_hinge_start=1))
            elif i == n_s - 1:
                members_list.append(
                    rfem.structure_core.Member(
                        no=mem_num,
                        node_start=node_ref + i + 2 * n_s + 5 + j * nns,
                        node_end=node_ref + i + 1 + 2 * n_s + 5 + j * nns,
                        type=rfem.structure_core.Member.TYPE_BEAM,
                        section_start=section_bottom_chord_side,
                        rotation_angle=pi,
                        member_hinge_end=1))
            else:
                members_list.append(
                    rfem.structure_core.Member(
                        no=mem_num,
                        node_start=node_ref + i + 2 * n_s + 5 + j * nns,
                        node_end=node_ref + i + 1 + 2 * n_s + 5 + j * nns,
                        type=rfem.structure_core.Member.TYPE_BEAM,
                        section_start=section_bottom_chord_side,
                        rotation_angle=pi))

            mem_num += 1

        for i in range(n_s + 1):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + i + n_s + 1 + j * nns,
                    node_end=node_ref + i + 1 + n_s + 1 + j * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_top_chord_side))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + i + 2 * n_s + 5 + n_s + 1 + j * nns,
                    node_end=node_ref + i + 1 + 2 * n_s + 5 + n_s + 1 + j * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_top_chord_side))

            mem_num += 1

        for i in range(n_s):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + i + j * nns,
                    node_end=node_ref + i + 2 + n_s + j * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_diagonals_side,
                    member_hinge_start=1,
                    member_hinge_end=1))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + i + 1 + j * nns,
                    node_end=node_ref + i + 2 + n_s + j * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_diagonals_side,
                    member_hinge_start=1,
                    member_hinge_end=1))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + i + 2 * n_s + 5 + j * nns,
                    node_end=node_ref + i + 2 + n_s + 2 * n_s + 5 + j * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_diagonals_side,
                    member_hinge_start=1,
                    member_hinge_end=1))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + i + 1 + 2 * n_s + 5 + j * nns,
                    node_end=node_ref + i + 2 + n_s + 2 * n_s + 5 + j * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_diagonals_side,
                    member_hinge_start=1,
                    member_hinge_end=1))

            mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + j * nns,
                node_end=node_ref + n_s + 1 + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + n_s + j * nns,
                node_end=node_ref + 2 * n_s + 2 + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + 2 * n_s + 5 + j * nns,
                node_end=node_ref + n_s + 1 + 2 * n_s + 5 + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + n_s + 2 * n_s + 5 + j * nns,
                node_end=node_ref + 2 * n_s + 2 + 2 * n_s + 5 + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + 2 * n_s + 3 + j * nns,
                node_end=node_ref + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + 2 * n_s + 4 + j * nns,
                node_end=node_ref + n_s + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + 4 * n_s + 8 + j * nns,
                node_end=node_ref + 2 * n_s + 5 + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=node_ref + 4 * n_s + 9 + j * nns,
                node_end=node_ref + 3 * n_s + 5 + j * nns,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_columns_side))

        mem_num += 1

        if j < n_u:
            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + n_s + 1 + j * nns,
                    node_end=node_ref + n_s + 1 + (j + 1) * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_girders_side))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + 2 * n_s + 2 + j * nns,
                    node_end=node_ref + 2 * n_s + 2 + (j + 1) * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_girders_side))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + n_s + 1 + 2 * n_s + 5 + j * nns,
                    node_end=node_ref + n_s + 1 + 2 * n_s + 5 + (j + 1) * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_girders_side))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=node_ref + 2 * n_s + 2 + 2 * n_s + 5 + j * nns,
                    node_end=node_ref + 2 * n_s + 2 + 2 * n_s + 5 + (j + 1) * nns,
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_girders_side))

            mem_num += 1

        if j < n_u:
            if purlins_2:
                for i in range(n_s):

                    members_list.append(
                        rfem.structure_core.Member(
                            no=mem_num,
                            node_start=node_ref + n_s + 2 + i + j * nns,
                            node_end=node_ref + n_s + 2 + i + (j + 1) * nns,
                            type=rfem.structure_core.Member.TYPE_BEAM,
                            section_start=section_purlins_side))

                    mem_num += 1

                    members_list.append(
                        rfem.structure_core.Member(
                            no=mem_num,
                            node_start=node_ref + n_s + 2 + i + 2 * n_s + 5 + j * nns,
                            node_end=node_ref + n_s + 2 + i + 2 * n_s + 5 + (j + 1) * nns,
                            type=rfem.structure_core.Member.TYPE_BEAM,
                            section_start=section_purlins_side))

                    mem_num += 1

    if purlins_2:
        mmn = 10 * n_s + 14
        k = 2 * n_s
    else:
        mmn = 8 * n_s + 14
        k = 0

    for j in range(n_u):

        surface_members = []
        for i in range(n_s + 1):

            surface_members.append(mem_ref + 2 * n_s + 2 * i + j * mmn)
            surface_members.append(mem_ref + 2 * n_s + mmn + 2 * i + j * mmn)

        surface_members.append(mem_ref + mmn - 4 - k + j * mmn)
        surface_members.append(mem_ref + mmn - 3 - k + j * mmn)

        surfaces_list.append(
            rfem.structure_core.Surface(
                no=2 * j + n_u + 1,
                boundary_lines=surface_members,
                type=rfem.structure_core.Surface.TYPE_STANDARD,
                geometry=rfem.structure_core.Surface.GEOMETRY_PLANE,
                thickness=thickness_roof_slab_side))

        surface_members = []
        for i in range(n_s + 1):

            surface_members.append(mem_ref + 2 * n_s + 2 * i + 1 + j * mmn)
            surface_members.append(mem_ref + 2 * n_s + mmn + 2 * i + 1 + j * mmn)

        surface_members.append(mem_ref + mmn - 2 - k + j * mmn)
        surface_members.append(mem_ref + mmn - 1 - k + j * mmn)

        surfaces_list.append(
            rfem.structure_core.Surface(
                no=2 * j + n_u + 2,
                boundary_lines=surface_members,
                type=rfem.structure_core.Surface.TYPE_STANDARD,
                geometry=rfem.structure_core.Surface.GEOMETRY_PLANE,
                thickness=thickness_roof_slab_side))

    nodal_supports_list = [
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[supports[0],],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_x=0,
            rotational_restraint_y=0,
            rotational_restraint_z=inf),
        rfem.types_for_nodes.NodalSupport(
            no=2,
            nodes=supports[1:],
            spring_x=0,
            spring_y=0,
            spring_z=inf,
            rotational_restraint_x=0,
            rotational_restraint_y=0,
            rotational_restraint_z=inf)]

    rfem_app.create_object_list(nodes_list)
    rfem_app.create_object_list(members_list)
    rfem_app.update_object_list(lines_list)
    rfem_app.create_object_list(surfaces_list)
    rfem_app.create_object_list(nodal_supports_list)

    # Static Analysis Settings
    rfem_app.create_object(rfem.loading.StaticAnalysisSettings(no=1))

    # Load Cases
    rfem_app.create_object(
        rfem.loading.LoadCase(
            no=1,
            name="Self weight",
            static_analysis_settings=1))
