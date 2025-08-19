import datetime as dt


from typing import (
  List,
  Tuple,
)
from ..base import Fred
from ..params import (
  CategoryId,
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
)


def get_category(
  category_id: str | int,
) -> dict:
  """
  category_id: The id for a category.
      integer, default: 0 (root category)
  """
  param1 = CategoryId(category_id=category_id)
  return Fred.request(
    endpoint='category',
    params={
      'category_id': param1,
    }
  )


def get_category_children(
  category_id: str | int,
  realtime_start: str | dt.datetime,
  realtime_end: str | dt.datetime,
) -> dict:
  """
  category_id:
    The id for a category.
      integer, default: 0 (root category)
  realtime_start
    The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
    The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  param1 = CategoryId(category_id)
  param2 = RealtimeStart(realtime_start)
  param3 = RealtimeEnd(realtime_end)
  return Fred.request(
    endpoint='category/children',
    params={
      'category_id': param1,
      'realtime_start': param2,
      'realtime_end': param3,
    }
  )


def get_category_related(
  category_id: str | int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  category_id

  The id for a category.

      integer, required

  realtime_start

  The start of the real-time period. For more information, see Real-Time Periods.

      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end

  The end of the real-time period. For more information, see Real-Time Periods.

      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='category/releated',
    params={
      'category_id': CategoryId(category_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end)
    }
  )


def get_category_series(
  category_id: str | int,
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
  category_id
  The id for a category.
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
      One of the following strings: 'series_id', 'title', 'units', 'frequency', 'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end', 'popularity', 'group_popularity'.
      optional, default: series_id

  sort_order
    Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc

  filter_variable
    The attribute to filter results by.
      On of the following strings: 'frequency', 'units', 'seasonal_adjustment'.
      optional, no filter by default

  filter_value
    The value of the filter_variable attribute to filter results by.
      String, optional, no filter by default

  tag_names
    A semicolon delimited list of tag names that series match all of.
      String, optional, no filtering by tags by default
      Example value: 'income;bea'. Filter results to series having both tags 'income' and 'bea'.
      See the related request fred/tags. 

  exclude_tag_names
    A semicolon delimited list of tag names that series match none of.
      String, optional, no filtering by tags by default.
      Example value: 'discontinued;annual'. Filter results to series having neither tag 'discontinued' nor tag 'annual'.
      Parameter exclude_tag_names requires that parameter tag_names also be set to limit the number of matching series.
  """
  return Fred.request(
    endpoint='category/series',
    params={
      'category_id': CategoryId(category_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order),
      'filter_variable': FilterVariable(filter_variable),
      'filter_value': FilterValue(filter_value),
      'tag_names': TagNames(tag_names),
      'exclude_tag_names': ExcludeTagNames(exclude_tag_names),
    }
  )


def get_category_tags(
  category_id: str | int,
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
  category_id
    The id for a category.
      integer, required

  realtime_start
    The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
    The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
    A semicolon delimited list of tag names to only include in the response. See the related request fred/category/related_tags.
      String, optional, no filtering by tag names by default
      Example value: 'trade;goods'. This value filters results to only include tags 'trade' and 'goods'.

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
    endpoint='category/tags',
    params={
      'category_id': CategoryId(category_id),
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


def get_category_related_tags(
  category_id: str | int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  tag_names: str | List[str] | Tuple[str] = '',
  exclude_tag_names: str | List[str] | Tuple[str] = '',
  tag_group_id: str = '',
  search_text: str = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'series_count',
  sort_order: str = 'asc'
) -> dict:
  """
  category_id
  The id for a category.
      integer, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  tag_names
  A semicolon delimited list of tag names that series match all of. See the related request fred/category/tags.
      String, required, no default value.
      Example value: 'services;quarterly'. Find the related tags for series having both tags 'services' and 'quarterly'.

  exclude_tag_names
  A semicolon delimited list of tag names that series match none of.
      String, optional, no default value.
      Example value: 'goods;sa'. Find the related tags for series having neither tag 'goods' nor tag 'sa'.

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
    endpoint='category/related_tags',
    params={
      'category_id': CategoryId(category_id),
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