"""class Orientation: detect if the image file(s) is upside down or sideways
Copyright © 2025 John Liu
"""

from pathlib import Path

import cv2
import numpy as np
import pillow_heif
from loguru import logger
from PIL import Image

from batch_img.common import Common

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files

ORIENTATION_MAP = {
    1: "normal",
    2: "mirrored_horizontal",
    3: "upside_down",
    4: "mirrored_vertical",
    5: "rotated_left_mirrored",
    6: "rotated_left",
    7: "rotated_right_mirrored",
    8: "rotated_right",
}
EXIF_CW_ANGLE = {
    1: 0,
    2: 0,
    3: 180,
    4: 180,
    5: 270,
    6: 270,
    7: 90,
    8: 90,
}


class Orientation:
    @staticmethod
    def exif_orientation_2_cw_angle(file: Path) -> int:
        """Get image orientation by EXIF data

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270
        """
        try:
            with Image.open(file) as img:
                if "exif" not in img.info:
                    logger.warning(f"No EXIF data in {file}")
                    return -1
                exif_info = Common.decode_exif(img.info["exif"])
                if "Orientation" in exif_info:
                    return EXIF_CW_ANGLE.get(exif_info["Orientation"])
            logger.warning(f"No 'Orientation' tag in {exif_info=}")
            return -1
        except (AttributeError, FileNotFoundError, ValueError) as e:
            logger.error(e)
            return -1

    @staticmethod
    def _rotate_image(img, angle: int):
        """Helper to rotate image by the clock wise angle degree

        Args:
            img: image data
            angle: angle degree int: 0, 90, 180, 270

        Returns:
            image data
        """
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    def get_cw_angle_by_face(self, file: Path) -> int:
        """Detect orientation by face in mage by Haar Cascades:
        * Fastest but least accurate
        * Works best with frontal faces
        * May produce false positives

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270
        """
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        with Image.open(file) as safe_img:
            opencv_img = np.array(safe_img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")
            for angle_cw in (0, 90, 180, 270):
                img = self._rotate_image(opencv_img, angle_cw)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.2, minNeighbors=6
                )
                # logger.info(f"{len(faces)=}")
                if len(faces) > 0:
                    return angle_cw
        logger.warning(f"Found no face in {file}")
        return -1
