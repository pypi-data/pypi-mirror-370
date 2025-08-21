"""class Orientation: detect if the image file(s) is upside down or sideways
Copyright © 2025 John Liu
"""

from pathlib import Path

import cv2
import numpy as np
import pillow_heif
from PIL import Image

from batch_img.common import Common
from batch_img.log import log

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files

ROTATION_MAP = {  # map to the clockwise angle to correct
    "bottom": 0,
    "top": 180,
    "left": 270,  # rotated right
    "right": 90,  # rotated left
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
                    log.warning(f"No EXIF data in {file}")
                    return -1
                exif_info = Common.decode_exif(img.info["exif"])
                if "Orientation" in exif_info:
                    return EXIF_CW_ANGLE.get(exif_info["Orientation"])
            log.warning(f"No 'Orientation' tag in {exif_info=}")
            return -1
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
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
        """Get image orientation by face using Haar Cascades:
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
                if len(faces) > 0:
                    return angle_cw
        log.warning(f"Found no face in {file}")
        return -1

    @staticmethod
    def get_orientation_by_floor(file: Path) -> int:
        """Get image orientation by floor

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270
        """
        with Image.open(file) as img:
            opencv_img = np.array(img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")

        # Convert to HSV for color-based floor detection
        hsv = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2HSV)
        # Heuristic: floors are often low saturation, medium-low value (gray/brown)
        lower_floor = np.array([0, 0, 30])
        upper_floor = np.array([180, 100, 180])
        mask = cv2.inRange(hsv, lower_floor, upper_floor)

        h, w, _ = opencv_img.shape
        regions = {  # Divide image into 4 regions
            "top": mask[0 : h // 3, :],
            "bottom": mask[2 * h // 3 :, :],
            "left": mask[:, 0 : w // 3],
            "right": mask[:, 2 * w // 3 :],
        }
        counts = {k: cv2.countNonZero(v) for k, v in regions.items()}
        log.debug(f"Floor pixels cnt: {counts=}")

        max_region = max(counts, key=counts.get)
        cw_angle = ROTATION_MAP.get(max_region, -1)
        return cw_angle

    @staticmethod
    def get_cw_angle_by_sky(file: Path) -> int:
        """Get image orientation by sky, clouds

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270
        """
        with Image.open(file) as img:
            opencv_img = np.array(img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")

        hsv = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2HSV)
        sky_lower = np.array([90, 20, 70])
        sky_upper = np.array([140, 255, 255])

        cloud_lower = np.array([0, 0, 180])
        cloud_upper = np.array([180, 70, 255])

        sky_mask = cv2.inRange(hsv, sky_lower, sky_upper)
        cloud_mask = cv2.inRange(hsv, cloud_lower, cloud_upper)
        sky_cloud_mask = cv2.bitwise_or(sky_mask, cloud_mask)

        h, w, _ = opencv_img.shape
        regions = {
            "top": sky_cloud_mask[0 : h // 3, :],
            "bottom": sky_cloud_mask[2 * h // 3 :, :],
            "left": sky_cloud_mask[:, 0 : w // 3],
            "right": sky_cloud_mask[:, 2 * w // 3 :],
        }
        counts = {k: cv2.countNonZero(v) for k, v in regions.items()}
        log.debug(f"Sky/Cloud pixels cnt: {counts=}")
        return ROTATION_MAP.get(max(counts, key=counts.get), -1)
