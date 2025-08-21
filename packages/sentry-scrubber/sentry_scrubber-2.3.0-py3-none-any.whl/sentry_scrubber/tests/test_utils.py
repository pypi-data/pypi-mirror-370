import pytest

from utils import delete_item, distinct_by, extract_dict, get_first_item, get_last_item, get_value, \
    modify_value, order_by_utc_time


def test_first():
    assert get_first_item(None, '') == ''
    assert get_first_item([], '') == ''
    assert get_first_item(['some'], '') == 'some'
    assert get_first_item(['some', 'value'], '') == 'some'

    assert get_first_item((), '') == ''
    assert get_first_item(('some', 'value'), '') == 'some'

    assert get_first_item(None, None) is None


def test_last():
    assert get_last_item(None, '') == ''
    assert get_last_item([], '') == ''
    assert get_last_item(['some'], '') == 'some'
    assert get_last_item(['some', 'value'], '') == 'value'

    assert get_last_item((), '') == ''
    assert get_last_item(('some', 'value'), '') == 'value'

    assert get_last_item(None, None) is None


def test_delete():
    assert delete_item({}, None) == {}

    assert delete_item({'key': 'value'}, None) == {'key': 'value'}
    assert delete_item({'key': 'value'}, 'missed_key') == {'key': 'value'}
    assert delete_item({'key': 'value'}, 'key') == {}


def test_modify():
    assert modify_value(None, None, None) is None
    assert modify_value({}, None, None) == {}
    assert modify_value({}, '', None) == {}

    assert modify_value({}, 'key', lambda value: '') == {}
    assert modify_value({'a': 'b'}, 'key', lambda value: '') == {'a': 'b'}
    assert modify_value({'a': 'b', 'key': 'value'}, 'key', lambda value: '') == {'a': 'b', 'key': ''}


def test_safe_get():
    assert get_value(None, None, None) is None
    assert get_value(None, None, {}) == {}

    assert get_value(None, 'key', {}) == {}

    assert get_value({'key': 'value'}, 'key', {}) == 'value'
    assert get_value({'key': 'value'}, 'key1', {}) == {}


def test_distinct_none():
    # Test distinct_by with None
    assert distinct_by(None, lambda b: (b["timestamp"], b["message"])) is None


def test_distinct():
    # Test distinct_by with default getter
    values = [
        {'message': 'message 1', 'timestamp': 'timestamp 1', 'id': '1'},
        {'message': 'message 1', 'timestamp': 'timestamp 1', 'id': '2'},
        {'message': 'message 2', 'timestamp': 'timestamp 2', 'id': '3'}
    ]

    expected = [
        {'message': 'message 1', 'timestamp': 'timestamp 1', 'id': '1'},
        {'message': 'message 2', 'timestamp': 'timestamp 2', 'id': '3'}
    ]
    assert distinct_by(values, lambda b: (b["timestamp"], b["message"])) == expected


def test_distinct_key_error():
    # Test distinct_by with missing key in getter
    values = [
        {'message': 'message 1', },
    ]
    with pytest.raises(KeyError):
        distinct_by(values, lambda b: (b["timestamp"], b["message"]))


def test_distinct_none_in_list():
    # Test distinct_by with None in list
    values = [None]
    with pytest.raises(TypeError):
        distinct_by(values, lambda b: (b["timestamp"], b["message"]))


FORMATTED_VERSIONS = [
    (None, None),
    ('', ''),
    ('7.6.0', '7.6.0'),
    ('7.6.0-GIT', 'dev'),  # version from developers machines
    ('7.7.1-17-gcb73f7baa', '7.7.1'),  # version from deployment tester
    ('7.7.1-RC1-10-abcd', '7.7.1-RC1'),  # release candidate
    ('7.7.1-exp1-1-abcd ', '7.7.1-exp1'),  # experimental versions
    ('7.7.1-someresearchtopic-7-abcd ', '7.7.1-someresearchtopic'),
]


def test_extract_dict():
    assert not extract_dict(None, None)

    assert extract_dict({}, '') == {}
    assert extract_dict({'k': 'v', 'k1': 'v1'}, r'\w$') == {'k': 'v'}


OBFUSCATED_STRINGS = [
    ('', 'dress'),
    ('any', 'challenge'),
    ('string', 'quality'),
]


def test_order_by_utc_time():
    # Test order by timestamp
    breadcrumbs = [
        {
            "timestamp": "2016-04-20T20:55:53.887Z",
            "message": "3",
        },
        {
            "timestamp": "2016-04-20T20:55:53.845Z",
            "message": "1",
        },
        {
            "timestamp": "2016-04-20T20:55:53.847Z",
            "message": "2",
        },
    ]
    ordered_breadcrumbs = order_by_utc_time(breadcrumbs)
    messages = [d['message'] for d in ordered_breadcrumbs]
    assert messages == ['1', '2', '3']


def test_order_by_utc_time_empty_breadcrumbs():
    # Test empty breadcrumbs
    assert not order_by_utc_time(None)
