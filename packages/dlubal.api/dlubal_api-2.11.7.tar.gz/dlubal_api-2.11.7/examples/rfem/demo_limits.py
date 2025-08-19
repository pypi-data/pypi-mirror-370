from dlubal.api import rfem

material_no = 1
section_no = 1
thickness_no = 1


def create_material() -> list:
    return [
        rfem.structure_core.Material(
            no = material_no,
            name = 'S420MC 1.0980'
        )
    ]


def create_section() -> list:
    return [
        rfem.structure_core.Section(
            no = section_no,
            name = 'IPE 100',
            material = material_no
        )
    ]


def create_member(i: int) -> list:

    origin_x = i
    node_1_no = 2 * i - 1
    node_2_no = 2 * i
    line_no = i
    member_no = i

    return [
        # nodes
        rfem.structure_core.Node(
            no = node_1_no,
            coordinate_1 = origin_x,
            coordinate_2 = 1
        )
        , rfem.structure_core.Node(
            no = node_2_no,
            coordinate_1 = origin_x,
            coordinate_2 = 5
        )

        # lines
        , rfem.structure_core.Line(
            no = line_no,
            definition_nodes = [node_1_no, node_2_no]
        )

        # members
        , rfem.structure_core.Member(
            no = member_no,
            line = line_no,
            section_start = section_no
        )
    ]


def create_members(count: int):

    objects = []

    objects.extend(create_material())
    objects.extend(create_section())

    for i in range(1, count + 1):
        objects.extend(create_member(i))

    rfem_app.create_object_list(objects)


def create_one_member(no: int):
    rfem_app.create_object_list(create_member(no))


def create_thickness() -> list:
    return [
        rfem.structure_core.Thickness(
            no = thickness_no,
            material = material_no
        )
    ]


def create_surface(i: int) -> list:

    origin_x = 2 * i - 1

    node_1_no = 4 * i - 3
    node_2_no = 4 * i - 2
    node_3_no = 4 * i - 1
    node_4_no = 4 * i
    
    line_1_no = 4 * i - 3
    line_2_no = 4 * i - 2
    line_3_no = 4 * i - 1
    line_4_no = 4 * i

    surface_no = i

    return [
        # nodes
        rfem.structure_core.Node(
            no = node_1_no,
            coordinate_1 = origin_x,
            coordinate_2 = 1
        )
        , rfem.structure_core.Node(
            no = node_2_no,
            coordinate_1 = origin_x,
            coordinate_2 = 5
        )
        , rfem.structure_core.Node(
            no = node_3_no,
            coordinate_1 = origin_x + 1,
            coordinate_2 = 1
        )
        , rfem.structure_core.Node(
            no = node_4_no,
            coordinate_1 = origin_x + 1,
            coordinate_2 = 5
        )

        # lines
        , rfem.structure_core.Line(
            no = line_1_no,
            definition_nodes = [node_1_no, node_2_no]
        )
        , rfem.structure_core.Line(
            no = line_2_no,
            definition_nodes = [node_2_no, node_4_no]
        )
        , rfem.structure_core.Line(
            no = line_3_no,
            definition_nodes = [node_4_no, node_3_no]
        )
        , rfem.structure_core.Line(
            no = line_4_no,
            definition_nodes = [node_3_no, node_1_no]
        )

        # surfaces
        , rfem.structure_core.Surface(
            no = surface_no,
            boundary_lines = [line_1_no, line_2_no, line_3_no, line_4_no],
            thickness = thickness_no
        )
    ]


def create_surfaces(count: int):
    objects = []

    objects.extend(create_material())
    objects.extend(create_thickness())

    for i in range(1, count + 1):
        objects.extend(create_surface(i))

    rfem_app.create_object_list(objects)


