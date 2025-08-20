"""class Rotate: rotate image file(s) to clockwise angle
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image

from batch_img.common import Common
from batch_img.const import REPLACE

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Rotate:
    @staticmethod
    def rotate_1_image(in_path: Path, out_path: Path | str, angle_cw: int) -> tuple:
        """Rotate an image file and save to the output dir

        Args:
            in_path: input file path
            out_path: output dir path or REPLACE
            angle_cw: rotation angle clockwise: 90, 180, or 270

        Returns:
            tuple: bool, str
        """
        if angle_cw not in {90, 180, 270}:
            return False, f"Bad {angle_cw=}. Only allow 90, 180, 270"
        try:
            with Image.open(in_path) as img:
                exif_dict = {"0th": {}, "Exif": {}}
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)

                if out_path == REPLACE:
                    file = Path(f"{in_path.parent}/{in_path.stem}_tmp{in_path.suffix}")
                else:
                    file = Common.set_out_file(in_path, out_path, f"{angle_cw}cw")
                # img.rotate() for any angle (slower & slight quality loss)
                rotated_img = img
                if angle_cw == 90:
                    rotated_img = img.transpose(Image.ROTATE_270)
                elif angle_cw == 180:
                    rotated_img = img.transpose(Image.ROTATE_180)
                elif angle_cw == 270:
                    rotated_img = img.transpose(Image.ROTATE_90)

                rotated_img.save(file, img.format, exif=exif_bytes, optimize=True)
            logger.info(f"Saved ({angle_cw}°) clockwise rotated to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                logger.info(f"Replaced {in_path} with tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            logger.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def rotate_all_in_dir(in_path: Path, out_path: Path | str, angle_cw: int) -> bool:
        """Rotate all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            angle_cw: rotation angle clockwise: 90, 180, or 270

        Returns:
            bool: True - Success. False - Error
        """
        if angle_cw not in {90, 180, 270}:
            logger.error(f"Bad {angle_cw=}. Only allow 90, 180, 270")
            return False
        image_files = Common.prepare_all_files(in_path, out_path)
        if not image_files:
            logger.error(f"No image files at {in_path}")
            return False
        tasks = [(f, out_path, angle_cw) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            logger.error(f"No image files at {in_path}")
            return False

        logger.info(f"Rotate {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Rotate.rotate_1_image, "Rotate image files", tasks
        )
        logger.info(f"\nSuccessfully rotated {success_cnt}/{files_cnt} files")
        return True

    @staticmethod
    def set_exif_orientation(file: Path, o_val: int) -> bool:
        """Set orientation in the EXIF of an image file

        Args:
            file: image file path
            o_val: orientation value int

        Returns:
            bool: True - Success. False - Error
        """
        if o_val not in {1, 2, 3, 4, 5, 6, 7, 8}:
            logger.error(f"Quit due to bad orientation value: {o_val=}")
            return False
        try:
            tmp_file = Path(f"{file.parent}/{file.stem}_tmp{file.suffix}")
            with Image.open(file) as img:
                exif_dict = {"0th": {}, "Exif": {}}
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                exif_dict["0th"][piexif.ImageIFD.Orientation] = o_val
                exif_bytes = piexif.dump(exif_dict)
                img.save(tmp_file, img.format, exif=exif_bytes, optimize=True)
            logger.info(f"Saved the updated EXIF image to {tmp_file}")
            os.replace(tmp_file, file)
            logger.info(f"Replaced {file} with tmp_file")
            return True
        except (AttributeError, FileNotFoundError, ValueError) as e:
            logger.error(e)
            return False
