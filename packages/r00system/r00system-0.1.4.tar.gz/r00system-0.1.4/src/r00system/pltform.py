import os
from platform import system as plat_system
import sys

_OS_TYPE = plat_system()


def is_windows() -> bool:
    """Checks if the current operating system is Windows."""
    return _OS_TYPE == 'Windows'


def is_linux() -> bool:
    """Checks if the current operating system is Linux."""
    return _OS_TYPE == 'Linux'


def is_pycharm_hosted() -> bool:
    """Запускается ли код из PyCharm."""
    return 'PYCHARM_HOSTED' in os.environ or 'python-BaseException' in sys.modules


def is_pycharm_debug():
    """Проверяет, запущен ли код в режиме отладки PyCharm."""
    return True if '_pydev_bundle.pydev_log' in sys.modules.keys() else False
