import datetime as dt
from dateutil.relativedelta import relativedelta

from .exceptions import (
  InvalidAggregationMethod,
  InvalidApikeyFormat,
  InvalidFrequency,
  InvalidIncludeReleaseDatesWithNoData,
  InvalidOutputType,
  LimitExceeded,
  NotNumeric,
  NotPositiveInteger,
  InvalidOrderByInput,
  InvalidSortOrderInput,
  InvalidFilterVariableInput,
  InvalidTagGroupId,
  InvalidIncludeObservationValues,
  InvalidUnits,
  NotDateTime,
)
from typing import (
  Any, Tuple, List
)
from .tools import (
  is_datetime,
  typecheck,
  convert_parameter,
)
from .vars import (
  AGGREGATION_METHOD_LIST,
  DATE_FORMAT,
  ORDER_BY_LIST,
  OUTPUT_TYPE_LIST,
  SORT_ORDER_LIST,
  FILTER_VARIABLE_LIST,
  TAG_GROUP_ID_LIST,
  INCLUDE_RELEASE_DATES_WITH_NO_DATA_LIST,
  INCLUDE_OBSERVATION_VALUES_LIST,
  TIME_FORMAT,
  UNITS_LIST,
  FREQUENCY_LIST,
)


class FredParameter:
  """
  Base class for all FRED parameters
  """
  def __init__(
    self,
    alias: str,
    parameter: Any,
    types: Tuple[type, ...],
  ) -> None:
    typecheck(
      parameter=parameter,
      types=types,
      param_name=alias
    )
    self._alias = alias
    self._parameter = convert_parameter(parameter=parameter)

  def __repr__(self) -> str:
    return self._alias

  def __str__(self) -> str:
    return self._parameter


class Apikey(FredParameter):
  """
  api_key
  Read API Keys for more information.
  => https://fred.stlouisfed.org/docs/api/api_key.html
      32 character alpha-numeric lowercase string, required
  """
  def __init__(
    self,
    api_key: str,
  ) -> None:

    super().__init__(
      alias='api_key',
      parameter=api_key,
      types=(str,))

    if not api_key.isalnum():
      raise InvalidApikeyFormat()
    
    if len(api_key) != 32:
      raise InvalidApikeyFormat()


class FileType(FredParameter):
  """
  file_type

  A key or file extension that indicates the type of file to send.

      string, optional, default: xml
      One of the following values: 'xml', 'json'

      xml = Extensible Markup Language. The HTTP Content-Type is text/xml.
      json = JavaScript Object Notation. The HTTP Content-Type is application/json.

  """
  def __init__(
    self,
    file_type: str = 'json'
  ) -> None:
    super().__init__(
      alias='file_type',
      parameter=file_type,
      types=(str,))


class CategoryId(FredParameter):
  """
  The id for a category.
      integer, default: 0 (root category)
  """
  def __init__(
    self,
    category_id: str | int = '0',
  ) -> None:
    if isinstance(category_id, str):
      if not category_id.isnumeric():
        raise NotNumeric()

    super().__init__(
      alias='category_id',
      parameter=category_id,
      types=(str, int))


class RealtimeStart(FredParameter):
  """
  realtime_start

  The start of the real-time period. For more information,\
    see https://fred.stlouisfed.org/docs/api/fred/realtime_period.html

      YYYY-MM-DD formatted string, optional, default: today's date
  """
  def __init__(
    self,
    realtime_start: str | dt.datetime = '',
  ):
    
    if not realtime_start:
      realtime_start = dt.datetime.today() - relativedelta(days=1)
      realtime_start = realtime_start.strftime(DATE_FORMAT)
    
    if not is_datetime(realtime_start):
      raise NotDateTime(realtime_start)

    super().__init__(
      alias='realtime_start',
      parameter=realtime_start,
      types=(str, dt.datetime))


class RealtimeEnd(FredParameter):
  """
  realtime_end

  The start of the real-time period. For more information,\
    see https://fred.stlouisfed.org/docs/api/fred/realtime_period.html

      YYYY-MM-DD formatted string, optional, default: today's date
  """
  def __init__(
    self,
    realtime_end: str | dt.datetime = '',
  ):
    if not realtime_end:
      realtime_end = dt.datetime.today() - relativedelta(days=1)
      realtime_end = realtime_end.strftime(DATE_FORMAT)

    if not is_datetime(realtime_end):
      raise NotDateTime(realtime_end)

    super().__init__(
      alias='realtime_end',
      parameter=realtime_end,
      types=(str, dt.datetime))


