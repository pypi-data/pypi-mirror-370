import respx, httpx
from empowernow_common.oauth.sync import SyncOAuth
from empowernow_common.oauth.client import SecureOAuthConfig


def test_sync_get_token():
    token_url = "https://auth.example.com/token"

    with respx.mock(assert_all_called=True) as router:
        router.post(token_url + "/").mock(return_value=httpx.Response(200, json={"access_token": "abc", "expires_in": 3600}))

        cfg = SecureOAuthConfig(
            client_id="cli",
            client_secret="sec",
            token_url=token_url,
            authorization_url="https://auth.example.com/authorize",
        )
        oauth = SyncOAuth(cfg)
        token = oauth.get_token()
        assert token.access_token == "abc"


def test_secure_token_helper():
    token_url = "https://auth.example.com/token"

    with respx.mock(assert_all_called=True) as router:
        router.post(token_url + "/").mock(return_value=httpx.Response(200, json={"access_token": "xyz", "expires_in": 3600}))

        from empowernow_common import secure_token

        token = secure_token(
            client_id="cli",
            client_secret="sec",
            token_url=token_url,
            authorization_url="https://auth.example.com/authorize",
        )

        assert token.access_token == "xyz" 