import platform
import pwd
import grp

system = platform.system()

def get_user_info(uid):
    try:
        return pwd.getpwuid(uid)
    except:
        return None

def get_group_info(gid):
    try:
        return grp.getgrgid(gid)
    except:
        return None