from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_roundtrip():
    h = hash_password("SuperSecretPassword12!")
    assert verify_password("SuperSecretPassword12!", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token("user-uuid-123")
    assert decode_token(token) == "user-uuid-123"
