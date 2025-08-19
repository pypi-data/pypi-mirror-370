DEFAULT_TIMEOUT = 60
DEFAULT_ENCODING = 'utf-8'
DEFAULT_RETRIES = 1  # По умолчанию 1 попытка (без повторов)

# Операторы, обычно требующие shell=True
SHELL_OPERATORS = frozenset(["|", ">", "<", "&", ";", "$", "`", '"', "'", "\\", "*", "(", ")"])

# Команды, которые часто являются встроенными в shell
SHELL_BUILTINS = frozenset(["cd", "echo", "export", "twrp", "set", "unset", "source", "."])  # Добавьте по необходимости