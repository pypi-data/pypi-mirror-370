"""Licensing lib"""

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
import time
from datetime import datetime
from uuid import uuid4

from typing import Iterable, Set, TypedDict, cast, Any, Literal, Optional, List

from dlt_plus.common.exceptions import DltPlusException

SCOPE_ALL = "*"
"""Matches all scopes if present in license"""
KNOWN_SCOPES = [
    SCOPE_ALL,
    "dlt_plus",
    "dlt_plus.dbt_generator",
    "dlt_plus.sources.mssql",
    "dlt_plus.project",
]
"""List of known scopes, might be moved to pluggy to be extendable by other packages"""


class DltLicenseException(DltPlusException):
    pass


class DltLicenseExpiredException(DltLicenseException):
    def __init__(self) -> None:
        super().__init__("Your dlt License has expired.")


class DltLicenseSignatureInvalidException(DltLicenseException):
    def __init__(self) -> None:
        super().__init__("Your dlt License has an invalid signature.")


class DltLicenseScopeInvalidException(DltLicenseException):
    def __init__(self, scope: str, scopes: Iterable[str]) -> None:
        self.scope = scope
        self.scopes = scopes
        super().__init__(
            f"Your dlt License does not have the required scope: {scope}. "
            f"Available scopes: {scopes}"
        )


class DltLicenseFeatureScopeFormatInvalid(DltLicenseException):
    def __init__(self, scope: str):
        super().__init__(
            f"Feature scope {scope} has invalid format. Please use `package.feature` format when "
            "requiring license via decorator."
        )


class DltLicenseNotFoundException(DltLicenseException):
    def __init__(self) -> None:
        super().__init__(
            """

Could not find a dlt license. Please provide your license in the RUNTIME__LICENSE
environment variable, or in your local or global secrets.toml file:

[runtime]
license="1234"

If you would like a trial license for dlt+, please join our waiting list:
https://info.dlthub.com/waiting-list
"""
        )


class DltPrivateKeyNotFoundException(DltLicenseException):
    def __init__(self) -> None:
        super().__init__(
            """

Could not find private key for signing. Please provide the private key in
your local or global secrets.toml file:

[runtime]
license_private_key="1234"
"""
        )


class DltLicense(TypedDict, total=False):
    sub: str
    iat: int
    exp: int
    iss: str
    license_type: Literal["commercial", "trial"]
    jit: str
    scope: Optional[str]


def get_known_scopes() -> List[str]:
    """Get list of possible scopes from installed dlt packages.
    Package-level scope: grants access to everything in the package ie. dlt_plus
    Feature-level scope: grants access to a particular feature ie. dlt_plus.dbt_generator

    """
    return KNOWN_SCOPES
    # NOTE: the entry point is not used anymore, it does not work with python 3.10
    # scopes: List[str] = [SCOPE_ALL]
    # for info in list_dlt_packages():
    #     if info.license_scopes:
    #         scopes.append(info.module_name)
    #         scopes.extend(f"{info.module_name}.{scope}" for scope in info.license_scopes.split())
    # return scopes


def create_license(
    private_key: str,
    days_valid: int,
    licensee_name: str,
    license_type: Literal["commercial", "trial"],
    scope: str,
    additional_scopes: Set[str] = None,
) -> str:
    """Create a new license object"""

    private_key_bytes = bytes(private_key, "utf-8")

    # check that provided scopes actually exist
    if scope:
        known_scopes = set(get_known_scopes()) | (additional_scopes or set())
        scopes = scope.split(" ")
        for s in scopes:
            if s not in known_scopes:
                raise ValueError(f"Unknown scope: {s}, must be one of: {', '.join(known_scopes)}")

    now = int(time.time())
    exp = now + (days_valid * 24 * 60 * 60)

    license: DltLicense = {
        "iat": now,
        "exp": exp,
        "sub": licensee_name,
        "iss": "dltHub Inc.",
        "license_type": license_type,
        "jit": str(uuid4()),
    }
    if scope:
        license["scope"] = scope
    encoded = jwt.encode(cast(Any, license), private_key_bytes, algorithm="RS256")

    return encoded


def validate_license(public_key: str, license: str) -> DltLicense:
    """Validate a jwt with the public key and return the decoded license object"""
    if not public_key:
        raise DltLicenseSignatureInvalidException()

    try:
        return cast(
            DltLicense, jwt.decode(license, bytes(public_key, "utf-8"), algorithms=["RS256"])
        )
    except ExpiredSignatureError as e:
        raise DltLicenseExpiredException() from e
    except (ValueError, JWTError) as e:
        raise DltLicenseSignatureInvalidException() from e


def get_scopes(license: DltLicense) -> List[str]:
    scopes_string = license.get("scope", None) or SCOPE_ALL
    return scopes_string.split(" ")  # default to all if no scope given


def ensure_scope(available_scopes: Iterable[str], required_scope: str) -> None:
    if SCOPE_ALL in available_scopes:
        return
    # scope that is validated is always feature scope
    package, _ = required_scope.split(".", 1)
    # license must contains full package or exactly this feature
    if package not in available_scopes and required_scope not in available_scopes:
        raise DltLicenseScopeInvalidException(required_scope, available_scopes)


def ensure_feature_scope(scope: str) -> None:
    fragments = scope.split(".", 1)
    package, feature = "", ""
    if len(fragments) == 2:
        package, feature = fragments
    if package and feature:
        return
    raise DltLicenseFeatureScopeFormatInvalid(scope)


def decode_license(license: str) -> DltLicense:
    """Decode the license without verifying that the signature is valid"""
    return cast(DltLicense, jwt.get_unverified_claims(license))


def discover_license() -> str:
    import dlt
    from dlt.common.configuration.exceptions import ConfigFieldMissingException

    try:
        if license := dlt.secrets["runtime.license"]:
            return cast(str, license)
        raise DltLicenseNotFoundException()
    except ConfigFieldMissingException as e:
        raise DltLicenseNotFoundException from e


def discover_private_key() -> str:
    import dlt
    from dlt.common.configuration.exceptions import ConfigFieldMissingException

    try:
        return dlt.secrets["runtime.license_private_key"]  # type: ignore[no-any-return]
    except ConfigFieldMissingException as e:
        raise DltPrivateKeyNotFoundException from e


def _to_pretty_timestamp(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def prettify_license(license: str, with_license: bool = False) -> str:
    license_dict = decode_license(license)

    output = f"""
License Id: {license_dict.get("jit")}
Licensee: {license_dict["sub"]}
Issuer: {license_dict["iss"]}
License Type: {license_dict["license_type"]}
Issued: {_to_pretty_timestamp(license_dict["iat"])}
Scopes: {",".join(get_scopes(license_dict))}
Valid Until: {_to_pretty_timestamp(license_dict["exp"])}"""
    if with_license:
        output += f"""
===
{license}
===
"""

    return output
