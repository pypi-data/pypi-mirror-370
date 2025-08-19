from dlubal.api import rfem
from math import inf

def define_structure() -> list:
    """Returns a list of structural objects to be created."""

    return [
        rfem.structure_core.Material(
            no=1,
            name='S235',
        ),
        rfem.structure_core.Section(
            no=1,
            name='HEB 300',
            material=1,
            shear_stiffness_deactivated=True,
        ),
        rfem.structure_core.Node(
            no=1,
        ),
        rfem.structure_core.Node(
            no=2,
            coordinate_3=10.0,
        ),
        rfem.structure_core.Member(
            no = 1,
            line = 1,
            node_start=1,
            node_end=2,
            section_start = 1
        ),
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_x=5000000,
            rotational_restraint_y=5000000,
            rotational_restraint_z=inf,
        ),
        rfem.types_for_nodes.NodalSupport(
            no=2,
            nodes=[2],
            spring_x=inf,
            spring_y=inf,
            spring_z=0,
            rotational_restraint_x=0,
            rotational_restraint_y=0,
            rotational_restraint_z=inf,
        ),
    ]

def define_loading() -> list:
    """Returns a list of loading objects to be created."""

    return [
        rfem.loading.StaticAnalysisSettings(
            no=1,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_GEOMETRICALLY_LINEAR
        ),
        rfem.loading.StabilityAnalysisSettings(
            no=1,
            analysis_type=rfem.loading.StabilityAnalysisSettings.ANALYSIS_TYPE_EIGENVALUE_METHOD,
            number_of_lowest_eigenvalues=2,
        ),
        rfem.loading.LoadCase(
            no=1,
            stability_analysis_settings=1,
            calculate_critical_load=True,
            self_weight_active=False,
        ),
        rfem.loads.NodalLoad(
            no=1,
            load_case=1,
            nodes=[2],
            load_type=rfem.loads.NodalLoad.LOAD_TYPE_COMPONENTS,
            components_force_z=-1000000,
        ),
        rfem.loading.DesignSituation(
            no=1,
            design_situation_type=rfem.loading.DesignSituation.DESIGN_SITUATION_TYPE_STR_PERMANENT_AND_TRANSIENT_6_10,
        ),
        rfem.loading.LoadCombination(
            no=1,
            name='CO1',
            items =  rfem.loading.LoadCombination.ItemsTable(
                    rows=[
                        rfem.loading.LoadCombination.ItemsRow(
                            load_case=1,
                            factor=1,
                        ),
                    ]
            ),
            design_situation=1,
        ),
    ]

def define_steel_design() -> list:
    """Returns a list of steel design related objects to be created."""

    return [
        rfem.steel_design_objects.SteelDesignUlsConfiguration(
            no=1,
            assigned_to_all_members=True,
        ),
        rfem.types_for_steel_design.SteelEffectiveLengths(
            no=1,
            members=[1],
            import_from_stability_analysis_enabled=True,
            stability_import_data_loading_y=rfem.ObjectId(no=1, object_type=rfem.ObjectType.OBJECT_TYPE_LOAD_CASE),
            stability_import_data_loading_z=rfem.ObjectId(no=1, object_type =rfem.ObjectType.OBJECT_TYPE_LOAD_CASE),
            stability_import_data_mode_number_y=2,
            stability_import_data_mode_number_z=1,
            stability_import_data_member_y=1,
            stability_import_data_member_z=1,
        ),
    ]


"""Runs the example of column stability analysis."""
with rfem.Application() as rfem_app:

    # Step 1: Create a New Model
    rfem_app.close_all_models(save_changes=False)
    rfem_app.create_model(name='column_stability')

    # Configure Add-ons, Design Standards, and Global Settings in Base Data
    base_data = rfem_app.get_base_data()
    base_data.addons.structure_stability_active = True
    base_data.addons.steel_design_active = True
    base_data.standards.steel_design_standard = rfem.BaseData.Standards.STEEL_DESIGN_NATIONAL_ANNEX_AND_EDITION_EN_1993_DIN_2020_11_STANDARD
    base_data.general_settings.global_axes_orientation = rfem.BaseData.GeneralSettings.GLOBAL_AXES_ORIENTATION_ZUP
    rfem_app.set_base_data(base_data=base_data)

    # Step 3: Create Structure and Loading in Empty Model
    rfem_app.delete_all_objects()
    objects = define_structure() + define_loading()
    rfem_app.create_object_list(objects)

    # Step 4: Perform the Stability analysis
    stability_analysis = rfem_app.calculate_all(skip_warnings=True)
    print(f"\nStability Analysis:\n{stability_analysis}")

    # Step 5: Define Steel Design related objects
    objects = define_steel_design()
    rfem_app.create_object_list(objects)

    # Step 6: Perform the Steel design check
    steel_design = rfem_app.calculate_all(skip_warnings=True)
    print(f"\nSteel Design Check:\n{steel_design}")

    # Step 7: Get steel design check results
    steel_design_check = rfem_app.get_results(
        results_type=rfem.results.STEEL_DESIGN_MEMBERS_DESIGN_RATIOS_BY_LOCATION
    ).data
    print(f"\nResults | Steel Design Ratios by Location | All:")
    print(steel_design_check)

    # Step 8: Get steel design check details for the maximum ratio
    max_design_ratio_row = steel_design_check.loc[steel_design_check['design_ratio'].idxmax()]
    design_check_details_id = max_design_ratio_row['design_check_details_id']

    steel_design_details = rfem_app.get_results(
        results_type=rfem.results.STEEL_DESIGN_DESIGN_CHECK_DETAILS,
        filters=[rfem.results.ResultsFilter(
            column_id="design_check_details_id",
            filter_expression=str(design_check_details_id))],
    ).data
    print(steel_design_details)

     # Step 9: Get detail row for specific variable
    symbol = 'N<sub>c,Ed</sub>'
    n_ed_value = steel_design_details.loc[steel_design_details['symbol']==symbol, 'value'].values[0]
    n_ed_unit = steel_design_details.loc[steel_design_details['symbol']==symbol, 'unit'].values[0]
    print(f"\nN_Ed= {n_ed_value} [{n_ed_unit}]")

    symbol = 'N<sub>b,z,Rd</sub>'
    n_rd_value = steel_design_details.loc[steel_design_details['symbol']==symbol, 'value'].values[0]
    n_rd_unit = steel_design_details.loc[steel_design_details['symbol']==symbol, 'unit'].values[0]
    print(f"N_Rd= {n_rd_value} [{n_rd_unit}]")

    symbol = 'η'
    ratio_value = steel_design_details.loc[steel_design_details['symbol']==symbol, 'value_si'].values[0]
    print(f"η= {ratio_value} [-]")