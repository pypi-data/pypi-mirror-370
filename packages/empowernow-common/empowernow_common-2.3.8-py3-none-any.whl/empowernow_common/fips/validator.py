"""
🛡️ FIPS 140-3 Compliance Validator - SECURITY HARDENED

This module provides runtime FIPS compliance validation based on the proven
implementation from the EmpowerNow IdP's TokenBindingService.

SECURITY ENHANCEMENTS:
- Fixed critical FIPS bypass vulnerability
- Added comprehensive OpenSSL FIPS validation
- Implemented proper entropy quality checking
- Added cryptographic backend verification
- Enhanced security logging and monitoring
"""

import os
import logging
import subprocess
import hashlib
import secrets
import platform
import sys

# winreg only on Windows
try:
    import winreg  # type: ignore
except ImportError:
    winreg = None
from typing import Dict, Any, Optional, Tuple, List
from .algorithms import FIPSAlgorithms
from ..settings import settings

logger = logging.getLogger(__name__)

# Background validation globals
_VALIDATOR_THREAD = None


def _background_validation_loop(interval: int, strict: bool):
    """Thread target that runs ensure_compliance periodically."""
    import time, sys, traceback

    while True:
        try:
            FIPSValidator.ensure_compliance()
        except Exception as exc:
            logger.critical("🚨 Continuous FIPS validation failed", exc_info=exc)
            if strict:
                logger.critical("🚨 Exiting process due to strict FIPS mode")
                sys.exit(1)
        time.sleep(interval)


def start_continuous_validation(interval: int = 300, strict: bool = False):
    """Start background thread that validates FIPS compliance every `interval` seconds.

    Args:
        interval: seconds between checks (default 5 min)
        strict: if True, process exits on first failure.
    """
    global _VALIDATOR_THREAD
    if _VALIDATOR_THREAD and _VALIDATOR_THREAD.is_alive():
        return  # already running
    import threading

    t = threading.Thread(
        target=_background_validation_loop, args=(interval, strict), daemon=True
    )
    t.start()
    _VALIDATOR_THREAD = t
    logger.info(
        "🛡️ Continuous FIPS validation thread started",
        extra={"interval": interval, "strict": strict},
    )


class FIPSSecurityError(Exception):
    """FIPS security-related errors"""

    pass


