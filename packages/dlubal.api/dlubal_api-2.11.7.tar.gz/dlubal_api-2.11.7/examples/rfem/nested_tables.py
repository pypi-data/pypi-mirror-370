import dlubal.api.rfem as rfem
from dlubal.api.common import Vector3d

with rfem.Application() as client:
    client.close_all_models(save_changes=False)
    client.create_model(name="nested_tables")
    client.delete_all_objects()

    ############################################
    # Test NURBS line with nested tables:
    ############################################

    client.create_object_list([
        rfem.structure_core.Node(no=1, global_coordinates=Vector3d(x=3.000, y=-1.000, z=0.000)),
        rfem.structure_core.Node(no=2, global_coordinates=Vector3d(x=4.000, y=-1.000, z=0.000))
    ])

    # Prepare NURBS control points table.
    # The first and last row correspond to the end nodes so we don't need to set any data for them.
    control_points = rfem.structure_core.Line.NurbsControlPointsTable(
        rows=[
            rfem.structure_core.Line.NurbsControlPointsRow(),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=1.205, y=-2.793, z=0.000), weight=1.100),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=1.000, y=-4.000, z=0.000), weight=1.200),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=3.000, y=-4.000, z=0.000), weight=1.300),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=2.000, y=-6.000, z=0.000), weight=1.400),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=1.000, y=-8.000, z=0.000), weight=1.500),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=3.000, y=-8.000, z=0.000), weight=1.600),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=5.000, y=-5.000, z=0.000), weight=1.700),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=4.000, y=-3.000, z=0.000), weight=1.800),
            rfem.structure_core.Line.NurbsControlPointsRow(global_coordinates=Vector3d(x=6.000, y=-1.000, z=0.000), weight=1.900),
            rfem.structure_core.Line.NurbsControlPointsRow(),
        ]
    )

    # If we use the 'no' attribute, we are able to set specific rows.
    # If we don't use the 'no' attribute, the entire table will be reset,
    # and table will be truncated or enlarged to the number of rows set (if possible).
    # If the 'no' attribute is set, the table will only be enlarged to fit the largest row number,
    # but never truncated.
    # In this case, we set only row number 5 and other rows are left to be default.
    knot_values = rfem.structure_core.Line.NurbsKnotsTable(
        rows=[
            rfem.structure_core.Line.NurbsKnotsRow(no=5, knot_value=0.15),
        ]
    )

    line = rfem.structure_core.Line(
        no=1,
        type=rfem.structure_core.Line.TYPE_NURBS,
        definition_nodes=[1, 2],
        nurbs_control_points=control_points,
        nurbs_order=3,
        nurbs_knots=knot_values)

    client.create_object(line)

    ############################################
    # Test load combination nested tables:
    ############################################

    load_cases = [
        rfem.loading.LoadCase(no=1, name="Self weight"),
        rfem.loading.LoadCase(no=2, name="Live Load")
    ]

    client.create_object_list(load_cases)

    # Prepare load combination items table.
    items = rfem.loading.LoadCombination.ItemsTable(
        rows=[
            rfem.loading.LoadCombination.ItemsRow(load_case=1, factor=1.35),
            rfem.loading.LoadCombination.ItemsRow(load_case=2, factor=1.5)
        ]
    )
    co = rfem.loading.LoadCombination(no=1, items=items)
    client.create_object(co)

    # Get the created load combination and print it - we get the table data as well.
    co = client.get_object(rfem.loading.LoadCombination(no=1))
    print(co)
