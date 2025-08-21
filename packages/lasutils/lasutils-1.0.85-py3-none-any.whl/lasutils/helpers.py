import csv
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Union, Dict, List, Callable
from dateutil.parser import parse, ParserError
import time
from lasutils.exceptions import MissingEnvironmentVariable, ErroneousEnvironmentVariable

log = logging.getLogger()


def get_env(
    env_var: str,
    default=None,
    required: bool = False,
    valid_options: list = None,
    is_path: bool = False,
    is_json: bool = False,
    is_datetime: bool = False,
    is_list: bool = False,
):
    env = os.getenv(env_var, default)
    if required and not env:
        logging.error(f"Environment variable {env_var} is required.")
        raise MissingEnvironmentVariable(f"Environment variable {env_var} is required.")
    if not env:
        return default
    if valid_options and env not in valid_options:
        raise ErroneousEnvironmentVariable(
            f"{env} not a valid option: {valid_options}."
        )
    if is_path:
        return str(Path(env).absolute())
    if is_json:
        if env:
            return json.loads(env)
        return {}
    if is_datetime:
        try:
            return parse(env)
        except ParserError as err:
            raise ErroneousEnvironmentVariable(
                f"Cannot parse date: {env}, Error: {err}"
            )
    if is_list:
        return env.split(".") if type(env) == str else default
    return env


def get_nested(data: dict, keys: list):
    if data:
        return get_nested(data[keys[0]], keys[1:]) if keys else data
    return None


def set_nested(
    data: dict, keys: list, value: Union[str, int, float, Dict, List, Callable]
):
    if len(keys) > 1:
        if isinstance(data, list):
            for idx, _ in enumerate(data):
                set_nested(data[idx], keys, value)
        else:
            if data.get(keys[0]):
                set_nested(data[keys[0]], keys[1:], value)
    else:
        if isinstance(data, list):
            for idx, _ in enumerate(data):
                if data[idx].get(keys[0]):
                    data[idx][keys[0]] = value
        else:
            if data.get(keys[0]):
                data[keys[0]] = (
                    value(data[keys[0]]) if isinstance(value, Callable) else value
                )


def generate_hash(item: Union[Dict, str]) -> str:
    if isinstance(item, str):
        return hashlib.md5(item.encode("utf-8")).hexdigest()
    return hashlib.md5(json.dumps(item).encode("utf-8")).hexdigest()


# Return <sleep time>, <count>
def sleep_ticker(wakeup_interval: int):
    t = time.time()
    round = 0
    # First tick
    yield round
    while True:
        t += wakeup_interval
        round += 1
        time.sleep(max(t - time.time(), 0))
        yield round


# do_every(1,<function>,<args>)
def do_every(period, f, *args):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            t += period
            count += period
            yield max(t - time.time(), 0), count

    g = g_tick()
    while True:
        try:
            sleep_time, count = next(g)
            time.sleep(sleep_time)
            # time.sleep(next(g))
            f(count, *args)
        except KeyboardInterrupt:
            logging.info(f"Time loop interrupted.")
            break


class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[90m"
    green = "\x1b[92m"
    yellow = "\x1b[93m"
    red = "\x1b[91m"
    reset = "\x1b[0m"
    format = "%(asctime)s | %(levelname)-5.5s | %(module)-12.12s | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: reset + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: red + format + reset,
    }

    def format(self, record):
        record.levelname = "WARN" if record.levelname == "WARNING" else record.levelname
        record.levelname = (
            "ERROR" if record.levelname == "CRITICAL" else record.levelname
        )
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_csv_report(dir: str, filename: str, items: list):
    if not items:
        log.warning(f"No data found. Report not created.")
        return
    try:
        csv_file_name = f"{dir}/{filename}"
        with open(csv_file_name, "w", encoding="utf-8-sig", newline="") as csv_file:
            fieldnames = {}
            for item in items:
                # keys = list(item)
                fieldnames |= item
            fieldnames = list(fieldnames)
            # fieldnames = items[0].keys()
            csv_writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                restval=" ",
                delimiter=";",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                dialect="excel",
            )
            csv_writer.writeheader()
            res = csv_writer.writerows(items)
            log.info(f"Wrote file {csv_file_name}")
    except Exception as err:
        log.error(f"Failed to write file. Error: {err}")


def localize(num: float) -> str:
    return str(num).replace(".", ",") if isinstance(num, float) else num
