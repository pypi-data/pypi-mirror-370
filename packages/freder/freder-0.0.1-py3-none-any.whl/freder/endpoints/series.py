import datetime as dt


from ..base import Fred
from typing import List, Tuple
from ..params import (
  SeriesId,
  RealtimeEnd,
  RealtimeStart,
  Limit,
  Offset,
  ObservationStart,
  SortOrder,
  Units,
  AggregationMethod,
  Frequency,
  ObservationEnd,
  OutputType,
  VintageDates,
  SearchType,
  ExcludeTagNames,
  FilterValue,
  FilterVariable,
  OrderBy,
  SearchText,
  TagNames,
  StartTime,
  EndTime,
  SeriesSearchText,
  TagGroupId,
  TagSearchText,
)


def get_series(
  series_id: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  series_id
  The id for a series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='series',
    params={
      'series_id': SeriesId(series_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end)
    }
  )


def get_series_categories(
  series_id: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  series_id
  The id for a series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='series/categories',
    params={
      'series_id': SeriesId(series_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end)
    }
  )


def get_series_observations(
  series_id: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 100000,
  offset: int = 0,
  sort_order: str = 'asc',
  observation_start: str | dt.datetime = '1776-07-04',
  observation_end: str | dt.datetime = '9999-12-31',
  units: str = 'lin',
  frequency: str = '',
  aggregation_method: str ='avg',
  output_type: int | str = '1',
  vintage_dates: str | List[str | dt.datetime] = '',
) -> dict:
  """
  series_id
  The id for a series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods, vintage_dates.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods, vintage_dates.
      YYYY-MM-DD formatted string, optional, default: today's date

  limit
  The maximum number of results to return.
      integer between 1 and 100000, optional, default: 100000

  offset
      non-negative integer, optional, default: 0

  sort_order
  Sort results is ascending or descending observation_date order.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc

  observation_start
  The start of the observation period.
      YYYY-MM-DD formatted string, optional, default: 1776-07-04 (earliest available)

  observation_end
  The end of the observation period.
      YYYY-MM-DD formatted string, optional, default: 9999-12-31 (latest available)

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

      Note that an error will be returned if a frequency is specified that is higher than the native frequency of the series. For instance if a series has the native frequency 'Monthly' (as returned by the fred/series request), it is not possible to aggregate the series to the higher 'Daily' frequency using the frequency parameter value 'd'.
      No frequency aggregation will occur if the frequency specified by the frequency parameter matches the native frequency of the series. For instance if the value of the frequency parameter is 'm' and the native frequency of the series is 'Monthly' (as returned by the fred/series request), observations will be returned, but they will not be aggregated to a lower frequency.
      For most cases, it will be sufficient to specify a lower frequency without a period description (e.g. 'd', 'w', 'bw', 'm', 'q', 'sa', 'a') as opposed to frequencies with period descriptions (e.g. 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem') which only exist for the weekly and biweekly frequencies.
          The weekly and biweekly frequencies with periods exist to offer more options and override the default periods implied by values 'w' and 'bw'.
          The value 'w' defaults to frequency and period 'Weekly, Ending Friday' when aggregating daily series.
          The value 'bw' defaults to frequency and period 'Biweekly, Ending Wednesday' when aggregating daily and weekly series.
          Consider the difference between values 'w' for 'Weekly' and 'wef' for 'Weekly, Ending Friday'. When aggregating observations from daily to weekly, the value 'w' defaults to frequency and period 'Weekly, Ending Friday' which is the same as 'wef'. Here, the difference is that the period 'Ending Friday' is implicit for value 'w' but explicit for value 'wef'. However, if a series has native frequency 'Weekly, Ending Monday', an error will be returned for value 'wef' but not value 'w'.
      Note that frequency aggregation is currently only available for file_type equal to xml or json due to time constraints.
      Read the 'Frequency Aggregation' section of the FRED FAQs for implementation details.

  aggregation_method
  A key that indicates the aggregation method used for frequency aggregation. This parameter has no affect if the frequency parameter is not set.
      string, optional, default: avg
      One of the following values: 'avg', 'sum', 'eop'

      avg = Average
      sum = Sum
      eop = End of Period

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

  vintage_dates
  A comma separated string of YYYY-MM-DD formatted dates in history (e.g. 2000-01-01,2005-02-24). Vintage dates are used to download data as it existed on these specified dates in history. Vintage dates can be specified instead of a real-time period using realtime_start and realtime_end.
  Sometimes it may be useful to enter a vintage date that is not a date when the data values were revised. For instance you may want to know the latest available revisions on a particular date. Entering a vintage date is also useful to compare series on different releases with different release dates.
      string, optional, no vintage dates are set by default.

  Your query will be limited to a specific number of vintage dates depending on the series_id, file_type and output_type specified.
      output_type=2, series_id=USRECD: 110 csv, 55 xlsx
      output_type=2, any daily series: 450 csv, 225 xlsx
      any output_type or other series: 1000 csv, 1000 xlsx, 2000 json, 2000 xml

  """
  return Fred.request(
    endpoint='series/observations',
    params={
      'series_id': SeriesId(series_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'sort_order': SortOrder(sort_order),
      'observation_start': ObservationStart(observation_start),
      'observation_end': ObservationEnd(observation_end),
      'units': Units(units),
      'frequency': Frequency(frequency),
      'aggregation_method': AggregationMethod(aggregation_method),
      'output_type': OutputType(output_type),
      'vintage_dates': VintageDates(vintage_dates),
    }
  )


def get_series_release(
  series_id: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  series_id
  The id for a series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='series/release',
    params={
      'series_id': SeriesId(series_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end)
    }
  )


def get_series_search(
  search_text: str,
  search_type: str = 'full_text',
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_id',
  sort_order: str = 'asc',
  filter_variable: str = '',
  filter_value: str = '',
  tag_names: str | List[str] | Tuple[str] = '',
  exclude_tag_names: str | List[str] | Tuple[str] = '',
) -> dict:
  """
  search_text
  The words to match against economic data series.
  search_type
  Determines the type of search to perform.

      One of the following strings: 'full_text', 'series_id'.
      'full_text' searches series attributes title, units, frequency, and tags by parsing words into stems. This makes it possible for searches like 'Industry' to match series containing related words such as 'Industries'. Of course, you can search for multiple words like 'money' and 'stock'. Remember to url encode spaces (e.g. 'money%20stock').
      'series_id' performs a substring search on series IDs. Searching for 'ex' will find series containing 'ex' anywhere in a series ID. '*' can be used to anchor searches and match 0 or more of any character. Searching for 'ex*' will find series containing 'ex' at the beginning of a series ID. Searching for '*ex' will find series containing 'ex' at the end of a series ID. It's also possible to put an '*' in the middle of a string. 'm*sl' finds any series starting with 'm' and ending with 'sl'.
      optional, default: full_text.

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  limit
  The maximum number of results to return.
      integer between 1 and 1000, optional, default: 1000

  offset
      non-negative integer, optional, default: 0

  order_by
  Order results by values of the specified attribute.
      One of the following strings: 'search_rank', 'series_id', 'title', 'units', 'frequency', 'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end', 'popularity', 'group_popularity'.
      optional, default: If the value of search_type is 'full_text' then the default value of order_by is 'search_rank'. If the value of search_type is 'series_id' then the default value of order_by is 'series_id'.

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: If order_by is equal to 'search_rank' or 'popularity', then the default value of sort_order is 'desc'. Otherwise, the default sort order is 'asc'.

  filter_variable
  The attribute to filter results by.
      One of the following strings: 'frequency', 'units', 'seasonal_adjustment'.
      optional, no filter by default

  filter_value
  The value of the filter_variable attribute to filter results by.
      String, optional, no filter by default

  tag_names
  A semicolon delimited list of tag names that series match all of.
      String, optional, no filtering by tags by default
      Example value: 'usa;m2'. Filter results to series having both tags 'usa' and 'm2'.
      See the related request fred/tags. 

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no filtering by tags by default.
      Example value: 'discontinued;m1'. Filter results to series having neither tag 'discontinued' nor tag 'm1'.
      Parameter exclude_tag_names requires that parameter tag_names also be set to limit the number of matching series.
  """
  return Fred.request(
    endpoint='series/search',
    params={
      'search_text': SearchText(search_text),
      'search_type': SearchType(search_type),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
      'filter_variable': FilterVariable(filter_variable),
      'filter_value': FilterValue(filter_value),
      'tag_names': TagNames(tag_names),
      'exclude_tag_names': ExcludeTagNames(exclude_tag_names)
    }
  )


def get_series_search_tags(
  series_search_text: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str] = '',
  tag_group_id: str = '',
  tag_search_text: str ='',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc',
) -> dict:
  """
  series_search_text
  The words to match against economic data series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names to only include in the response. See the related request fred/series/search/related_tags.
      String, optional, no filtering by tag names by default
      Example value: 'm1;m2'. This value filters results to only include tags 'm1' and 'm2'.

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

  tag_search_text
  The words to find matching tags with.
      String, optional, no filtering by search words by default.

  limit
  The maximum number of results to return.
      integer between 1 and 1000, optional, default: 1000

  offset
      non-negative integer, optional, default: 0

  order_by
  Order results by values of the specified attribute.
      One of the following strings: 'series_count', 'popularity', 'created', 'name', 'group_id'.
      optional, default: series_count

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='series/search/tags',
    params={
      'series_search_text': SeriesSearchText(series_search_text),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'tag_names': TagNames(tag_names),
      'tag_group_id': TagGroupId(tag_group_id),
      'tag_search_text': TagSearchText(tag_search_text),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
    }
  )


def get_series_search_related_tags(
  series_search_text: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str] = '',
  exclude_tag_names: str | List[str] | Tuple[str]  = '',
  tag_group_id: str = '',
  tag_search_text: str = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc',
) -> dict:
  """
  series_search_text
  The words to match against economic data series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names that series match all of. See the related request fred/series/search/tags.
      String, required, no default value.
      Example value: '30-year;frb'. Find the related tags for series having both tags '30-year' and 'frb'.

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no default value.
      Example value: 'discontinued;monthly'. Find the related tags for series having neither tag 'discontinued' nor tag 'monthly'.

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

  tag_search_text
  The words to find matching tags with.
      String, optional, no filtering by search words by default.

  limit
  The maximum number of results to return.
      integer between 1 and 1000, optional, default: 1000

  offset
      non-negative integer, optional, default: 0

  order_by
  Order results by values of the specified attribute.
      One of the following strings: 'series_count', 'popularity', 'created', 'name', 'group_id'.
      optional, default: series_count

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='series/search/related_tags',
    params={
      'series_search_text': SeriesSearchText(series_search_text),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'tag_names': TagNames(tag_names),
      'exclude_tag_names': ExcludeTagNames(exclude_tag_names),
      'tag_group_id': TagGroupId(tag_group_id),
      'tag_search_text': TagSearchText(tag_search_text),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
    }
  )


