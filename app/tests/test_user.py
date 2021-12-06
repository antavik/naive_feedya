import datetime

from starlette.datastructures import Secret


def test_generate_token__no_input__token_exp(import_user):
    token, exp = import_user.generate_token()

    assert isinstance(token, Secret) and isinstance(exp, datetime.datetime)
    assert str(token)


def test_is_valid_credentials__valid_credentials__true(
        import_user_with_credential
):
    import_user, username, password = import_user_with_credential

    assert (
        import_user.is_valid_credentials(str(username), str(password)) is True
    )


def test_is_valid_credentials__invalid_credentials__false(
        import_user,
        fake_string
):
    assert (
        import_user.is_valid_credentials(fake_string, fake_string) is False
    )


def test_is_valid_token__valid_token__true(import_user_with_token):
    import_user, token, _ = import_user_with_token

    assert import_user.is_valid_token(token) is True


def test_is_valid_token__invalid_token__false(
        import_user,
        fake_token
):

    assert import_user.is_valid_token(fake_token) is False


def test_is_valid_token__expired_token__false(import_user_with_expired_token):
    import_user, token, _ = import_user_with_expired_token

    assert import_user.is_valid_token(token) is False


def test_get_expiration_date__no_input__expiration_date(
        import_user
):
    expiration = import_user._get_expiration_date()

    assert isinstance(expiration, datetime.datetime)
