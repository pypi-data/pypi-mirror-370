from ..endpoints import (
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


def test_all():
  r = get_category(category_id=0)
  print(r)
  r = get_category_children(
    category_id=0,
    realtime_start='2024-01-01',
    realtime_end='2025-06-30'
  )
  print(r)
  r = get_category_related(
    category_id=0,
    realtime_start='2024-01-01',
    realtime_end='2025-06-30',
  )
  print(r)
  r = get_category_related_tags(
    category_id=0,
    realtime_start='2020-01-01',
    tag_names='balance'
  )
  print(r)
  r = get_category_series(
    category_id=2,
    realtime_start='2024-01-01',
    realtime_end='2025-06-30',
    tag_names='balance'
  )
  print(r)
