import json
import string
import uuid
import random
import pandas
import pytest
import scoring_api

from pandas import DataFrame
from pathlib import Path
from models import *

APPROXIMATION_ALLOWED = 1e-3


class LocalTestContext(Model):
    dataset_id: str = None
    dataframe: DataFrame = None
    rows: int = None
    function: Dict = None
    template_id: str = None
    scored_dataset_id: str = None


@pytest.fixture(scope="module", autouse=True)
def share_and_clean_up_data() -> LocalTestContext:
    yield LocalTestContext()
    data = scoring_api.get_datasets_list()
    for item in data:
        if "Auto" in item.name:
            scoring_api.delete_dataset(item.dataset_id, expected_code=204)


@pytest.fixture(scope="module", autouse=True)
def prepare_dataset(share_and_clean_up_data: LocalTestContext):
    path = Path('data/scoring_100_with_meta.csv')
    filename = str(uuid.uuid4())
    response = scoring_api.upload_dataset(f"Auto-{filename}.csv", path)
    dataset = share_and_clean_up_data.dataset_id = response.result.dataset_id

    df = pandas.read_csv(path, sep='\t')  # read dataset
    desirability_function = json.loads(df[f"Column_2_logarithmic_parameter"].iloc[0])
    share_and_clean_up_data.function = DesirabilityFunction(**desirability_function)
    share_and_clean_up_data.dataframe = df
    share_and_clean_up_data.rows = df.shape[0]  # number of rows
    yield dataset
    scoring_api.delete_dataset(dataset, expected_code=204)


@pytest.fixture(scope="module", autouse=True)
def prepare_scored_dataset(share_and_clean_up_data: LocalTestContext):
    name = f"Auto_{''.join(random.choices(string.ascii_letters + string.digits, k=20))}"
    request = PostScoringTemplate(name=name, dataset_id=share_and_clean_up_data.dataset_id)
    template_data = scoring_api.scoring_template_post(request_body=request, expected_code=201)
    share_and_clean_up_data.template_id = template_data.created_id
    column = "Column_2"
    column_data = share_and_clean_up_data.dataframe.loc[:, f"{column}"]  # extract current column from dataframe
    property_body = RequestTemplateProperty(column_name=column,
                                            enabled_for_scoring=True,
                                            importance=1,
                                            desirability_function=share_and_clean_up_data.function
                                            )
    property_data = scoring_api.scoring_template_properties_post(property_body, template_data.created_id,
                                                                 expected_code=201)
    share_and_clean_up_data.scored_dataset_id = scoring_api.scored_dataset_post(
        share_and_clean_up_data.dataset_id, template_data.created_id, expected_code=201).created_id
    yield
    scoring_api.scored_dataset_delete(share_and_clean_up_data.scored_dataset_id, expected_code=204)
    scoring_api.scoring_template_properties_delete(template_data.created_id, property_data.created_id,
                                                   expected_code=204)
    scoring_api.scoring_template_delete(template_data.created_id, expected_code=204)


@pytest.mark.parametrize("per_page, order", [(25, "asc"), (25, "desc"), (50, "asc"), (50, "desc"),
                                             (100, "asc"), (100, "desc")])
def test_sort_result_model(share_and_clean_up_data: LocalTestContext, per_page, order):
    if share_and_clean_up_data.rows % per_page == 0:
        pages_num = share_and_clean_up_data.rows // per_page
    else:
        pages_num = share_and_clean_up_data.rows // per_page + 1
    page = random.randint(1, pages_num)
    column = "Column_2"

    response = scoring_api.get_dataset_result_model(dataset_id=share_and_clean_up_data.dataset_id, page=page,
                                                    per_page=per_page, sort=column, order=order)
    if order == "asc":
        rows = share_and_clean_up_data.dataframe.sort_values(column).iloc[(page*per_page - per_page):(page*per_page)]
    else:
        rows = share_and_clean_up_data.dataframe.sort_values(column, ascending=False).iloc[(page*per_page - per_page):
                                                                                   (page*per_page)]
    actual_rows = [float(row.value) for item in response.dataset.columns
                   if item.name == column for row in item.values]
    expected_rows = rows.loc[:, f"{column}"].to_list()  # extract current column from dataframe
    assert pytest.approx(actual_rows, APPROXIMATION_ALLOWED) == expected_rows, \
        "Different actual and expected rows order or number"


@pytest.mark.parametrize("per_page, order", [(25, "asc"), (25, "desc"), (50, "asc"), (50, "desc"),
                                             (100, "asc"), (100, "desc")])
def test_sort_by_scored_column(share_and_clean_up_data: LocalTestContext, per_page, order):
    if share_and_clean_up_data.rows % per_page == 0:
        pages_num = share_and_clean_up_data.rows // per_page
    else:
        pages_num = share_and_clean_up_data.rows // per_page + 1
    page = random.randint(1, pages_num)
    column = "Column_2_logarithmic"
    compare_column = "Column_2_unit_step"

    response = scoring_api.get_dataset_result_model(dataset_id=share_and_clean_up_data.dataset_id, page=page,
                                                    per_page=per_page, sort='Scored_column', order=order)
    if order == "asc":
        rows = share_and_clean_up_data.dataframe.sort_values(column).iloc[
               (page*per_page - per_page):(page*per_page)]
    else:
        rows = share_and_clean_up_data.dataframe.sort_values(column, ascending=False).iloc[
               (page*per_page - per_page):(page*per_page)]
    actual_column = response.scored.scored_column
    actual_rows = [round(float(item), 10) if item != 'nonquantifiable' else item
                   for item in actual_column]
    expected_rows = rows.loc[:, column].to_list()  # extract current column from dataframe
    actual_compare_rows = [float(row.value) for item in response.dataset.columns
                           if item.name == compare_column for row in item.values]
    expected_compare_rows = rows.loc[:, f"{compare_column}"].to_list()  # extract column to compare
    assert expected_rows == pytest.approx(actual_rows, APPROXIMATION_ALLOWED), \
        "Different actual and expected rows order or number"
    assert expected_compare_rows == pytest.approx(actual_compare_rows), \
        "Sorting is only for scored column, not for the whole dataset"
