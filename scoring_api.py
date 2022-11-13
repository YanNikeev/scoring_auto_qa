import requests
import time

from typing import Tuple
from json import JSONDecodeError
from pathlib import Path
from models import *
from variables import ENV, ACCESS_TOKEN, REFRESH_TOKEN


def send_request(url: str, method: str, query_params: dict = None,
                 body_parameters: Union[Dict, Tuple, List, BaseModel] = None, headers: dict = None, files: dict = None,
                 data: dict = None, expected_code: Union[str, int] = None, check_code=True, allow_redirects=True,
                 token: str = None) -> requests.Response:
    full_url = "{}{}".format(ENV, url)
    method_lower = method.lower()
    if token:
        request_headers = {'Authorization': token}
    elif "refresh" in full_url:
        request_headers = {'Authorization': REFRESH_TOKEN}
    else:
        request_headers = {'Authorization': ACCESS_TOKEN}
    if headers:
        request_headers.update(headers)
    if query_params:
        normalized_params = {item: query_params[item] for item in query_params if query_params[item] is not None}
    else:
        normalized_params = None
    request_parameters = {'url': full_url,
                          'params': normalized_params,
                          'headers': request_headers,
                          'allow_redirects': allow_redirects
                          }
    if files:
        request_parameters['files'] = files
    else:
        if isinstance(body_parameters, BaseModel):
            request_parameters['json'] = body_parameters.dict(by_alias=True, exclude_none=True)
        else:
            request_parameters['json'] = body_parameters
    if data:
        request_parameters['data'] = data

    response = requests.request(method_lower, **request_parameters)

    if check_code:
        if expected_code is not None:
            assert response.status_code == expected_code, f"Response code is not expected: " \
                                                          f"{response.status_code} != {expected_code}. {response.content}"
        else:
            assert response.status_code == requests.codes.ok, f"Response code is not expected: " \
                                                              f"{response.status_code} != {requests.codes.ok}. {response.content}"

    return response

# -------------------------
# AUTHORIZATION ENDPOINTS
# -------------------------


