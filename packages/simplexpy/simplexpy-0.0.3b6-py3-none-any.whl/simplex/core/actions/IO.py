def save_json(project_proto, filename: str):
    """
    Save the project proto to a JSON file.
    """
    from google.protobuf.json_format import MessageToJson
    with open(filename, 'w') as f:
        json_data = message_to_json(project_proto)
        f.write(json_data)
    
def message_to_json(project_proto):
    """
    Convert a protobuf message to JSON format.
    """
    from google.protobuf.json_format import MessageToJson
    return MessageToJson(project_proto, indent=2, use_integers_for_enums=False, including_default_value_fields=True, float_precision=3)