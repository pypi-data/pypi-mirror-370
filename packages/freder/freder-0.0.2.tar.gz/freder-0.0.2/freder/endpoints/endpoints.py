ENDPOINTS = {
  'Categories': {
    'category': {
      'params': ['category_id', 'api_key', 'file_type']
    },
    'category/children': {
      'params': [
        'api_key', 'file_type', 'category_id',
        'realtime_start', 'realtime_end',
      ]
    },
    'category/related': {
      'params': [
        'api_key', 'file_type', 'category_id',
        'realtime_start', 'realtime_end',
      ]
    },
    'category/series': {
      'params': [
        'api_key', 'file_type', 'category_id',
        'realtime_start', 'realtime_end', 'limit',
        'offset', 'order_by', 'sort_order',
        'filter_variable', 'filter_value',
        'tag_names', 'exclude_tag_names',
      ]
    },
    'category/tags': {
      'params': [
        'api_key', 'file_type', 'category_id',
        'realtime_start', 'realtime_end', 'tag_names',
        'tag_group_id', 'search_text', 'limit',
        'offset', 'order_by', 'sort_order',
      ]
    },
    'category/related_tags': {
      'params': [
        'api_key', 'file_type', 'category_id',
        'realtime_start', 'realtime_end', 'tag_names',
        'exclude_tag_names', 'tag_group_id', 'search_text',
        'limit', 'offset', 'order_by', 'sort_order'
      ]
    },
  },
  'Releases': {
    'releases': {
      'params': [
        'api_key', 'file_type', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'order_by', 'sort_order',
      ]
    },
    'releases/dates': {
      'params': [
        'api_key', 'file_type', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'order_by', 'sort_order',
        'include_release_dates_with_no_data',
      ]
    },
    'release': {
      'params': [
        'api_key', 'file_type', 'release_id', 'realtime_start',
        'realtime_end',
      ]
    },
    'release/dates': {
      'params': [
        'api_key', 'file_type', 'release_id', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'sort_order', 'includes_release_dates_with_no_data',
      ]
    },
    'release/series': {
      'params': [
        'api_key', 'file_type', 'release_id', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'order_by', 'sort_order', 'filter_variable',
        'filter_value', 'tag_names', 'exclude_tag_names',
      ]
    },
    'release/sources': {
      'params': [
        'api_key', 'file_type', 'release_id', 'realtime_start', 'realtime_end'
      ]
    },
    'release/tags': {
      'params': [
        'api_key', 'file_type', 'release_id', 'realtime_start', 'realtime_end',
        'tag_names', 'tag_group_id', 'search_text', 'limit', 'offset',
        'order_by', 'sort_order',
      ]
    },
    'release/related_tags': {
      'params': [
        'api_key', 'file_type', 'release_id', 'realtime_start', 'realtime_end',
        'tag_names', 'exlude_tag_names', 'tag_group_id', 'search_text',
        'limit', 'offset', 'order_by', 'sort_order'
      ]
    },
    'release/tables': {
      'params': [
        'api_key', 'file_type', 'release_id', 'element_id', 'include_observation_values',
        'observation_date'
      ]
    },
  },
  'Series': {
    'series': {
      'params': [
        'api_key', 'file_type', 'series_id', 'realtime_start', 'realtime_end'
      ]
    },
    'series/categories': {
      'params': [
        'api_key', 'file_type', 'series_id', 'realtime_start', 'realtime_end'
      ]
    },
    'series/observations': {
      'params': [
        'api_key', 'file_type', 'series_id', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'sort_order', 'observation_start', 'observation_end',
        'units', 'frequency', 'aggregation_method', 'output_type', 'vintage_dates'
      ]
    },
    'series/release': {
      'params': [
        'api_key', 'file_type', 'series_id', 'realtime_start', 'realtime_end'
      ]
    },
    'series/search': {
      'params': [
        'api_key', 'file_type', 'search_text', 'search_type',
        'realtime_start', 'realtime_end', 'limit', 'offset',
        'order_by', 'sort_order', 'filter_variable', 'filter_value',
        'tag_names', 'exclude_tag_names',
      ]
    },
    'series/search/tags': {
      'params': [
        'api_key', 'file_type', 'series_search_text', 'realtime_start',
        'realtime_end', 'tag_names', 'tag_group_id', 'tag_search_text',
        'limit', 'offset', 'order_by', 'sort_order'
      ]
    },
    'series/search/related_tags': {
      'params': [
        'api_key', 'file_type', 'series_search_text', 'realtime_start',
        'realtime_end', 'tag_names', 'exclude_tag_names', 'tag_group_id',
        'tag_search_text', 'limit', 'offset', 'order_by', 'osrt_order',
      ]
    },
    'series/tags': {
      'params': [
        'api_key', 'file_type', 'series_id', 'realtime_start',
        'realtime_end', 'order_by', 'sort_order',
      ]
    },
    'series/updates': {
      'params': {
        'api_key', 'file_type', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'filter_value', 'start_time', 'end_time'
      }
    },
    'series/vintagedates': {
      'params': [
        'api_key', 'file_type', 'series_id', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'sort_order',
      ]
    },
  },
  'Sources': {
    'sources': {
      'params': [
        'api_key', 'file_type', 'realtime_start', 'realtime_end',
        'limit', 'offset', 'order_by', 'sort_order',
      ]
    },
    'source': {
      'params': [
        'api_key', 'file_type', 'source_id', 'realtime_start', 'realtime_end'
      ]
    },
  },
  'Tags': {
    'tags': {
      'params': [
        'api_key', 'file_type', 'realtime_start', 'realtime_end', 'tag_names',
        'tag_group_id', 'search_text', 'limit', 'offset', 'order_by', 'sort_order',
      ]
    },
    'related_tags': {
      'params': [
        'api_key', 'file_type', 'realtime_start', 'realtime_end', 'tag_names',
        'exclude_tag_names', 'tag_group_id', 'search_text', 'limit', 'offset',
        'order_by', 'sort_order',
      ]
    },
    'tags/series': {
      'params': [
        'api_key', 'file_type', 'tag_names', 'exclude_tag_names', 'realtime_start',
        'realtime_end', 'limit', 'offset', 'order_by', 'sort_order'
      ],
    },
  }
}