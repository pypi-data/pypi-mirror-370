import pytest
import json
import tempfile
from pathlib import Path as FSPath
from src.lunar_policy import ComponentData, Path, NoDataError


def assert_result(result, expected_value, expected_paths):
    assert result is not None
    assert result.value == expected_value
    assert result.paths == expected_paths


def assert_all_results(result, expected):
    assert result is not None
    assert len(result) == len(expected)
    for idx, (expected_value, expected_paths) in enumerate(expected):
        assert result[idx].value == expected_value
        assert result[idx].paths == expected_paths


class TestDataLoading():
    def test_from_component_json(self):
        component_json = {
            'string': 'hello world'
        }
        data = ComponentData.from_component_json(json.dumps(component_json))
        assert_result(
            data.get_merged(Path('.string')),
            'hello world',
            ['string']
        )
        assert_all_results(
            data.get_all(Path('.string')),
            [('hello world', ['string'])]
        )

    def test_from_json(self):
        test_data = {
            'bundle_info': {},
            'metadata_instances': [
                {
                    'payload': {
                        'string': 'hello world'
                    }
                }
            ],
            'merged_blob': {
                'string': 'hello world'
            }
        }
        data = ComponentData.from_json(json.dumps(test_data))
        assert_result(
            data.get_merged(Path('.string')),
            'hello world',
            ['string']
        )
        assert_all_results(
            data.get_all(Path('.string')),
            [('hello world', ['string'])]
        )

    def test_from_file(self):
        test_data = {
            'bundle_info': {},
            'metadata_instances': [
                {
                    'payload': {
                        'string': 'hello world'
                    }
                }
            ],
            'merged_blob': {
                'string': 'hello world'
            }
        }

        with tempfile.NamedTemporaryFile(
            'w+', delete=False, suffix='.json'
        ) as tmpfile:
            tmpfile.write(json.dumps(test_data))
            tmpfile.flush()
            tmp_path = FSPath(tmpfile.name)

        data = ComponentData.from_file(FSPath(tmp_path))
        assert_result(
            data.get_merged(Path('.string')),
            'hello world',
            ['string']
        )
        assert_all_results(
            data.get_all(Path('.string')),
            [('hello world', ['string'])]
        )


class TestGetMerged():
    @pytest.fixture
    def snippet_data(self):
        test_data = {
            'bundle_info': {},
            'metadata_instances': [],
            'merged_blob': {
                'string': 'hello world',
                'array': ['hello', 'world'],
                'object1': {'hello': 'world'},
                'object2': {'hello': 'moon'}
            }
        }
        return ComponentData.from_json(json.dumps(test_data))

    def test_get_single_value(self, snippet_data):
        result = snippet_data.get_merged(Path('.string'))
        assert_result(result, 'hello world', ['string'])

    def test_get_missing(self, snippet_data):
        with pytest.raises(NoDataError):
            snippet_data.get_merged(Path('.missing'))

    def test_get_missing_workflows_finished(self, snippet_data):
        snippet_data._data["bundle_info"]["workflows_finished"] = True
        with pytest.raises(ValueError):
            snippet_data.get_merged(Path('.missing'))

    def test_get_array(self, snippet_data):
        result = snippet_data.get_merged(Path('.array'))
        assert_result(result, ['hello', 'world'], ['array'])

    def test_get_array_index(self, snippet_data):
        result = snippet_data.get_merged(Path('.array[0]'))
        assert_result(result, 'hello', ['array.[0]'])

    def test_get_nested_object(self, snippet_data):
        result = snippet_data.get_merged(Path('.object1.hello'))
        assert_result(result, 'world', ['object1.hello'])

    def test_get_nested_object_missing(self, snippet_data):
        with pytest.raises(NoDataError):
            snippet_data.get_merged(
                Path('.object1.missing')
            )

    def test_get_nested_object_missing_workflows_finished(self, snippet_data):
        snippet_data._data["bundle_info"]["workflows_finished"] = True
        with pytest.raises(ValueError):
            snippet_data.get_merged(
                Path('.object1.missing')
            )

    def test_multi_match_array_index(self, snippet_data):
        result = snippet_data.get_merged(Path('.array[*]'))
        assert_result(
            result,
            ['hello', 'world'],
            ['array.[0]', 'array.[1]']
        )

    def test_multi_match_object_key(self, snippet_data):
        result = snippet_data.get_merged(Path('..hello'))
        assert_result(
            result,
            ['world', 'moon'],
            ['object1.hello', 'object2.hello']
        )


