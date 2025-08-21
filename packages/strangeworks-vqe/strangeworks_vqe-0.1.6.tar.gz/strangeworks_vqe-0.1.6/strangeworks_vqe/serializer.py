import base64
import pickle


def pickle_serializer(obj, return_type="dict"):
    o_type = type(obj)
    # o_pickle = pickle.dumps(obj)
    o_pickle: bytes = pickle.dumps(obj)
    if return_type == "json":
        return {
            "type": str(o_type),
            "pickle": str(base64.urlsafe_b64encode(o_pickle), encoding="utf-8"),
        }
    return {"type": o_type, "pickle": base64.urlsafe_b64encode(o_pickle)}


def pickle_deserializer(p, input_type="dict"):

    if input_type == "json":
        o_pickle = base64.urlsafe_b64decode(bytes(p["pickle"], encoding="utf-8"))
    else:
        o_pickle = base64.urlsafe_b64decode(bytes(p["pickle"]))

    return pickle.loads(o_pickle)
