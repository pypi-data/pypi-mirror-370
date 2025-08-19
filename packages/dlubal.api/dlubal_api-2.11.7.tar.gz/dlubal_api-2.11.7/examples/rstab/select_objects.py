from dlubal.api import rstab

with rstab.Application() as rstab_app:


    print(f"Get object list | All")
    selected_members = rstab_app.get_object_list(
        objs=[rstab.structure_core.Member()],
    )
    for member in selected_members:
        print(f"Member No.: {member.no}")


    print(f"Get object list | Only selected")
    selected_members = rstab_app.get_object_list(
        objs=[rstab.structure_core.Member()],
        only_selected=True,
    )
    for member in selected_members:
        print(f"Member No.: {member.no}")


    print(f"Get object list | Select different")
    rstab_app.select_objects(objs=[])
    rstab_app.select_objects(
        objs=[
            rstab.structure_core.Member(no=46),
            rstab.structure_core.Member(no=52),
        ]
    )
    selected_members = rstab_app.get_object_list(
        objs=[
            rstab.structure_core.Member(),
        ],
        only_selected=True,
    )
    for member in selected_members:
        print(f"Member No.: {member.no}")

