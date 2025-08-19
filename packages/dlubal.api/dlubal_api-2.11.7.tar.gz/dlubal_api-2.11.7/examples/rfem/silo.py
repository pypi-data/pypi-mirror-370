from math import inf
from dlubal.api import rfem

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Create empty new model named 'silo'
    rfem_app.create_model(name='silo')

    # Cleanup the model
    rfem_app.delete_all_objects()

    # Define list of model objects to be created
    lst = [
        # Materials
        rfem.structure_core.Material(
            no=1,
            name="S450 | EN 1993-1-1:2005-05"),
        rfem.structure_core.Material(
            no=2,
            name="Sand, well-graded (SW) | DIN 18196:2011-05"),
        rfem.structure_core.Material(
            no=3,
            name="Dry air | --"),
        rfem.structure_core.Material(
            no=4,
            name="S450 | EN 1993-1-1:2005-05"),

        # Sections
        rfem.structure_core.Section(
            no=1,
            material=1,
            name="IPN 300"),
        rfem.structure_core.Section(
            no=2,
            material=1,
            name="UPE 200"),
        rfem.structure_core.Section(
            no=3,
            material=1,
            name="MSH KHP 88.9x3.6"),
        rfem.structure_core.Section(
            no=4,
            material=1,
            name="MSH KHP 88.9x3.6"),
        rfem.structure_core.Section(
            no=5,
            material=1,
            name="LU 0.3/0.2/0.01/0.01/0"),

        # Thicknesses
        rfem.structure_core.Thickness(
            no=1,
            material=4,
            uniform_thickness=0.01,
            assigned_to_surfaces=[2, 3, 4, 5]),
        rfem.structure_core.Thickness(
            no=2,
            material=1,
            uniform_thickness=0.008,
            assigned_to_surfaces=[1, 6, 7, 8, 9]),
        rfem.structure_core.Thickness(
            no=3,
            material=4,
            uniform_thickness=0.005,
            assigned_to_surfaces=[11]),

        # Nodes
        rfem.structure_core.Node(
            no=1,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=2,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=3,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=4,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=5,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=6,
            coordinate_1=1.5,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=7,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=8,
            coordinate_1=3.0,
            coordinate_2=1.5,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=9,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=10,
            coordinate_1=1.5,
            coordinate_2=3.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=11,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=12,
            coordinate_1=0.0,
            coordinate_2=1.5,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=13,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=14,
            coordinate_1=1.5,
            coordinate_2=0.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=15,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=16,
            coordinate_1=3.0,
            coordinate_2=1.5,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=17,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=18,
            coordinate_1=1.5,
            coordinate_2=3.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=19,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=20,
            coordinate_1=0.0,
            coordinate_2=1.5,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=21,
            coordinate_1=0.75,
            coordinate_2=0.75,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=22,
            coordinate_1=2.25,
            coordinate_2=0.75,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=23,
            coordinate_1=2.25,
            coordinate_2=2.25,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=24,
            coordinate_1=0.75,
            coordinate_2=2.25,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=25,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-12.0),
        rfem.structure_core.Node(
            no=26,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=-12.0),
        rfem.structure_core.Node(
            no=27,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=-12.0),
        rfem.structure_core.Node(
            no=28,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=-12.0),

        # Lines
        rfem.structure_core.Line(
            no=1,
            definition_nodes=[1, 5]),
        rfem.structure_core.Line(
            no=2,
            definition_nodes=[2, 7]),
        rfem.structure_core.Line(
            no=3,
            definition_nodes=[3, 9]),
        rfem.structure_core.Line(
            no=4,
            definition_nodes=[4, 11]),
        rfem.structure_core.Line(
            no=5,
            definition_nodes=[5, 13]),
        rfem.structure_core.Line(
            no=6,
            definition_nodes=[7, 15]),
        rfem.structure_core.Line(
            no=7,
            definition_nodes=[9, 17]),
        rfem.structure_core.Line(
            no=8,
            definition_nodes=[11, 19]),
        rfem.structure_core.Line(
            no=9,
            definition_nodes=[13, 14]),
        rfem.structure_core.Line(
            no=10,
            definition_nodes=[14, 15]),
        rfem.structure_core.Line(
            no=11,
            definition_nodes=[15, 16]),
        rfem.structure_core.Line(
            no=12,
            definition_nodes=[16, 17]),
        rfem.structure_core.Line(
            no=13,
            definition_nodes=[17, 18]),
        rfem.structure_core.Line(
            no=14,
            definition_nodes=[18, 19]),
        rfem.structure_core.Line(
            no=15,
            definition_nodes=[19, 20]),
        rfem.structure_core.Line(
            no=16,
            definition_nodes=[20, 13]),
        rfem.structure_core.Line(
            no=17,
            definition_nodes=[1, 6]),
        rfem.structure_core.Line(
            no=18,
            definition_nodes=[2, 6]),
        rfem.structure_core.Line(
            no=19,
            definition_nodes=[2, 8]),
        rfem.structure_core.Line(
            no=20,
            definition_nodes=[3, 8]),
        rfem.structure_core.Line(
            no=21,
            definition_nodes=[3, 10]),
        rfem.structure_core.Line(
            no=22,
            definition_nodes=[4, 10]),
        rfem.structure_core.Line(
            no=23,
            definition_nodes=[4, 12]),
        rfem.structure_core.Line(
            no=24,
            definition_nodes=[1, 12]),
        rfem.structure_core.Line(
            no=25,
            definition_nodes=[5, 14]),
        rfem.structure_core.Line(
            no=26,
            definition_nodes=[7, 14]),
        rfem.structure_core.Line(
            no=27,
            definition_nodes=[7, 16]),
        rfem.structure_core.Line(
            no=28,
            definition_nodes=[9, 16]),
        rfem.structure_core.Line(
            no=29,
            definition_nodes=[9, 18]),
        rfem.structure_core.Line(
            no=30,
            definition_nodes=[11, 18]),
        rfem.structure_core.Line(
            no=31,
            definition_nodes=[11, 20]),
        rfem.structure_core.Line(
            no=32,
            definition_nodes=[5, 20]),
        rfem.structure_core.Line(
            no=33,
            definition_nodes=[5, 6]),
        rfem.structure_core.Line(
            no=34,
            definition_nodes=[6, 7]),
        rfem.structure_core.Line(
            no=35,
            definition_nodes=[7, 8]),
        rfem.structure_core.Line(
            no=36,
            definition_nodes=[8, 9]),
        rfem.structure_core.Line(
            no=37,
            definition_nodes=[9, 10]),
        rfem.structure_core.Line(
            no=38,
            definition_nodes=[10, 11]),
        rfem.structure_core.Line(
            no=39,
            definition_nodes=[11, 12]),
        rfem.structure_core.Line(
            no=40,
            definition_nodes=[12, 5]),
        rfem.structure_core.Line(
            no=41,
            definition_nodes=[21, 22]),
        rfem.structure_core.Line(
            no=42,
            definition_nodes=[22, 23]),
        rfem.structure_core.Line(
            no=43,
            definition_nodes=[23, 24]),
        rfem.structure_core.Line(
            no=44,
            definition_nodes=[24, 21]),
        rfem.structure_core.Line(
            no=45,
            definition_nodes=[13, 21]),
        rfem.structure_core.Line(
            no=46,
            definition_nodes=[15, 22]),
        rfem.structure_core.Line(
            no=47,
            definition_nodes=[17, 23]),
        rfem.structure_core.Line(
            no=48,
            definition_nodes=[19, 24]),
        rfem.structure_core.Line(
            no=49,
            definition_nodes=[13, 25]),
        rfem.structure_core.Line(
            no=50,
            definition_nodes=[15, 26]),
        rfem.structure_core.Line(
            no=51,
            definition_nodes=[17, 27]),
        rfem.structure_core.Line(
            no=52,
            definition_nodes=[19, 28]),
        rfem.structure_core.Line(
            no=53,
            definition_nodes=[25, 26]),
        rfem.structure_core.Line(
            no=54,
            definition_nodes=[26, 27]),
        rfem.structure_core.Line(
            no=55,
            definition_nodes=[27, 28]),
        rfem.structure_core.Line(
            no=56,
            definition_nodes=[28, 25]),

        # Surfaces
        rfem.structure_core.Surface(
            no=1,
            boundary_lines=[41, 42, 43, 44]),
        rfem.structure_core.Surface(
            no=2,
            boundary_lines=[45, 41, 46, 10, 9]),
        rfem.structure_core.Surface(
            no=3,
            boundary_lines=[46, 42, 47, 12, 11]),
        rfem.structure_core.Surface(
            no=4,
            boundary_lines=[47, 43, 48, 14, 13]),
        rfem.structure_core.Surface(
            no=5,
            boundary_lines=[48, 44, 45, 16, 15]),
        rfem.structure_core.Surface(
            no=6,
            boundary_lines=[9, 10, 50, 53, 49]),
        rfem.structure_core.Surface(
            no=7,
            boundary_lines=[11, 12, 51, 54, 50]),
        rfem.structure_core.Surface(
            no=8,
            boundary_lines=[13, 14, 52, 55, 51]),
        rfem.structure_core.Surface(
            no=9,
            boundary_lines=[15, 16, 49, 56, 52]),
        rfem.structure_core.Surface(
            no=10,
            boundary_lines=[9, 10, 11, 12, 13, 14, 15, 16]),
        rfem.structure_core.Surface(
            no=11,
            boundary_lines=[53, 54, 55, 56]),

        # Beams
        rfem.structure_core.Member(
            no=1,
            line=1,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=2,
            line=2,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=3,
            line=3,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=4,
            line=4,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=5,
            line=5,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=6,
            line=6,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=7,
            line=7,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=8,
            line=8,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),

        # Ribs
        rfem.structure_core.Member(
            no=9,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=9),
        rfem.structure_core.Member(
            no=10,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=10),
        rfem.structure_core.Member(
            no=11,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=11),
        rfem.structure_core.Member(
            no=12,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=12),
        rfem.structure_core.Member(
            no=13,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=13),
        rfem.structure_core.Member(
            no=14,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=14),
        rfem.structure_core.Member(
            no=15,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=15),
        rfem.structure_core.Member(
            no=16,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=16),

        # Beams
        rfem.structure_core.Member(
            no=17,
            line=17,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=18,
            line=18,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=19,
            line=19,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=20,
            line=20,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=21,
            line=21,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=22,
            line=22,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=23,
            line=23,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=24,
            line=24,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=25,
            line=25,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=26,
            line=26,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=27,
            line=27,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=28,
            line=28,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=29,
            line=29,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=30,
            line=30,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=31,
            line=31,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=32,
            line=32,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=33,
            line=33,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=34,
            line=34,
            section_start=4,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=35,
            line=35,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=36,
            line=36,
            section_start=4,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=37,
            line=37,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=38,
            line=38,
            section_start=4,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=39,
            line=39,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=40,
            line=40,
            section_start=5,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=41,
            line=49,
            section_start=5,
            rotation_angle=1.57079632679487),
        rfem.structure_core.Member(
            no=42,
            line=50,
            section_start=5),
        rfem.structure_core.Member(
            no=43,
            line=51,
            section_start=5,
            rotation_angle=-1.57079632679487),
        rfem.structure_core.Member(
            no=44,
            line=52,
            section_start=5,
            rotation_angle=3.14159265358974),

        # Solid
        rfem.structure_core.Solid(
            no=1,
            type=rfem.structure_core.Solid.TYPE_STANDARD,
            material=2,
            boundary_surfaces=[1, 2, 3, 4, 5, 10]),

        # Nodal Support
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1, 2, 3, 4],
            spring_x=700000,
            spring_y=800000,
            spring_z=5000000),

        # Member Hinge
        rfem.types_for_members.MemberHinge(
            no=1,
            moment_release_mt=28000,
            axial_release_n=inf,
            axial_release_vy=inf,
            axial_release_vz=inf),
        rfem.types_for_members.MemberHinge(
            no=2,
            moment_release_mt=29000,
            axial_release_n=inf,
            axial_release_vy=inf,
            axial_release_vz=inf,
            moment_release_mz=inf),

        # Static Analysis Settings
        rfem.loading.StaticAnalysisSettings(
            no=1),
        rfem.loading.StaticAnalysisSettings(
            no=2,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_SECOND_ORDER_P_DELTA,
            number_of_load_increments=2),
        rfem.loading.StaticAnalysisSettings(
            no=3,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_LARGE_DEFORMATIONS,
            number_of_load_increments=10),

        # Load Cases
        rfem.loading.LoadCase(
            no=1,
            name="Self weight",
            static_analysis_settings=1),
        rfem.loading.LoadCase(
            no=2,
            name="Live load",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_IMPOSED_GQ),
        rfem.loading.LoadCase(
            no=3,
            name="Stability - linear",
            static_analysis_settings=1,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_IMPOSED_GQ,
            self_weight_active=True),
    ]

    # Create all objects related to loading in active model
    rfem_app.create_object_list(lst)

    # Connection is terminated automatically at the end of the scope manager or at the end of the script.
    # If the connection needs to be terminated separately, use rfem_app.close_connection().
    rfem_app.calculate_all(skip_warnings=True)

    # Results access
    surface_filter = rfem.results.ResultsFilter(
            column_id='surface_no',
            filter_expression='2, 3, 4, 5'
    )

    print("\nAll Results | Grid Points:")
    results_grid_df = rfem_app.get_results(
        results_type=rfem.results.STATIC_ANALYSIS_SURFACES_BASIC_INTERNAL_FORCES_GRID_POINTS,
        filters = [surface_filter],
    ).data
    print(results_grid_df)


    print("\nAll Results | Mesh Nodes:")
    results_mesh_df = rfem_app.get_results(
        results_type=rfem.results.STATIC_ANALYSIS_SURFACES_BASIC_INTERNAL_FORCES_MESH_NODES,
        filters = [surface_filter],
    ).data
    print(results_mesh_df)
