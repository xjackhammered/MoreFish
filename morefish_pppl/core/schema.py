def generate_response_schema(success, status_code, message, serializer_instance=None):
    response_schema = {
        "type": "object",
        "properties": {
            "success": {"type": "string"},
            "status_code": {"type": "integer"},
            "message": {"type": "string"},
        },
        "example": {
            "success": success,
            "status_code": status_code,
            "message": message,
        }
    }
    if serializer_instance:
        serialized_data = serializer_instance.data
        response_schema["example"]["data"] = serialized_data
    return response_schema
