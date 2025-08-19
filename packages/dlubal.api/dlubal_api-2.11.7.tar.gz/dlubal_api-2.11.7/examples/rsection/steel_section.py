from dlubal.api import rsection
import os

def define_structure() -> list:

    objs = []

    # Define material
    objs.append(
        rsection.structure_core.Material(
            no=1,
            name='S235',
        )
    )

    # --- Points table ---
    points = [
        (1, 0.0000, -0.0040), (2, 0.0000, 0.0000), (3, 0.0000, 0.0040), (4, 0.0000, 0.1680), (5, 0.0000, 0.1720), (6, 0.0000, 0.1760),
        (7, 0.0338, 0.0040), (8, 0.0338, 0.1680), (9, 0.0402, 0.0066), (10, 0.0402, 0.1654), (11, 0.0429, 0.0130), (12, 0.0429, 0.1590),
        (13, 0.0455, 0.0000), (14, 0.0455, 0.1720), (15, 0.0455, -0.0040), (16, 0.0455, 0.1760), (17, 0.0481, 0.0130), (18, 0.0481, 0.1590),
        (19, 0.0508, 0.0066), (20, 0.0508, 0.1654), (21, 0.0571, 0.0040), (22, 0.0571, 0.1680), (23, 0.0910, 0.0000), (24, 0.0910, 0.1720),
        (25, 0.0910, -0.0040), (26, 0.0910, 0.0005), (27, 0.0910, 0.0040), (28, 0.0910, 0.1680), (29, 0.0910, 0.1760), (30, 0.0920, 0.0030),
        (31, 0.0945, 0.0040), (32, 0.1560, 0.0040), (33, 0.1609, 0.0061), (34, 0.1630, 0.011), (35, 0.1630, 0.0325), (36, 0.1640, 0.0350),
        (37, 0.1665, 0.0360), (38, 0.1670, 0.0000), (39, 0.1670, 0.0360), (40, 0.1670, -0.0040), (41, 0.1710, -0.0040), (42, 0.1710, 0.0000),
        (43, 0.1710, 0.0360)
    ]

    for p in points:
        objs.append(
            rsection.structure_core.Point(
                no=p[0],
                coordinate_1=p[1],
                coordinate_2=p[2],
            )
        )

    # --- Lines table ---
    # For Polyline: (line_no, start, end, type, None, None, None, None)
    # For Arc:      (line_no, start, end, type, arc_control_y, arc_control_z, arc_center_y, arc_center_z)

    lines = [
        (1, 1, 3, 'Polyline', None, None, None, None), (2, 4, 6, 'Polyline', None, None, None, None), (3, 3, 7, 'Polyline', None, None, None, None),
        (4, 8, 4, 'Polyline', None, None, None, None), (5, 15, 1, 'Polyline', None, None, None, None), (6, 6, 16, 'Polyline', None, None, None, None),
        (7, 12, 8, 'Arc', 0.0402, 0.1654, 0.0339, 0.1590), (8, 7, 11, 'Arc', 0.0402, 0.0066, 0.0339, 0.0130), (9, 11, 12, 'Polyline', None, None, None, None),
        (10, 18, 17, 'Polyline', None, None, None, None), (11, 17, 21, 'Arc', 0.0508, 0.0066, 0.0571, 0.0130), (12, 18, 22, 'Arc', 0.0508, 0.1654, 0.0571, 0.1590),
        (13, 25, 15, 'Polyline', None, None, None, None), (14, 16, 29, 'Polyline', None, None, None, None), (15, 21, 27, 'Polyline', None, None, None, None),
        (16, 28, 22, 'Polyline', None, None, None, None), (17, 27, 26, 'Polyline', None, None, None, None), (18, 29, 28, 'Polyline', None, None, None, None),
        (19, 26, 31, 'Arc', 0.0920, 0.0030, 0.0945, 0.0005), (20, 31, 32, 'Polyline', None, None, None, None), (21, 40, 25, 'Polyline', None, None, None, None),
        (22, 32, 34, 'Arc', 0.1609, 0.0061, 0.1560, 0.0110), (23, 34, 35, 'Polyline', None, None, None, None), (24, 35, 37, 'Arc', 0.1640, 0.0350, 0.1665, 0.0325),
        (25, 37, 43, 'Polyline', None, None, None, None), (26, 41, 40, 'Polyline', None, None, None, None), (27, 42, 41, 'Polyline', None, None, None, None),
        (28, 43, 42, 'Polyline', None, None, None, None)
    ]

    type_map = {
        'Polyline': rsection.structure_core.Line.TYPE_POLYLINE,
        'Arc': rsection.structure_core.Line.TYPE_ARC
    }

    boundary_lines = []
    for l in lines:
        line_no, start, end, type_str, arc_control_y, arc_control_z, arc_center_y, arc_center_z = l
        objs.append(
            rsection.structure_core.Line(
                no=line_no,
                definition_points=[start, end],
                type=type_map[type_str],
                arc_control_point_y=arc_control_y,
                arc_control_point_z=arc_control_z,
                arc_center_y=arc_center_y,
                arc_center_z=arc_center_z,
            )
        )
        boundary_lines.append(line_no)

    # Define part
    objs.append(
        rsection.structure_core.Part(
            material=1,
            boundary_lines=boundary_lines,
        )
    )

    return objs

with rsection.Application() as rsection_app:

    # Step 1: Create a new model
    rsection_app.create_model(name='steel_section')

    # Step 2: Clear existing objects
    rsection_app.delete_all_objects()

    # Step 3: Define and create all objects
    objects = define_structure()
    rsection_app.create_object_list(objects)

    # Step 4: Calculate section
    rsection_app.calculate_all(
        skip_warnings=True
    )

    # Step 5: Save model with results
    model_path = os.path.abspath('./steel_section')
    rsection_app.save_model(path=model_path)
    print(f"\nModel File Path:\n{rsection_app.get_model_main_parameters().model_path}")

