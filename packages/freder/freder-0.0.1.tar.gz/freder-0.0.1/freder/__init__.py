"""FRED API Python package"""

__version__ = '0.0.0'
__author__ = 'Yunjong Guk'


from .params import (
  set_apikey,
  show_apikey,
)
from .base import Fred
from .endpoints import (
  get_category,
  get_category_children,
  get_category_related,
  get_category_related_tags,
  get_category_series,
  get_category_tags,
  get_release,
  get_release_dates,
  get_release_related_tags,
  get_release_series,
  get_release_sources,
  get_release_tables,
  get_release_tags,
  get_releases,
  get_releases_dates,
  get_series,
  get_series_categories,
  get_series_observations,
  get_series_release,
  get_series_search,
  get_series_search_related_tags,
  get_series_search_tags,
  get_series_tags,
  get_series_updates,
  get_series_vintageupdates,
  get_source,
  get_source_releases,
  get_sources,
  get_tags,
  get_related_tags,
  get_tags_series,
)
from .test import test_all


__all__ = [
  'set_apikey',
  'show_apikey',
  'Fred',
  'get_category',
  'get_category_children',
  'get_category_related',
  'get_category_related_tags',
  'get_category_series',
  'get_category_tags',
  'get_release',
  'get_release_dates',
  'get_release_related_tags',
  'get_release_series',
  'get_release_sources',
  'get_release_tables',
  'get_release_tags',
  'get_releases',
  'get_releases_dates',
  'get_series',
  'get_series_categories',
  'get_series_observations',
  'get_series_release',
  'get_series_search',
  'get_series_search_related_tags',
  'get_series_search_tags',
  'get_series_tags',
  'get_series_updates',
  'get_series_vintageupdates',
  'get_source',
  'get_source_releases',
  'get_sources',
  'get_tags',
  'get_related_tags',
  'get_tags_series',
  'test_all',
]