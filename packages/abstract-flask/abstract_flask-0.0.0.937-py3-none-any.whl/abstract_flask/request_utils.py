from abstract_utilities.json_utils import (json,
                                           get_only_kwargs,
                                           get_desired_key_values,
                                           makeParams,
                                           dump_if_json,
                                           make_list
                                           )
import inspect
from flask import jsonify
from abstract_utilities.log_utils import print_or_log

def get_proper_kwargs(strings, **kwargs):
    # Convert the provided strings to lowercase for case-insensitive matching
    strings_lower = [string.lower() for string in strings]
    matched_keys = {}  # This will store matched keys and their corresponding values
    
    remaining_kwargs = kwargs.copy()  # Copy the kwargs so we can remove matched keys

    # Exact matching: Find exact lowercase matches first and remove them
    for string in strings_lower:
        for key in list(remaining_kwargs):  # Iterate over a copy of the keys
            if key.lower() == string:
                matched_keys[key] = remaining_kwargs.pop(key)  # Remove matched key from remaining_kwargs
                break

    # Partial matching: Check for keys that contain the string and remove them
    for string in strings_lower:
        for key in list(remaining_kwargs):  # Iterate over a copy of the keys
            if string in key.lower():
                matched_keys[key] = remaining_kwargs.pop(key)  # Remove matched key from remaining_kwargs
                break

    # Return the first matched value or None if no match
    if matched_keys:
        return list(matched_keys.values())[0]
    
    # Log or raise an error if no key was found for debugging
    print(f"No matching key found for: {strings} in {kwargs.keys()}")
    return None
async def async_makeParams(*arg,**kwargs):
   return makeParams(*arg,**kwargs)

def parse_request(flask_request):
    """Parse incoming Flask request and return args and kwargs."""
    args = []
    kwargs = {}

    if flask_request.method == 'POST' and flask_request.is_json:
        # Parse from JSON body
        data = flask_request.get_json()
        args = data.get('args', [])
        kwargs = {key: value for key, value in data.items() if key != 'args'}
    else:
        # Parse from query parameters
        args = flask_request.args.getlist('args')
        kwargs = {key: value for key, value in flask_request.args.items() if key != 'args'}

    return args,kwargs
def parse_and_return_json(flask_request):
    args,kwargs = parse_request(flask_request)
    return {
        'args': args,
        'kwargs': kwargs
    }
def parse_and_spec_vars(flask_request,varList):
    if isinstance(varList,dict):
      varList = list(varList.keys())
    args,kwargs = parse_request(flask_request)
    kwargs = get_only_kwargs(varList,*args,**kwargs)
    return kwargs
   

def required_keys(keys,req,defaults=None):
    defaults = defaults or {}
    datas = get_request_data(req)
    for key in keys:
        value = datas.get(key) or defaults.get(key)
        if not value:
            return {"error": f"could not find {key} in values","status_code":400}
    return datas
def get_request_data(req):
    """Retrieve JSON data (for POST) or query parameters (for GET)."""
    if req.method == 'POST':
        return req.json
    else:
        return req.args.to_dict()
def get_request_data(req):
    """
    Returns a dict from:
     1) JSON body (regardless of Content-Type),
     2) form data,
     3) query string,
    in that order.
    """
    # 1) Try JSON body, ignore headers if not valid JSON
    json_data = req.get_json(force=True, silent=True)
    if isinstance(json_data, dict) and json_data:
        return json_data

    # 2) Try form POST data
    if req.form and req.form.to_dict():
        return req.form.to_dict(flat=True)

    # 3) Finally, try query string
    if req.args and req.args.to_dict():
        return req.args.to_dict(flat=True)

    # Nothing found
    return {}
def execute_request(keys,req,func=None,desired_keys=None,defaults=None):
   
    try:
        datas = required_keys(keys,req,defaults=defaults)
        if datas and isinstance(datas,dict) and datas.get('error'):
            return datas
        desired_key_values = get_desired_key_values(obj=datas,keys=desired_keys,defaults=defaults)
        result = func(**desired_key_values)
        return {"result": result,"status_code":200}
    except Exception as e:
        return {"error": f"{e}","status_code":500}

def get_json_call_response(value, status_code, data=None,logMsg=None):
    response_body = {}
    if status_code == 200:
        response_body["success"] = True
        response_body["result"] = value
        logMsg = logMsg or "success"
        initialize_call_log(value=value,
                            data=data,
                            logMsg=logMsg,
                            log_level='info')
    else:
        response_body["success"] = False
        response_body["error"] = value
        logMsg = logMsg or f"ERROR: {logMsg}"
        initialize_call_log(value=value,
                            data=data,
                            logMsg=logMsg,
                            log_level='error')
    return jsonify(response_body), status_code


def initialize_call_log(value=None,
                        data=None,
                        logMsg=None,
                        log_level=None):
    """
    Inspect the stack to find the first caller *outside* this module,
    then log its function name and file path.
    """
    # Grab the current stack
    stack = inspect.stack()
    caller_name = "<unknown>"
    caller_path = "<unknown>"
    log_level = log_level or 'info'
    try:
        # Starting at index=1 to skip initialize_call_log itself
        for frame_info in stack[1:]:
            modname = frame_info.frame.f_globals.get("__name__", "")
            # Skip over frames in your logging modules:
            if not modname.startswith("abstract_utilities.log_utils") \
               and not modname.startswith("abstract_flask.request_utils") \
               and not modname.startswith("logging"):
                caller_name = frame_info.function
                caller_path = frame_info.filename
                break
    finally:
        # Avoid reference cycles
        del stack

    logMsg = logMsg or "initializing"
    full_message = (
        f"{logMsg}\n"
        f"calling_function: {caller_name}\n"
        f"path: {caller_path}\n"
        f"data: {data}"
    )

    print_or_log(full_message,level=log_level)
