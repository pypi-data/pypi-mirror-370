from empowernow_common.idp import IdPCatalogue, IdPConfig


def test_longest_prefix_match(tmp_path):
    yaml_text = """
idps:
  - name: a
    issuer: https://example.com/
    introspection_url: https://example.com/introspect
    client_id: x
    client_secret: y
  - name: a-sub
    issuer: https://example.com/sub
    introspection_url: https://example.com/sub/introspect
    client_id: x
    client_secret: y
"""
    p = tmp_path / "idps.yaml"
    p.write_text(yaml_text)

    cat = IdPCatalogue(p)
    idp = cat.for_issuer("https://example.com/sub/path")
    assert idp is not None
    assert idp.name == "a-sub" 