from dlubal.api import rfem, common

with rfem.Application() as rfem_app:


    model_list = rfem_app.get_model_list()
    print(f"\nModel List:\n{model_list}")

    for model_id in model_list.model_info:

        if rfem_app.has_results(
            model_id=common.ModelId(
                guid=model_id.guid
            )).value :

            # --- Retriev results from the specified model (already calculated) ---

            # 1. get_results: Returns all results of the specified type from the specified model's database.
            #    This retrieves the complete result dataset, including all possible columns. It is suitable for
            #    detailed analytics, filtering, or accessing values not shown in the RFEM GUI.
            #    The `model_id` parameter ensures results are pulled from the correct model context.

            df_internal_forces = rfem_app.get_results(
                results_type=rfem.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
                model_id=common.ModelId(guid=model_id.guid)
            ).data
            print(f"\nInternal Forces | All | {model_id.name}:")
            print(df_internal_forces)



            # 2. get_result_table: Returns a simplified result table as shown in the RFEM GUI by default.
            #    This includes only the key summary values, providing a quick overview for end users or exports.
            #    The `model_id` parameter ensures the table is retrieved for the correct model instance.

            df_internal_forces_table = rfem_app.get_result_table(
                table = rfem.results.ResultTable.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES_TABLE,
                loading= rfem.ObjectId(
                    no=1,
                    object_type=rfem.OBJECT_TYPE_LOAD_CASE,
                ),
                model_id = common.ModelId(guid=model_id.guid)
            ).data
            print(f"\nInternal Forces | Table | {model_id.name}:")
            print(df_internal_forces_table)
