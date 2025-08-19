from dlubal.api import rfem, common
import google.protobuf.json_format

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Get Block data (block must already exist):
    block = rfem_app.get_object(rfem.structure_advanced.Block(no=1))

    print("Block parameters table:")
    print(google.protobuf.json_format.MessageToJson(block.parameters))
    print("")

    # Use helper functions to access specific parts of the parameter tree:
    print("Block parameter item 'Length':")
    length = common.get_tree_item(block.parameters, ['geometry', 'l'])
    print(length)
    print("")

    print("Block length value: ", common.get_tree_value(block.parameters, ['geometry', 'l']))
    print("")

    # Edit Block parameters:
    print("Parameters to set:")
    parameters = rfem.structure_advanced.Block.ParametersTable()
    common.set_tree_value(parameters, ['geometry', 'l'], 4.5)
    print(google.protobuf.json_format.MessageToJson(parameters))

    rfem_app.update_object(rfem.structure_advanced.Block(no=1, parameters=parameters))
