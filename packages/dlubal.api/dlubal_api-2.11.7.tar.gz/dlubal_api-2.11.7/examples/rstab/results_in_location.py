
from dlubal.api import rstab
import numpy

def get_member_internal_force(member_no: int, loading: str = 'LC1', force: str = 'm_y', location: float = 0) -> float:
    df_results = rstab_app.get_results(
        results_type=rstab.results.STATIC_ANALYSIS_MEMBERS_INTERNAL_FORCES,
        filters=[
            rstab.results.ResultsFilter(
                column_id="member_no",
                filter_expression=str(member_no)
            ),
            rstab.results.ResultsFilter(
                column_id="loading",
                filter_expression=str(loading)
            ),
        ]
    ).data

    # Get locations and forces as arrays
    locations = df_results['location_x'].to_numpy(dtype=float)
    forces = df_results[force].to_numpy(dtype=float)

    # Check range
    if not (locations[0] <= location <= locations[-1]):
        print('Location is out of range')
        return 0

    # Linear interpolation
    return float(numpy.interp(location, locations, forces))



with rstab.Application() as rstab_app:

    # --- Retriev results from the active model (already calculated) ---

    v_z = get_member_internal_force(member_no=46, loading = 'CO2', force = 'v_z', location = 0.4)
    print(v_z)
