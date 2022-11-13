import uuid
import pytest
import scoring_api

from typing import Union
from pathlib import Path
from models import DatasetExtendedCardOut, Model


class LocalTestContext(Model):
    created_dataset: Union[DatasetExtendedCardOut, None]


@pytest.fixture(scope="module", autouse=True)
def share_and_clean_up_data() -> LocalTestContext:
    yield LocalTestContext()
    data = scoring_api.get_datasets_list()
    for item in data:
        if "Auto" in item.name:
            scoring_api.delete_dataset(item.dataset_id, expected_code=204)


def test_file_upload(share_and_clean_up_data: LocalTestContext):
    filename = str(uuid.uuid4())
    result = scoring_api.upload_dataset(f"Auto-{filename}.csv", Path('data/20_20.csv'))
    share_and_clean_up_data.created_dataset = result.result
    assert result.result.name == f"Auto-{filename}.csv", f"Filename doesn't match with the expected one. " \
                                                         f"Expected: f'Auto-{filename}.csv', " \
                                                         f"actual: {result.result.name}"


def test_get_dataset(share_and_clean_up_data: LocalTestContext):
    expected_dataset = share_and_clean_up_data.created_dataset
    result_model = scoring_api.get_dataset_result_model(expected_dataset.dataset_id, page=1, per_page=25,
                                                        sort="", order="")


def test_file_get_in_the_list(share_and_clean_up_data: LocalTestContext):
    expected_dataset = share_and_clean_up_data.created_dataset
    datasets_list = scoring_api.get_datasets_list()
    actual_dataset = next((dataset for dataset in datasets_list
                           if dataset.dataset_id == expected_dataset.dataset_id), None)
    assert actual_dataset, f"Created dataset {expected_dataset.dataset_id} isn't presented in response: {datasets_list}"


def test_file_delete(share_and_clean_up_data: LocalTestContext):
    expected_dataset = share_and_clean_up_data.created_dataset
    scoring_api.delete_dataset(expected_dataset.dataset_id, expected_code=204)
    datasets_list = scoring_api.get_datasets_list()
    actual_dataset = next((dataset for dataset in datasets_list
                           if dataset.dataset_id == expected_dataset.dataset_id), None)
    assert not actual_dataset, f"Created dataset {expected_dataset.dataset_id} is presented in response: {datasets_list}"


def test_file_restore(share_and_clean_up_data: LocalTestContext):
    expected_dataset = share_and_clean_up_data.created_dataset
    scoring_api.restore_dataset(expected_dataset.dataset_id, expected_code=200)
    datasets_list = scoring_api.get_datasets_list()
    actual_dataset = next((dataset for dataset in datasets_list
                           if dataset.dataset_id == expected_dataset.dataset_id), None)
    assert actual_dataset, f"Created dataset {expected_dataset.dataset_id} is presented in response: {datasets_list}"