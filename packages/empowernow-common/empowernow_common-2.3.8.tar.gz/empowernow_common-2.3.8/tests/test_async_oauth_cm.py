import anyio
import httpx
import respx

from empowernow_common import async_oauth


async def _fetch():
    token_url = "https://auth.example.com/token"
    with respx.mock(assert_all_called=True) as route:
        route.post(token_url + "/").mock(return_value=httpx.Response(200, json={"access_token": "def", "expires_in": 30}))

        async with async_oauth(
            client_id="c",
            client_secret="s",
            token_url=token_url,
            authorization_url="https://auth.example.com/authorize",
        ) as oauth:
            tok = await oauth.get_token()
            assert tok.access_token == "def"

        # After context exit the http client should be closed
        # (accessing protected member only in test)
        assert oauth._http_client is None or oauth._http_client.is_closed


def test_async_oauth_cm():
    anyio.run(_fetch) 