def get_series_tags(
  series_id: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  order_by: str = 'series_count',
  sort_order: str = 'asc',
) -> dict:
  """
  series_id
  The id for a series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  order_by
  Order results by values of the specified attribute.
      One of the following strings: 'series_count', 'popularity', 'created', 'name', 'group_id'.
      optional, default: series_count

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='series/tags',
    params={
      'series_id': SeriesId(series_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
    }
  )


def get_series_updates(
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  filter_value: str ='all',
  start_time: str | dt.datetime = '',
  end_time: str | dt.datetime = '',
) -> dict:
  """
  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  limit
  The maximum number of results to return.
      integer between 1 and 1000, optional, default: 1000

  offset
      non-negative integer, optional, default: 0

  filter_value
  Limit results by geographic type of economic data series; namely 'macro', 'regional', and 'all'.
      String, optional, default: 'all' meaning no filter.
      One of the values: 'macro', 'regional', 'all'
      'macro' limits results to macroeconomic data series. In general, these are series for entire countries that are not subregions of the United States. 'regional' limits results to series for parts of the US; namely, series for US states, counties, and Metropolitan Statistical Areas (MSA). 'all' does not filter results.

  start_time
  Start time for limiting results for a time range, can filter down to minutes
      YYYYMMDDHhmm formatted string, optional, end_time is required if start_time is set
      Example: 2018-03-02 14:20 would be 201803021420

  end_time
  End time for limiting results for a time range, can filter down to minutes
      YYYYMMDDHhmm formatted string, optional, , start_time is required if end_time is set<
      Example: 2018-03-02 2:20 would be 201803020220
  """
  return Fred.request(
    endpoint='series/updates',
    params={
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'filter_value': FilterValue(filter_value),
      'start_time': StartTime(start_time),
      'end_time': EndTime(end_time),
    }
  )


def get_series_vintageupdates(
  series_id: str,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  sort_order: str = 'asc',
) -> dict:
  """
  series_id
  The id for a series.
      string, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: 1776-07-04 (earliest available)

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: 9999-12-31 (latest available)

  limit
  The maximum number of results to return.
      integer between 1 and 10000, optional, default: 10000

  offset
      non-negative integer, optional, default: 0

  sort_order
  Sort results is ascending or descending vintage_date order.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='series/vintageupdates',
    params={
      'series_id': SeriesId(series_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'sort_order': SortOrder(sort_order)
    }
  )