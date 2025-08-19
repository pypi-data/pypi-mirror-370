import os


from ..params import (
  Apikey,
  FileType,
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
  IncludeObservationValues,
  IncludeReleaseDatesWithNoData,
  ReleaseId,
  ElementId,
  ObservationDate,
  ObservationStart,
  ObservationEnd,
  Units,
  Frequency,
  AggregationMethod,
  OutputType,
  VintageDates,
  TagSearchText,
  Offset,
  SeriesSearchText,
  FilterValue,
  SeriesId,
  SearchType,
  StartTime,
  EndTime,
  SourceId,
)
from dotenv import load_dotenv, find_dotenv
DOTENV = load_dotenv(find_dotenv())


api_key = Apikey(str(os.getenv('FRED_APIKEY')))
file_type = FileType('json')
category_id = CategoryId('0')
realtime_start = RealtimeStart('2024-01-01')
realtime_end = RealtimeEnd('2025-06-30')
limit = Limit(1000)
order_by = OrderBy('series_id')
sort_order = SortOrder('asc')
filter_variable = FilterVariable('')
tag_names = TagNames()
exclude_tag_names = ExcludeTagNames()
tag_group_id = TagGroupId()
search_text = SearchText()
include_observation_values = IncludeObservationValues()