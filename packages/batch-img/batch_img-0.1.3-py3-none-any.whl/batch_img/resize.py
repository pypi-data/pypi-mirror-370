"""class Resize: resize the image file(s)
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import piexif
import pillow_heif
from PIL import Image

from batch_img.common import Common
from batch_img.const import REPLACE
from batch_img.log import logger

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Resize:
    @staticmethod
    def resize_an_image(args: tuple) -> tuple:
        """Resize an image file and save to the output dir

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE
            length: max pixels length (width or height)

        Returns:
            tuple: bool, output file path
        """
        in_path, out_path, length = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                max_size = (length, length)
                # The thumbnail() keeps the original aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                file = Common.set_out_file(in_path, out_path, f"{length}")
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(file, img.format, optimize=True, exif=exif_bytes)
                else:
                    img.save(file, img.format, optimize=True)
            logger.debug(f"Saved resized image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                logger.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            logger.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def resize_all_progress_bar(
        in_path: Path, out_path: Path | str, length: int
    ) -> bool:
        """Resize all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            length: max length (width or height) in pixels

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        if not image_files:
            logger.error(f"No image files at {in_path}")
            return False
        tasks = [(f, out_path, length) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            logger.error(f"No image files at {in_path}")
            return False

        logger.debug(f"Resize {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Resize.resize_an_image, "Resize image files", tasks
        )
        logger.info(f"\nSuccessfully resized {success_cnt}/{files_cnt} files")
        return True
