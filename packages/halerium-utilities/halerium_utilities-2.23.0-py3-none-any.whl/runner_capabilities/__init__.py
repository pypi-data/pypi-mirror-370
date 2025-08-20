from .get_runner_capabilities import get_runner_capabilities

try:
    globals().update(get_runner_capabilities())
except:
    pass

del get_runner_capabilities
