"""Claims normalisation utilities.

Turn heterogeneous IdP claim layouts into a uniform structure:

    {
        "roles": [...],
        "permissions": [...],
    }

Usage
-----
>>> from empowernow_common.oauth.claims import ClaimsMapper
>>> out = ClaimsMapper.normalize(jwt_claims)
"""

from __future__ import annotations

from typing import Any, Dict, List, Iterable, Optional, Set

from ..idp import IdPConfig

__all__ = ["ClaimsMapper"]


class ClaimsMapper:
    """Static helpers for extracting roles & permissions from JWT claims."""

    # Default claim paths looked up for roles / perms
    _DEFAULT_PATHS = {
        "roles": [
            "roles",
            "realm_access.roles",
            "app_roles",
            "groups",
            "wids",  # Azure AD role IDs
        ],
        "permissions": [
            "permissions",
            "scope",  # Auth0 style space-separated list
            "scp",  # MS Graph delegated permissions
        ],
    }

    @classmethod
    def normalize(
        cls, claims: Dict[str, Any], idp_cfg: Optional[IdPConfig] = None
    ) -> Dict[str, List[str]]:
        """Return dict with *roles* and *permissions* deduplicated & sorted."""

        paths = cls._DEFAULT_PATHS.copy()

        # Custom mapping from catalogue
        if idp_cfg and idp_cfg.claims_mapping:
            for k in ("roles", "permissions"):
                custom = (
                    idp_cfg.claims_mapping.get(k) if idp_cfg.claims_mapping else None
                )
                if custom and isinstance(custom, dict) and "paths" in custom:
                    paths[k] = custom["paths"] + paths[k]

        roles = set()
        perms = set()

        # walk configured paths
        for path in paths["roles"]:
            roles.update(_extract_values(claims, path))
        for path in paths["permissions"]:
            perms.update(
                _extract_values(claims, path, is_scope_field=(path in {"scope", "scp"}))
            )

        # wildcard *_roles / *_permissions catcher
        for key, value in claims.items():
            if key.endswith("_roles"):
                roles.update(_to_list(value))
            if key.endswith("_permissions"):
                perms.update(_to_list(value))

        return {
            "roles": sorted(roles),
            "permissions": sorted(perms),
        }


# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------


def _to_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        # space-separated scope list
        return value.split()
    if isinstance(value, (list, set, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def _extract_values(
    claims: Dict[str, Any], path: str, *, is_scope_field: bool = False
) -> Set[str]:
    # Traverse dotted path
    parts = path.split(".")
    current: Any = claims
    for p in parts:
        if not isinstance(current, dict) or p not in current:
            return set()
        current = current[p]

    values = _to_list(current)
    if is_scope_field and len(values) == 1 and " " in values[0]:
        # scope string already handled in _to_list, nothing extra
        pass
    return set(values)
