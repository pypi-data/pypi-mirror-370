from pathlib import Path
from typing import Dict, Callable
from .command import run
from r00logger import log

def get_file_metadata(file_path: Path) -> Dict:
    """
    Получает метаданные файла через CLI утилиту 'stat'.

    :param file_path: Путь к файлу.
    :return: Словарь с метаданными.
    """
    # %a: права доступа в восьмеричном виде (напр. "644")
    # %u: ID пользователя (UID)
    # %g: ID группы (GID)
    # %X: время последнего доступа (atime) в секундах с эпохи
    # %Y: время последней модификации (mtime) в секундах с эпохи
    # %C: SELinux security context
    result = run(f'stat -c "%a %u %g %X %Y" {str(file_path)}', ignore_errors=True, disable_log=True)

    if not result.success:
        raise FileNotFoundError(f"Ошибка получения метаданных для {file_path}: {result.stderr}")

    parts = result.stdout.strip().split()
    return {
        "mode": parts[0],
        "uid": int(parts[1]),
        "gid": int(parts[2]),
        "atime": float(parts[3]),
        "mtime": float(parts[4]),
    }


def set_file_metadata(file_path: Path, metadata: Dict):
    """
    Устанавливает метаданные для файла через CLI, используя sudo.

    :param file_path: Путь к файлу, которому устанавливаются метаданные.
    :param metadata: Словарь с метаданными от get_file_metadata.
    """
    # Команды выполняются через sudo, так как целевой файл может принадлежать root
    run(f'sudo chown {metadata['uid']}:{metadata['gid']} {str(file_path)}', disable_log=True)
    run(f'sudo chmod {metadata['mode']} {str(file_path)}', disable_log=True)
    # Установка времени доступа (atime) и модификации (mtime)
    run(f'sudo touch -a -d @{metadata['atime']} {str(file_path)}', disable_log=True)
    run(f'sudo touch -m -d @{metadata['mtime']} {str(file_path)}', disable_log=True)


class FullAccessFile:
    def __init__(self, filepath: str | Path):
        self._filepath = Path(filepath)
        self._metadata = None

    def __enter__(self) -> Path:
        self._metadata = get_file_metadata(self._filepath)
        run(f'sudo chmod 777 {self._filepath}', disable_log=True)
        return self

    def __getattr__(self, name) -> Path:
        return getattr(self._filepath, name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_file_metadata(self._filepath, self._metadata)
        if exc_type is not None:
            log.error(f"[{self._filepath}] Внутри блока произошло исключение: {exc_val}")
        return False