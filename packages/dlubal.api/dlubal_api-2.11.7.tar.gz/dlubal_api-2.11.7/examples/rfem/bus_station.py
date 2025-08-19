from math import inf
from dlubal.api import rfem
from dlubal.api import common

# Connect to the RFEM application
with rfem.Application() as rfem_app:
    # Create new empty model
    rfem_app.create_model(name="bus_station")

    # Cleanup the model
    rfem_app.delete_all_objects()

    # List of model objects to be created
    lst = [
        # Structure
        rfem.structure_core.Material(
            no=1,
            name="S235 | EN 1993-1-1:2005-05",
        ),
        rfem.structure_core.Material(
            no=2,
            name="C12/15 | EN 1992-1-1:2004/A1:2014",
        ),
        # Section
        rfem.structure_core.Section(
            no=1,
            material=1,
            name="IPE 240 | -- | British Steel",
            shear_stiffness_deactivated=True,
        ),
        rfem.structure_core.Section(
            no=2, material=1, name="IPE 180 | -- | British Steel"
        ),
        # Thickness
        rfem.structure_core.Thickness(
            no=1, material=2, uniform_thickness=0.12, assigned_to_surfaces=[1, 2, 3, 4]
        ),
        # Nodes
        rfem.structure_core.Node(no=1, coordinate_1=0, coordinate_2=0, coordinate_3=-4),
        rfem.structure_core.Node(
            no=2, coordinate_1=9.5, coordinate_2=0, coordinate_3=-4
        ),
        rfem.structure_core.Node(
            no=3, coordinate_1=9.5, coordinate_2=6, coordinate_3=-4
        ),
        rfem.structure_core.Node(
            no=4,
            coordinate_1=0,
            coordinate_2=6,
            coordinate_3=-4,
        ),
        rfem.structure_core.Node(
            no=6,
            coordinate_1=5,
            coordinate_2=2,
            coordinate_3=-4,
        ),
        rfem.structure_core.Node(
            no=7,
            coordinate_1=7,
            coordinate_2=2,
            coordinate_3=-4,
        ),
        rfem.structure_core.Node(
            no=8,
            coordinate_1=7,
            coordinate_2=4,
            coordinate_3=-4,
        ),
        rfem.structure_core.Node(
            no=9,
            coordinate_1=5,
            coordinate_2=4,
            coordinate_3=-4,
        ),
        rfem.structure_core.Node(
            no=10,
            coordinate_1=0,
            coordinate_2=6,
            coordinate_3=0,
        ),
        rfem.structure_core.Node(
            no=11,
            coordinate_1=0,
            coordinate_2=0,
            coordinate_3=0,
        ),
        rfem.structure_core.Node(
            no=12,
            coordinate_1=6,
            coordinate_2=6,
            coordinate_3=-4,
        ),
        rfem.structure_core.Node(
            no=13,
            coordinate_1=9.5,
            coordinate_2=0,
            coordinate_3=0,
        ),
        rfem.structure_core.Node(
            no=14,
            coordinate_1=9.5,
            coordinate_2=6,
            coordinate_3=0,
        ),
        rfem.structure_core.Node(
            no=16,
            coordinate_1=6,
            coordinate_2=6,
            coordinate_3=0,
        ),
        rfem.structure_core.Node(
            no=17,
            coordinate_1=0,
            coordinate_2=5,
            coordinate_3=-3,
        ),
        rfem.structure_core.Node(
            no=18,
            coordinate_1=0,
            coordinate_2=3,
            coordinate_3=-3.52,
        ),
        rfem.structure_core.Node(
            no=19,
            coordinate_1=0,
            coordinate_2=1,
            coordinate_3=-3,
        ),
        rfem.structure_core.Node(
            no=20,
            coordinate_1=0,
            coordinate_2=5.456,
            coordinate_3=0,
        ),
        rfem.structure_core.Node(
            no=21,
            coordinate_1=0,
            coordinate_2=0.588,
            coordinate_3=0,
        ),
        # Lines
        rfem.structure_core.Line(
            no=1,
            definition_nodes=[1, 2],
        ),
        rfem.structure_core.Line(
            no=2,
            definition_nodes=[11, 13],
        ),
        rfem.structure_core.Line(
            no=3,
            definition_nodes=[12, 3],
        ),
        rfem.structure_core.Line(
            no=4,
            definition_nodes=[4, 1],
        ),
        rfem.structure_core.Line(
            no=5,
            definition_nodes=[17, 20],
        ),
        rfem.structure_core.Line(
            no=6,
            definition_nodes=[2, 3],
        ),
        rfem.structure_core.Line(
            no=7,
            definition_nodes=[6, 7],
        ),
        rfem.structure_core.Line(
            no=8,
            definition_nodes=[7, 8],
        ),
        rfem.structure_core.Line(
            no=9,
            definition_nodes=[8, 9],
        ),
        rfem.structure_core.Line(
            no=10,
            definition_nodes=[9, 6],
        ),
        rfem.structure_core.Line(
            no=11,
            definition_nodes=[4, 10],
        ),
        rfem.structure_core.Line(
            no=12,
            definition_nodes=[10, 20],
        ),
        rfem.structure_core.Line(
            no=13,
            definition_nodes=[11, 1],
        ),
        rfem.structure_core.Line(
            no=14,
            definition_nodes=[2, 13],
        ),
        rfem.structure_core.Line(
            no=15,
            type=rfem.structure_core.Line.TYPE_ARC,
            arc_first_node=17,
            arc_second_node=19,
            arc_control_point=common.Vector3d(x=0, y=3, z=-3.52),
        ),
        rfem.structure_core.Line(
            no=16,
            definition_nodes=[13, 14],
        ),
        rfem.structure_core.Line(
            no=17,
            definition_nodes=[3, 14],
        ),
        rfem.structure_core.Line(
            no=18,
            definition_nodes=[4, 12],
        ),
        rfem.structure_core.Line(
            no=19,
            definition_nodes=[12, 16],
        ),
        rfem.structure_core.Line(
            no=21,
            definition_nodes=[20, 21],
        ),
        rfem.structure_core.Line(
            no=22,
            definition_nodes=[21, 11],
        ),
        rfem.structure_core.Line(
            no=23,
            definition_nodes=[21, 19],
        ),
        # Members
        rfem.structure_core.Member(
            no=1,
            line=18,
            section_start=1,
        ),
        rfem.structure_core.Member(
            no=2,
            line=3,
            section_start=1,
        ),
        rfem.structure_core.Member(
            no=3,
            line=19,
            section_start=2,
        ),
        # Surfaces
        rfem.structure_core.Surface(
            no=1,
            boundary_lines=[4, 13, 22, 21, 12, 11],
            grid_origin=common.Vector3d(x=0, y=6, z=-4),
        ),
        rfem.structure_core.Surface(
            no=2,
            boundary_lines=[6, 14, 16, 17],
            grid_origin=common.Vector3d(x=9.5, y=0, z=-4),
        ),
        rfem.structure_core.Surface(
            no=3,
            boundary_lines=[2, 14, 1, 13],
            grid_origin=common.Vector3d(x=0, y=0, z=0),
        ),
        rfem.structure_core.Surface(
            no=4,
            boundary_lines=[1, 6, 3, 18, 4],
            grid_origin=common.Vector3d(x=0, y=0, z=-4),
        ),
        # Openings
        rfem.structure_core.Opening(
            no=1,
            boundary_lines=[5, 15, 23, 21],
        ),
        rfem.structure_core.Opening(
            no=5,
            boundary_lines=[7, 8, 9, 10],
        ),
        # Nodal Support
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[16],
            spring=common.Vector3d(x=inf, y=inf, z=inf),
            rotational_restraint=common.Vector3d(x=0, y=0, z=inf),
        ),
        # Line Support
        rfem.types_for_lines.LineSupport(
            no=1,
            lines=[2, 12, 16, 22],
            spring=common.Vector3d(x=inf, y=inf, z=inf),
            rotational_restraint=common.Vector3d(x=0, y=0, z=inf),
        ),
        # Member Eccentricity
        rfem.types_for_members.MemberEccentricity(
            no=1,
            name="Relative and Absolute | Middle - Top | Local xyz",
            specification_type=rfem.types_for_members.MemberEccentricity.SPECIFICATION_TYPE_RELATIVE_AND_ABSOLUTE,
            vertical_section_alignment=rfem.types_for_members.MemberEccentricity.VERTICAL_SECTION_ALIGNMENT_TOP,
        ),
        # Member Hinge
        rfem.types_for_lines.LineMeshRefinement(
            no=1,
            type=rfem.types_for_lines.LineMeshRefinement.TYPE_LENGTH,
            target_length=0.1,
            number_of_layers=2,
        ),
        # Surface Mesh Refinement
        rfem.types_for_surfaces.SurfaceMeshRefinement(
            no=1,
            surfaces=[3],
            target_length=0.8,
        ),
        # Solid Mesh Refinement
        rfem.types_for_solids.SolidMeshRefinement(
            no=1,
            target_length=0.01,
        ),
        # Load Cases
        rfem.loading.LoadCase(
            no=1,
            name="Self weight",
            static_analysis_settings=1,
        ),
        rfem.loading.LoadCase(
            no=2,
            name="Live load",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_IMPOSED_LOADS_CATEGORY_H_ROOFS_QI_H,
        ),
        # Nodal Load
        rfem.loads.NodalLoad(
            no=1,
            load_case=2,
            load_type=rfem.loads.NodalLoad.LOAD_TYPE_COMPONENTS,
            nodes=[12],
            components_force_x=1000,
            components_force_y=2000,
            components_force_z=3000,
        ),
        # Line Load
        rfem.loads.LineLoad(
            no=1,
            load_case=2,
            lines=[15],
            magnitude=1250.0,
            load_type=rfem.loads.LineLoad.LOAD_TYPE_FORCE,
            load_distribution=rfem.loads.LineLoad.LOAD_DISTRIBUTION_UNIFORM,
            load_direction=rfem.loads.LineLoad.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH,
        ),
        # Member Load
        rfem.loads.MemberLoad(
            no=1,
            load_case=2,
            members=[1, 2],
            magnitude=1250,
            coordinate_system=common.CoordinateSystemRepresentation(
                type=common.CoordinateSystemRepresentation.COORDINATE_SYSTEM_TYPE_LOCAL),
            load_type=rfem.loads.MemberLoad.LOAD_TYPE_FORCE,
        ),
        # Surface Load
        rfem.loads.SurfaceLoad(
            no=1,
            load_case=2,
            load_type=rfem.loads.SurfaceLoad.LOAD_TYPE_FORCE,
            surfaces=[4],
            uniform_magnitude=750,
        ),

        # Design Situation
        rfem.loading.DesignSituation(
            no=1,
            user_defined_name_enabled=True,
            name="DS 1",
            design_situation_type=rfem.loading.DesignSituation.DESIGN_SITUATION_TYPE_STR_PERMANENT_AND_TRANSIENT_6_10,
        ),

        # Static Analysis Settings
        rfem.loading.StaticAnalysisSettings(no=1),
        rfem.loading.StaticAnalysisSettings(
            no=2,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_SECOND_ORDER_P_DELTA,
        ),
        rfem.loading.StaticAnalysisSettings(
            no=3,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_LARGE_DEFORMATIONS,
            number_of_load_increments=10,
        ),
    ]

    # Create all objects from the list in the active model.
    rfem_app.create_object_list(lst)

    # Calculate all
    rfem_app.calculate_all(skip_warnings=True)
