import os
from math import inf
from dlubal.api import rstab

def define_structure() -> list:
    """Define and return a list of structural objects."""

    return [
        # Define material
        rstab.structure_core.Material(
            no=1,
            name='S235',
        ),

        # Define section
        rstab.structure_core.Section(
            no=1,
            name='HE 300 A',
            material=1,
        ),

        # Define nodes
        rstab.structure_core.Node(
            no=1,
        ),
        rstab.structure_core.Node(
            no=2,
            coordinate_1=6.0,
        ),

        # Define member
        rstab.structure_core.Member(
            no=1,
            node_start=1,
            node_end=2,
            section_start=1,
        ),

        # Define nodal support at Node 1 (fully fixed)
        rstab.types_for_nodes.NodalSupport(
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
        rstab.loading.StaticAnalysisSettings(
            no=1,
            analysis_type=rstab.loading.StaticAnalysisSettings.ANALYSIS_TYPE_GEOMETRICALLY_LINEAR
        ),

        # Define load cases
        rstab.loading.LoadCase(
            no=1,
            static_analysis_settings=1,
        ),
        rstab.loading.LoadCase(
            no=2,
            static_analysis_settings=1,
        ),

        # Define nodal loads
        rstab.loads.NodalLoad(
            no=1,
            load_case=1,
            nodes=[2],
            load_type=rstab.loads.NodalLoad.LOAD_TYPE_COMPONENTS,
            components_force_y=5000,  # Force in Y direction (N)
            components_force_z=10000,  # Force in Z direction (N)
        ),
        rstab.loads.MemberLoad(
            no=1,
            load_case=2,
            members=[1],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=10000,
        ),

        # Define design situation
        rstab.loading.DesignSituation(
            no=1,
            design_situation_type=rstab.loading.DesignSituation.DESIGN_SITUATION_TYPE_STR_PERMANENT_AND_TRANSIENT_6_10,
        ),

        # Define load combination
        rstab.loading.LoadCombination(
            no=1,
            name='CO1',
            items =  rstab.loading.LoadCombination.ItemsTable(
                    rows=[
                        rstab.loading.LoadCombination.ItemsRow(
                            load_case=1,
                            factor=1.35,
                        ),
                        rstab.loading.LoadCombination.ItemsRow(
                            load_case=2,
                            factor=1.5,
                        )
                    ]
            ),
            design_situation=1,
        ),
        rstab.loading.LoadCombination(
            no=2,
            name='CO2',
            items =  rstab.loading.LoadCombination.ItemsTable(
                    rows=[
                        rstab.loading.LoadCombination.ItemsRow(
                            load_case=1,
                            factor=0.85,
                        ),
                        rstab.loading.LoadCombination.ItemsRow(
                            load_case=2,
                            factor=1.0,
                        )
                    ]
            ),
            design_situation=1,
        ),
    ]


""" ----- Creat and calculate a Cantilever model in RSTAB ----- """

with rstab.Application() as rstab_app:

    # Step 1: Create a new RFEM model for the cantilever structure
    rstab_app.create_model(name='cantilever')

    # Step 2: Ensure the model is empty by removing all pre-existing objects
    rstab_app.delete_all_objects()

    # Step 3: Define and generate all structure and loading objects
    objects = define_structure() + define_loading()
    rstab_app.create_object_list(objects)

    # Step 4: Retrieve and print information about load combinations in the model
    print("\nLoad Combinations:")
    object_list = rstab_app.get_object_list([rstab.loading.LoadCombination()])
    for object in object_list:
        print(f"{object.DESCRIPTOR.name} | {object.name} | {object.combination_rule_str}")

    # Step 5: Calculate the model
    calculation = rstab_app.calculate_all(skip_warnings=True)
    print(f"\nCalculation Info:\n{calculation}")

    # Step 6: Get results for nodal support forces (reactions) after calculation
    supp_forces = rstab_app.get_results(
        results_type=rstab.results.STATIC_ANALYSIS_NODES_SUPPORT_FORCES
    ).data
    print(f"\nResults | Nodes Support Forces:\n{supp_forces}")

    # Step 7: Save the model with results to the specified path
    model_path = os.path.abspath('./cantilever')
    rstab_app.save_model(path=model_path)
    print(f"\nModel File Path:\n{rstab_app.get_model_main_parameters().model_path}")
