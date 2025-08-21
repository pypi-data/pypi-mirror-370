"""class Auto - do auto actions to the image file(s):
    * Resize to 1280 pixels as the max length
    * Add the border of 5 pixel width in green color
    * Auto-rotate if upside down or sideways
Copyright © 2025 John Liu
"""

from pathlib import Path

import piexif
import pillow_heif
from PIL import Image

from batch_img.common import Common
from batch_img.const import BD_COLOR, BD_WIDTH, MAX_LENGTH
from batch_img.log import logger
from batch_img.orientation import Orientation
from batch_img.rotate import Rotate

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Auto:
    @staticmethod
    def resize_add_border(in_path: Path, out_path: Path) -> tuple:
        """Resize and add border to an image file:
        * 1280 as the max length
        * the border of 5-pixel width in green color

        Args:
            in_path: input file path
            out_path: output dir path

        Returns:
            tuple: bool, str
        """
        try:
            with Image.open(in_path) as img:
                # Resize
                max_size = (MAX_LENGTH, MAX_LENGTH)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Add border
                width, height = img.size
                logger.debug(f"{width=}, {height=}")
                box = Common.get_crop_box(width, height, BD_WIDTH)
                cropped_img = img.crop(box)
                bd_img = Image.new(img.mode, (width, height), BD_COLOR)
                bd_img.paste(cropped_img, (BD_WIDTH, BD_WIDTH))

                out_path.mkdir(parents=True, exist_ok=True)
                out_file = out_path
                if out_path.is_dir():
                    filename = (
                        f"{in_path.stem}_{MAX_LENGTH}_bw{BD_WIDTH}{in_path.suffix}"
                    )
                    out_file = Path(f"{out_path}/{filename}")

                exif_dict = None
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                if exif_dict:
                    exif_bytes = piexif.dump(exif_dict)
                    bd_img.save(out_file, img.format, optimize=True, exif=exif_bytes)
                else:
                    bd_img.save(out_file, img.format, optimize=True)
            logger.debug(f"Saved {out_file}")
            return True, out_file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def rotate_if_needed(in_path: Path, out_path: Path) -> tuple:
        """Rotate if the image is upside down or sideways

        Args:
            in_path: image file path
            out_path: output dir path

        Returns:
            tuple: bool, file path
        """
        # JL 2025-08-18: not get orientation from EXIF as it's unreliable
        # cw_angle = Orientation.exif_orientation_2_cw_angle(in_path)
        # logger.info(f"From exif: {cw_angle=}")
        cw_angle = Orientation.get_orientation_by_floor(in_path)
        logger.debug(f"By face: {cw_angle=}")
        if cw_angle in {-1, 0}:
            logger.warning(f"Skip due to bad or 0 clockwise angle: {cw_angle=}")
            return False, in_path
        ok, out_file = Rotate.rotate_1_image((in_path, out_path, cw_angle))
        return ok, out_file

    @staticmethod
    def do_actions(args: tuple) -> tuple:
        """Do default actions on one image file:
        * Resize to 1280 pixels as the max length
        * Add the border of 5 pixel width in green color
        * Auto-rotate if upside down or sideways

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path

        Returns:
            tuple: bool, str
        """
        in_path, out_path = args
        Common.set_log_by_process()
        _, file = Auto.rotate_if_needed(in_path, out_path)
        return Auto.resize_add_border(file, out_path)

    @staticmethod
    def run_on_all(in_path: Path, out_path: Path) -> bool:
        """Apply default actions on all images in a folder

        Args:
            in_path: input file path
            out_path: output dir path

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            logger.error(f"No image files at {in_path}")
            return False

        logger.debug(f"Do auto actions on {files_cnt} files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Auto.do_actions, "Auto actions on image files", tasks
        )
        logger.info(f"\nFinished auto actions on {success_cnt}/{files_cnt} files")
        return True
