import datetime as dt


from typing import (
  List,
  Tuple,
)
from ..base import Fred
from ..params import (
  RealtimeEnd,
  RealtimeStart,
  Limit,
  Offset,
  SortOrder,
  ExcludeTagNames,
  OrderBy,
  SearchText,
  TagNames,
  TagGroupId,
)


def get_tags(
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str] = '',
  tag_group_id: str = '',
  search_text: str = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc',
) -> dict:
  """
  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names to only include in the response. See the related request fred/related_tags.
      String, optional, no filtering by tag names by default
      Example value: 'gdp;oecd'. This value filters results to only include tags 'gdp' and 'oecd'.

  tag_group_id
  A tag group id to filter tags by type.
      String, optional, no filtering by tag group by default.
      One of the following: 'freq', 'gen', 'geo', 'geot', 'rls', 'seas', 'src', 'cc'.

      freq = Frequency
      gen = General or Concept
      geo = Geography
      geot = Geography Type
      rls = Release
      seas = Seasonal Adjustment
      src = Source
      cc = Citation & Copyright

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
    endpoint='tags',
    params={
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'tag_names': TagNames(tag_names),
      'tag_group_id': TagGroupId(tag_group_id),
      'search_text': SearchText(search_text),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
    }
  )


def get_related_tags(
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str] = '',
  exclude_tag_names: str | List[str] | Tuple[str] = '',
  tag_group_id: str = '',
  search_text: str ='',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc',
) -> dict:
  """
  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names that series match all of. See the related request fred/tags.
      String, required, no default value.
      Example value: 'monetary+aggregates;weekly'. Find the related tags for series having both tags 'monetary aggregates' and 'weekly'. The '+' in 'monetary+aggregates;weekly' is an URL encoded space character.

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no default value.
      Example value: 'discontinued;currency'. Find the related tags for series having neither tag 'discontinued' nor tag 'currency'.

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
    endpoint='related_tags',
    params={
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'tag_names': TagNames(tag_names),
      'exclude_tag_names': ExcludeTagNames(exclude_tag_names),
      'tag_group_id': TagGroupId(tag_group_id),
      'search_text': SearchText(search_text),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order)
    }
  )


def get_tags_series(
  tag_names: str | List[str] | Tuple[str],
  exclude_tag_names: str | List[str] | Tuple[str] = '',
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_id',
  sort_order: str = 'asc',
) -> dict:
  """
  tag_names
  A semicolon delimited list of tag names that series match all of.
      String, required, no default value.
      Example value: 'slovenia;food'. Filter results to series having both tags 'slovenia' and 'food'.
      See the related request fred/tags. 

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no default value.
      Example value: 'alchohol;quarterly'. Filter results to series having neither tag 'alchohol' nor tag 'quarterly'.

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
      One of the following strings: 'series_id', 'title', 'units', 'frequency', 'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end', 'popularity', 'group_popularity'.
      optional, default: series_id

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='tags/series',
    params={
      'tag_names': TagNames(tag_names),
      'exclude_tag_names': ExcludeTagNames(exclude_tag_names),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order)
    }
  )