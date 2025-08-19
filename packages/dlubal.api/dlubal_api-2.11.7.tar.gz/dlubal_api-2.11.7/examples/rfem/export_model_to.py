import os
from math import inf
from dlubal.api import rfem, common

def define_structure() -> list:
    """Define and return a list of structural objects."""

    return [
        # Define material
        rfem.structure_core.Material(
            no=1,
            name='S235',
        ),

        # Define section
        rfem.structure_core.Section(
            no=1,
            name='HE 300 A',
            material=1,
        ),

        # Define nodes
        rfem.structure_core.Node(
            no=1,
        ),
        rfem.structure_core.Node(
            no=2,
            coordinate_1=6.0,
        ),

        # Define line
        rfem.structure_core.Line(
            no=1,
            definition_nodes=[1, 2],
        ),

        # Define member
        rfem.structure_core.Member(
            no=1,
            line=1,
            section_start=1,
        ),

        # Define nodal support at Node 1 (fully fixed)
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_x=inf,
            rotational_restraint_y=inf,
            rotational_restraint_z=inf,
        ),
    ]

def define_loading() -> list:
    """Define and return a list of loading objects."""

    return [
        # Static analysis settings
        rfem.loading.StaticAnalysisSettings(
            no=1,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_GEOMETRICALLY_LINEAR
        ),

        # Define load cases
        rfem.loading.LoadCase(
            no=1,
            static_analysis_settings=1,
        ),
        rfem.loading.LoadCase(
            no=2,
            static_analysis_settings=1,
        ),

        # Define nodal loads
        rfem.loads.NodalLoad(
            no=1,
            load_case=1,
            nodes=[2],
            load_type=rfem.loads.NodalLoad.LOAD_TYPE_COMPONENTS,
            components_force_y=5000,  # Force in Y direction (N)
            components_force_z=10000,  # Force in Z direction (N)
        ),
        rfem.loads.MemberLoad(
            no=1,
            load_case=2,
            members=[1],
            load_type=rfem.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=10000,
        ),

        # Define design situation
        rfem.loading.DesignSituation(
            no=1,
            design_situation_type=rfem.loading.DesignSituation.DESIGN_SITUATION_TYPE_STR_PERMANENT_AND_TRANSIENT_6_10,
        ),

        # Define load combination
        rfem.loading.LoadCombination(
            no=1,
            name='CO1',
            items =  rfem.loading.LoadCombination.ItemsTable(
                    rows=[
                        rfem.loading.LoadCombination.ItemsRow(
                            load_case=1,
                            factor=1.35,
                        ),
                        rfem.loading.LoadCombination.ItemsRow(
                            load_case=2,
                            factor=1.5,
                        )
                    ]
            ),
            design_situation=1,
        ),
        rfem.loading.LoadCombination(
            no=2,
            name='CO2',
            items =  rfem.loading.LoadCombination.ItemsTable(
                    rows=[
                        rfem.loading.LoadCombination.ItemsRow(
                            load_case=1,
                            factor=0.85,
                        ),
                        rfem.loading.LoadCombination.ItemsRow(
                            load_case=2,
                            factor=1.0,
                        )
                    ]
            ),
            design_situation=1,
        ),
    ]


"""Runs the structural analysis example."""

with rfem.Application() as rfem_app:

    # Step 1: Create a new model
    rfem_app.close_all_models(save_changes=False)
    rfem_app.create_model(name='cantilever')

    # Step 2: Clear existing objects
    rfem_app.delete_all_objects()

    # Step 3: Define and create all objects
    objects = define_structure() + define_loading()
    rfem_app.create_object_list(objects)

    # Step 4: Export model as python script
    rfem_app.export_model_to(
        filepath=os.path.abspath('./model_exported.py'),
        export_attributes=common.import_export.PythonGrpcExportAttributes()
    )

    rfem_app.export_model_to(
        filepath=os.path.abspath('./model_exported.ifc'),
        export_attributes=common.import_export.IfcExportAttributes()
    )