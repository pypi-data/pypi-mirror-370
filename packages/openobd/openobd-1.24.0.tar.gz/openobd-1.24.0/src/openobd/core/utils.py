import os

def _get_value_from_kwargs_or_env(kwargs, kwarg_key, env_key):
    if kwarg_key in kwargs:
        return kwargs[kwarg_key]
        return kwargs[kwarg_key]
    elif env_key in os.environ:
        return os.environ[env_key]
    else:
        raise AssertionError(f"Argument \"{kwarg_key}\" could not be found. Pass it explicitly, or ensure it is available as an environment variable named \"{env_key}\".")
