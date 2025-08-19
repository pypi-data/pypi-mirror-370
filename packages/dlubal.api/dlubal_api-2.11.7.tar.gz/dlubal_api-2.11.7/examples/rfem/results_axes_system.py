from dlubal.api import rfem

with rfem.Application() as rfem_app:

    # --- Retriev Nodes Support Forces from the active model (already calculated) ---

    # a) Local Coordination System = Default
    df_reactions_local = rfem_app.get_results(
        results_type=rfem.results.ResultsType.STATIC_ANALYSIS_NODES_SUPPORT_FORCES,
    ).data
    print(f"\nNodes Support Forces | Local (default):")
    print(df_reactions_local)

    # b) Global Coordination System
    df_reactions_global = rfem_app.get_results(
        results_type=rfem.results.ResultsType.STATIC_ANALYSIS_NODES_SUPPORT_FORCES,
        nodal_support_coordinate_system=rfem.results.settings.CoordinateSystem.COORDINATE_SYSTEM_GLOBAL
    ).data
    print(f"\nNodes Support Forces | Global:")
    print(df_reactions_global)


    # --- Retriev Member Internal Forces from the active model (already calculated) ---

    # a) Member Local Axes (y, z) = Default
    df_forces_local = rfem_app.get_results(
        results_type=rfem.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        filters=[
            rfem.results.ResultsFilter(
                column_id='loading',
                filter_expression='DS1'
            )
        ]

    ).data
    print(f"\nMember Internal Forces | Local Axes (y, z) = Default:")
    print(df_forces_local)

    # Principal Axes (u, v)
    df_forces_principal = rfem_app.get_results(
        results_type=rfem.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        member_axes_system=rfem.results.settings.MEMBER_AXES_SYSTEM_PRINCIPAL_AXES_X_U_V,
        filters=[
            rfem.results.ResultsFilter(
                column_id='loading',
                filter_expression='DS1'
            )
        ]
    ).data
    print(f"\nMember Internal Forces | Principal Axes (u, v):")
    print(df_forces_principal)


    # c) Member Local Axes Rotated (y, z) => (x, y)
    base_data = rfem_app.get_base_data()
    base_data.general_settings.local_axes_orientation = rfem.BaseData.GeneralSettings.LOCAL_AXES_ORIENTATION_YUPZ
    rfem_app.set_base_data(base_data=base_data)

    rfem_app.calculate_all(skip_warnings=True)

    df_forces_rotated = rfem_app.get_results(
        results_type=rfem.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        member_axes_system=rfem.results.settings.MEMBER_AXES_SYSTEM_MEMBER_AXES_X_Y_Z
    ).data
    print(f"\nMember Internal Forces | Local Axes Rotated (y, z) => (x, y)")
    print(df_forces_rotated)