class Limit(FredParameter):
  """
  limit

  The maximum number of results to return.

      integer between 1 and 1000, optional, default: 1000
  """
  def __init__(
    self,
    limit: int = 1000,
  ):
    if limit < 1 or limit > 100000:
      raise LimitExceeded()

    super().__init__(
      alias='limit',
      parameter=limit,
      types=(int,)
    )


class Offset(FredParameter):
  """
  offset

      non-negative integer, optional, default: 0
  """
  def __init__(
    self,
    offset: int = 0
  ) -> None:
    if offset < 0:
      raise NotPositiveInteger()

    super().__init__(
      alias='offset',
      parameter=offset,
      types=(int,)
    )


class OrderBy(FredParameter):
  """
  order_by

  Order results by values of the specified attribute.

      One of the following strings: 'series_id', 'title', 'units', 'frequency', 'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end', 'popularity', 'group_popularity'.
      optional, default: series_id
  """
  def __init__(
    self,
    order_by: str = 'series_id',
  ):
    if order_by not in ORDER_BY_LIST:
      raise InvalidOrderByInput()
  
    super().__init__(
      alias='order_by',
      parameter=order_by,
      types=(str,)
    )


class SortOrder(FredParameter):
  """
  sort_order

  Sort results is ascending or descending order for attribute values specified by order_by.

      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  def __init__(
    self,
    sort_order: str = 'asc',
  ):
    if sort_order not in SORT_ORDER_LIST:
      raise InvalidSortOrderInput()

    super().__init__(
      alias='sort_order',
      parameter=sort_order,
      types=(str,)
    )


class FilterVariable(FredParameter):
  """
  filter_variable

  The attribute to filter results by.

      On of the following strings: 'frequency', 'units', 'seasonal_adjustment'.
      optional, no filter by default
  """
  def __init__(
    self,
    filter_variable: str = '',
  ):
    if filter_variable:
      if filter_variable not in FILTER_VARIABLE_LIST:
        raise InvalidFilterVariableInput()

    super().__init__(
      alias='filter_variable',
      parameter=filter_variable,
      types=(str,))


class FilterValue(FredParameter):
  """
  filter_value

  The value of the filter_variable attribute to filter results by.

      String, optional, no filter by default
  """
  def __init__(
    self,
    filter_value: str = '',
  ):
    super().__init__(
      alias='filter_value',
      parameter=filter_value,
      types=(str,))

class TagNames(FredParameter):
  """
  tag_names

  A semicolon delimited list of tag names that series match all of.

      String, optional, no filtering by tags by default
      Example value: 'income;bea'. Filter results to series having both tags 'income' and 'bea'.
      See https://fred.stlouisfed.org/docs/api/fred/tags.html
  """
  def __init__(
    self,
    tag_names: str | List[str] | Tuple[str] = '',
  ):
    super().__init__(
      alias='tag_names',
      parameter=tag_names,
      types=(str, List[str], Tuple[str],)
    )

class ExcludeTagNames(FredParameter):
  """
  exclude_tag_names

  A semicolon delimited list of tag names that series match none of.

      String, optional, no filtering by tags by default.
      Example value: 'discontinued;annual'. Filter results to series having neither tag 'discontinued' nor tag 'annual'.
      Parameter exclude_tag_names requires that parameter tag_names also be set to limit the number of matching series.

  """
  def __init__(
    self,
    exclude_tag_names: str | List[str] | Tuple[str] = '',
  ):
    super().__init__(
      alias='exclude_tag_names',
      parameter=exclude_tag_names,
      types=(str, List[str], Tuple[str]))


class TagGroupId(FredParameter):
  """
  tag_group_id

  A tag group id to filter tags by type.

      String, optional, no filtering by tag group by default.
      One of the following: 'freq', 'gen', 'geo', 'geot', 'rls', 'seas', 'src'.

      freq = Frequency
      gen = General or Concept
      geo = Geography
      geot = Geography Type
      rls = Release
      seas = Seasonal Adjustment
      src = Source

  """
  def __init__(
    self,
    tag_group_id: str = '',
  ):
    if tag_group_id:
      if tag_group_id not in TAG_GROUP_ID_LIST:
        raise InvalidTagGroupId()

    super().__init__(
      alias='tag_group_id',
      parameter=tag_group_id,
      types=(str,))
    

class SearchText(FredParameter):
  """
  search_text

  The words to find matching tags with.

      String, optional, no filtering by search words by default.

  """
  def __init__(
    self,
    search_text: str = '',
  ):
    super().__init__(
      alias='search_text',
      parameter=search_text,
      types=(str,))


class SearchType(FredParameter):
  """
  search_type

  Determines the type of search to perform.

      One of the following strings: 'full_text', 'series_id'.
      'full_text' searches series attributes title, units, frequency, and tags by parsing words into stems. This makes it possible for searches like 'Industry' to match series containing related words such as 'Industries'. Of course, you can search for multiple words like 'money' and 'stock'. Remember to url encode spaces (e.g. 'money%20stock').
      'series_id' performs a substring search on series IDs. Searching for 'ex' will find series containing 'ex' anywhere in a series ID. '*' can be used to anchor searches and match 0 or more of any character. Searching for 'ex*' will find series containing 'ex' at the beginning of a series ID. Searching for '*ex' will find series containing 'ex' at the end of a series ID. It's also possible to put an '*' in the middle of a string. 'm*sl' finds any series starting with 'm' and ending with 'sl'.
      optional, default: full_text.
  """
  def __init__(
    self,
    search_type: str = 'full_text',
  ):
    super().__init__(
      alias='search_type',
      parameter=search_type,
      types=(str,))


class IncludeReleaseDatesWithNoData(FredParameter):
  """
  include_release_dates_with_no_data

  Determines whether release dates with no data available are returned. The defalut value 'false' excludes release dates that do not have data. In particular, this excludes future release dates which may be available in the FRED release calendar or the ALFRED release calendar.

  If include_release_dates_with_no_data is set to true, the XML tag release_date has an extra attribute release_last_updated that can be compared to the release date to determine if data has been updated.

      One of the following strings: 'true', 'false'.
      optional, default: false
  """
  def __init__(
    self,
    include_release_dates_with_no_data: str = 'false',
  ):
    if include_release_dates_with_no_data not in INCLUDE_RELEASE_DATES_WITH_NO_DATA_LIST:
      raise InvalidIncludeReleaseDatesWithNoData()

    super().__init__(
      alias='include_release_dates_with_no_data',
      parameter=include_release_dates_with_no_data,
      types=(str,))
    

class ReleaseId(FredParameter):
  """
  release_id

  The id for a release.

      integer, required
  """
  def __init__(
    self,
    release_id: str | int,
  ):
    if isinstance(release_id, str):
      if not release_id.isnumeric():
        raise NotNumeric()

    super().__init__(
      alias='release_id',
      parameter=release_id,
      types=(str, int,))


class ElementId(FredParameter):
  """
  element_id

  The release table element id you would like to retrieve.

      integer, optional
      When the parameter is not passed, the root(top most) element for the release is given.

  """
  def __init__(
    self,
    element_id: str | int = '',
  ):
    super().__init__(
      alias='element_id',
      parameter=element_id,
      types=(str, int,))


class IncludeObservationValues(FredParameter):
  """
  include_observation_values

  A flag to indicate that observations need to be returned. Observation value and date will only be returned for a series type element.

      One of the following strings: 'true', 'false'.
      optional, default: false
  """
  def __init__(
    self,
    include_observation_values: str = 'false',
  ):
    if include_observation_values not in INCLUDE_OBSERVATION_VALUES_LIST:
      raise InvalidIncludeObservationValues()

    super().__init__(
      alias='include_observation_values',
      parameter=include_observation_values,
      types=(str,))


class ObservationDate(FredParameter):
  """
  observation_date

  The observation date to be included with the returned release table.

      YYYY-MM-DD formatted string, optional, default: 9999-12-31 (latest available)
  """
  def __init__(
    self,
    observation_date: str | dt.datetime = '9999-12-31',
  ):
    if not is_datetime(observation_date):
      raise NotDateTime(observation_date)

    super().__init__(
      alias='observation_date',
      parameter=observation_date,
      types=(str, dt.datetime,))


class ObservationStart(FredParameter):
  """
  observation_start

  The start of the observation period.

      YYYY-MM-DD formatted string, optional, default: 1776-07-04 (earliest available)
  """
  def __init__(
    self,
    observation_start: str | dt.datetime = '1776-07-04',
  ):
    if not is_datetime(observation_start):
      raise NotDateTime(observation_start)

    super().__init__(
      alias='observation_start',
      parameter=observation_start,
      types=(str, dt.datetime,))


class ObservationEnd(FredParameter):
  """
  observation_end

  The end of the observation period.

      YYYY-MM-DD formatted string, optional, default: 9999-12-31 (latest available)
  """
  def __init__(
    self,
    observation_end: str | dt.datetime = '9999-12-21'
  ):
    if not is_datetime(observation_end):
      raise NotDateTime(observation_end)

    super().__init__(
      alias='observation_end',
      parameter=observation_end,
      types=(str, dt.datetime,))


class Units(FredParameter):
  """
  units

  A key that indicates a data value transformation.

      string, optional, default: lin (No transformation)
      One of the following values: 'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log'

      lin = Levels (No transformation)
      chg = Change
      ch1 = Change from Year Ago
      pch = Percent Change
      pc1 = Percent Change from Year Ago
      pca = Compounded Annual Rate of Change
      cch = Continuously Compounded Rate of Change
      cca = Continuously Compounded Annual Rate of Change
      log = Natural Log
      For unit transformation formulas, see: https://alfred.stlouisfed.org/help#growth_formulas
  """
  def __init__(
    self,
    units: str = 'lin'
  ):
    if units not in UNITS_LIST:
      raise InvalidUnits()

    super().__init__(
      alias='lin',
      parameter=units,
      types=(str,))


class Frequency(FredParameter):
  """
  frequency

  An optional parameter that indicates a lower frequency to aggregate values to. The FRED frequency aggregation feature converts higher frequency data series into lower frequency data series (e.g. converts a monthly data series into an annual data series). In FRED, the highest frequency data is daily, and the lowest frequency data is annual. There are 3 aggregation methods available- average, sum, and end of period. See the aggregation_method parameter.

      string, optional, default: no value for no frequency aggregation
      One of the following values: 'd', 'w', 'bw', 'm', 'q', 'sa', 'a', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem'

      Frequencies without period descriptions:

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
  """
  def __init__(
    self,
    frequency: str = '',
  ):
    if frequency:
      if frequency not in FREQUENCY_LIST:
        raise InvalidFrequency()

    super().__init__(
      alias='frequency',
      parameter=frequency,
      types=(str,))


class AggregationMethod(FredParameter):
  """
  aggregation_method

  A key that indicates the aggregation method used for frequency aggregation. This parameter has no affect if the frequency parameter is not set.

      string, optional, default: avg
      One of the following values: 'avg', 'sum', 'eop'

      avg = Average
      sum = Sum
      eop = End of Period
  """
  def __init__(
    self,
    aggregation_method: str = 'avg',
  ):
    if aggregation_method not in AGGREGATION_METHOD_LIST:
      raise InvalidAggregationMethod()

    super().__init__(
      alias='aggregation_method',
      parameter=aggregation_method,
      types=(str,))


class OutputType(FredParameter):
  """
  output_type

  An integer that indicates an output type.

      integer, optional, default: 1
      One of the following values: '1', '2', '3', '4'

      1 = Observations by Real-Time Period
      2 = Observations by Vintage Date, All Observations
      3 = Observations by Vintage Date, New and Revised Observations Only
      4 = Observations, Initial Release Only
      For output types '2' and '3', some XML attribute names start with the series ID which may have a first character that is a number (i.e. 0 through 9). In this case only, the XML attribute name starts with an underscore then the series ID in order to avoid invalid XML. If the series ID starts with a letter (i.e. A through Z) then an underscore is not prepended.
      For more information, read: https://alfred.stlouisfed.org/help/downloaddata#outputformats
  """
  def __init__(
    self,
    output_type: str | int = '1'
  ):
    if str(output_type) not in OUTPUT_TYPE_LIST:
      raise InvalidOutputType()

    super().__init__(
      alias='output_type',
      parameter=output_type,
      types=(str, int,))


class VintageDates(FredParameter):
  """
  vintage_dates

  A comma separated string of YYYY-MM-DD formatted dates in history (e.g. 2000-01-01,2005-02-24). Vintage dates are used to download data as it existed on these specified dates in history. Vintage dates can be specified instead of a real-time period using realtime_start and realtime_end.

  Sometimes it may be useful to enter a vintage date that is not a date when the data values were revised. For instance you may want to know the latest available revisions on a particular date. Entering a vintage date is also useful to compare series on different releases with different release dates.

      string, optional, no vintage dates are set by default.

  Your query will be limited to a specific number of vintage dates depending on the series_id, file_type and output_type specified.

      output_type=2, series_id=USRECD: 110 csv, 55 xlsx
      output_type=2, any daily series: 450 csv, 225 xlsx
      any output_type or other series: 1000 csv, 1000 xlsx, 2000 json, 2000 xml
  """
  def __init__(
    self,
    vintage_dates: str | List[str | dt.datetime] = ''
  ):
    vintage_dates_string = ''

    if isinstance(vintage_dates, List):
      temp: List[str]= [
        d.strftime(DATE_FORMAT)
        if isinstance(d, dt.datetime)
        else d
        for d in vintage_dates
      ]
      vintage_dates_string = ','.join(temp)
    else:
      vintage_dates_string = vintage_dates

    super().__init__(
      alias='vintage_dates',
      parameter=vintage_dates_string,
      types=(str, list,))


class TagSearchText(FredParameter):
  """
  tag_search_text

  The words to find matching tags with.

      String, optional, no filtering by search words by default.
  """
  def __init__(
    self,
    tag_search_text: str = '',
  ):
    super().__init__(
      alias='tag_search_text',
      parameter=tag_search_text,
      types=(str,))


class SeriesSearchText(FredParameter):
  """
  series_search_text

  The words to match against economic data series.

      string, required
  """
  def __init__(
    self,
    series_search_text: str = '',
  ):
    super().__init__(
      alias='series_search_text',
      parameter=series_search_text,
      types=(str,))


class SeriesId(FredParameter):
  """
  series_id

  The id for a series.

      string, required
  """
  def __init__(
    self,
    series_id: str,
  ):
    super().__init__(
      alias='series_id',
      parameter=series_id,
      types=(str,))


class StartTime(FredParameter):
  """
  start_time

  Start time for limiting results for a time range, can filter down to minutes

      YYYYMMDDHhmm formatted string, optional, end_time is required if start_time is set
      Example: 2018-03-02 14:20 would be 201803021420
  """
  def __init__(
    self,
    start_time: str | dt.datetime = '',
  ):
    if start_time:
      if isinstance(start_time, dt.datetime):
        start_time = start_time.strftime(TIME_FORMAT)
      elif isinstance(start_time, str):
        if not (len(start_time) == 12 and start_time.isnumeric()):
          raise NotNumeric()

    super().__init__(
      alias='start_time',
      parameter=start_time,
      types=(str, dt.datetime))


class EndTime(FredParameter):
  """
  end_time

  End time for limiting results for a time range, can filter down to minutes

      YYYYMMDDHhmm formatted string, optional, , start_time is required if end_time is set<
      Example: 2018-03-02 2:20 would be 201803020220
  """
  def __init__(
    self,
    end_time: str | dt.datetime = '',
  ):
    if end_time:
      if isinstance(end_time, dt.datetime):
        end_time = end_time.strftime(TIME_FORMAT)
      elif isinstance(end_time, str):
        if not (len(end_time) == 12 and end_time.isnumeric()):
          raise NotNumeric()

    super().__init__(
      alias='end_time',
      parameter=end_time,
      types=(str, dt.datetime))


class SourceId(FredParameter):
  """
  source_id

  The id for a source.

      integer, required
  """
  def __init__(
    self,
    source_id: str | int,
  ) -> None:
    if isinstance(source_id, str):
      if not source_id.isnumeric():
        raise NotNumeric()

    super().__init__(
      alias='source_id',
      parameter=source_id,
      types=(str, int),)