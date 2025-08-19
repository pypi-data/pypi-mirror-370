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

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Rotate:
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

    @staticmethod
    def rotate_1_image_file(in_path: Path, out_path: Path, angle_cw: int) -> tuple:
        """Rotate an image file and save to the output dir

        Args:
            in_path: input file path
            out_path: output dir path
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
                # logger.info(f"{exif_dict=}")
                exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)

                out_path.mkdir(parents=True, exist_ok=True)
                out_file = out_path
                if out_path.is_dir():
                    filename = f"{in_path.stem}_{angle_cw}cw{in_path.suffix}"
                    out_file = Path(f"{out_path}/{filename}")
                # img.rotate() for any angle (slower & slight quality loss)
                if angle_cw == 90:
                    rotated_img = img.transpose(Image.ROTATE_270)
                elif angle_cw == 180:
                    rotated_img = img.transpose(Image.ROTATE_180)
                elif angle_cw == 270:
                    rotated_img = img.transpose(Image.ROTATE_90)
                else:
                    rotated_img = img

                rotated_img.save(out_file, img.format, exif=exif_bytes, optimize=True)
            logger.info(f"Saved ({angle_cw}°) clockwise rotated to {out_file}")
            return True, out_file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def rotate_all_in_dir(in_path: Path, out_path: Path, angle_cw: int) -> bool:
        """Rotate all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path
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

        logger.info(f"Rotate {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Rotate.rotate_1_image_file, "Rotate image files", tasks
        )
        logger.info(f"\nSuccessfully rotated {success_cnt}/{files_cnt} files")
        return True
