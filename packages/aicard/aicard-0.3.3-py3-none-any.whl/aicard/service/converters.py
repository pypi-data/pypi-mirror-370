def dynamic2dict(data, mixed: set=None):
    if mixed:
        if not isinstance(data, dict): return dynamic2dict(data)
        if "data" not in data: return dynamic2dict(data)
        for mix in mixed: assert mix in data, f"No {mix} key dictionary key found"
        data_segment = dynamic2dict(data["data"])
        assert isinstance(data_segment, dict), "Data segment could not be parsed into a dictionary"
        return {mix: data[mix] for mix in mixed}|data_segment
    if isinstance(data, list) and all(isinstance(item, dict) and len(item)==2 and "name" in item and "value" in item for item in data):
        return {item["name"]: dynamic2dict(item["value"]) for item in data}
    return data

def dict2dynamic(data, mixed: set=None):
    if mixed:
        assert isinstance(data, dict)
        for mix in mixed: assert mix in data
        return {mix: data[mix] for mix in mixed}|{"data": dict2dynamic({k: v for k, v in data.items() if k not in mixed})}
    if isinstance(data, dict): return [{"name": k, "value": dict2dynamic(v)} for k, v in data.items()]
    return data
