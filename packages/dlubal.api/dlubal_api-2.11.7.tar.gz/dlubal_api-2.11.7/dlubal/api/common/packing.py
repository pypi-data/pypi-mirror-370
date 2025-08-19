from dlubal.api.common.common_messages_pb2 import Object, ObjectList
from dlubal.api.common.table import Table
from dlubal.api.common.table_data_pb2 import TableData
from dlubal.api.common.common_pb2 import Value
from google.protobuf.any_pb2 import Any
from google.protobuf import descriptor_pool
from google.protobuf.message_factory import GetMessageClass
import pandas as pd
from pandas import DataFrame

def pack_message_to_any(msg) -> Any:
    packed = Any()
    packed.Pack(msg)
    return packed

def pack_object(object, model_id=None) -> Object:
    packed = Any()
    packed.Pack(object)

    if model_id is None:
        return Object(object=packed)

    return Object(object=packed, model_id=model_id)


pool = None

def unpack_object(packed_object: Object, Type = None):
    if Type is None:
        # Find the object type dynamically
        type_url = packed_object.object.type_url
        message_type_name = type_url.split('/')[-1]

        # Initialize descriptor pool
        global pool
        if pool is None:
            pool = descriptor_pool.Default()

        try:
            # Look up the descriptor for the message
            descriptor = pool.FindMessageTypeByName(message_type_name)
            if not descriptor:
                raise ValueError(f"Message type '{message_type_name}' not found")

            # Dynamically create a class for the message type based on the descriptor
            message_class = GetMessageClass(descriptor)

            # Unpack the Any into the correct message type
            message_instance = message_class()
            packed_object.object.Unpack(message_instance)
            return message_instance

        except Exception as e:
            print(f"Error unpacking Any message: {str(e)}. Probably because of incompatible version of the client.")
            return None
    else:
        result = Type()
        packed_object.object.Unpack(result)
        return result


def pack_object_list(object_list, model_id=None):
    packed_list = ObjectList(model_id=model_id)
    for obj in object_list:
        if isinstance(obj, tuple) and len(obj) == 2:
            obj_to_pack, obj_model_id = obj
            packed_list.objects.append(pack_object(obj_to_pack, obj_model_id))
        elif isinstance(obj, Object):
            if obj.model_id is not None:
                packed_list.objects.append(pack_object(obj.object, obj.model_id))
            else:
                packed_list.objects.append(pack_object(obj.object, model_id))
        else:
            packed_list.objects.append(pack_object(obj, model_id))
    return packed_list


def unpack_object_list(packed_object_list: ObjectList, objs: list):
    type_list = []
    for o in objs:
        if isinstance(o, tuple) and len(o) == 2:
            type_list.append(type(o[0]))
        else:
            type_list.append(type(o))
    unpacked_list = []
    dynamic_type = len(type_list) != len(packed_object_list.objects)
    for i, object in enumerate(packed_object_list.objects):
        typ = None if dynamic_type else type_list[i]
        unpacked_list.append(unpack_object(object, typ))
    return unpacked_list


def get_internal_value(value: Value):
    '''
    Get the internal value stored in a generic Value object
    '''
    kind = value.WhichOneof("kind")
    if not kind or kind == "null_value":
        return None
    else:
        return getattr(value, kind)


def set_internal_value(wrapped_value: Value, value: int | float | str | bool | None):
    match value:
        case int():
            wrapped_value.int_value = value
        case float():
            wrapped_value.double_value = value
        case str():
            wrapped_value.string_value = value
        case bool():
            wrapped_value.bool_value = value


def convert_table_data_to_table(table_data: TableData) -> Table:
    '''
    Converts TableData from API response to a Pandas-based Table.

    Args:
        table_data (TableData): Raw API response in TableData format.

    Returns:
        Table: Converted table with appropriate data types.
    '''
    rows_data = [
        [pd.NA if (value := get_internal_value(v)) is None else value for v in row.values]
        for row in table_data.rows
    ]

    df = DataFrame(columns=list(table_data.column_ids), data=rows_data)

    # Convert DataFrame columns to their best possible numeric nullable dtypes.
    df_conv = df.convert_dtypes()

    # Ensure float columns remain float, even if they contain only whole numbers
    float_cols = df.select_dtypes(include=["float"]).columns
    df_conv[float_cols] = df_conv[float_cols].astype('Float64')

    # Convert non-numeric object type columns to Pandas' nullable string type.
    object_cols = df_conv.select_dtypes(include=["object"]).columns
    df_conv[object_cols] = df_conv[object_cols].astype('string')

    return Table(df_conv)
