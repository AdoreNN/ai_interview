from datetime import timedelta
import uuid

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    normalize_email,
    verify_password,
)


def test_email_normalization():
    assert normalize_email("  User.Name@Example.COM ") == "user.name@example.com"


def test_password_hashing_and_verification():
    encoded = hash_password("correct horse battery staple")
    assert encoded != "correct horse battery staple"
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("incorrect password", encoded)


def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    assert decode_access_token(create_access_token(user_id)) == user_id


def test_invalid_access_token_is_rejected():
    with pytest.raises(ValueError):
        decode_access_token("not-a-jwt")


def test_expired_access_token_is_rejected():
    token = create_access_token(uuid.uuid4(), expires_delta=timedelta(seconds=-1))
    with pytest.raises(ValueError):
        decode_access_token(token)

