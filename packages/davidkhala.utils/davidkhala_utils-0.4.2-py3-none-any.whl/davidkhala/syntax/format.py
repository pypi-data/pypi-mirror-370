import json

def JSONReadable(data):
    return json.dumps(data, indent=4, sort_keys=True)
