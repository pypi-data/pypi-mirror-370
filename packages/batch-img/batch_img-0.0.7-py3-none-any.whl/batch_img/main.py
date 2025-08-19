"""class Main: the entry point of the tool
Copyright © 2025 John Liu
"""

import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from batch_img.border import Border
from batch_img.const import PKG_NAME, TS_FORMAT
from batch_img.defaults import Defaults
from batch_img.resize import Resize
from batch_img.rotate import Rotate


class Main:
    @staticmethod
    def init_log_file() -> str:
        """Set up the unique name log file for each run

        Returns:
            str: log file path
        """
        log_file = f"run_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        logger.add(
            f"{os.getcwd()}/{log_file}", backtrace=True, diagnose=True, enqueue=True
        )
        return log_file

    @staticmethod
    def resize(options: dict) -> bool:
        """Resize the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        in_path = Path(options["src_path"])
        length = options.get("length")
        output = options.get("output")
        if not length or length == 0:
            logger.warning(f"No resize due to bad {length=}")
            return False
        if not output:
            output = Path(os.getcwd())
        else:
            output = Path(output)
        if in_path.is_file():
            ok, _ = Resize.resize_an_image(in_path, output, length)
        else:
            ok = Resize.resize_all_progress_bar(in_path, output, length)
        return ok

    @staticmethod
    def rotate(options: dict) -> bool:
        """Rotate the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        in_path = Path(options["src_path"])
        angle = options.get("angle")
        output = options.get("output")
        if not angle or angle == 0:
            logger.warning(f"No rotate due to bad {angle=}")
            return False
        if not output:
            output = Path(os.getcwd())
        else:
            output = Path(output)
        if in_path.is_file():
            ok, _ = Rotate.rotate_1_image_file(in_path, output, angle)
        else:
            ok = Rotate.rotate_all_in_dir(in_path, output, angle)
        return ok

    @staticmethod
    def border(options: dict) -> bool:
        """Add border to the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        in_path = Path(options["src_path"])
        bd_width = options.get("border_width")
        bd_color = options.get("border_color")
        output = options.get("output")
        if not bd_width or bd_width == 0:
            logger.warning(f"No add border due to bad {bd_width=}")
            return False
        if not output:
            output = Path(os.getcwd())
        else:
            output = Path(output)
        if in_path.is_file():
            ok, _ = Border.add_border_1_image(in_path, output, bd_width, bd_color)
        else:
            ok = Border.add_border_all_in_dir(in_path, output, bd_width, bd_color)
        return ok

    @staticmethod
    def default_run(options: dict) -> bool:
        """Do the default action on the image file(s):
        * Resize to 1280 pixels as the max length
        * Add the border of 5 pixel width in green color
        * Auto-rotate if upside down or sideways
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        in_path = Path(options["src_path"])
        output = options.get("output")
        if not output:
            output = Path(os.getcwd())
        else:
            output = Path(output)
        if in_path.is_file():
            ok, _ = Defaults.do_actions(in_path, output)
        else:
            ok = Defaults.run_on_all(in_path, output)
        return ok
