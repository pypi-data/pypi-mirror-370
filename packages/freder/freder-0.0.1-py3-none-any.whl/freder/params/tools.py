import datetime as dt


from .exceptions import (
  ParameterTypeError,
)
from typing import (
  Tuple, Any,
)
from .vars import (
  DATE_FORMAT,
  DATE_REGEX,
)
from . import vars


def set_apikey(val: str):
  vars.APIKEY = val


def show_apikey():
  print(vars.APIKEY)

def typecheck(
  parameter: Any,
  types: Tuple[type, ...],
  param_name: str,
) -> bool:
  if not parameter:
    return True
  if isinstance(parameter, types):
    return True
  raise ParameterTypeError(
    types=types,
    param_name=param_name
  )


def convert_parameter(parameter: Any) -> Any:
  if isinstance(parameter, dt.datetime):
    return parameter.strftime(DATE_FORMAT)
  elif isinstance(parameter, (list, tuple)):
    return ';'.join(parameter)
  elif isinstance(parameter, int):
    return str(parameter)
  return parameter


def is_datetime(input: Any):
  if not isinstance(input, str):
    return False
  
  if isinstance(input, dt.datetime):
    return True

  if isinstance(input, str):
    return DATE_REGEX.match(input) is not None