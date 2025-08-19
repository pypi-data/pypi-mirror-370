from dlubal.api import rstab

with rstab.Application() as rstab_app:

    # --- Retriev results from the active model (already calculated) ---

    # 1. get_results: Returns all results of the specified type directly from the database.
    #    This is the full dataset, including all possible columns and data. Use this for custom analytics,
    #    advanced filtering, or to access values not shown in the GUI summary.
    df_internal_forces = rstab_app.get_results(
        results_type=rstab.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES
    ).data
    print(f"\nInternal Forces | All:")
    print(df_internal_forces)



    # 2. get_result_table: Returns a specific result table as it appears in the desktop GUI in default state.
    #    Only the most important values are included, mirroring what end users see for quick review or export.
    df_internal_forces_table = rstab_app.get_result_table(
        table = rstab.results.ResultTable.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES_TABLE,
        loading= rstab.ObjectId(
            no=1,
            object_type=rstab.OBJECT_TYPE_LOAD_COMBINATION
        )
    ).data
    print(f"\nInternal Forces | Table:")
    print(df_internal_forces_table)


    # Both methods return a Table, which is a convenience wrapper around a pandas DataFrame.
    # The DataFrame can be accessed directly via the .data attribute.


    # 3. has_results: Checks if results exist for the specified loading condition.
    #    Use this before calling result retrieval methods to avoid errors or unnecessary data requests.
    has_results = rstab_app.has_results(
        loading = rstab.ObjectId
        (
            object_type = rstab.OBJECT_TYPE_LOAD_COMBINATION,
            no = 1
        )
    )
    print(f"Has results: {has_results.value}")