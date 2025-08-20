from unittest.mock import patch

from liveramp_automation.helpers.file import FileHelper


def mocked_raise_KeyError(*args, **kwargs):
    raise KeyError("KeyError")


def mocked_raise_Exception(*args, **kwargs):
    raise Exception("Exception")


def test_read_init_file():
    file_name = "test.ini"
    ini_file = FileHelper.read_init_file("tests/resources/", file_name)
    assert ini_file


def test_read_json_report_file():
    file_path = "tests/resources/test.json"
    json_str = FileHelper.read_json_report(file_path)
    assert json_str


def test_load_env_yaml():
    file_prefix = "test"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str


def test_load_env_yaml_file_not_found():
    file_prefix = "test_not_found"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str is None


def test_load_env_yaml_parse_error():
    file_prefix = "test_parse_error"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str is None


# The following Unit test case is not working
def test_deal_testcase_json():
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_testcase_json(file_path)
    print(testcase)
    assert testcase


def test_deal_testcase_json_file_not_exist():
    file_path = "tests/resources/test_not_exist.json"
    testcase = FileHelper.read_testcase_json(file_path)
    assert testcase is None


def test_deal_testcase_json_key_not_found():
    file_path = "tests/resources/test_key_not_found.json"
    testcase = FileHelper.read_testcase_json(file_path)
    assert testcase is None


def test_deal_testcase_json_incorrect_format():
    file_path = "tests/resources/junit.xml"
    testcase = FileHelper.read_testcase_json(file_path)
    assert testcase is None


def test_read_junit_xml_report():
    file_path = "tests/resources/junit.xml"
    testcase = FileHelper.read_junit_xml_report(file_path)
    print(testcase)
    assert testcase


def test_read_junit_xml_report_not_exist():
    file_path = "junit.xml"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


def test_read_junit_xml_report_file_incorrect_format():
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


@patch('xml.etree.ElementTree.parse', side_effect=mocked_raise_Exception)
def test_read_junit_xml_report_raise_Exception(self):
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


@patch('xml.etree.ElementTree.parse', side_effect=mocked_raise_KeyError)
def test_read_junit_xml_report_raise_KeyError(self):
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


def test_read_json_report_file_not_exist():
    file_path = "tests/resources/test_not_exist.json"
    return_dict = FileHelper.read_json_report(file_path)
    assert return_dict == {}


def test_read_json_report_file_incorrect_format():
    file_path = "tests/resources/junit.xml"
    return_dict = FileHelper.read_json_report(file_path)
    assert return_dict == {}


def test_read_init_file_not_exist():
    file_name = "file_not_exist.ini"
    ini_file = FileHelper.read_init_file("tests/resources/", file_name)
    assert ini_file == {}


def test_read_init_file_incorrect_format():
    file_name = "test.csv"
    ini_file = FileHelper.read_init_file("tests/resources/", file_name)
    assert ini_file == {}


def test_files_under_folder_with_suffix_xlsx():
    path_string = "tests/resources/"
    file_list = FileHelper.files_under_folder_with_suffix_xlsx(path_string)
    assert file_list == ["test.xlsx"]


def test_files_under_folder_with_suffix_csv():
    path_string = "tests/resources/"
    file_list = FileHelper.files_under_folder_with_suffix_csv(path_string)
    assert file_list == ["test.csv"]
