from abc import ABC
from typing import List

from fa_common import CamelModel


class AuditEventBase(CamelModel, ABC):
    """
    Base Model to use for the Audit Event received from
    `_call_home()` in fa_common.licence.utils.

    Create this collection by implmenting it as a Beanie Document or equivlient
    """

    product: str = ""
    product_version: str = ""
    licensee: str = ""
    expiry: str = ""
    audit_url: str = ""
    features: List[str] = []
    container_id: str = ""
    username: str = ""
    node: str = ""
    python_version: str = ""
    platform: str = ""
    distro: str = ""
