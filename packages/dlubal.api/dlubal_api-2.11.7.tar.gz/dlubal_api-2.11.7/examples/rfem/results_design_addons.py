from dlubal.api import rfem

with rfem.Application() as rfem_app:

    calculation_info = rfem_app.calculate_all(
        skip_warnings=False
    )

    if calculation_info.succeeded:

        # --- Retriev results from the active model (already calculated) ---

        # 1. get_results: Returns all results of the specified type directly from the database.
        #    This is the full dataset, including all possible columns and data. Use this for custom analytics,
        #    advanced filtering, or to access values not shown in the GUI summary.
        design_ratios_df = rfem_app.get_results(
            results_type=rfem.results.ResultsType.STEEL_DESIGN_MEMBERS_DESIGN_RATIOS
        ).data
        print(f"\n\nSteel Design | Design Ratios | Raw Data")
        print(design_ratios_df)


        # 2. get_result_table: Returns a specific result table as it appears in the desktop GUI in default state.
        #    Only the most important values are included, mirroring what end users see for quick review or export.
        design_ratios_by_member_df = rfem_app.get_result_table(
            table = rfem.results.ResultTable.STEEL_DESIGN_MEMBERS_DESIGN_RATIOS_BY_MEMBER_TABLE,
            loading = None
        ).data
        print(f"\n\nSteel Design | Design Ratios by Member | Table:")
        print(design_ratios_by_member_df)


        # 1. get_results: Returns all results of the specified type directly from the database.
        #    This is the full dataset, including all possible columns and data. Use this for custom analytics,
        #    advanced filtering, or to access values not shown in the GUI summary.
        design_check_details = rfem_app.get_results(
            results_type=rfem.results.ResultsType.STEEL_DESIGN_DESIGN_CHECK_DETAILS,
            filters=[
                rfem.results.ResultsFilter(
                    column_id='design_check_details_id', filter_expression="13"
                )
            ]
        ).data
        print(f"\n\nSteel Design | Details:")
        print(design_check_details)

    else:
        # 2. get_result_table: Returns a specific result table as it appears in the desktop GUI in default state.
        #    Only the most important values are included, mirroring what end users see for quick review or export.
        errors_warning_df = rfem_app.get_result_table(
            table = rfem.results.ResultTable.ERRORS_AND_WARNINGS_TABLE,
            loading = None
        ).data
        print(f"\n\nErrors and Warnings | Table:")
        print(errors_warning_df)



