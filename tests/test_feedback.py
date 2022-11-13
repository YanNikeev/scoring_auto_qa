import scoring_api

from datetime import date


def test_get_feedback():
    response = scoring_api.feedback_get(f"{date(2022, 1, 1)}", f"{date.today()}")
