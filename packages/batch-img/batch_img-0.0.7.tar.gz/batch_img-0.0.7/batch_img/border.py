"""class Border: add border to the image file(s)
Copyright © 2025 John Liu
"""

from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image

from batch_img.common import Common

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Border:
    @staticmethod
    def add_border_1_image(
        in_path: Path, out_path: Path, border_width: int, border_color: str
    ) -> tuple:
        """Add internal border to an image file, not to expand the size

        Args:
            in_path: input file path
            out_path: output dir path
            border_width: border width int
            border_color: border color str

        Returns:
            tuple: bool, str
        """
        try:
            with Image.open(in_path) as img:
                width, height = img.size
                box = Common.get_crop_box(width, height, border_width)
                cropped_img = img.crop(box)
                bd_img = Image.new(img.mode, (width, height), border_color)
                bd_img.paste(cropped_img, (border_width, border_width))

                out_path.mkdir(parents=True, exist_ok=True)
                out_file = out_path
                if out_path.is_dir():
                    filename = f"{in_path.stem}_bw{border_width}{in_path.suffix}"
                    out_file = Path(f"{out_path}/{filename}")
                exif_dict = None
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                if exif_dict:
                    exif_bytes = piexif.dump(exif_dict)
                    bd_img.save(out_file, img.format, optimize=True, exif=exif_bytes)
                else:
                    bd_img.save(out_file, img.format, optimize=True)
            logger.info(f"Saved {out_file}")
            return True, out_file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def add_border_all_in_dir(
        in_path: Path, out_path: Path, border_width: int, border_color: str
    ) -> bool:
        """Add border to all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path
            border_width: border width int
            border_color: border color str

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        if not image_files:
            logger.error(f"No image files at {in_path}")
            return False
        tasks = [(f, out_path, border_width, border_color) for f in image_files]
        files_cnt = len(tasks)

        logger.info(f"Add border to {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Border.add_border_1_image, "Add border to image files", tasks
        )
        logger.info(f"\nSuccessfully added border to {success_cnt}/{files_cnt} files")
        return True
