import os
import sys
import time
from contextvars import ContextVar
from functools import wraps

from loguru import logger as log
from decohints import decohints
from .helpers.constants import *
from typing import Optional
from pathlib import Path



# --- Настройка кастомных цветов для уровней ---
log.level("TRACE", color="<fg #739cc8>")
log.level("DEBUG", color="<fg #bbd853>")
log.level("INFO", color="<fg #82c36a><bold>")
log.level("SUCCESS", color="<fg #1dd301><bold>")
log.level("WARNING", color="<fg #ff9d57>")
log.level("ERROR", color="<red><bold>")
log.level("CRITICAL", color="<red><bold><underline")
indent_var = ContextVar('indent', default=0)

def all_arguments(*args, **kwargs):
    """ Форматирует аргументы функции для лога. """
    all_args = []
    all_kw = []
    args_list = list(args)

    if kwargs.get("no_self"):
        kwargs.pop("no_self")
        if len(args_list) > 0:
            if hasattr(args_list[0], '__class__') and args_list[0].__class__.__module__ != "builtins":
                args_list.pop(0)

    for arg in args_list:
        if isinstance(arg, dict):
            formatted_dict = ', '.join(f'{repr(k)}={repr(v)}' for k, v in arg.items())
            all_args.append(f"{{{formatted_dict}}}")
        else:
            all_args.append(repr(arg))

    if kwargs:
        all_kw.append(', '.join(f'{str(k)}={repr(v)}' for k, v in kwargs.items()))

    result = ', '.join(all_args + all_kw)
    result = result.strip(', ')
    return result

def indent_patcher(record):
    """Патчер для Loguru, добавляющий отступ в extra."""
    indent_level = indent_var.get()
    indent_string = '... ' * indent_level
    record["extra"]["indent_str"] = indent_string

def add_stdout():
    """Настраивает и добавляет обработчик для вывода в stdout с отступами."""
    log.remove()
    log.configure(
        extra={"indent_str": ""}, # Устанавливаем дефолтное значение
        patcher=indent_patcher    # Устанавливаем глобальный патчер
    )
    log.add(
        sys.stdout,
        level=os.environ.get(ENV_LEVEL_NAME, DEFAULT_LOG_LEVEL).upper(),
        colorize=True,
        backtrace=True,
        diagnose=True,
        format=FMT
    )

def _expand_path(p: str) -> str:
    return os.path.expanduser(os.path.expandvars(p))

def add_file(log_file: str, level: Optional[str] = None, replace_stdout: bool = False):
    """
    Добавляет sink на файл. Если replace_stdout=True — отключает stdout и пишет только в файл.
    Если хотите видеть и файл, и stdout — используйте replace_stdout=False (но тогда не редиректите stdout в тот же файл,
    иначе получите дубли).
    """
    lvl = (level or os.environ.get(ENV_LEVEL_NAME, DEFAULT_LOG_LEVEL)).upper()

    # Создадим каталог
    path = _expand_path(log_file)
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    if replace_stdout:
        log.remove()
        log.configure(extra={"indent_str": ""}, patcher=indent_patcher)

    log.add(
        path,
        level=lvl,
        colorize=False,
        backtrace=True,
        diagnose=True,
        format=FMT,
        encoding="utf-8",
        enqueue=True,     # безопасно для потоков/подпроцессов
        # rotation="20 MB",   # при желании включите ротацию
        # retention="14 days"
    )

def set_level(level:str):
    """
    Устанавливает уровень логирования для обработчика stdout.
    """
    level = level.upper()
    valid_levels = ['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if level not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {', '.join(valid_levels)}.")

    log.remove()
    log.configure(
        extra={"indent_str": ""},
        patcher=indent_patcher
    )
    log.add(
        sys.stdout,
        level=level, # Используем новый уровень
        colorize=True,
        backtrace=True,
        diagnose=True,
        format=FMT
    )

@decohints
def log_script(func):
    """Декоратор для логирования входа/выхода функции с отступами."""
    @wraps(func)
    def logscript(*args, **kwargs):
        func_name = func.__qualname__
        should_remove_self = kwargs.get("no_self", True)
        log_args = args[1:] if should_remove_self and len(args) > 0 and hasattr(args[0], '__class__') and args[0].__class__.__module__ != "builtins" else args
        log_kwargs = {k: v for k, v in kwargs.items() if k != "no_self"}
        all_arg_str = all_arguments(*log_args, **log_kwargs)

        funclog = f'{func_name}({all_arg_str})'
        log.debug(f"▼ {funclog}...")
        current_indent = indent_var.get()
        token = indent_var.set(current_indent + 1)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        except:
             indent_var.reset(token)
             raise
        else:
            indent_var.reset(token)
            elapsed = time.time() - start_time
            log.debug(f"▲ [{elapsed:.3f}] {func_name}: {result}")
        return result
    return logscript


@decohints
def log_result(_func=None, *, level="TRACE"):
    def decorator_log_result(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_method = False
            if args:
                first_arg = args[0]
                if hasattr(first_arg, '__class__') and func.__name__ in dir(first_arg.__class__):
                    is_method = True

            # Передаем no_self=True только если это действительно метод
            all_arg_str = all_arguments(*args, **kwargs, no_self=is_method)
            funclog = f'{func.__name__}({all_arg_str})'
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise
            else:
                elapsed = time.time() - start_time

                # Получаем метод логирования динамически
                log_method_name = level.lower()
                if log_method_name == "debug": # ↘ ⭐ ↗
                    msg = f"⭐ [{elapsed:.3f}] {funclog} -> {result!r}"
                else:
                    msg = f"⇒ [{elapsed:.3f}] {funclog} -> {result!r}"
                logger_func = getattr(log, log_method_name, None)
                if not callable(logger_func):
                    log.warning(f"Некорректный уровень логирования '{level}' для @log_result. Используется TRACE.")
                    logger_func = log.trace if hasattr(log, 'trace') else log.debug  # Fallback

                # Формируем сообщение - обратите внимание на эмодзи, если нужен другой
                # Ваш оригинальный эмодзи был "⭐ ‍️" - это звезда и мужской значок.
                # Возможно, вы хотели просто "⭐" или "✨"
                logger_func(msg)
            return result

        return wrapper

    if _func is None:
        # Вызван как @log_result(level="DEBUG")
        return decorator_log_result
    else:
        # Вызван как @log_result
        return decorator_log_result(_func)

add_stdout()