class TestGetAll():
    @pytest.fixture
    def snippet_data(self):
        test_data = {
            'bundle_info': {},
            'merged_blob': {},
            'metadata_instances': [
                {
                    'payload': {
                        'single': 'hello world',
                        'double': 'hello1',
                        'single_array': ['hello', 'world'],
                        'double_array': ['goodbye', 'moon'],
                        'single_object': {'hello': 'world'},
                        'double_object': {'hello': 'moon'}
                    }
                },
                {
                    'payload': {
                        'double': 'hello2',
                        'double_array': ['mars', 'i', 'guess'],
                        'double_object': {'hello': 'venus'}
                    }
                }
            ]
        }
        return ComponentData.from_json(json.dumps(test_data))

    def test_get_single_key_in_one_delta(self, snippet_data):
        result = snippet_data.get_all(Path('.single'))
        assert_all_results(result, [
            ('hello world', ['single'])
        ])

    def test_get_single_key_in_two_deltas(self, snippet_data):
        result = snippet_data.get_all(Path('.double'))
        assert_all_results(result, [
            ('hello2', ['double']),
            ('hello1', ['double'])
        ])

    def test_get_missing(self, snippet_data):
        with pytest.raises(NoDataError):
            snippet_data.get_all(Path('.missing'))

    def test_get_missing_workflows_finished(self, snippet_data):
        snippet_data._data["bundle_info"]["workflows_finished"] = True
        with pytest.raises(ValueError):
            snippet_data.get_all(Path('.missing'))

    def test_get_single_array(self, snippet_data):
        result = snippet_data.get_all(Path('.single_array'))
        assert_all_results(result, [
            (['hello', 'world'], ['single_array'])
        ])

    def test_get_single_array_index(self, snippet_data):
        result = snippet_data.get_all(Path('.single_array[0]'))
        assert_all_results(result, [
            ('hello', ['single_array.[0]'])
        ])

    def test_get_double_array(self, snippet_data):
        result = snippet_data.get_all(Path('.double_array'))
        assert_all_results(result, [
            (['mars', 'i', 'guess'], ['double_array']),
            (['goodbye', 'moon'], ['double_array'])
        ])

    def test_get_double_array_index(self, snippet_data):
        result = snippet_data.get_all(Path('.double_array[0]'))
        assert_all_results(result, [
            ('mars', ['double_array.[0]']),
            ('goodbye', ['double_array.[0]'])
        ])

    def test_get_double_array_index_some_out_of_bounds(self, snippet_data):
        result = snippet_data.get_all(Path('.double_array[2]'))
        assert_all_results(result, [
            ('guess', ['double_array.[2]'])
        ])

    def test_get_single_object(self, snippet_data):
        result = snippet_data.get_all(Path('.single_object'))
        assert_all_results(result, [
            ({'hello': 'world'}, ['single_object'])
        ])

    def test_get_double_object(self, snippet_data):
        result = snippet_data.get_all(Path('.double_object'))
        assert_all_results(result, [
            ({'hello': 'venus'}, ['double_object']),
            ({'hello': 'moon'}, ['double_object'])
        ])

    def test_get_single_object_key(self, snippet_data):
        result = snippet_data.get_all(
            Path('.single_object.hello')
        )
        assert_all_results(result, [
            ('world', ['single_object.hello'])
        ])

    def test_get_double_object_key(self, snippet_data):
        result = snippet_data.get_all(
            Path('.double_object.hello')
        )
        assert_all_results(result, [
            ('venus', ['double_object.hello']),
            ('moon', ['double_object.hello'])
        ])

    def test_get_single_object_key_missing(self, snippet_data):
        with pytest.raises(NoDataError):
            snippet_data.get_all(
                Path('.single_object.missing')
            )

    def test_get_single_object_key_missing_wflows_finished(self, snippet_data):
        snippet_data._data["bundle_info"]["workflows_finished"] = True
        with pytest.raises(ValueError):
            snippet_data.get_all(
                Path('.single_object.missing')
            )

    def test_get_double_object_key_missing(self, snippet_data):
        with pytest.raises(NoDataError):
            snippet_data.get_all(
                Path('.double_object.missing')
            )

    def test_get_double_object_key_missing_wflows_finished(self, snippet_data):
        snippet_data._data["bundle_info"]["workflows_finished"] = True
        with pytest.raises(ValueError):
            snippet_data.get_all(
                Path('.double_object.missing')
            )

    def test_multi_match_single_array_index(self, snippet_data):
        result = snippet_data.get_all(Path('.single_array[*]'))
        assert_all_results(result, [
            (['hello', 'world'], ['single_array.[0]', 'single_array.[1]'])
        ])

    def test_multi_match_double_array_index(self, snippet_data):
        result = snippet_data.get_all(Path('.double_array[*]'))
        assert_all_results(result, [
            (
                ['mars', 'i', 'guess'],
                ['double_array.[0]', 'double_array.[1]', 'double_array.[2]']
            ),
            (
                ['goodbye', 'moon'],
                ['double_array.[0]', 'double_array.[1]']
            )
        ])

    def test_multi_match_object_key(self, snippet_data):
        result = snippet_data.get_all(Path('..hello'))
        assert_all_results(result, [
            ('venus', ['double_object.hello']),
            (['world', 'moon'], ['single_object.hello', 'double_object.hello'])
        ])


class TestJsonPathExpression():
    def test_invalid_json_path(self):
        with pytest.raises(ValueError):
            Path('.[invalid')

    def test_invalid_snippet_data(self):
        with pytest.raises(ValueError):
            ComponentData({})

    def test_invalid_snippet_data_missing_merged_blob(self):
        with pytest.raises(ValueError):
            ComponentData({
                'metadata_instances': []
            })

    def test_invalid_snippet_data_missing_metadata_instances(self):
        with pytest.raises(ValueError):
            ComponentData({
                'merged_blob': {}
            })

    def test_pretty_print_paths(self):
        path = Path('.string')
        assert str(path) == '.string'
        assert repr(path) == '$.string'
        assert f"{path}" == ".string"
