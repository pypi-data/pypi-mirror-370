import os
from dlubal.api import rstab
from dlubal.api import common

# Connect to the RSTAB application
with rstab.Application() as rstab_app:

    rstab_app.create_model(name='ifc_structure')

    # Import IFC model
    example = os.path.join(os.path.dirname(__file__), 'src', 'ifc_structure.ifc')

    rstab_app.import_model_from(
        filepath=example,
        import_attributes=common.import_export.IfcImportAttributes()
    )

    # Get all imported IFC models
    ifc_models = rstab_app.get_object_list([rstab.ifc_objects.IfcFileModelObject()])

    # Edit IFC model
    ifc_model = ifc_models[0]
    edited_ifc_model = rstab.ifc_objects.IfcFileModelObject(
        no=ifc_model.no,
        mirror_axis_z=True)
    rstab_app.update_object(edited_ifc_model)


    # Get all IFC objects
    ifc_model_objects = rstab_app.get_object_list([rstab.ifc_objects.IfcModelObject()])

    members = list()
    surfaces = list()
    solids = list()

    # Find IFC objects that will be converted to straight members and solids
    for ifc_object in ifc_model_objects:
        ifc_type = ifc_object.ifc_type
        if ifc_type in ["IfcColumn", "IfcBeam"]:
            members.append(ifc_object)

    rstab_app.convert_objects(
        convert_into=common.ConvertObjectInto.CONVERT_IFC_OBJECT_INTO_STRAIGHT_MEMBER,
        objects=members
    )
