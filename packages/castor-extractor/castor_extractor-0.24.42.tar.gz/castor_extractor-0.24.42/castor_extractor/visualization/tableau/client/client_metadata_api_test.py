import pytest

from .client_metadata_api import _TIMEOUT_MESSAGE, _check_errors, _deduplicate
from .errors import TableauApiError, TableauApiTimeout


def test__deduplicate():
    result_pages = iter(
        [
            [
                {"id": 1, "name": "workbook_1"},
                {"id": 2, "name": "workbook_2"},
            ],
            [
                {"id": 1, "name": "workbook_1"},
                {"id": 3, "name": "workbook_3"},
                {"id": 4, "name": "workbook_4"},
            ],
            [
                {"id": 4, "name": "workbook_4"},
                {"id": 5, "name": "workbook_5"},
                {"id": 5, "name": "workbook_5"},
                {"id": 5, "name": "workbook_5"},
            ],
            [
                {"id": 1, "name": "workbook_1"},
                {"id": 3, "name": "workbook_3"},
            ],
        ]
    )
    deduplicated = _deduplicate(result_pages)
    assert len(deduplicated) == 5
    deduplicated_keys = {item["id"] for item in deduplicated}
    assert deduplicated_keys == {1, 2, 3, 4, 5}


def _timeout_error():
    return {"message": _TIMEOUT_MESSAGE}


def _critical_error():
    return {
        "message": "critical error",
        "extensions": {"severity": "Error"},
    }


def _unknown_severity_error():
    return {
        "message": "unknown severity error",
        "extensions": {"severity": None},
    }


def _warning():
    return {
        "message": "critical error",
        "extensions": {"severity": "Warning"},
    }


def test__check_errors():
    answer = {"data": []}  # no errors
    assert _check_errors(answer) is None

    # only warnings
    answer = {
        "data": [],
        "errors": [
            _warning(),
            _warning(),
            _warning(),
        ],
    }
    assert _check_errors(answer) is None

    # timeout issues should be prio (because they can be retried)
    answer = {
        "data": [],
        "errors": [
            _warning(),
            _critical_error(),
            _timeout_error(),
            _warning(),
        ],
    }
    with pytest.raises(TableauApiTimeout):
        _check_errors(answer)

    # expect critical error
    answer = {
        "data": [],
        "errors": [
            _warning(),
            _warning(),
            _critical_error(),
        ],
    }
    with pytest.raises(TableauApiError):
        _check_errors(answer)

    # unknown severity is considered as critical
    answer = {
        "data": [],
        "errors": [
            _unknown_severity_error(),
            _warning(),
        ],
    }
    with pytest.raises(TableauApiError):
        _check_errors(answer)
