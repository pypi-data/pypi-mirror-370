import httpx
import inspect
import types


def function_creator(function_spec):
    endpoint = function_spec["endpoint"]["url"]
    name = function_spec["function"]["name"]
    description = function_spec["function"]["description"]
    parameters = function_spec["function"]["parameters"]["properties"]

    default_params = ["__halerium_card", "__halerium_user"]

    def function(**kwargs):
        # fetch automatic arguments
        default_args = {}
        frame = inspect.currentframe().f_back
        for p in default_params:
            if p in frame.f_locals:
                default_args[p] = frame.f_locals[p]
            elif p in frame.f_globals:
                default_args[p] = frame.f_globals[p]
            else:
                pass

        response = httpx.post(f"http://0.0.0.0:8800{endpoint}",
                              json={**default_args, **kwargs})
        return response.json()

    # Create a new function with the desired name
    named_function = types.FunctionType(function.__code__, function.__globals__, name, function.__defaults__,
                                        function.__closure__)
    named_function.__annotations__ = function.__annotations__
    named_function.__doc__ = description + "\n\nParameters:\n" + "\n".join(
        [f"{param}: {details['description']}" for param, details in parameters.items()]
    )
    named_function.__module__ = function.__module__
    named_function.__name__ = name  # Set the function name directly
    named_function.__qualname__ = name  # Set the function name directly

    return {name: named_function}


def get_runner_capabilities(skip_code_interpreter=True):
    response = httpx.get("http://0.0.0.0:8800/functions")
    function_specs = response.json()

    functions = {}
    for function_name, function_spec in function_specs.items():
        if skip_code_interpreter and function_name == "code_interpreter":
            continue
        functions.update(function_creator(function_spec=function_spec))

    return functions

