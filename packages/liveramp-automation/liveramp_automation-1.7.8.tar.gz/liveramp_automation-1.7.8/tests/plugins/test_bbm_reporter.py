import pytest
from unittest.mock import MagicMock, patch
from liveramp_automation.plugins.bbm_reporter import BBMReporter


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.getoption.side_effect = lambda opt: (
        "test_project"
        if opt == "--bbm-bigquery-project-id"
        else "test_dataset"
        if opt == "--bbm-bigquery-dataset-id"
        else "round_table"
        if opt == "--bbm-bigquery-round-table"
        else "feature_table"
        if opt == "--bbm-bigquery-feature-table"
        else "scenario_table"
        if opt == "--bbm-bigquery-scenario-table"
        else "step_table"
        if opt == "--bbm-bigquery-step-table"
        else "test_env"
        if opt == "--bbm-test-env"
        else "test_product"
        if opt == "--bbm-test-product"
        else "test_bucket"
        if opt == "--bbm-bucket-name"
        else "test_reports"
        if opt == "--bbm-report-folder"
        else "test_path"
        if opt == "--bbm-bucket-path-name"
        else None
    )
    return config


@pytest.fixture
def reporter(mock_config):
    bbm = BBMReporter(mock_config)
    bbm.env = "test_env"
    bbm.product = "test_product"
    return bbm


def test_insert_into_bigquery_success(reporter):
    with patch("liveramp_automation.plugins.bbm_reporter.bigquery.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.get_table.return_value = "table_ref"
        mock_instance.insert_rows.return_value = []
        reporter.insert_into_bigquery([{"foo": "bar"}], "table_name")
        mock_instance.insert_rows.assert_called_once()


def test_insert_into_bigquery_failure(reporter):
    with patch("liveramp_automation.plugins.bbm_reporter.bigquery.Client") as mock_client, \
            patch("liveramp_automation.plugins.bbm_reporter.Logger") as mock_logger:
        mock_instance = mock_client.return_value
        mock_instance.get_table.return_value = "table_ref"
        mock_instance.insert_rows.return_value = ["error"]
        reporter.insert_into_bigquery([{"foo": "bar"}], "table_name")
        mock_logger.error.assert_called_once()


def test_build_scenario_row(reporter):
    scenario = {
        "name": "Scenario 1",
        "description": "desc",
        "line_number": 10,
        "keyword": "Scenario",
        "tags": ["tag1", "tag2"]
    }
    row = reporter._build_scenario_row(scenario, "sid", "test_name")
    assert row["scenario_name"] == "Scenario 1"
    assert row["scenario_tags"] == "tag1,tag2"


def test_build_step_rows(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": 1, "duration": 1, "location": "loc1"},
        {"name": "step2", "keyword": "When", "line_number": 2, "duration": 2, "location": "loc2", "failed": True}
    ]
    report = MagicMock()
    report.longreprtext = "error details"
    rows = reporter._build_step_rows(steps, report)
    assert len(rows) == 2
    assert rows[1]["step_status"] == "failed"
    assert rows[1]["step_error_message"] == "error details"


def test_build_feature_row_new_and_existing(reporter):
    feature = {"rel_filename": "file.feature",
               "name": "Feature", "description":
                   "desc", "line_number": 5,
               "keyword": "Feature"}
    item = MagicMock()
    item.parent.name = "parent.py"
    scenario_id = "sid"
    reporter._build_feature_row(feature, item, scenario_id)
    assert len(reporter.feature_map) == 1
    # Call again to test existing feature
    reporter._build_feature_row(feature, item, "sid2")
    key = "parent_file.feature"
    assert len(reporter.feature_map[key]["feature_scenarios"]) == 2


def test_update_features_with_scenario_ids(reporter):
    reporter.feature_map = {
        "k1": {"feature_scenarios": ["s1", "s2"], "id": "id1"},
        "k2": {"feature_scenarios": ["s3"], "id": "id2"},
    }
    rows = reporter.update_features_with_scenario_ids()
    assert rows[0]["feature_scenarios"] == "s1,s2"
    assert rows[1]["feature_scenarios"] == "s3"


def test_build_round_row(reporter):
    features = [{"id": "f1"}, {"id": "f2"}]
    scenarios = [1, 2, 3]
    row = reporter._build_round_row(features, scenarios, 1, "passed")
    assert row["round_feature_ids"] == "f1,f2"
    assert row["round_scenario_count"] == 3
    assert row["round_execution_result"] == "passed"


def test_upload_artifacts_to_gcs_bucket(reporter):
    with patch("liveramp_automation.plugins.bbm_reporter.BucketHelper") as mock_helper:
        instance = mock_helper.return_value
        reporter.upload_artifacts_to_gcs_bucket()
        instance.upload_file.assert_called_once()


def test_pytest_sessionfinish(reporter):
    with patch.object(reporter, "update_features_with_scenario_ids",
                      return_value=[{"id": "f1", "feature_scenarios": "s1"}]), \
            patch.object(reporter, "insert_into_bigquery") as mock_insert, \
            patch.object(reporter, "upload_artifacts_to_gcs_bucket") as mock_upload:
        reporter.scenario_rows = [{"id": "s1"}]
        reporter.step_rows = [{"id": "step1"}]
        session = MagicMock()
        session.testsfailed = 0
        reporter.pytest_sessionfinish(session)
        assert mock_insert.call_count == 4
        mock_upload.assert_called_once()
