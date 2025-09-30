import platform
import pwd
import grp
from typing import Optional, Any

# Detect current system
system: str = platform.system()


def get_user_info(uid: int) -> Optional[pwd.struct_passwd]:
    """
    Get user information by UID.

    Args:
        uid: User ID (integer).

    Returns:
        pwd.struct_passwd object containing user info if found, else None.
    """
    try:
        return pwd.getpwuid(uid)
    except KeyError:
        return None
    except Exception:
        return None


def get_group_info(gid: int) -> Optional[grp.struct_group]:
    """
    Get group information by GID.

    Args:
        gid: Group ID (integer).

    Returns:
        grp.struct_group object containing group info if found, else None.
    """
    try:
        return grp.getgrgid(gid)
    except KeyError:
        return None
    except Exception:
        return None
