from datetime import timezone, datetime, timedelta, date
import logging
import re
from time import time
from typing import Tuple, Optional

import aiohttp
from aiohttp import ClientResponse


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__


def timestamp() -> int:
    return int(time())


def get_moscow_datetime():
    est_timezone = timezone(timedelta(hours=3))

    return datetime.now(est_timezone)


def get_moscow_date():
    return get_moscow_datetime().date()


def current_data_add(
    days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0
):
    return date.today() + timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )


def get_logger(
    name: str | int = None, label: str = "", filename: str = None
) -> logging.Logger:
    if label != "":
        label = f"\t[{label}]\t"
    else:
        label = "\t"

    # Создание кастомного форматтера
    formatter = logging.Formatter(f"%(asctime)s\t%(levelname)s{label}-\t%(message)s")

    # Настройка логгера
    logger = logging.getLogger(f"custom_logger_{name}")
    logger.setLevel(logging.DEBUG)

    # Создание обработчика (stdout)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # all_handler = logging.FileHandler(filename="../logs/everything.txt", mode="a")
    # all_handler.setFormatter(formatter)
    # logger.addHandler(all_handler)

    # Создание обработчика (file out)
    if filename:
        fh = logging.FileHandler(filename=filename, mode="a")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.addHandler(handler)

    return logger


def digits_only(v: str) -> str:
    if not re.fullmatch(r"\d+", v):
        raise ValueError("Must contain only digits")
    return v


def format_number(v: int) -> str:
    return f"{v:,}".replace(",", " ")


async def get_real_ip(proxy: Optional[str] = None) -> Tuple[ClientResponse, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://ip.8525.ru", proxy=proxy) as response:
            return response, (await response.text()).strip()
