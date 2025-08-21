import json


def sse_stream_to_dict_list(content: bytes):
    """Convert a Server-Sent Event stream to a list of event dicts."""
    output_list = []
    for chunk in content.decode('utf-8').split('\r\n\r\n'):
        if not chunk:
            continue
        lines = chunk.split('\n')
        event_dict = {}
        for line in lines:
            if not line:
                continue
            key, value = line.split(':', 1)
            # Try to parse the value as JSON, else strip and return as string
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = value.strip()
            event_dict[key.strip()] = value
        output_list.append(event_dict)
    return output_list
