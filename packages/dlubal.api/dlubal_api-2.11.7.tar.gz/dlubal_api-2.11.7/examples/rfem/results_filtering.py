from dlubal.api import rfem
import os

with rfem.Application() as rfem_app:

    # --- Retriev results from the active model (already calculated) ---

    # Filters are used to limit the results to:
    # - members with numbers 1 and 2
    # - load cases or combinations named 'LC1' and 'CO2'
    df_internal_forces = rfem_app.get_results(
        results_type=rfem.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        filters=[
            rfem.results.ResultsFilter(column_id='member_no', filter_expression='1,2'),
            rfem.results.ResultsFilter(column_id='loading', filter_expression='LC1'),
        ]
    ).data
    print(f"\nInternal Forces | All:")
    print(df_internal_forces)


   # --- Export the results to a CSV file ---

    # Save the dataframe to a CSV file in the current working directory.
    file_path = os.path.abspath('./internal_forces.csv')
    df_internal_forces.to_csv(path_or_buf=file_path)
    print(f"\nResults have been exported to: {file_path}")

