import datetime as dt


from ..base import Fred
from ..params import (
  RealtimeEnd,
  RealtimeStart,
  Limit,
  Offset,
  SortOrder,
  OrderBy,
  SourceId,
)


def get_sources(
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'source_id',
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
      One of the following strings: 'source_id', 'name', 'realtime_start', 'realtime_end'.
      optional, default: source_id

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='sources',
    params={
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order)
    }
  )


def get_source(
  source_id: str | int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
) -> dict:
  """
  source_id
  The id for a source.
      integer, required

  realtime_start
  The start of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date

  realtime_end
  The end of the real-time period. For more information, see Real-Time Periods.
      YYYY-MM-DD formatted string, optional, default: today's date
  """
  return Fred.request(
    endpoint='source',
    params={
      'source_id': SourceId(source_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
    }
  )


def get_source_releases(
  source_id: str | int,
  realtime_start: str | dt.datetime = '',
  realtime_end: str | dt.datetime = '',
  limit: int = 1000,
  offset: int = 0,
  order_by: str = 'release_id',
  sort_order: str = 'asc',
) -> dict:
  """
  source_id
  The id for a source.
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
      One of the following strings: 'release_id', 'name', 'press_release', 'realtime_start', 'realtime_end'.
      optional, default: release_id

  sort_order
  Sort results is ascending or descending order for attribute values specified by order_by.
      One of the following strings: 'asc', 'desc'.
      optional, default: asc
  """
  return Fred.request(
    endpoint='source/releases',
    params={
      'source_id': SourceId(source_id),
      'realtime_start': RealtimeStart(realtime_start),
      'realtime_end': RealtimeEnd(realtime_end),
      'limit': Limit(limit),
      'offset': Offset(offset),
      'order_by': OrderBy(order_by),
      'sort_order': SortOrder(sort_order)
    }
  )