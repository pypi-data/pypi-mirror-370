from dlubal.api import rstab


def define_structure() -> list:
    """Define and return a list of structural objects."""

    inf = float('inf')

    return [
        # Define material
        rstab.structure_core.Material(no=1, name='S235'),

        # Define section
        rstab.structure_core.Section(no=1, name='HE 200 A', material=1),

        # Define nodes
        rstab.structure_core.Node(no=1),
        rstab.structure_core.Node(no=2, coordinate_3=-3.0),
        rstab.structure_core.Node(no=3, coordinate_1=4.0, coordinate_3=-3.0),
        rstab.structure_core.Node(no=4, coordinate_1=4.0),

        # Define member
        rstab.structure_core.Member(no=1, node_start=1, node_end=2, section_start=1),
        rstab.structure_core.Member(no=2, node_start=2, node_end=3, section_start=1),
        rstab.structure_core.Member(no=3, node_start=3, node_end=4, section_start=1),

        # Define nodal support at Node 1 (fully fixed)
        rstab.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1,4],
            spring_x=inf, spring_y=inf, spring_z=inf,
            rotational_restraint_x=inf,
            rotational_restraint_y=inf,
            rotational_restraint_z=inf
        ),
    ]


def define_loads() -> list:
    """Define and return a list of loading objects."""

    return [
        # Static analysis settings
        rstab.loading.StaticAnalysisSettings(
            no=1,
            analysis_type=rstab.loading.StaticAnalysisSettings.ANALYSIS_TYPE_GEOMETRICALLY_LINEAR,
        ),

        # Define load cases
        rstab.loading.LoadCase(
            no=1,
            name='Self-weight',
            self_weight_active=True,
            static_analysis_settings=1,
        ),
        rstab.loading.LoadCase(
            no=2,
            name='Snow',
            action_category=rstab.loading.LoadCase.ACTION_CATEGORY_SNOW_ICE_LOADS_H_LESS_OR_EQUAL_TO_1000_M_QS,
            static_analysis_settings=1,
        ),
        rstab.loading.LoadCase(
            no=3,
            name='Wind +x',
            action_category=rstab.loading.LoadCase.ACTION_CATEGORY_WIND_QW,
            static_analysis_settings=1,
        ),
        rstab.loading.LoadCase(
            no=4,
            name='Wind +x, with wind suction',
            action_category=rstab.loading.LoadCase.ACTION_CATEGORY_WIND_QW,
            static_analysis_settings=1,
        ),
        rstab.loading.LoadCase(
            no=5,
            name='Wind -x',
            action_category=rstab.loading.LoadCase.ACTION_CATEGORY_WIND_QW,
            static_analysis_settings=1,
        ),
        rstab.loading.LoadCase(
            no=6,
            name='Wind -x, with wind suction',
            action_category=rstab.loading.LoadCase.ACTION_CATEGORY_WIND_QW,
            static_analysis_settings=1,
        ),

        # Define loads
        rstab.loads.MemberLoad(
            no=1,
            load_case=1,
            members=[2],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=1000
        ),
        rstab.loads.MemberLoad(
            no=2,
            load_case=2,
            members=[2],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=3000
        ),
        rstab.loads.MemberLoad(
            no=3,
            load_case=3,
            members=[1],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=2000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=4,
            load_case=3,
            members=[3],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=1000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=5,
            load_case=4,
            members=[1],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=2000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=6,
            load_case=4,
            members=[3],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=1000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=7,
            load_case=4,
            members=[2],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=-500
        ),
        rstab.loads.MemberLoad(
            no=8,
            load_case=5,
            members=[1],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=-2000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=9,
            load_case=5,
            members=[3],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=-1000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=10,
            load_case=6,
            members=[1],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=-2000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=11,
            load_case=6,
            members=[3],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=-1000,
            load_direction=rstab.loads.MemberLoad.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH,
        ),
        rstab.loads.MemberLoad(
            no=12,
            load_case=6,
            members=[2],
            load_type=rstab.loads.MemberLoad.LOAD_TYPE_FORCE,
            magnitude=-500
        ),
        rstab.loading.CombinationWizard(
            no=1,
            static_analysis_settings=1,
        ),
        rstab.loading.DesignSituation(
            no=1,
            design_situation_type=rstab.loading.DesignSituation.DESIGN_SITUATION_TYPE_STR_PERMANENT_AND_TRANSIENT_6_10,
            combination_wizard=1,
        ),
    ]


with rstab.Application() as rstab_app:

    # Step 1: Create a new model and clear existing objects
    rstab_app.create_model(name='frame')
    rstab_app.delete_all_objects()

    # Step 2: Define and create the structure and load objects
    base_data = rstab_app.get_base_data()
    base_data.combinations_settings.activate_combination_wizard = True
    base_data.combinations_settings.result_combinations_active = True
    rstab_app.set_base_data(base_data=base_data)

    # Step 3: Define and create the structure and load objects
    objects = define_structure() + define_loads()
    rstab_app.create_object_list(objects)

    # Step 4: Generate Load Combinations
    print("\nLoad Combinations:")
    rstab_app.generate_combinations()
    all_load_combi = rstab_app.get_object_list([rstab.loading.LoadCombination()])

    # Step 5: Create Result Combination as an envelope from all Load Combinations
    result_combi_rows = []
    for i, load_combi in enumerate(all_load_combi):
        # Check if this is the last item in the list
        print(f"CO{load_combi.no} - {load_combi.combination_rule_str}")

        if i < len(all_load_combi) - 1:
            operator = rstab.loading.ResultCombination.ItemsRow.OPERATOR_OR
        else:
            operator = rstab.loading.ResultCombination.ItemsRow.OPERATOR_NONE

        result_combi_rows.append(
            rstab.loading.ResultCombination.ItemsRow(
                case_object_item=rstab.ObjectId(
                    no=load_combi.no,
                    object_type=rstab.OBJECT_TYPE_LOAD_COMBINATION,
                ),
                case_object_factor=1,
                operator=operator,
            )
        )

    print("\nResult Combination:")
    rstab_app.create_object(
        rstab.loading.ResultCombination(
            no=1,
            user_defined_name_enabled=True,
            name='All ULS',
            design_situation=1,
            items=rstab.loading.ResultCombination.ItemsTable(
                rows = result_combi_rows,
            )
        )
    )
    result_combi = rstab_app.get_object(rstab.loading.ResultCombination(no=1))
    print(f"{result_combi.name} - {result_combi.combination_rule_str}")

    # Step 6: Calculate specific
    rstab_app.calculate_specific(
        loadings=[
            rstab.ObjectId(
                no=1,
                object_type=rstab.OBJECT_TYPE_RESULT_COMBINATION
            )
        ],
        skip_warnings=False,
    )

    # Step 7: Read results using optional filtering
    member_filter = rstab.results.ResultsFilter(
        column_id='member_no',
        filter_expression='2'
    )

    results_df = rstab_app.get_results(
        results_type=rstab.results.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        filters=[member_filter],
    ).data

    print("\nAll Results:")
    print(results_df)

    # Step 8: Find maximum m_y envelope on specific member
    loading = "RC1"
    tag = 'm_y_max'

    my_max_df = results_df[
        (results_df['loading'] == loading) &
        (results_df['tag'] == tag)
    ]

    print("\nMaximum My:")
    print(my_max_df)