def create_solid(i: int) -> list:

    origin_x = 2 * i - 1

    node_1_no = 8 * i - 7
    node_2_no = 8 * i - 6
    node_3_no = 8 * i - 5
    node_4_no = 8 * i - 4
    node_5_no = 8 * i - 3
    node_6_no = 8 * i - 2
    node_7_no = 8 * i - 1
    node_8_no = 8 * i

    line_1_no = 12 * i - 11
    line_2_no = 12 * i - 10
    line_3_no = 12 * i - 9
    line_4_no = 12 * i - 8
    line_5_no = 12 * i - 7
    line_6_no = 12 * i - 6
    line_7_no = 12 * i - 5
    line_8_no = 12 * i - 4
    line_9_no = 12 * i - 3
    line_10_no = 12 * i - 2
    line_11_no = 12 * i - 1
    line_12_no = 12 * i

    surface_1_no = 6 * i - 5
    surface_2_no = 6 * i - 4
    surface_3_no = 6 * i - 3
    surface_4_no = 6 * i - 2
    surface_5_no = 6 * i - 1
    surface_6_no = 6 * i

    solid_no = i

    return [
        # nodes
        rfem.structure_core.Node(
            no = node_1_no,
            coordinate_1 = origin_x,
            coordinate_2 = 1
        )
        , rfem.structure_core.Node(
            no = node_2_no,
            coordinate_1 = origin_x,
            coordinate_2 = 5
        )
        , rfem.structure_core.Node(
            no = node_3_no,
            coordinate_1 = origin_x + 1,
            coordinate_2 = 1
        )
        , rfem.structure_core.Node(
            no = node_4_no,
            coordinate_1 = origin_x + 1,
            coordinate_2 = 5
        )

        , rfem.structure_core.Node(
            no = node_5_no,
            coordinate_1 = origin_x,
            coordinate_2 = 1,
            coordinate_3 = -2
        )
        , rfem.structure_core.Node(
            no = node_6_no,
            coordinate_1 = origin_x,
            coordinate_2 = 5,
            coordinate_3 = -2
        )
        , rfem.structure_core.Node(
            no = node_7_no,
            coordinate_1 = origin_x + 1,
            coordinate_2 = 1,
            coordinate_3 = -2
        )
        , rfem.structure_core.Node(
            no = node_8_no,
            coordinate_1 = origin_x + 1,
            coordinate_2 = 5,
            coordinate_3 = -2
        )

        # lines
        , rfem.structure_core.Line(
            no = line_1_no,
            definition_nodes = [node_1_no, node_2_no]
        )
        , rfem.structure_core.Line(
            no = line_2_no,
            definition_nodes = [node_2_no, node_4_no]
        )
        , rfem.structure_core.Line(
            no = line_3_no,
            definition_nodes = [node_4_no, node_3_no]
        )
        , rfem.structure_core.Line(
            no = line_4_no,
            definition_nodes = [node_3_no, node_1_no]
        )

        , rfem.structure_core.Line(
            no = line_5_no,
            definition_nodes = [node_5_no, node_6_no]
        )
        , rfem.structure_core.Line(
            no = line_6_no,
            definition_nodes = [node_6_no, node_8_no]
        )
        , rfem.structure_core.Line(
            no = line_7_no,
            definition_nodes = [node_8_no, node_7_no]
        )
        , rfem.structure_core.Line(
            no = line_8_no,
            definition_nodes = [node_7_no, node_5_no]
        )

        , rfem.structure_core.Line(
            no = line_9_no,
            definition_nodes = [node_1_no, node_5_no]
        )
        , rfem.structure_core.Line(
            no = line_10_no,
            definition_nodes = [node_2_no, node_6_no]
        )
        , rfem.structure_core.Line(
            no = line_11_no,
            definition_nodes = [node_3_no, node_7_no]
        )
        , rfem.structure_core.Line(
            no = line_12_no,
            definition_nodes = [node_4_no, node_8_no]
        )

        # solids
        , rfem.structure_core.Solid(
            no = solid_no,
            boundary_surfaces = [surface_1_no, surface_2_no, surface_3_no, surface_4_no, surface_5_no, surface_6_no],
            material = material_no
        )

        # surfaces
        , rfem.structure_core.Surface(
            no = surface_1_no,
            type = rfem.structure_core.Surface.TYPE_WITHOUT_THICKNESS,
            boundary_lines = [line_1_no, line_2_no, line_3_no, line_4_no],
        )
        , rfem.structure_core.Surface(
            no = surface_2_no,
            type = rfem.structure_core.Surface.TYPE_WITHOUT_THICKNESS,
            boundary_lines = [line_5_no, line_6_no, line_7_no, line_8_no],
        )
        , rfem.structure_core.Surface(
            no = surface_3_no,
            type = rfem.structure_core.Surface.TYPE_WITHOUT_THICKNESS,
            boundary_lines = [line_1_no, line_9_no, line_5_no, line_10_no],
        )
        , rfem.structure_core.Surface(
            no = surface_4_no,
            type = rfem.structure_core.Surface.TYPE_WITHOUT_THICKNESS,
            boundary_lines = [line_2_no, line_10_no, line_6_no, line_12_no],
        )
        , rfem.structure_core.Surface(
            no = surface_5_no,
            type = rfem.structure_core.Surface.TYPE_WITHOUT_THICKNESS,
            boundary_lines = [line_3_no, line_11_no, line_7_no, line_12_no],
        )
        , rfem.structure_core.Surface(
            no = surface_6_no,
            type = rfem.structure_core.Surface.TYPE_WITHOUT_THICKNESS,
            boundary_lines = [line_4_no, line_9_no, line_8_no, line_11_no],
        )
    ]


def create_solids(count: int):
    objects = []

    objects.extend(create_material())

    for i in range(1, count + 1):
        objects.extend(create_solid(i))

    rfem_app.create_object_list(objects)


with rfem.Application() as rfem_app:
    
    rfem_app.delete_all_objects()

    # create_members(11) # under limit
    # create_members(12) # on limit
    create_members(13) # over limit

    # create_members(12) # on limit
    # create_one_member(15) # over limit

    # create_surfaces(1) # under limit
    # create_surfaces(2) # on limit
    # create_surfaces(3) # over limit

    # create_solids(1) # under limit
    # create_solids(2) # on limit
    # create_solids(3) # over limit

    # rfem_app.calculate_all(skip_warnings=True)