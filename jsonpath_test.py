import json
from dictpath_main import get_dict_item, update_dict_element, write_new_dict_element
from dictpath_utils import validate_dict_path
import pytest

# assumes the current working directory is the root of the project
with open('./tests/data.json', 'r') as f:
    TEST_DATA = json.load(f)


def test_get_present_item():
    path = '$.Friends[?Name="Bill"].CanThisFriendLiftMe'
    expected_result = True
    assert get_dict_item(TEST_DATA, path) == expected_result, f'Did not find {str(expected_result)} at {path}'


def test_get_missing_item():
    path = '$.Friends[?Name="Bob"].CanThisFriendLiftMe'
    expected_result = None
    assert get_dict_item(TEST_DATA, path) == expected_result, f'Did not find {str(expected_result)} at {path}'


def test_update_present_item():
    path = '$.Friends[?Name="Sue"].Pets[?Name="Whiskers"].Friendly'
    value = True
    update_dict_element(TEST_DATA, path, value)
    assert get_dict_item(TEST_DATA, path) == value, f'The value at {path} is not equal to {value}'


def test_update_missing_item():
    path = '$.Friends[?Name="Sue"].Pets[?Name="Spot"].Friendly'
    value = True
    with pytest.raises(Exception):
        update_dict_element(TEST_DATA, path, value)


def test_write_field_at_valid_path():
    path = '$.Friends[?Name="Sue"].Pets[?Name="Whiskers"]'
    new_field_name = 'Eats'
    value = 'Mice'
    write_new_dict_element(TEST_DATA, path, value, new_field_name)
    assert get_dict_item(TEST_DATA, path + '.Eats') == 'Mice', f'The value at {path}.Eats is not Mice'


def test_write_array_at_valid_path():
    path = '$'
    new_array_name = 'Enemies'
    value = []
    write_new_dict_element(TEST_DATA, path, value, new_array_name)
    assert get_dict_item(TEST_DATA, path + '.Enemies') == [], f'The value at {path}.Enemies is not an empty array'


def test_add_item_to_array():
    path = '$.Enemies'
    value = {'Name': 'Donald', 'IsJerk': True}
    write_new_dict_element(TEST_DATA, path, value)
    assert get_dict_item(TEST_DATA,
                         path + '[?Name="Donald"].IsJerk') == True, f'The value at {path}+[?Name="Donald"].IsJerk is not True'


def test_add_item_at_invalid_path():
    path = '$.Enemies[?Name="Bill"]'
    new_field_name = 'HostilitiesBegan'
    value = '2022-04-11'
    with pytest.raises(Exception):
        write_new_dict_element(TEST_DATA, path, value, new_field_name)


def test_multiple_criteria():
    path = '$.Friends[?Name="Bill"].Pets[?Name="Spot"&&Species="Dog"].Name'
    value = 'Spot'
    assert get_dict_item(TEST_DATA, path) == value, f'The value at {path} is not {value}.'


def test_json_path_validation():
    good_paths = ['$.Things.Stuff', '$.Things[?Name="Foo"].Stuff', '$.Things[?FirstName="Foo" && LastName="Bar"]']
    bad_paths = ['$.[?Name="Foo"]', '$.[0]', '$.Things[?Name=Foo]', '$.Things[Name="Foo"]',
                 '$.Things[?FirstName="Foo"&LastName="Bar"]']
    for path in good_paths:
        assert validate_dict_path(path)[0] == True
    for path in bad_paths:
        assert validate_dict_path(path)[0] == False


def test_find_value_at_invalid_path():
    try:
        item = get_dict_item(TEST_DATA, '$.Friends.Name=Bill')
        print(item)
        if item:
            assert False
    except Exception as e:
        assert str(e) == 'Syntax errors were found in the following parts of the supplied JSON path: Name=Bill'