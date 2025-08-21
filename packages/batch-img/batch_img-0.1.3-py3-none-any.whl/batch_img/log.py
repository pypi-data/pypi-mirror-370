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
        level = config.get("level")
        mode = config.get("mode")
        if mode.lower() == "dev":
            logformat = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
            backtrace = True
            diagnose = True
        else:
            # prod output
            logformat = "{time:HH:mm:ss} | {process} | {level} | {message}"
            backtrace = False
            diagnose = False
        logger.add(
            sys.stderr,
            level=level,
            format=logformat,
            backtrace=backtrace,
            diagnose=diagnose,
        )
        pid = os.getpid()
        Log._file = f"run_{PKG_NAME}_{pid}_{datetime.now().strftime(TS_FORMAT)}.log"
        log_f = f"{os.getcwd()}/{Log._file}"
        logger.add(
            log_f, level=level, format=logformat, backtrace=backtrace, diagnose=diagnose
        )
        return Log._file

    @staticmethod
    def set_worker_log():
        """Set up the logger for each worker process in multiprocessing

        Returns:
            logger: for this worker process
        """
        logger.remove()
        config = Log.load_config(f"{dirname(__file__)}/config.json")
        level = config.get("level")
        mode = config.get("mode")
        if mode.lower() == "dev":
            logformat = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
            bktrace = True
            diag = True
        else:
            # prod output
            logformat = "{time:HH:mm:ss} | {process} | {level} | {message}"
            bktrace = False
            diag = False
        logger.add(
            sys.stderr,
            level=level,
            format=logformat,
            backtrace=bktrace,
            diagnose=diag,
        )
        # JL 2025-08-20: skip due to too many run_{pid}_batch_img_*.log files
        # f = f"run_{os.getpid()}_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        # logger.add(
        #     f, level=level, format=logformat, backtrace=bktrace, diagnose=diag
        # )
        return logger