def authorization_me_get(token=None, expected_code=None) -> UserResponse:
    """
    Test User
    """
    url = f"/api/authorization/me"
    method = "get"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code, token=token)
    try:
        result_object = response.json()
        result_object = UserResponse(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def authorization_refresh_get(expected_code=None) -> RefreshResponse:
    """
    Refresh Jwt Token
    """
    url = f"/api/authorization/refresh"
    method = "post"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = RefreshResponse(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def authorization_name_patch(name, expected_code):
    """
    Rename User
    """
    url = f"/api/authorization/name"
    method = "patch"
    query = {"name": name}
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = UserResponse(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object

# ---------------------------
# UPLOAD AND TASKS ENDPOINTS
# ---------------------------


def upload_datasets_upload_params_get(filename: str, expected_code=None) -> UploadParams:
    """
    Dataset Upload Params
    """
    url = f"/api/upload/datasets/upload_params"
    method = "get"
    query = {"filename": filename}
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = UploadParams(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def upload_datasets_validate_post(request_body: ValidateDataset, expected_code=None) -> Task:
    """
    Dataset Validate
    """
    url = f"/api/upload/datasets/validate"
    method = "post"
    query = None
    body_parameters = request_body
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = Task(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def task_task_id_status_get(task_id: str, expected_code=None) -> Task:
    """
    Task Status
    """
    url = f"/api/task/{task_id}/status"
    method = "get"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = Task(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def task_task_id_result_get(task_id: str, expected_code=None) -> Task:
    """
    Task Result Status
    """
    url = f"/api/task/{task_id}/result"
    method = "get"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = Task(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def upload_dataset(filename: str, path_to_file: Path, timeout: int = 300) -> Task:
    """
    Upload dataset using new mechanism
    """
    upload_params = upload_datasets_upload_params_get(filename)

    with open(path_to_file, 'rb') as file:
        files = {'file': (filename, file, "text/csv")}
        response = requests.post(upload_params.data["url"], data=upload_params.data["fields"], files=files)
        assert response.status_code == 204, \
            f"Uploading file to bucket returned unexpected code: {response.content}"

    validate_dataset = ValidateDataset(filepath=upload_params.data["fields"]["key"])
    task = upload_datasets_validate_post(validate_dataset)
    task = task_task_id_status_get(task.id)

    wait_period = 0.5
    ticks_to_timeout = timeout / wait_period
    while task.status in {"PENDING", "STARTED"}:
        time.sleep(0.5)
        task = task_task_id_status_get(task.id)
        ticks_to_timeout -= 1
        if ticks_to_timeout == 0:
            raise Exception("Uploading reached timeout")
    task_result = task_task_id_result_get(task.id)
    return task_result

# ---------------------------
# DATASET ENDPOINTS
# ---------------------------


def get_datasets_list(limit: int=None, expected_code=None) -> List[DatasetExtendedCardOut]:
    """
    Datasets List
    """
    url = f"/api/datasets"
    method = "get"
    query = {"limit": limit}
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = [DatasetExtendedCardOut(**item) for item in result_object]
    except JSONDecodeError:
        result_object = response.content
    return result_object


def get_dataset_result_model(dataset_id: str, page: int = None, per_page: int = None, sort: str = None,
                             order: str = None, expected_code=None) -> ResultModel:
    """
    Get Dataset
    """
    url = f"/api/datasets/{dataset_id}/result_model"
    method = "get"
    query = {"page": page,
             "per_page": per_page,
             "sort": sort,
             "order": order}
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = ResultModel(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def delete_dataset(dataset_id: str, expected_code=None) -> Dict:
    """
    Dataset Delete
    """
    url = f"/api/datasets/{dataset_id}"
    method = "delete"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
    except JSONDecodeError:
        result_object = response.content
    return result_object


def restore_dataset(dataset_id: str, expected_code=None) -> Dict:
    """
    Restore Dataset
    """
    url = f"/api/datasets/{dataset_id}/restore"
    method = "post"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
    except JSONDecodeError:
        result_object = response.content
    return result_object

# ---------------------------
# SCORING ENDPOINTS
# ---------------------------


def scoring_template_post(request_body: PostScoringTemplate, expected_code=None) -> CreateResponse:
    """
    Add Scoring Template
    """
    url = f"/api/scoring"
    method = "post"
    query = None
    body_parameters = request_body
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = CreateResponse(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def scoring_template_delete(template_id: str, expected_code=None):
    """
    Delete Scoring Template
    """
    url = f"/api/scoring/{template_id}"
    method = "delete"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
    except JSONDecodeError:
        result_object = response.content
    return result_object


def scoring_template_properties_post(request_body: RequestTemplateProperty, template_id: str,
                                     expected_code=None) -> CreateResponse:
    """
    Add Template Property
    """
    url = f"/api/scoring/{template_id}/template_properties"
    method = "post"
    query = None
    body_parameters = request_body
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = CreateResponse(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def scoring_template_properties_delete(template_id: str, template_property_id: str, expected_code=None):
    """
    Delete Template Property
    """
    url = f"/api/scoring/{template_id}/template_properties/{template_property_id}"
    method = "delete"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
    except JSONDecodeError:
        result_object = response.content
    return result_object


def scored_dataset_post(dataset_id: str, template_id: str, expected_code=None) -> CreateResponse:
    """
    Add Scored Dataset
    """
    url = f"/api/scored_dataset"
    method = "post"
    query = {"dataset_id": dataset_id,
             "template_id": template_id}
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = CreateResponse(**result_object)
    except JSONDecodeError:
        result_object = response.content
    return result_object


def scored_dataset_delete(scored_dataset_id: str, expected_code=None):
    """
    Delete Scored Dataset
    """
    url = f"/api/scored_dataset/{scored_dataset_id}"
    method = "delete"
    query = None
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
    except JSONDecodeError:
        result_object = response.content
    return result_object


# ---------------------------
# USER FEEDBACK ENDPOINTS
# ---------------------------


def feedback_get(after: str, before: str, expected_code=None) -> Dict:
    """
    Get the list with users feedbacks
    after: date to filter feedbacks - include posted after this date (inclusive)
    before: date to filter feedbacks - include posted before this date (exclusive)
        date format: yyyy-mm-dd
    """
    url = f"/api/feedback/user-feedback"
    method = "get"
    query = {"after": after,
             "before": before}
    body_parameters = None
    file = None
    response = send_request(url, method, query, body_parameters, files=file, expected_code=expected_code)
    try:
        result_object = response.json()
        result_object = [UserFeedback(**item) for item in result_object]
    except JSONDecodeError:
        result_object = response.content
    return result_object
