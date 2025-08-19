from dlubal.api import rstab

# Connect to the RSTAB application
with rstab.Application() as rstab_app:

    rstab_app.close_all_models(save_changes=False)
    rstab_app.create_model(name='dataframe')

    # GetResults returns Table, which is just a convenience wrapper around a Pandas Dataframe.
    # The Dataframe can be directly accessed as .data

    print("Filtered results:")
    results = rstab_app.get_results(
        rstab.results.TEST,
        filters=[rstab.results.ResultsFilter(
            column_id="support_force_p_x",
            filter_expression="max")],
    )

    print(results.data)
