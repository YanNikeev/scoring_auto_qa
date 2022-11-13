import uuid
import pytest
import scoring_api

# TODO: tests with empty/invalid tokens


def test_user_info():
    scoring_api.authorization_me_get()


def test_refresh_token():
    response = scoring_api.authorization_refresh_get()
    new_token = f"Bearer {response.access_token}"
    scoring_api.authorization_me_get(new_token)


@pytest.mark.parametrize("name", ["", "_", "user#", "user-имя", f"Auto-renamed-{uuid.uuid4()}"],
                         ids=["Empty name", "Only one symbol", "Invalid character", "Invalid letter",
                              "Too long name size"])
def test_invalid_rename_user(name):
    scoring_api.authorization_name_patch(name, expected_code=400)


def test_rename_user():
    new_name = f"{uuid.uuid4()}"[:30]
    scoring_api.authorization_name_patch(new_name, expected_code=200)
    user_info = scoring_api.authorization_me_get()
    assert user_info.name == new_name, f"User name is not correct: {new_name} != {user_info.name}"
