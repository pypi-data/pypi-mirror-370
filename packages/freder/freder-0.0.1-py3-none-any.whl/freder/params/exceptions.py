from typing import (
  Any, List, Tuple
)
from .vars import (
  INCLUDE_RELEASE_DATES_WITH_NO_DATA_LIST,
  ORDER_BY_LIST,
  SEARCH_TYPE_LIST,
  SORT_ORDER_LIST,
  INCLUDE_OBSERVATION_VALUES_LIST,
  FILTER_VARIABLE_LIST,
)


class MissingApikey(Exception):

  def __init__(self, *args: object) -> None:
    message =   '''
    API key is missing,
    Please use "set_apikey" or
    create ".env" file with "FRED_APIKEY" variable
    '''
    super().__init__(message)


class InvalidApikeyFormat(Exception):

  def __init__(
    self,
  ) -> None:
    message = f'''
    api_key consists of 32 alpha-numeric characters
    Please visit https://fred.stlouisfed.org/docs/api/api_key.html for more info
    '''
    super().__init__(message)


class NotDateTime(Exception):

  def __init__(
    self,
    input: Any
  ):
    message = f'''
    The parameter input is not a valid datetime or formatted string:{input}
    '''
    super().__init__(message)


class ParameterTypeError(Exception):

  def __init__(
    self,
    types: List | Tuple,
    param_name: str = 'This parameter'
  ) -> None:
    types_str = ', '.join([str(t) for t in types])
    if param_name != 'This parameter':
      param_name = f'"{param_name}"'
    message = f'''
    {param_name} only accepts {types_str}
    '''
    super().__init__(message)


class NotNumeric(Exception):

  def __init__(self) -> None:
    message =   '''
    The parameter is not numeric
    '''
    super().__init__(message)


class LimitExceeded(Exception):

  def __init__(self) -> None:
    message =   '''
    limit must be between 1 and 1000
    '''
    super().__init__(message)


class NotPositiveInteger(Exception):

  def __init__(self) -> None:
    message = '''
    This number must be a positive integer
    '''
    super().__init__(message)

class InvalidOrderByInput(Exception):

  def __init__(self) -> None:
    message = f'''
    "order_by" input must be one of the following values:
    {ORDER_BY_LIST}
    '''
    super().__init__(message)

class InvalidSortOrderInput(Exception):

  def __init__(self) -> None:
    message = f'''
    "sort_order" input must be one of the following values:
    {SORT_ORDER_LIST}
    '''
    super().__init__(message)


class InvalidFilterVariableInput(Exception):

  def __init__(self) -> None:
    message = f'''
    "filter_variable" input must be one of the following values:
    {FILTER_VARIABLE_LIST}
    '''
    super().__init__(message)


class InvalidTagNamesInput(Exception):

  def __init__(self) -> None:
    message = '''
    "tag_names" must include ";" as a string
    '''
    super().__init__(message)


class InvalidTagGroupId(Exception):
  
  def __init__(self) -> None:
    message = f'''
    "tag_group_id" must be one of the following values:
    freq = Frequency
    gen = General or Concept
    geo = Geography
    geot = Geography Type
    rls = Release
    seas = Seasonal Adjustment
    src = Source 
    '''
    super().__init__(message)


class InvalidIncludeReleaseDatesWithNoData(Exception):

  def __init__(self) -> None:
    message = f'''
    "include_release_dates_with_no_data" must be one of the following values:
    {INCLUDE_RELEASE_DATES_WITH_NO_DATA_LIST}
    '''
    super().__init__(message)


class InvalidIncludeObservationValues(Exception):

  def __init__(self) -> None:
    message = f'''
    "include_observation_values" must be one of the following values:
    {INCLUDE_OBSERVATION_VALUES_LIST}
    '''
    super().__init__(message)


class InvalidUnits(Exception):

  def __init__(self) -> None:
    message = f'''
    "units" must be one of the following values:
    lin = Levels (No transformation)
    chg = Change
    ch1 = Change from Year Ago
    pch = Percent Change
    pc1 = Percent Change from Year Ago
    pca = Compounded Annual Rate of Change
    cch = Continuously Compounded Rate of Change
    cca = Continuously Compounded Annual Rate of Change
    log = Natural Log
    '''
    super().__init__(message)


class InvalidFrequency(Exception):

  def __init__(self) -> None:
    message = f'''
    "frequency" must be one of the following values:
    d = Daily
    w = Weekly
    bw = Biweekly
    m = Monthly
    q = Quarterly
    sa = Semiannual
    a = Annual

    Frequencies with period descriptions:

    wef = Weekly, Ending Friday
    weth = Weekly, Ending Thursday
    wew = Weekly, Ending Wednesday
    wetu = Weekly, Ending Tuesday
    wem = Weekly, Ending Monday
    wesu = Weekly, Ending Sunday
    wesa = Weekly, Ending Saturday
    bwew = Biweekly, Ending Wednesday
    bwem = Biweekly, Ending Monday 
    '''
    super().__init__(message)


class InvalidAggregationMethod(Exception):

  def __init__(self) -> None:
    message = f'''
    "aggregation_method" must be one of the following values:
    avg = Average
    sum = Sum
    eop = End of Period
    '''
    super().__init__(message)


class InvalidOutputType(Exception):

  def __init__(self) -> None:
    message = f'''
    "output_type" must be one of the following values:
    1 = Observations by Real-Time Period
    2 = Observations by Vintage Date, All Observations
    3 = Observations by Vintage Date, New and Revised Observations Only
    4 = Observations, Initial Release Only
    '''
    super().__init__(message)


class InvalidSearchType(Exception):

  def __init__(self) -> None:
    message = f'''
    "search_type" must be one of the following values:
    {SEARCH_TYPE_LIST}
    '''
    super().__init__(message)