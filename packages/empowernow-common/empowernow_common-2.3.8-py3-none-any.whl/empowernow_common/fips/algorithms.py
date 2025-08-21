"""
FIPS 140-3 Approved Algorithms

This module defines the FIPS-approved cryptographic algorithms based on the
proven implementation from the EmpowerNow IdP.

References:
- NIST SP 800-131A Rev. 2
- NIST SP 800-186
- RFC 9449 (DPoP)
"""

from typing import Dict, List, Set
from cryptography.hazmat.primitives.asymmetric import ec


class FIPSAlgorithms:
    """
    FIPS 140-3 approved algorithms registry.

    Based on the production-tested implementation from EmpowerNow IdP.
    """

    # FIPS-approved algorithms for different operations
    # These are the exact algorithms validated in the IdP
    APPROVED_ALGORITHMS: Dict[str, List[str]] = {
        "jwt_signing": [
            "RS256",
            "RS384",
            "RS512",  # RSASSA-PKCS1-v1_5 with SHA-256/384/512
            "PS256",
            "PS384",
            "PS512",  # RSASSA-PSS with SHA-256/384/512
            "ES256",
            "ES384",
            "ES512",  # ECDSA with SHA-256/384/512
        ],
        "dpop_signing": [
            "RS256",
            "PS256",
            "ES256",  # RFC 9449 + FIPS subset
        ],
        "symmetric": [
            "AES-256-GCM",
            "AES-192-GCM",
            "AES-128-GCM",
        ],
        "hash": [
            "SHA-256",
            "SHA-384",
            "SHA-512",
        ],
        "mac": [
            "HMAC-SHA256",
            "HMAC-SHA384",
            "HMAC-SHA512",
        ],
    }

    # FIPS-approved elliptic curves (NIST SP 800-186)
    APPROVED_CURVES: Dict[str, str] = {
        "P-256": "secp256r1",
        "P-384": "secp384r1",
        "P-521": "secp521r1",
    }

    # FIPS minimum key sizes (NIST SP 800-131A Rev. 2)
    MIN_KEY_SIZES: Dict[str, int] = {
        "RSA": 2048,  # Minimum RSA key size
        "EC": 256,  # Minimum EC curve size
        "AES": 128,  # Minimum symmetric key size
    }

    # Mapping curve names to cryptography objects
    CURVE_OBJECTS: Dict[str, ec.EllipticCurve] = {
        "P-256": ec.SECP256R1(),
        "P-384": ec.SECP384R1(),
        "P-521": ec.SECP521R1(),
    }

    @classmethod
    def is_algorithm_approved(cls, algorithm: str, operation: str) -> bool:
        """
        Check if an algorithm is FIPS-approved for a specific operation.

        Args:
            algorithm: Algorithm name (e.g., "RS256", "ES256")
            operation: Operation type (e.g., "jwt_signing", "dpop_signing")

        Returns:
            bool: True if algorithm is FIPS-approved for the operation
        """
        approved = cls.APPROVED_ALGORITHMS.get(operation, [])
        return algorithm in approved

    @classmethod
    def get_approved_algorithms(cls, operation: str) -> List[str]:
        """
        Get list of FIPS-approved algorithms for an operation.

        Args:
            operation: Operation type

        Returns:
            List[str]: List of approved algorithms
        """
        return cls.APPROVED_ALGORITHMS.get(operation, []).copy()

    @classmethod
    def is_curve_approved(cls, curve_name: str) -> bool:
        """
        Check if an elliptic curve is FIPS-approved.

        Args:
            curve_name: Curve name (e.g., "P-256")

        Returns:
            bool: True if curve is FIPS-approved
        """
        return curve_name in cls.APPROVED_CURVES

    @classmethod
    def get_curve_object(cls, curve_name: str) -> ec.EllipticCurve:
        """
        Get cryptography curve object for FIPS-approved curve.

        Args:
            curve_name: Curve name (e.g., "P-256")

        Returns:
            ec.EllipticCurve: Cryptography curve object

        Raises:
            ValueError: If curve is not FIPS-approved
        """
        if not cls.is_curve_approved(curve_name):
            approved_curves = list(cls.APPROVED_CURVES.keys())
            raise ValueError(
                f"Curve '{curve_name}' is not FIPS-approved. "
                f"Approved curves: {approved_curves}"
            )

        return cls.CURVE_OBJECTS[curve_name]

    @classmethod
    def is_key_size_sufficient(cls, key_type: str, key_size: int) -> bool:
        """
        Check if key size meets FIPS minimum requirements.

        Args:
            key_type: Key type ("RSA", "EC", "AES")
            key_size: Key size in bits

        Returns:
            bool: True if key size is sufficient
        """
        min_size = cls.MIN_KEY_SIZES.get(key_type, 0)
        return key_size >= min_size

    @classmethod
    def get_min_key_size(cls, key_type: str) -> int:
        """
        Get minimum FIPS key size for key type.

        Args:
            key_type: Key type ("RSA", "EC", "AES")

        Returns:
            int: Minimum key size in bits
        """
        return cls.MIN_KEY_SIZES.get(key_type, 0)

    @classmethod
    def validate_algorithm_for_operation(cls, algorithm: str, operation: str) -> None:
        """
        Validate algorithm is FIPS-approved for operation.

        Args:
            algorithm: Algorithm name
            operation: Operation type

        Raises:
            ValueError: If algorithm is not FIPS-approved
        """
        if not cls.is_algorithm_approved(algorithm, operation):
            approved = cls.get_approved_algorithms(operation)
            raise ValueError(
                f"Algorithm '{algorithm}' is not FIPS-approved for '{operation}'. "
                f"Approved algorithms: {approved}"
            )

    @classmethod
    def validate_key_strength(cls, key_type: str, key_size: int) -> None:
        """
        Validate key meets FIPS minimum strength requirements.

        Args:
            key_type: Key type
            key_size: Key size in bits

        Raises:
            ValueError: If key size is below FIPS minimum
        """
        min_size = cls.get_min_key_size(key_type)
        if not cls.is_key_size_sufficient(key_type, key_size):
            raise ValueError(
                f"{key_type} key size {key_size} bits is below FIPS minimum "
                f"of {min_size} bits"
            )

    @classmethod
    def get_all_approved_algorithms(cls) -> Set[str]:
        """
        Get set of all FIPS-approved algorithms across all operations.

        Returns:
            Set[str]: Set of all approved algorithms
        """
        all_algorithms = set()
        for algorithms in cls.APPROVED_ALGORITHMS.values():
            all_algorithms.update(algorithms)
        return all_algorithms
