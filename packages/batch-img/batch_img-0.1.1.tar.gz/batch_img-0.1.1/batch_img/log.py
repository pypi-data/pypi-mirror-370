"""class Log - config logging
Copyright © 2025 John Liu
"""

import json
import os
import sys
from datetime import datetime
from os.path import dirname

from loguru import logger

from batch_img.const import PKG_NAME, TS_FORMAT


class Log:
    _file = ""

    @staticmethod
    def load_config(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Logging config file not found: {path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {}

    @staticmethod
    def init_log_file() -> str:
        """Set up the unique name log file for each run

        Returns:
            str: log file path
        """
        if Log._file:  # init only once
            return Log._file

        logger.remove()
        config = Log.load_config(f"{dirname(__file__)}/config.json")
        mode = config.get("mode", "dev").lower()
        level = config.get("level")
        if mode == "dev":
            # verbose, colorful
            logger.add(
                sys.stderr,
                level=level,
                format=(
                    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                    "<level>{message}</level>"
                ),
                backtrace=True,
                diagnose=True,
            )
        else:
            # cleaner output
            logger.add(
                sys.stderr,
                level=level,
                format="{time:HH:mm:ss} | {level} | {message}",
                backtrace=False,
                diagnose=False,
            )
        Log._file = f"run_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        log_f = f"{os.getcwd()}/{Log._file}"
        logger.add(log_f, backtrace=True, diagnose=True, enqueue=True)
        return Log._file


log = logger
