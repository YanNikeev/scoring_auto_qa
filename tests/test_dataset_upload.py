import uuid
import pytest
import scoring_api

from pathlib import Path

# TODO: tests with invalid file format, invalid delimiter, too large size


@pytest.fixture(scope="module", autouse=True)
def clean_up_datasets():
    yield
    data = scoring_api.get_datasets_list()
    for item in data:
        if "Auto" in item.name:
            scoring_api.delete_dataset(item.dataset_id, expected_code=204)


def test_file_upload():
    filename = str(uuid.uuid4())
    result = scoring_api.upload_dataset(f"Auto-{filename}.csv", Path('data/20_20.csv'))
    assert result.result.name == f"Auto-{filename}.csv", f"Filename doesn't match with the expected one. " \
                                                            f"Expected: f'Auto-{filename}.csv', " \
                                                            f"actual: {result.result.name}"


@pytest.mark.parametrize("filename", [".csv", "_.csv", "20-20@data.csv", "20-20дата.csv", f"verylongnam{'e'*90}.csv"],
                         ids=["Empty name", "Only one symbol", "Invalid character", "Invalid letter",
                              "Too long name size"]
                         )
def test_file_upload_invalid_name(filename):
    response = scoring_api.upload_datasets_upload_params_get(filename, expected_code=400)
