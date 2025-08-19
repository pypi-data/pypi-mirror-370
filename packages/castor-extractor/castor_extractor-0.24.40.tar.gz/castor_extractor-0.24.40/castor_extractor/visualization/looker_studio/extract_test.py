import pytest

from .extract import _validate_user_emails


def test__validate_user_emails():
    with pytest.raises(TypeError):
        _validate_user_emails("toto@tata.com")

    with pytest.raises(TypeError):
        _validate_user_emails({"not": "the", "right": "format"})

    with pytest.raises(ValueError):
        _validate_user_emails([])

    with pytest.raises(TypeError):
        _validate_user_emails([1, 2, 3, 4])

    _validate_user_emails(["admin@toto.com", "tata@toto.com"])
