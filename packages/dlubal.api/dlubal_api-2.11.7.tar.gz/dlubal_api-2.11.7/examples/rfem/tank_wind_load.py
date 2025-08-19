import dlubal.api.rfem as rfem
import math

with rfem.Application() as rfem_app:

    rfem_app.close_all_models(save_changes=False)
    rfem_app.create_model(name='tank_wind_load')

    rfem_app.delete_all_objects()

    inf=float("inf")
    structure=[
        rfem.structure_core.Material(no=1, name="S355"),

        rfem.structure_core.Section(no=1, material=1, name="HE 320 A"),
        rfem.structure_core.Section(no=2, material=1, name="IPE 450"),

        rfem.structure_core.Thickness(no=1, uniform_thickness=0.01, material=1),

        rfem.structure_core.Node(no=2, coordinate_1=-4, coordinate_2=0, coordinate_3=0),
        rfem.structure_core.Node(no=3, coordinate_1=-4, coordinate_2=0, coordinate_3=-3),
        rfem.structure_core.Node(no=10, coordinate_1=0, coordinate_2=0, coordinate_3=-3.6),

        rfem.structure_core.Line(no=2, definition_nodes=[2,3]),
        rfem.structure_core.Line(no=3, type=rfem.structure_core.Line.TYPE_ARC,
                                 arc_first_node=3, arc_second_node=10,
                                 arc_control_point_x=-2.022, arc_control_point_y=0, arc_control_point_z=-3.449,
                                 arc_center_x=0, arc_center_y=0, arc_center_z=10.033,
                                 arc_height=0.151, arc_radius=13.633, arc_alpha=0.2977533),
        rfem.structure_core.Line(no=4, type=rfem.structure_core.Line.TYPE_CIRCLE,
                                 circle_center_coordinate_1=0, circle_center_coordinate_2=0, circle_center_coordinate_3=-3,
                                 circle_radius=4,
                                 circle_rotation=3.141594,
                                 circle_normal_coordinate_1=0, circle_normal_coordinate_2=0, circle_normal_coordinate_3=1),
        rfem.structure_core.Line(no=5, type=rfem.structure_core.Line.TYPE_CIRCLE,
                                 circle_center_coordinate_1=0, circle_center_coordinate_2=0, circle_center_coordinate_3=0,
                                 circle_radius=4,
                                 circle_rotation=3.141594,
                                 circle_normal_coordinate_1=0, circle_normal_coordinate_2=0, circle_normal_coordinate_3=1),

        rfem.structure_core.Surface(no=1, geometry=rfem.structure_core.Surface.GEOMETRY_ROTATED,
                                    rotated_boundary_line=3,
                                    rotated_angle_of_rotation=6.283188,
                                    thickness=1, material=1),
        rfem.structure_core.Surface(no=2, geometry=rfem.structure_core.Surface.GEOMETRY_ROTATED,
                                    rotated_boundary_line=2,
                                    rotated_angle_of_rotation=6.283188,
                                    thickness=1, material=1),

        rfem.types_for_lines.LineSupport(no=1, lines=[5], spring_x=inf, spring_y=inf, spring_z=inf)
    ]

    rfem_app.create_object_list(structure)
    print("Structure created")

    loading = [
        rfem.loading.StaticAnalysisSettings(
            no=1,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_GEOMETRICALLY_LINEAR,
        ),
        rfem.loading.LoadCase(
            no=1,
            name="wind-load",
            analysis_type=rfem.loading.LoadCase.ANALYSIS_TYPE_STATIC_ANALYSIS,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_G,
            static_analysis_settings=1,
            self_weight_active=True,
            self_weight_factor_z=1,
        ),
    ]
    rfem_app.create_object_list(loading)
    print("Loading created")

    #calculating inputs for free rectangular load
    circle_radius = 4
    calculation_height = 3.6
    v_ref = 20
    z_0 = 0.2
    angles = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360]
    cp0 = [[1.0, 0.7, 0.1, -0.65, -1.45, -1.97, -2.15, -1.95, -1.25, -0.40, -0.40, -0.40, -0.40, -0.40, -0.40, -0.40, -1.25, -1.95, -2.15, -1.97, -1.45, -0.65, 0.1, 0.7, 1.0],
           [1.0, 0.7, 0.1, -0.60, -1.35, -1.76, -1.73, -1.40, -0.70, -0.70, -0.70, -0.70, -0.70, -0.70, -0.70, -0.70, -0.70, -1.40, -1.73, -1.76, -1.35, -0.60, 0.1, 0.7, 1.0],
           [1.0, 0.7, 0.1, -0.55, -1.20, -1.50, -1.30, -0.80, -0.80, -0.80, -0.80, -0.80, -0.80, -0.80, -0.80, -0.80, -0.80, -0.80, -1.30, -1.50, -1.20, -0.55, 0.1, 0.7, 1.0]]
    Re_vals = [5e5, 2e6, 1e7]
    alpha_min = [85, 80, 75]
    alpha_a = [135, 120, 105]

    l = calculation_height / (circle_radius * 2)
    psi_lambda = 1 / (1 + l**2)

    v_ze = v_ref * math.log(calculation_height / z_0)

    # Reynolds_number
    Re = (circle_radius * v_ze) / 15e-6

    #End_effect_factor_Psi_lambda_a
    def End_effect_factor_psi_lambda_a(angles, alpha_min, alpha_a, psi_lambda):
        psi_lambda_a = []
        for alpha in angles:
            if (0 < alpha < alpha_min):
                psi_lambda_a.append(1),
            elif (alpha < alpha_a):
                psi_lambda_a.append(psi_lambda + (1 - psi_lambda) * math.cos(math.pi / 2 * (alpha - alpha_min) / (alpha_a - alpha_min))),
            else:
                psi_lambda_a.append(psi_lambda)
        return psi_lambda_a

    q_p = 0.613 * v_ref**2
    # External_pressure_coefficient_cpe:
    lvps = [None] * (len(angles))

    for i, alpha in enumerate(angles):
        factor = 1
        alpha_min_int = 0
        alpha_A_int = 0
        psi_lambda_a = End_effect_factor_psi_lambda_a(angles, alpha_min_int, alpha_A_int, psi_lambda)

        # Calculate cpe
        if Re < Re_vals[0]:
            alpha_min_int = alpha_min[0]
            alpha_A_int = alpha_a[0]
            cpe = cp0[0][i] * psi_lambda_a[i]
        elif Re <= Re_vals[1]:
            factor = (Re - Re_vals[0]) / (Re_vals[1] - Re_vals[0])
            alpha_min_int = alpha_min[0] + (alpha_min[1] - alpha_min[0]) * factor
            alpha_A_int = alpha_a[0] + (alpha_a[1] - alpha_a[0]) * factor
            cpe = (cp0[0][i] + (cp0[1][i] - cp0[0][i]) * factor) * psi_lambda_a[i]
        elif Re <= Re_vals[2]:
            factor = (Re - Re_vals[1]) / (Re_vals[2] - Re_vals[1])
            alpha_min_int = alpha_min[1] + (alpha_min[2] - alpha_min[1]) * factor
            alpha_A_int = alpha_a[1] + (alpha_a[2] - alpha_a[1]) * factor
            cpe = (cp0[1][i] + (cp0[2][i] - cp0[1][i]) * factor) * psi_lambda_a[i]
        else:
            alpha_min_int = alpha_min[2]
            alpha_A_int = alpha_a[2]
            cpe = cp0[2][i] * psi_lambda_a[i]

        # Assign values to lvps
        lvps[i] = {
            'no': i + 1,
            'row': {
                'factor': cpe,
                'alpha': alpha / 180.0 * math.pi
            }
        }

    #Create the table with rows
    rows = []
    for i, data in enumerate(lvps):
        row = rfem.loads.FreeRectangularLoad.LoadVaryingAlongPerimeterParametersRow(
            no=data['no'],
            description="",
            alpha=data['row']['alpha'],
            recalculated_magnitude=q_p * 1000,
            factor=data['row']['factor'],
            note=""
        )
        rows.append(row)

    # Create the table and assign rows
    load_varying_table = rfem.loads.FreeRectangularLoad.LoadVaryingAlongPerimeterParametersTable(rows=rows)

    rfem_app.create_object(
        rfem.loads.FreeRectangularLoad(
            no=1, surfaces=[2], load_case=1,
            load_distribution=rfem.loads.FreeRectangularLoad.LOAD_DISTRIBUTION_VARYING_ALONG_PERIMETER,
            load_direction=rfem.loads.FreeRectangularLoad.LOAD_DIRECTION_LOCAL_Z,
            load_projection=rfem.loads.FreeRectangularLoad.LOAD_PROJECTION_XY_OR_UV,
            load_location_rectangle=rfem.loads.FreeRectangularLoad.LOAD_LOCATION_RECTANGLE_CENTER_AND_SIDES,
            load_location_center_x=0,
            load_location_center_y=0,
            load_location_center_side_a=9,
            load_location_center_side_b=9,
            axis_start_angle=math.pi,
            magnitude_uniform=q_p * 1000,
            axis_definition_p1={'x': 0, 'y': 0, 'z': 0},
            axis_definition_p2={'x': 0, 'y': 0, 'z': -1},
            load_varying_along_perimeter_parameters=load_varying_table
        )
    )
    print("Loads created")
