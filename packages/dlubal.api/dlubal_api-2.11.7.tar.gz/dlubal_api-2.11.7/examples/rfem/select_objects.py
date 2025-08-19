from dlubal.api import rfem

with rfem.Application() as rfem_app:


    print(f"Get object list | All")
    selected_members = rfem_app.get_object_list(
        objs=[rfem.structure_core.Member()],
    )
    for member in selected_members:
        print(f"Member No.: {member.no}")


    print(f"Get object list | Only selected")
    selected_members = rfem_app.get_object_list(
        objs=[rfem.structure_core.Member()],
        only_selected=True,
    )
    for member in selected_members:
        print(f"Member No.: {member.no}")


    print(f"Get object list | Select different")
    rfem_app.select_objects(objs=[])
    rfem_app.select_objects(
        objs=[
            rfem.structure_core.Member(no=46),
            rfem.structure_core.Member(no=52),
        ]
    )
    selected_members = rfem_app.get_object_list(
        objs=[
            rfem.structure_core.Member(),
        ],
        only_selected=True,
    )
    for member in selected_members:
        print(f"Member No.: {member.no}")

