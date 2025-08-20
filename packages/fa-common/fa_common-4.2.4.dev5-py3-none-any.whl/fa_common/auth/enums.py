from enum import Enum


class AccessLevel(Enum):
    """Access levels."""

    NO_ACCESS = 0
    READ = 1
    WRITE = 2
    DEVELOPER = 3
    ADMIN = 4


class PermissionType(str, Enum):
    """Permission types."""

    APP_ACCESS = "app_access"
    """Standard permissions to access the App
        0 - No access
        1 - Read only access
        2 - Regular User R/W access
        3 - Developer access (Hidden logs & Features)
        4 - Admin access
    """
    APP_FEATURE = "app_feature"
    """Access to a named feature within an app"""
