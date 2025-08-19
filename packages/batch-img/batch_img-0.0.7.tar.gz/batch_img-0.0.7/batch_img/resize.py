"""class Resize: resize the image file(s)
Copyright © 2025 John Liu
"""

from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image

from batch_img.common import Common

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Resize:
    @staticmethod
    def resize_an_image(in_path: Path, out_path: Path, length: int) -> tuple:
        """Resize an image file and save to the output dir

        Args:
            in_path: input file path
            out_path: output dir path
            length: max length (width or height) in pixels

        Returns:
            tuple: bool, output file path
        """
        try:
            with Image.open(in_path) as img:
                max_size = (length, length)
                # The thumbnail() keeps the original aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                out_path.mkdir(parents=True, exist_ok=True)
                out_file = out_path
                if out_path.is_dir():
                    filename = f"{in_path.stem}_{length}{in_path.suffix}"
                    out_file = Path(f"{out_path}/{filename}")

                exif_dict = None
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                if exif_dict:
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(out_file, img.format, optimize=True, exif=exif_bytes)
                else:
                    img.save(out_file, img.format, optimize=True)
            logger.info(f"Saved {out_file}")
            return True, out_file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def resize_all_progress_bar(in_path: Path, out_path: Path, length: int) -> bool:
        """Resize all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path
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

        logger.info(f"Resize {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Resize.resize_an_image, "Resize image files", tasks
        )
        logger.info(f"\nSuccessfully resized {success_cnt}/{files_cnt} files")
        return True
