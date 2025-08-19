from datetime import datetime

from fsai_shared_funcs.proto_helpers.json_format import MessageToDict, ParseDict


def dict_to_proto(input_dict, proto_class, ignore_unknown_fields=True):   
    # Perform conversion of values to match ParseDict's requirements
    for key, value in input_dict.items():
        # Convert to .isoformat("T") + "Z" to match the format of the protobuf timestamp
        if isinstance(value, datetime):
            input_dict[key] = value.isoformat("T") + "Z"

    return ParseDict(input_dict, proto_class(), ignore_unknown_fields=ignore_unknown_fields)


def dict_to_proto_list(input_list, proto_class, ignore_unknown_fields=True):
    """
    Convert a list of dictionaries to a list of protobuf messages.
    
    Args:
        input_list (list[dict]): List of dictionaries to be converted.
        proto_class (protobuf message class): The protobuf message class to convert to.
        ignore_unknown_fields (bool, optional): Whether to ignore unknown fields when parsing. Default is True.
    
    Returns:
        list[protobuf message]: List of protobuf messages.
    """
    return [dict_to_proto(item, proto_class, ignore_unknown_fields=ignore_unknown_fields) for item in input_list]

    
def proto_to_dict(input_proto, including_default_value_fields=True, preserving_proto_field_name=True, float_precision=14):
    """
    Convert a protobuf message to a dictionary.
    
    Args:
        input_proto (protobuf message): The protobuf message to be converted.
        including_default_value_fields (bool, optional): Whether to include fields that have default values. Default is True.
        preserving_proto_field_name (bool, optional): Whether to preserve the original proto field names. Default is True.
        float_precision (int, optional): The number of decimal places to preserve for floats. Default is 14.
    
    Returns:
        dict: The protobuf message as a dictionary.
    """
    output_dict = MessageToDict(
        input_proto,
        including_default_value_fields=including_default_value_fields,
        preserving_proto_field_name=preserving_proto_field_name,
        float_precision=float_precision,
    )

    # Perform conversion of values to match ParseDict's requirements
    for key, value in output_dict.items():
        # Convert to datetime object
        if isinstance(value, str) and len(value) == 27 and value[-1] == "Z":
            try:
                output_dict[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
            except Exception as e:
                pass

    return output_dict
