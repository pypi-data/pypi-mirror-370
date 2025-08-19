import re


BASEURL = 'https://api.stlouisfed.org/fred'
DATE_FORMAT= '%Y-%m-%d'
TIME_FORMAT = '%Y%m%d%H%M'
DATE_REGEX = re.compile(r'^\d{4}\-\d{2}\-\d{2}$')
APIKEY = ''
ORDER_BY_LIST = [
  'series_id', 'title', 'units',
  'frequency', 'seasonal_adjustment',
  'realtime_start', 'realtime_end',
  'last_updated', 'observation_start',
  'observation_end', 'popularity',
  'group_popularity', 'series_count'
]
SORT_ORDER_LIST = [
  'asc', 'desc'
]
FILTER_VARIABLE_LIST = [
  'frequency', 'units', 'seasonal_adjustment',
]
TAG_GROUP_ID_LIST = [
  'freq', 'gen', 'geo', 'geot', 'rls', 'seas', 'src'
]
INCLUDE_RELEASE_DATES_WITH_NO_DATA_LIST = [
  'true', 'false'
]
INCLUDE_OBSERVATION_VALUES_LIST = [
  'true', 'false'
]
UNITS_LIST = [
  'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch',
  'cca', 'log'
]
FREQUENCY_LIST = [
  'd', 'w', 'bw', 'm', 'q', 'sa', 'a'
  'wef', 'weth', 'wew', 'wetu', 'wem',
  'wesu', 'wesa', 'bwew', 'bwem'
]
AGGREGATION_METHOD_LIST = [
  'avg', 'sum', 'eop'
]
OUTPUT_TYPE_LIST = [
  '1', '2', '3', '4'
]
SEARCH_TYPE_LIST = [
  'full_text',  
  'series_id',
]