from dlubal.api import rstab

with rstab.Application() as rstab_app:

    # --- Retriev Nodes Support Forces from the active model (already calculated) ---

    # a) Local Coordintation System = Default
    df_reactions_global = rstab_app.get_results(
        results_type=rstab.results.ResultsType.STATIC_ANALYSIS_NODES_SUPPORT_FORCES,
    ).data
    print(f"\nNodes Support Forces | Local (default):")
    print(df_reactions_global)

    # b) Global Coordination System
    df_reactions_local = rstab_app.get_results(
        results_type=rstab.results.ResultsType.STATIC_ANALYSIS_NODES_SUPPORT_FORCES,
        nodal_support_coordinate_system=rstab.results.settings.CoordinateSystem.COORDINATE_SYSTEM_GLOBAL
    ).data
    print(f"\nNodes Support Forces | Global:")
    print(df_reactions_local)


    # --- Retriev Member Internal Forces from the active model (already calculated) ---

    # a) Member Local Axes (y, z) = Default
    df_forces_local = rstab_app.get_results(
        results_type=rstab.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
    ).data
    print(f"\nMember Internal Forces | Local Axes (y, z) = Default:")
    print(df_forces_local)

    # Principal Axes (u, v)
    df_forces_principal = rstab_app.get_results(
        results_type=rstab.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        member_axes_system=rstab.results.settings.MEMBER_AXES_SYSTEM_PRINCIPAL_AXES_X_U_V
    ).data
    print(f"\nMember Internal Forces | Principal Axes (u, v):")
    print(df_forces_principal)


    # c) Member Local Axes Rotated (y, z) => (x, y)
    base_data = rstab_app.get_base_data()
    base_data.general_settings.local_axes_orientation = rstab.BaseData.GeneralSettings.LOCAL_AXES_ORIENTATION_YUPZ
    rstab_app.set_base_data(base_data=base_data)

    rstab_app.calculate_all(skip_warnings=True)

    df_forces_rotated = rstab_app.get_results(
        results_type=rstab.results.ResultsType.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        member_axes_system=rstab.results.settings.MEMBER_AXES_SYSTEM_MEMBER_AXES_X_Y_Z
    ).data
    print(f"\nMember Internal Forces | Local Axes Rotated (y, z) => (x, y)")
    print(df_forces_rotated)
