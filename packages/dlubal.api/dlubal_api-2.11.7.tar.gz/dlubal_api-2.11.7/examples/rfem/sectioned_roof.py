from math import inf
from dlubal.api import rfem

# Basic Settings
n_u = 4
n_b = 7

L = 35
H_1 = 7
H_2 = 1
d = 2
s = 8

section_beam = 1
section_verticals = 2
section_3 = 2

thickness_material = 2
thickness_roof = 1
roof_thick = 0.2

nodal_supports = 1

assert n_b % 2 == 1, "n_b should be odd"

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Close all models opened in application without saving
    rfem_app.close_all_models(save_changes=False)

    # Create new model named 'sectioned_roof'
    rfem_app.create_model(name='sectioned_roof')

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
        rfem.structure_core.Section(
            no=2,
            name='SHS 100x100x10.0',
            material=1),
        rfem.structure_core.Thickness(
            no=thickness_roof,
            user_defined_name_enabled=True,
            name='Roof',
            uniform_thickness=roof_thick,
            material=thickness_material)
    ]

    rfem_app.create_object_list(material_section_thickness)

    node_count = 1

    for j in range(n_u + 1):

        nodes_list = []
        for i in range(2 * n_b + 1):

            x = i * L / (2 * n_b)
            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=x,
                    coordinate_2=j * s,
                    coordinate_3=-H_1 * (1 - (x - (L / 2)) ** 2 / (L / 2) ** 2)))
            node_count += 1

        rfem_app.create_object_list(nodes_list)

        nodes_list = []
        for i in range((n_b - 1) // 2):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=0 + i * L / n_b,
                    coordinate_2=j * s,
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=3 + 2 * i)).coordinate_3))

            node_count += 1

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L / (2 * n_b) + i * L / n_b,
                    coordinate_2=j * s,
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=3 + 2 * i)).coordinate_3))

            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L / 2 - L / (2 * n_b),
                coordinate_2=j * s,
                coordinate_3=-H_1 - H_2))

        node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L / 2,
                coordinate_2=j * s,
                coordinate_3=-H_1 - H_2))

        node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L / 2 + L / (2 * n_b),
                coordinate_2=j * s,
                coordinate_3=-H_1 - H_2))

        node_count += 1

        rfem_app.create_object_list(nodes_list)

        nodes_list = []
        for i in range((n_b - 1) // 2):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L / 2 + L / n_b + i * L / n_b,
                    coordinate_2=j * s,
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=n_b + 2 + 2 * i)).coordinate_3))

            node_count += 1

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L / 2 + 1.5 * L / n_b + i * L / n_b,
                    coordinate_2=j * s,
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=n_b + 2 + 2 * i)).coordinate_3))

            node_count += 1

        rfem_app.create_object_list(nodes_list)

    srf_node_ref = node_count

    for j in range(2):

        nodes_list = []
        for i in range((n_b - 1) // 2):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=0 + i * L / n_b,
                    coordinate_2=-d + j * (n_u * s + 2 * d),
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=3 + 2 * i)).coordinate_3))

            node_count += 1

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L / n_b + i * L / n_b,
                    coordinate_2=-d + j * (n_u * s + 2 * d),
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=3 + 2 * i)).coordinate_3))

            node_count += 1

        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L / 2 - L / (2 * n_b),
                coordinate_2=-d + j * (n_u * s + 2 * d),
                coordinate_3=-H_1 - H_2))
        node_count += 1
        nodes_list.append(
            rfem.structure_core.Node(
                no=node_count,
                coordinate_1=L / 2 + L / (2 * n_b),
                coordinate_2=-d + j * (n_u * s + 2 * d),
                coordinate_3=-H_1 - H_2))

        node_count += 1

        rfem_app.create_object_list(nodes_list)

        nodes_list = []
        for i in range((n_b - 1) // 2):

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L / 2 + L / (2 * n_b) + i * L / n_b,
                    coordinate_2=-d + j * (n_u * s + 2 * d),
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=n_b + 2 + 2 * i)).coordinate_3))

            node_count += 1

            nodes_list.append(
                rfem.structure_core.Node(
                    no=node_count,
                    coordinate_1=L / 2 + 1.5 * L / n_b + i * L / n_b,
                    coordinate_2=-d + j * (n_u * s + 2 * d),
                    coordinate_3=rfem_app.get_object(
                        rfem.structure_core.Node(
                            no=n_b + 2 + 2 * i)).coordinate_3))

            node_count += 1

        rfem_app.create_object_list(nodes_list)

    mem_num = 1

    members_list = []
    lines_list = []

    for j in range(n_u + 1):

        for i in range(n_b):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=2 * i + 1 + j * (4 * n_b + 2),
                    node_end=2 * i + 3 + j * (4 * n_b + 2),
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_beam))

            nodes = rfem_app.get_object(
                rfem.structure_core.Node(
                    no=2 * i + 2 + j * (4 * n_b + 2)))

            lines_list.append(
                rfem.structure_core.Line(
                    no=mem_num,
                    type=rfem.structure_core.Line.TYPE_PARABOLA,
                    parabola_first_node=2 * i + 1 + j * (4 * n_b + 2),
                    parabola_second_node=2 * i + 3 + j * (4 * n_b + 2),
                    parabola_control_point={
                        'x': nodes.coordinate_1,
                        'y': nodes.coordinate_2,
                        'z': nodes.coordinate_3
                    }
                )
            )

            mem_num += 1

        for i in range((n_b - 1) // 2):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=2 * i + 1 + j * (4 * n_b + 2),
                    node_end=2 * n_b + 2 + 2 * i + j * (4 * n_b + 2),
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_verticals))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=2 * i + 2 + j * (4 * n_b + 2),
                    node_end=2 * n_b + 3 + 2 * i + j * (4 * n_b + 2),
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_verticals))

            mem_num += 1

        for i in range(3):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=n_b + i + j * (4 * n_b + 2),
                    node_end=2 * n_b + n_b + i + 1 + j * (4 * n_b + 2),
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_verticals))

            mem_num += 1

        for i in range((n_b - 1) // 2):

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=n_b + 3 + 2 * i + j * (4 * n_b + 2),
                    node_end=3 * n_b + 4 + 2 * i + j * (4 * n_b + 2),
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_verticals))

            mem_num += 1

            members_list.append(
                rfem.structure_core.Member(
                    no=mem_num,
                    node_start=n_b + 3 + 2 * i + 1 + j * (4 * n_b + 2),
                    node_end=3 * n_b + 5 + 2 * i + j * (4 * n_b + 2),
                    type=rfem.structure_core.Member.TYPE_BEAM,
                    section_start=section_verticals))

            mem_num += 1

    for i in range(n_b - 1):

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=srf_node_ref + 2 * i + 1,
                node_end=srf_node_ref + 2 * i + 2,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_3))

        mem_num += 1

        members_list.append(
            rfem.structure_core.Member(
                no=mem_num,
                node_start=srf_node_ref + 2 * i + 2 * n_b + 1,
                node_end=srf_node_ref + 2 * i + 2 * n_b + 2,
                type=rfem.structure_core.Member.TYPE_BEAM,
                section_start=section_3))

        mem_num += 1

    rfem_app.create_object_list(members_list)
    rfem_app.update_object_list(lines_list)

    srf_line_ref = mem_num

    lines_list = []

    for i in range(n_b):

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                definition_nodes=[
                    srf_node_ref + 2 * i,
                    srf_node_ref + 2 * i + 1]))

        mem_num += 1

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                definition_nodes=[
                    srf_node_ref + 2 * i + 2 * n_b,
                    srf_node_ref + 2 * i + 1 + 2 * n_b]))

        mem_num += 1

    for i in range(2 * n_b):

        lines_list.append(
            rfem.structure_core.Line(
                no=mem_num,
                definition_nodes=[
                    srf_node_ref + i,
                    srf_node_ref + i + 2 * n_b]))

        mem_num += 1

    surfaces_list = []

    for i in range(1, n_b + 1):

        surfaces_list.append(
            rfem.structure_core.Surface(
                no=i,
                boundary_lines=[
                    srf_line_ref + 2 * (i - 1),
                    srf_line_ref + 2 * n_b + 1 + 2 * (i - 1),
                    srf_line_ref + 2 * (i - 1) + 1,
                    srf_line_ref + 2 * n_b + 2 * (i - 1)],
                type=rfem.structure_core.Surface.TYPE_STANDARD,
                geometry=rfem.structure_core.Surface.GEOMETRY_PLANE,
                thickness=thickness_roof))

    nodal_supports_list = []
    support_nodes = []

    for i in range(n_u + 1):

        support_nodes.append(i * (4 * n_b + 2) + 1)
        support_nodes.append(2 * n_b + i * (4 * n_b + 2) + 1)

    nodal_supports_list = [
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[support_nodes[0],],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_x=0,
            rotational_restraint_y=0,
            rotational_restraint_z=inf),
        rfem.types_for_nodes.NodalSupport(
            no=2,
            nodes=support_nodes[1:],
            spring_x=0,
            spring_y=0,
            spring_z=inf,
            rotational_restraint_x=0,
            rotational_restraint_y=0,
            rotational_restraint_z=inf)]

    rfem_app.create_object_list(lines_list)
    rfem_app.create_object_list(surfaces_list)
    rfem_app.create_object_list(nodal_supports_list)

    # Static Analysis Settings
    rfem_app.create_object(
        rfem.loading.StaticAnalysisSettings(no=1)
    )

    # Load Cases
    rfem_app.create_object(
        rfem.loading.LoadCase(
            no=1,
            name="Self weight",
            static_analysis_settings=1,
        )
    )
