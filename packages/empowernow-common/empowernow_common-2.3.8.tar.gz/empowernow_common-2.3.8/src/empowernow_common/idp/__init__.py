"""Identity-Provider catalogue utilities.

The catalogue allows multi-tenant services to look up per-issuer settings
(e.g. client credentials or claim mappings) from a YAML file at runtime.

Example YAML (see *docs/samples/idp-catalogue.yaml*):

```yaml
idps:
  - name: acme-okta
    issuer: https://acme.okta.com/oauth2/default
    introspection_url: https://acme.okta.com/oauth2/default/v1/introspect
    client_id: srv-acme
    client_secret: s3cr3t
    claims_mapping:
      roles: paths: ["realm_access.roles", "roles"]
  - name: azure-ad
    issuer: https://login.microsoftonline.com/<tenant>/v2.0
    introspection_url: https://login.microsoftonline.com/<tenant>/introspect
    client_id: srv-azure
    client_secret: s3cr3t
```
"""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover – optional dep
    yaml = None  # type: ignore


@dataclass(slots=True)
class IdPConfig:
    """Single Identity-Provider configuration entry."""

    name: str
    issuer: str
    introspection_url: str
    client_id: str
    client_secret: str
    claims_mapping: Optional[Dict[str, Any]] = None


class IdPCatalogue:
    """Load & query an IdP YAML catalogue.

    Parameters
    ----------
    path:
        Path to the YAML file.  Environment variables inside the path are
        expanded (e.g. ``"$HOME/idps.yaml"``).
    auto_reload:
        If *True*, the file's *mtime* is checked on every lookup and the file
        is re-loaded automatically when it changes.  Cheap `stat()` call; safe
        for hot-reload in dev containers.
    """

    def __init__(self, path: str | Path, *, auto_reload: bool = False):
        self._path = Path(os.path.expandvars(path)).expanduser().resolve()
        self._auto_reload = auto_reload
        self._idps: List[IdPConfig] = []
        self._mtime = 0.0

        self._load()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def for_issuer(self, issuer: str) -> Optional[IdPConfig]:
        """Return the IdP whose ``issuer`` is the longest prefix of *issuer*."""

        if self._auto_reload:
            self._maybe_reload()

        best: Optional[IdPConfig] = None
        for idp in self._idps:
            if issuer.startswith(idp.issuer) and (
                best is None or len(idp.issuer) > len(best.issuer)
            ):
                best = idp
        return best

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _maybe_reload(self) -> None:
        try:
            m = self._path.stat().st_mtime
            if m != self._mtime:
                self._load()
        except FileNotFoundError:
            # Catalogue deleted – keep old copy
            pass

    def _load(self) -> None:
        if yaml is None:
            raise ImportError("PyYAML required: pip install pyyaml")

        raw = yaml.safe_load(self._path.read_text("utf-8")) or {}
        entries = raw.get("idps", [])
        self._idps = [IdPConfig(**entry) for entry in entries]
        self._mtime = self._path.stat().st_mtime

    # Convenience len / iter implementation
    def __len__(self) -> int:  # noqa: D401 – simple wrapper
        return len(self._idps)

    def __iter__(self):  # noqa: D401
        return iter(self._idps)


__all__ = ["IdPConfig", "IdPCatalogue"]
