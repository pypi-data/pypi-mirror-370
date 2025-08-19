import shlex
import subprocess
from dataclasses import dataclass, field
from typing import Union, List, Tuple, Optional

from .constants import SHELL_BUILTINS, SHELL_OPERATORS
from ..pltform import is_windows


def determine_shell_and_command(
        command: Union[str, List[str]],
        force_shell: Union[bool, None] = None
) -> Tuple[Union[str, List[str]], bool]:
    """
    Определяет, требуется ли shell=True, и подготавливает команду.
    :param command: Строка команды или список.
    :param force_shell: Явно установите Shell = true или Shell = false. Нет для автоматического определения.
    :return: Кортеж, содержащий (потенциально модифицированную) команду, и логический оболочек.
    """
    original_command_str = command if isinstance(command, str) else ' '.join(command)

    if force_shell is not None:
        use_shell = force_shell
        # Если shell=False принудительно, но команда строка, разделим ее
        if not use_shell and isinstance(command, str):
            command = shlex.split(command, posix=not is_windows())
        # Если shell=True принудительно, но команда список, объединим ее (хотя это редко нужно)
        elif use_shell and isinstance(command, list):
            command = ' '.join(shlex.quote(arg) for arg in command)  # Безопасное объединение
        return command, use_shell

    if is_windows():
        # В Windows часто безопаснее использовать shell=True, особенно для bat/cmd файлов
        # Но для простых команд без операторов можно и False
        if not any(op in original_command_str for op in SHELL_OPERATORS):
            try:
                # Попробуем разделить, если не получается, используем shell=True
                command_list = shlex.split(original_command_str, posix=False)
                # Проверим, не является ли первая часть встроенной командой shell
                if command_list and command_list[0].lower() in SHELL_BUILTINS:
                    use_shell = True
                else:
                    command = command_list
                    use_shell = False
            except ValueError:
                use_shell = True  # Не удалось разделить безопасно
        else:
            use_shell = True
    else:  # Linux/macOS
        if any(op in original_command_str for op in SHELL_OPERATORS):
            use_shell = True
        else:
            try:
                command_list = shlex.split(original_command_str, posix=True)
                if command_list and command_list[0] in SHELL_BUILTINS:
                    use_shell = True
                else:
                    command = command_list
                    use_shell = False
            except ValueError:
                use_shell = True  # Не удалось разделить безопасно

    # Если используем shell=True, команда должна быть строкой
    if use_shell and isinstance(command, list):
        command = original_command_str  # Возвращаем исходную строку

    return command, use_shell


@dataclass(repr=False)
class CMDResult:
    command: Union[str, List[str]]
    _stdout: Optional[bytes] = field(default=None)
    _stderr: Optional[bytes] = field(default=None)
    return_code: Optional[int] = None
    duration: Optional[float] = None
    process: Optional[subprocess.CompletedProcess] = None

    def __post_init__(self):
        # Конструктор для обратной совместимости, если кто-то передает строки
        if isinstance(self._stdout, str):
            self._stdout = self._stdout.encode('utf-8', errors='replace')
        if isinstance(self._stderr, str):
            self._stderr = self._stderr.encode('utf-8', errors='replace')

    @property
    def stdout_bytes(self) -> Optional[bytes]:
        """Возвращает stdout как сырые байты."""
        return self._stdout

    @property
    def stderr_bytes(self) -> Optional[bytes]:
        """Возвращает stderr как сырые байты."""
        return self._stderr

    @property
    def stdout(self) -> Optional[str]:
        """Возвращает stdout, декодированный в строку."""
        if self._stdout is None:
            return None
        return self._stdout.decode('utf-8', errors='replace')

    @property
    def stderr(self) -> Optional[str]:
        """Возвращает stderr, декодированный в строку."""
        if self._stderr is None:
            return None
        return self._stderr.decode('utf-8', errors='replace')

    @property
    def output(self) -> str:
        """
        Возвращает объединенный вывод stdout и stderr в виде строки.
        Идеально для логов и сообщений об ошибках.
        """
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)

    @property
    def success(self) -> bool:
        """Возвращает True, если код возврата равен 0."""
        return self.return_code == 0

    @property
    def failed(self) -> bool:
        """Возвращает True, если код возврата не равен 0."""
        return self.return_code is not None and self.return_code != 0

    def __str__(self) -> str:
        """Возвращает строковое представление основного вывода (stdout или stderr)."""
        return self.stdout or self.stderr or ""

    def __repr__(self) -> str:
        duration_str = f"{self.duration:.2f}s" if self.duration is not None else "N/A"

        # Показываем длину байт для наглядности
        stdout_info = f"len={len(self._stdout)}" if self._stdout is not None else "None"
        stderr_info = f"len={len(self._stderr)}" if self._stderr is not None else "None"

        return (
            f"CMDResult(command={self.command!r}, "
            f"return_code={self.return_code}, success={self.success}, "
            f"stdout_bytes={stdout_info}, stderr_bytes={stderr_info}, "
            f"duration={duration_str})"
        )

    # def __contains__(self, item: str) -> bool:
    #     """
    #     Проверяет наличие подстроки в stdout или stderr.
    #
    #     Args:
    #         item: Строка для поиска.
    #
    #     Returns:
    #         True, если строка найдена в stdout или stderr, иначе False.
    #     """
    #     if not isinstance(item, str):
    #         return False
    #     return (self.stdout is not None and item in self.stdout) or \
    #         (self.stderr is not None and item in self.stderr)

    # def check(self) -> 'CMDResult':
    #     """
    #     Вызывает исключение CommandError, если команда завершилась неудачно.
    #
    #     Если команда выполнена успешно (код возврата 0), возвращает self.
    #     Полезно для цепочек вызовов или явной проверки успеха.
    #
    #     Returns:
    #         Себя (self), если команда успешна.
    #
    #     Raises:
    #         CommandError: Если код возврата команды не равен 0.
    #     """
    #     if self.failed:
    #         raise CommandError(
    #             f"Команда '{self.command}' завершилась с кодом {self.return_code}.\n"
    #             f"Stderr: {self.stderr or 'N/A'}"
    #         )
    #     return self
