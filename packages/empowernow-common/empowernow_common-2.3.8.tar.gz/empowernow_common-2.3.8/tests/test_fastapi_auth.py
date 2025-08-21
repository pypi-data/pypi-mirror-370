import base64, json

import respx, httpx
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from empowernow_common.fastapi import build_auth_dependency
from empowernow_common.idp import IdPCatalogue
from empowernow_common.oauth.client import SecureOAuthConfig, HardenedOAuth


def _jwt(iss: str, sub: str = "user") -> str:
    h = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps({"iss": iss, "sub": sub}).encode()).rstrip(b"=").decode()
    return f"{h}.{p}."


def test_auth_dependency_success(tmp_path):
    # Prepare IdP YAML
    yaml_path = tmp_path / "idps.yaml"
    yaml_path.write_text(
        """
    idps:
      - name: example
        issuer: https://example.com/
        introspection_url: https://example.com/introspect
        client_id: c
        client_secret: s
    """
    )

    catalogue = IdPCatalogue(yaml_path)

    oauth_cfg = SecureOAuthConfig(
        client_id="c",
        client_secret="s",
        token_url="https://example.com/token",
        authorization_url="https://example.com/authorize",
        introspection_url="https://example.com/introspect",
    )
    oauth = HardenedOAuth(oauth_cfg)

    dep = build_auth_dependency(catalogue, oauth)

    app = FastAPI()

    @app.get("/")
    async def root(user=Depends(dep)):
        return {"uid": user["unique_id"]}

    token = _jwt("https://example.com/")

    with respx.mock(assert_all_called=True) as router:
        router.post("https://example.com/introspect/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "active": True,
                    "iss": "https://example.com/",
                    "sub": "user",
                    "exp": 9999999999,
                },
            )
        )

        client = TestClient(app)
        r = client.get("/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["uid"].startswith("auth:account:example:")
        # normalized claims attached
        assert r.json().get("normalized_claims") is None  # endpoint returns only uid, but state should have it 