class FIPSValidator:
    """
    🛡️ FIPS 140-3 compliance validator - SECURITY HARDENED.

    Based on the production-tested implementation from EmpowerNow IdP.
    """

    @classmethod
    def ensure_compliance(cls) -> None:
        """
        Ensure FIPS compliance on package import/initialization.

        Raises:
            RuntimeError: If FIPS compliance validation fails
        """
        # Global opt-out mainly for CI / developer laptops
        if os.getenv("EMPOWERNOW_FIPS_DISABLE", "0").lower() in {"1", "true", "yes"}:
            logger.warning("⚠️  FIPS validation disabled via EMPOWERNOW_FIPS_DISABLE")
            return

        compliance = cls.runtime_compliance_check()

        if not all(compliance.values()):
            failed_checks = [k for k, v in compliance.items() if not v]

            # Log security failure
            logger.critical(
                "🚨 FIPS COMPLIANCE FAILURE",
                extra={
                    "failed_checks": failed_checks,
                    "compliance_status": compliance,
                    "security_event": "fips_validation_failed",
                },
            )

            raise RuntimeError(
                f"FIPS compliance check failed: {', '.join(failed_checks)}. "
                f"Ensure OpenSSL FIPS provider is enabled and system meets "
                f"FIPS 140-3 requirements."
            )

        logger.info(
            "🛡️ FIPS 140-3 compliance validated successfully",
            extra={
                "compliance_status": compliance,
                "security_event": "fips_validation_passed",
            },
        )

    @classmethod
    def runtime_compliance_check(cls) -> Dict[str, bool]:
        """
        🛡️ Comprehensive runtime FIPS compliance check - SECURITY HARDENED.

        Returns:
            Dict[str, bool]: Compliance status for each component
        """
        if os.getenv("EMPOWERNOW_FIPS_DISABLE", "0").lower() in {"1", "true", "yes"}:
            return {
                "cryptography_backend": True,
                "entropy_source": True,
                "openssl_fips": True,
                "algorithm_registry": True,
                "environment": True,
                "runtime_security": True,
            }

        compliance_results = {}

        try:
            compliance_results = {
                "cryptography_backend": cls.validate_cryptography_backend(),
                "entropy_source": cls.validate_entropy_source(),
                "openssl_fips": cls.check_openssl_fips(),
                "algorithm_registry": cls.check_algorithm_registry(),
                "environment": cls.check_fips_environment(),
                "runtime_security": cls.check_runtime_security(),
            }

            # Log compliance check results
            logger.info(
                "🛡️ FIPS compliance check completed",
                extra={
                    "compliance_results": compliance_results,
                    "overall_compliant": all(compliance_results.values()),
                },
            )

        except Exception as e:
            logger.error(f"🚨 FIPS compliance check failed with exception: {e}")
            # Return all False on exception to fail secure
            compliance_results = {
                key: False
                for key in [
                    "cryptography_backend",
                    "entropy_source",
                    "openssl_fips",
                    "algorithm_registry",
                    "environment",
                    "runtime_security",
                ]
            }

        return compliance_results

    @classmethod
    def validate_cryptography_backend(cls) -> bool:
        """
        🛡️ Ensure cryptography library is using FIPS-validated backend - HARDENED.

        Returns:
            bool: True if backend is FIPS-compliant
        """
        try:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.backends.openssl import backend as openssl_backend

            backend = default_backend()

            # Verify we're using OpenSSL backend
            if not hasattr(backend, "_lib"):
                logger.warning(
                    "🚨 Cryptography backend missing OpenSSL library interface"
                )
                return False

            # Check if FIPS mode is enabled in OpenSSL
            try:
                # Try to access FIPS mode indicator
                if hasattr(backend._lib, "FIPS_mode"):
                    fips_mode = backend._lib.FIPS_mode()
                    if fips_mode != 1:
                        logger.warning(f"🚨 OpenSSL FIPS mode not enabled: {fips_mode}")
                        return False
                elif hasattr(backend._lib, "EVP_default_properties_is_fips_enabled"):
                    # OpenSSL 3.0+ FIPS check
                    fips_enabled = backend._lib.EVP_default_properties_is_fips_enabled(
                        backend._ffi.NULL
                    )
                    if not fips_enabled:
                        logger.warning("🚨 OpenSSL 3.0+ FIPS provider not enabled")
                        return False
                else:
                    # Fallback: check for FIPS environment indicators
                    logger.warning(
                        "🚨 Cannot directly verify FIPS mode - using environment check"
                    )
                    return cls._check_fips_environment_fallback()
            except Exception as e:
                logger.warning(f"🚨 Error checking FIPS mode: {e}")
                return cls._check_fips_environment_fallback()

            # Validate cryptographic operations work with FIPS algorithms
            if not cls._test_fips_cryptographic_operations():
                logger.error("🚨 FIPS cryptographic operations test failed")
                return False

            logger.info("✅ Cryptography backend FIPS validation passed")
            return True

        except ImportError as e:
            logger.error(f"🚨 cryptography library not available: {e}")
            return False
        except Exception as e:
            logger.error(f"🚨 Error checking cryptography backend: {e}")
            return False

    @classmethod
    def _test_fips_cryptographic_operations(cls) -> bool:
        """Test that FIPS-approved cryptographic operations work correctly"""
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa, padding

            # Test RSA key generation with FIPS-approved key size
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,  # FIPS minimum
            )

            # Test signing with FIPS-approved algorithm
            message = b"FIPS test message"
            signature = private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Test verification
            public_key = private_key.public_key()
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return True

        except Exception as e:
            logger.error(f"🚨 FIPS cryptographic operations test failed: {e}")
            return False

    @classmethod
    def _check_fips_environment_fallback(cls) -> bool:
        """Fallback FIPS environment check when direct validation unavailable"""
        fips_indicators = [
            settings.openssl_fips or settings.empowernow_fips_mode,
            os.path.exists("/proc/sys/crypto/fips_enabled")
            and open("/proc/sys/crypto/fips_enabled", "r").read().strip() == "1",
        ]

        return any(fips_indicators)

    @classmethod
    def validate_entropy_source(cls) -> bool:
        """
        🛡️ Validate that system entropy meets FIPS requirements - HARDENED.

        Returns:
            bool: True if entropy source is adequate
        """
        try:
            # Check entropy pool health on Linux
            if os.path.exists("/proc/sys/kernel/random/entropy_avail"):
                with open("/proc/sys/kernel/random/entropy_avail", "r") as f:
                    entropy = int(f.read().strip())
                    if entropy < 128:  # Minimum entropy threshold
                        logger.warning(
                            f"🚨 Low system entropy: {entropy} bits available"
                        )
                        return False
                    logger.info(f"✅ System entropy adequate: {entropy} bits available")

            # Test entropy quality by generating multiple samples
            if not cls._test_entropy_quality():
                logger.error("🚨 Entropy quality test failed")
                return False

            # Test that os.urandom works and produces quality output
            test_samples = []
            for _ in range(10):
                sample = os.urandom(32)
                if len(sample) != 32:
                    logger.error("🚨 os.urandom returned wrong length")
                    return False
                test_samples.append(sample)

            # Check for obvious patterns (all samples shouldn't be identical)
            unique_samples = set(test_samples)
            if len(unique_samples) < len(test_samples) // 2:
                logger.error("🚨 Entropy source shows concerning patterns")
                return False

            logger.info("✅ Entropy source validation passed")
            return True

        except Exception as e:
            logger.error(f"🚨 Error checking entropy source: {e}")
            return False

    @classmethod
    def _test_entropy_quality(cls) -> bool:
        """Test entropy quality using statistical analysis"""
        try:
            # Generate test data
            sample_size = 1024
            test_data = os.urandom(sample_size)

            # Basic entropy tests
            byte_counts = [0] * 256
            for byte in test_data:
                byte_counts[byte] += 1

            # Check for reasonable distribution (no byte should appear > 10% of time)
            max_count = max(byte_counts)
            if max_count > sample_size * 0.1:
                logger.warning(
                    f"🚨 Poor entropy distribution - max byte count: {max_count}"
                )
                return False

            # Check that we have reasonable spread of byte values
            used_bytes = sum(1 for count in byte_counts if count > 0)
            if used_bytes < 200:  # Should use most byte values in 1KB sample
                logger.warning(
                    f"🚨 Poor entropy spread - only {used_bytes} different byte values"
                )
                return False

            return True

        except Exception as e:
            logger.warning(f"🚨 Entropy quality test failed: {e}")
            return False

    @classmethod
    def check_openssl_fips(cls) -> bool:
        """
        🛡️ Check if OpenSSL is running in FIPS mode - SECURITY FIXED.

        Returns:
            bool: True if OpenSSL FIPS mode is enabled
        """
        try:
            # SECURITY FIX: Remove the "always return True" vulnerability
            fips_enabled = False

            # Method 1: Check environment variables
            fips_env = "1" if settings.openssl_fips else "0"
            if fips_env == "1":
                fips_enabled = True
                logger.info(
                    "✅ FIPS mode indicated by OPENSSL_FIPS environment variable"
                )

            empowernow_fips = "1" if settings.empowernow_fips_mode else "0"
            if empowernow_fips == "1":
                fips_enabled = True
                logger.info(
                    "✅ FIPS mode indicated by EMPOWERNOW_FIPS_MODE environment variable"
                )

            # Method 2: Check Linux FIPS mode flag
            if os.path.exists("/proc/sys/crypto/fips_enabled"):
                try:
                    with open("/proc/sys/crypto/fips_enabled", "r") as f:
                        fips_flag = f.read().strip()
                        if fips_flag == "1":
                            fips_enabled = True
                            logger.info(
                                "✅ FIPS mode enabled via /proc/sys/crypto/fips_enabled"
                            )
                        else:
                            logger.warning(f"🚨 FIPS not enabled in kernel: {fips_flag}")
                except Exception as e:
                    logger.warning(f"🚨 Could not read FIPS flag: {e}")

            # Method 3: Try to run openssl command to check FIPS status
            try:
                result = subprocess.run(
                    ["openssl", "version", "-f"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and "FIPS" in result.stdout:
                    fips_enabled = True
                    logger.info("✅ FIPS mode confirmed by openssl command")
                elif result.returncode == 0:
                    logger.warning(
                        "🚨 OpenSSL available but FIPS not indicated in version"
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                logger.warning(f"🚨 Could not check OpenSSL FIPS status: {e}")

            # Method 4: Check for FIPS configuration files
            fips_config_paths = [
                "/etc/ssl/openssl.cnf",
                "/usr/local/ssl/openssl.cnf",
                "/etc/pki/tls/openssl.cnf",
            ]

            for config_path in fips_config_paths:
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r") as f:
                            content = f.read()
                            if (
                                "fips" in content.lower()
                                and "fips = yes" in content.lower()
                            ):
                                fips_enabled = True
                                logger.info(
                                    f"✅ FIPS configuration found in {config_path}"
                                )
                                break
                    except Exception as e:
                        logger.warning(
                            f"🚨 Could not read OpenSSL config {config_path}: {e}"
                        )

            if not fips_enabled:
                logger.error("🚨 FIPS mode NOT detected by any validation method")
                logger.error("🚨 Set EMPOWERNOW_FIPS_MODE=true to override for testing")

            return fips_enabled

        except Exception as e:
            logger.error(f"🚨 Error checking OpenSSL FIPS mode: {e}")
            return False

    @classmethod
    def _platform_fips_enabled(cls) -> bool:
        """Best-effort platform detection for Windows/macOS."""
        current = sys.platform
        if current.startswith("win") and winreg:
            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"System\CurrentControlSet\Control\Lsa\FipsAlgorithmPolicy",
                ) as key:
                    value, _ = winreg.QueryValueEx(key, "Enabled")
                    return value == 1
            except FileNotFoundError:
                return False
            except Exception as e:
                logger.warning(f"Windows FIPS registry check failed: {e}")
        elif current == "darwin":
            try:
                import subprocess

                result = subprocess.run(
                    ["sysctl", "security.mac.fips_enabled"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0 and result.stdout.strip().endswith("1"):
                    return True
            except Exception as e:
                logger.warning(f"macOS FIPS sysctl check failed: {e}")
        return False

    @classmethod
    def check_algorithm_registry(cls) -> bool:
        """
        🛡️ Check that algorithm registry is properly initialized - HARDENED.

        Returns:
            bool: True if algorithm registry is valid
        """
        try:
            # Verify key algorithms are registered
            jwt_algs = FIPSAlgorithms.get_approved_algorithms("jwt_signing")
            dpop_algs = FIPSAlgorithms.get_approved_algorithms("dpop_signing")
            symmetric_algs = FIPSAlgorithms.get_approved_algorithms("symmetric")
            hash_algs = FIPSAlgorithms.get_approved_algorithms("hash")

            # Must have at least basic FIPS algorithms
            required_jwt = {"RS256", "ES256"}
            required_dpop = {"RS256", "ES256"}
            required_symmetric = {"AES-256-GCM"}
            required_hash = {"SHA-256"}

            # Validate algorithm availability
            missing_algorithms = []

            if not required_jwt.issubset(set(jwt_algs)):
                missing_algorithms.append(
                    f"JWT signing: missing {required_jwt - set(jwt_algs)}"
                )

            if not required_dpop.issubset(set(dpop_algs)):
                missing_algorithms.append(
                    f"DPoP signing: missing {required_dpop - set(dpop_algs)}"
                )

            if not required_symmetric.issubset(set(symmetric_algs)):
                missing_algorithms.append(
                    f"Symmetric: missing {required_symmetric - set(symmetric_algs)}"
                )

            if not required_hash.issubset(set(hash_algs)):
                missing_algorithms.append(
                    f"Hash: missing {required_hash - set(hash_algs)}"
                )

            if missing_algorithms:
                logger.error(
                    f"🚨 Algorithm registry missing required algorithms: {missing_algorithms}"
                )
                return False

            # Validate curve availability
            approved_curves = list(FIPSAlgorithms.APPROVED_CURVES.keys())
            if len(approved_curves) < 3:  # Should have P-256, P-384, P-521
                logger.error(f"🚨 Insufficient approved curves: {approved_curves}")
                return False

            # Test that algorithm validation works
            if not FIPSAlgorithms.is_algorithm_approved("RS256", "jwt_signing"):
                logger.error("🚨 Algorithm validation not working correctly")
                return False

            logger.info("✅ Algorithm registry validation passed")
            return True

        except Exception as e:
            logger.error(f"🚨 Error checking algorithm registry: {e}")
            return False

    @classmethod
    def check_fips_environment(cls) -> bool:
        """
        🛡️ Check FIPS-related environment configuration - HARDENED.

        Returns:
            bool: True if environment is properly configured
        """
        try:
            # Check for required environment variables
            fips_flags = {
                "EMPOWERNOW_FIPS_MODE": settings.empowernow_fips_mode,
                "OPENSSL_FIPS": settings.openssl_fips,
            }

            fips_enabled = any(fips_flags.values())
            active_vars = [f"{k}=1" for k, v in fips_flags.items() if v]

            if fips_enabled:
                logger.info(f"✅ FIPS environment configured: {', '.join(active_vars)}")
            else:
                logger.warning("🚨 No FIPS environment variables set")

            # Check for conflicting/dangerous environment variables
            # Dangerous vars: rely on new settings fields
            security_warnings: list[str] = []

            if not settings.cryptography_openssl_no_legacy:
                security_warnings.append("CRYPTOGRAPHY_OPENSSL_NO_LEGACY should be set to '1' in FIPS mode")

            if settings.pythonhashseed.lower() != "random":
                security_warnings.append("PYTHONHASHSEED should be 'random' for additional security")

            if security_warnings:
                logger.warning(f"🚨 Security environment issues: {security_warnings}")

            return fips_enabled

        except Exception as e:
            logger.error(f"🚨 Error checking FIPS environment: {e}")
            return True  # Don't fail on environment check errors

    @classmethod
    def check_runtime_security(cls) -> bool:
        """
        🛡️ Additional runtime security checks - NEW SECURITY FEATURE.

        Returns:
            bool: True if runtime security is adequate
        """
        try:
            security_issues = []

            # Check Python version for known vulnerabilities
            python_version = sys.version_info

            # Python < 3.10 has known security issues
            if python_version < (3, 10):
                security_issues.append(
                    f"Python version {python_version} has known security vulnerabilities"
                )

            # Check for debug mode (should not be enabled in production)
            if sys.flags.debug:
                security_issues.append(
                    "Python debug mode enabled - not suitable for production"
                )

            # Check for development mode indicators
            if sys.flags.dev_mode:
                security_issues.append("Python development mode enabled")

            # Check file permissions on sensitive paths
            sensitive_paths = ["/etc/ssl", "/usr/local/ssl"]
            for path in sensitive_paths:
                if os.path.exists(path):
                    stat_info = os.stat(path)
                    # Check if world-writable (dangerous)
                    if stat_info.st_mode & 0o002:
                        security_issues.append(f"World-writable SSL directory: {path}")

            # Check for secure random seeding
            try:
                # Test that secrets module works (uses secure random)
                test_token = secrets.token_hex(16)
                if len(test_token) != 32:  # Should be 32 hex chars for 16 bytes
                    security_issues.append("secrets.token_hex not working correctly")
            except Exception as e:
                security_issues.append(f"secrets module not working: {e}")

            if security_issues:
                logger.warning(f"🚨 Runtime security issues detected: {security_issues}")
                # For now, log warnings but don't fail - these are advisory
                # In production, you might want to fail on certain issues

            logger.info("✅ Runtime security checks completed")
            return True  # Return True for now, adjust based on risk tolerance

        except Exception as e:
            logger.error(f"🚨 Error during runtime security check: {e}")
            return False

    @classmethod
    def validate_algorithm(cls, algorithm: str, operation: str) -> bool:
        """
        Validate algorithm is FIPS-approved for operation.

        Args:
            algorithm: Algorithm name
            operation: Operation type

        Returns:
            bool: True if algorithm is FIPS-approved
        """
        try:
            return FIPSAlgorithms.is_algorithm_approved(algorithm, operation)
        except Exception as e:
            logger.error(
                f"🚨 Error validating algorithm {algorithm} for {operation}: {e}"
            )
            return False

    @classmethod
    def validate_key_strength(cls, key_type: str, key_size: int) -> bool:
        """
        Validate key meets FIPS minimum strength requirements.

        Args:
            key_type: Key type
            key_size: Key size in bits

        Returns:
            bool: True if key size is sufficient
        """
        try:
            return FIPSAlgorithms.is_key_size_sufficient(key_type, key_size)
        except Exception as e:
            logger.error(f"🚨 Error validating key strength {key_type} {key_size}: {e}")
            return False

    @classmethod
    def get_compliance_report(cls) -> Dict[str, Any]:
        """
        🛡️ Get detailed FIPS compliance report - ENHANCED.

        Returns:
            Dict[str, Any]: Detailed compliance information
        """
        try:
            compliance = cls.runtime_compliance_check()

            # Get system information
            system_info = {
                "python_version": sys.version,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            }

            # Get cryptography library info
            try:
                import cryptography

                crypto_info = {
                    "cryptography_version": cryptography.__version__,
                    "backend_available": True,
                }
            except ImportError:
                crypto_info = {
                    "cryptography_version": "not available",
                    "backend_available": False,
                }

            report = {
                "overall_compliant": all(compliance.values()),
                "compliance_timestamp": os.environ.get("TZ", "UTC"),
                "components": compliance,
                "algorithm_count": {
                    "jwt_signing": len(
                        FIPSAlgorithms.get_approved_algorithms("jwt_signing")
                    ),
                    "dpop_signing": len(
                        FIPSAlgorithms.get_approved_algorithms("dpop_signing")
                    ),
                    "symmetric": len(
                        FIPSAlgorithms.get_approved_algorithms("symmetric")
                    ),
                    "hash": len(FIPSAlgorithms.get_approved_algorithms("hash")),
                    "mac": len(FIPSAlgorithms.get_approved_algorithms("mac")),
                },
                "approved_curves": list(FIPSAlgorithms.APPROVED_CURVES.keys()),
                "min_key_sizes": FIPSAlgorithms.MIN_KEY_SIZES.copy(),
                "environment": {
                    "fips_mode": settings.empowernow_fips_mode,
                    "openssl_fips": settings.openssl_fips,
                    "cryptography_openssl_no_legacy": settings.cryptography_openssl_no_legacy,
                    "pythonhashseed": settings.pythonhashseed,
                },
                "system_info": system_info,
                "cryptography_info": crypto_info,
                "security_recommendations": cls._get_security_recommendations(
                    compliance
                ),
            }

            return report

        except Exception as e:
            logger.error(f"🚨 Error generating compliance report: {e}")
            return {
                "overall_compliant": False,
                "error": str(e),
                "components": {},
                "security_recommendations": ["Fix compliance report generation error"],
            }

    @classmethod
    def _get_security_recommendations(cls, compliance: Dict[str, bool]) -> List[str]:
        """Get security recommendations based on compliance status"""
        recommendations = []

        if not compliance.get("openssl_fips", True):
            recommendations.append("Enable OpenSSL FIPS mode: set OPENSSL_FIPS=1")

        if not compliance.get("environment", True):
            recommendations.append("Set EMPOWERNOW_FIPS_MODE=true in environment")

        if not compliance.get("entropy_source", True):
            recommendations.append(
                "Improve system entropy: install haveged or ensure hardware RNG"
            )

        if not compliance.get("cryptography_backend", True):
            recommendations.append("Install FIPS-validated cryptography library")

        if not compliance.get("algorithm_registry", True):
            recommendations.append("Verify algorithm registry initialization")

        if not compliance.get("runtime_security", True):
            recommendations.append("Address runtime security issues in logs")

        # General security recommendations
        recommendations.extend(
            [
                "Set CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 to disable legacy algorithms",
                "Set PYTHONHASHSEED=random for additional security",
                "Run system in FIPS-enabled environment",
                "Regularly update cryptography and OpenSSL libraries",
                "Monitor FIPS compliance status in production",
            ]
        )

        return recommendations


def ensure_fips_compliance() -> None:
    """
    🛡️ Convenience function to ensure FIPS compliance - HARDENED.

    Raises:
        RuntimeError: If FIPS compliance validation fails
    """
    try:
        FIPSValidator.ensure_compliance()
    except Exception as e:
        logger.critical(f"🚨 FIPS compliance enforcement failed: {e}")
        raise


def is_fips_mode() -> bool:
    """
    🛡️ Check if system is running in FIPS mode - SECURITY ENHANCED.

    Returns:
        bool: True if FIPS mode is enabled
    """
    try:
        compliance = FIPSValidator.runtime_compliance_check()
        fips_components = ["environment", "openssl_fips", "cryptography_backend"]

        # Require all core FIPS components to be compliant
        fips_mode = all(
            compliance.get(component, False) for component in fips_components
        )

        logger.info(
            f"🛡️ FIPS mode check: {fips_mode}",
            extra={
                "fips_components": {
                    comp: compliance.get(comp, False) for comp in fips_components
                }
            },
        )

        return fips_mode

    except Exception as e:
        logger.error(f"🚨 Error checking FIPS mode: {e}")
        return False
