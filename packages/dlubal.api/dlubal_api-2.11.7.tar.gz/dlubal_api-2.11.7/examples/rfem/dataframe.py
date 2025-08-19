from dlubal.api import rfem

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    rfem_app.close_all_models(save_changes=False)
    rfem_app.create_model(name='dataframe')

    # GetResults returns Table, which is just a convenience wrapper around a Pandas Dataframe.
    # The Dataframe can be directly accessed as .data

    print("Filtered results:")
    results = rfem_app.get_results(
        rfem.results.TEST,
        filters=[rfem.results.ResultsFilter(
            column_id="support_force_p_x",
            filter_expression="max")],
    )

    print(results.data)
