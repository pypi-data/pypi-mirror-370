from dlubal.api import rfem
from math import inf
import os


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


""" ----- Creat and calculate a Cantilever model in RFEM ----- """

with rfem.Application() as rfem_app:

    # Step 1: Create a new RFEM model for the cantilever structure
    rfem_app.create_model(name='cantilever')

    # Step 2: Ensure the model is empty by removing all pre-existing objects
    rfem_app.delete_all_objects()

    # Step 3: Define and generate all structure and loading objects
    objects = define_structure() + define_loading()
    rfem_app.create_object_list(objects)

    # Step 4: Retrieve and print information about load combinations in the model
    print("\nLoad Combinations:")
    object_list = rfem_app.get_object_list([rfem.loading.LoadCombination()])
    for object in object_list:
        print(f"{object.DESCRIPTOR.name} | {object.name} | {object.combination_rule_str}")

    # Step 5: Calculate the model
    calculation_info = rfem_app.calculate_all(skip_warnings=True)
    print(f"\nCalculation Info:\n{calculation_info}")

    # Step 6: Get results for nodal support forces (reactions) after calculation
    results_reactions = rfem_app.get_results(
        results_type=rfem.results.STATIC_ANALYSIS_NODES_SUPPORT_FORCES
    ).data
    print(f"\nResults | Nodes Support Forces:\n{results_reactions}")

    # Step 7: Save the model with results to the specified path
    model_path = os.path.abspath('./cantilever')
    rfem_app.save_model(path=model_path)
    print(f"\nModel File Path:\n{rfem_app.get_model_main_parameters().model_path}")
