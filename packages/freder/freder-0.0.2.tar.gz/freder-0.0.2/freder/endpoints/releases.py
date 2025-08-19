import datetime as dt


from ..base import Fred
from typing import (
  List,
  Tuple,
)
from ..params import (
  RealtimeStart,
  RealtimeEnd,
  Limit,
  OrderBy,
  SortOrder,
  FilterVariable,
  TagNames,
  ExcludeTagNames,
  TagGroupId,
  SearchText,
  Offset,
  FilterValue,
  ElementId,
  IncludeObservationValues,
  IncludeReleaseDatesWithNoData,
  ObservationDate,
  ReleaseId
)


def get_releases(
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'release_id',
  sort_order: str = 'asc',
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

  order_by
  Order results by values of the specified attribute.
      One of the following strings: 'release_id', 'name', 'press_release', 'realtime_start', 'realtime_end'.
      optional, default: release_id

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='releases',
    params={
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
    }
  )


def get_releases_dates(
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'release_date',
  sort_order: str = 'asc',
  include_release_dates_with_no_data = 'false',
) -> dict:
  """
  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: First day of the current year

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: 9999-12-31 (latest available)

  limit
  The maximum number of results to return.
      integer between 1 and 1000, optional, default: 1000

  offset
      non-negative integer, optional, default: 0

  order_by
  Order results by values of the specified attribute.
      One of the following strings: 'release_date', 'release_id', 'release_name'.
      optional, default: release_date

  sort_order
  Sort results is ascending or descending release date order.
      One of the following strings: 'asc', 'desc'.
      optional, default: desc

  include_release_dates_with_no_data
  Determines whether release dates with no data available are returned. The defalut value 'false' excludes release dates that do not have data. In particular, this excludes future release dates which may be available in the FRED release calendar or the ALFRED release calendar.

  If include_release_dates_with_no_data is set to true, the XML tag release_date has an extra attribute release_last_updated that can be compared to the release date to determine if data has been updated.
      One of the following strings: 'true', 'false'.
      optional, default: false
  """
  return Fred.request(
    endpoint='releases/dates',
    params={
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
      'include_release_dates_with_no_data': IncludeReleaseDatesWithNoData(include_release_dates_with_no_data)
    },
  )


def get_release(
  release_id: int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  release_id
  The id for a release.
      integer, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='release',
    params={
      'release_id': ReleaseId(release_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end)
    }
  )


def get_release_dates(
  release_id: int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 10000,
  offset: int = 0,
  sort_order: str = 'asc',
  include_release_dates_with_no_data: str = 'false'
) -> dict:
  """
  release_id
  The id for a release.
      integer, required

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
  Sort results is ascending or descending release date order.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc

  include_release_dates_with_no_data
  Determines whether release dates with no data available are returned. The defalut value 'false' excludes release dates that do not have data. In particular, this excludes future release dates which may be available in the FRED release calendar or the ALFRED release calendar.
      One of the following strings: 'true', 'false'.
      optional, default: false
  """
  return Fred.request(
    endpoint='release/dates',
    params={
      'release_id': ReleaseId(release_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'sort_order': SortOrder(sort_order),
      'include_release_dates_with_no_data': IncludeReleaseDatesWithNoData(include_release_dates_with_no_data)
    }
  )


def get_release_series(
  release_id: int,
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
  release_id
  The id for a release.
      integer, required

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
      One of the following strings: 'series_id', 'title', 'units', 'frequency', 'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end', 'popularity','group_popularity'.
      optional, default: series_id

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc

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
      Example value: 'japan;imports'. Filter results to series having both tags 'japan' and 'imports'.
      See the related request fred/tags. 

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no filtering by tags by default.
      Example value: 'imports;services'. Filter results to series having neither tag 'imports' nor tag 'services'.
      Parameter exclude_tag_names requires that parameter tag_names also be set to limit the number of matching series.
  """
  return Fred.request(
    endpoint='release/series',
    params={
      'release_id': ReleaseId(release_id),
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


def get_release_sources(
  release_id: int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  release_id
  The id for a release.
      integer, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='release/sources',
    params={
      'release_id': ReleaseId(release_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end)
    }
  )


def get_release_tags(
  release_id: int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str]  = '',
  tag_group_id: str = '',
  search_text: str = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc',
) -> dict:
  """
  release_id
  The id for a release.
      integer, required
  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names to only include in the response. See the related request fred/release/related_tags.
      String, optional, no filtering by tag names by default
      Example value: 'gnp;quarterly'. This value filters results to only include tags 'gnp' and 'quarterly'.

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

  search_text
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
    endpoint='release/tags',
    params={
      'release_id': ReleaseId(release_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'tag_names': TagNames(tag_names),
      'tag_group_id': TagGroupId(tag_group_id),
      'search_text': SearchText(search_text),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order)
    }
  )


def get_release_related_tags(
  release_id: int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str] = '',
  exclude_tag_names: str = '',
  tag_group_id: str = '',
  search_text: str = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc'
) -> dict:
  """
  release_id
  The id for a release.
      integer, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names that series match all of. See the related request fred/release/tags.
      String, required, no default value.
      Example value: 'defense;investment'. Find the related tags for series having both tags 'defense' and 'investment'.

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no default value.
      Example value: 'monthly;financial'. Find the related tags for series having neither tag 'monthly' nor tag 'financial'.

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

  search_text
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
    endpoint='release/related_tags',
    params={
      'release_id': ReleaseId(release_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'tag_names': TagNames(tag_names),
      'exclude_tag_names': ExcludeTagNames(exclude_tag_names),
      'tag_group_id': TagGroupId(tag_group_id),
      'search_text': SearchText(search_text),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
    }
  )


def get_release_tables(
  release_id: int,
  element_id: int | str = '',
  include_observation_values: str = 'false',
  observation_date: str | dt.datetime = '9999-12-31'
) -> dict:
  """
  release_id
  The id for a release.
      integer, required

  element_id
  The release table element id you would like to retrieve.
      integer, optional
      When the parameter is not passed, the root(top most) element for the release is given.

  include_observation_values
  A flag to indicate that observations need to be returned. Observation value and date will only be returned for a series type element.
      One of the following strings: 'true', 'false'.
      optional, default: false

  observation_date
  The observation date to be included with the returned release table.
      YYYY-MM-DD formatted string, optional, default: 9999-12-31 (latest available)
  """
  return Fred.request(
    endpoint='release/tables',
    params={
      'release_id': ReleaseId(release_id),
      'element_id': ElementId(element_id),
      'include_observation_values': IncludeObservationValues(include_observation_values),
      'observation_date': ObservationDate(observation_date)
    },
  )