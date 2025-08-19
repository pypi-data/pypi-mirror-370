import dlubal.api.rstab as rstab
from dlubal.api.common import Vector3d

with rstab.Application() as client:
    client.close_all_models(save_changes=False)
    client.create_model(name="nested_tables")
    client.delete_all_objects()


    load_cases = [
        rstab.loading.LoadCase(no=1, name="Self weight"),
        rstab.loading.LoadCase(no=2, name="Live Load"),
    ]

    client.create_object_list(load_cases)

    # Prepare load combination items table.
    items = rstab.loading.LoadCombination.ItemsTable(
        rows=[
            rstab.loading.LoadCombination.ItemsRow(load_case=1, factor=1.35),
            rstab.loading.LoadCombination.ItemsRow(load_case=2, factor=1.5),
        ]
    )
    co = rstab.loading.LoadCombination(no=1, items=items)
    client.create_object(co)

    # Get the created load combination and print it - we get the table data as well.
    co = client.get_object(rstab.loading.LoadCombination(no=1))
    print(co)
