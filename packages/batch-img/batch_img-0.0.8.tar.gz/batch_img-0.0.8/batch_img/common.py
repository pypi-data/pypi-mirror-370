"""class Common: common utilities
Copyright © 2025 John Liu
"""

import itertools
import json
import subprocess
import tomllib
from datetime import datetime
from importlib.metadata import version
from multiprocessing import Pool, cpu_count
from os.path import getmtime, getsize
from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image, ImageChops
from PIL.TiffImagePlugin import IFDRational
from tqdm import tqdm

from batch_img.const import PATTERNS, PKG_NAME, REPLACE, TS_FORMAT, VER

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Common:
    @staticmethod
    def get_version() -> str:
        """
        Get this package version using several ways
        """
        try:
            return version(PKG_NAME)
        except (FileNotFoundError, ImportError, ValueError) as e:
            # Use lazy % formatting in logging for efficiency
            logger.warning(f"importlib.metadata.version Error: {e}")
            logger.debug("Try to get version from pyproject.toml file")
            pyproject = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject, "rb") as f:
                return tomllib.load(f)["project"][VER]

    @staticmethod
    def run_cmd(cmd: str) -> tuple:
        """Run a command on the host and get the output

        Args:
            cmd (str): a command line with options

        Returns:
            tuple: returnCode, StdOut, StdErr
        """
        logger.debug(f"{cmd=}")
        try:
            p = subprocess.run(
                cmd, capture_output=True, text=True, shell=True, check=True
            )
            r_code = p.returncode
            stdout = p.stdout
            stderr = p.stderr
            logger.debug(f"'{cmd}'\n {r_code=}\n {stdout=}\n {stderr=}")
            return r_code, stdout, stderr
        except subprocess.CalledProcessError as e:
            logger.exception(e)
            raise e

    @staticmethod
    def readable_file_size(in_bytes: int) -> str:
        """Convert bytes to human-readable KB, MB, or GB

        Args:
            in_bytes: input bytes integer

        Returns:
            str
        """
        for _unit in ["B", "KB", "MB", "GB"]:
            if in_bytes < 1024:
                break
            in_bytes /= 1024
        res = f"{in_bytes} B" if _unit == "B" else f"{in_bytes:.1f} {_unit}"
        return res

    @staticmethod
    def decode_exif(exif_data: str) -> dict:
        """Decode the EXIF data

        Args:
            exif_data: str

        Returns:
            dict
        """
        exif_dict = piexif.load(exif_data)
        _dict = {}
        for ifd_name, val in exif_dict.items():
            # Canon EOS 5D Mark II 'thumbnail': b'\xff\xd8\xff\xdb...
            # 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
            if not val or ifd_name == "thumbnail":
                continue
            for tag_id, value in val.items():
                tag_name = piexif.TAGS[ifd_name].get(tag_id, {}).get("name", tag_id)
                _dict[tag_name] = value
        # logger.info(f"{_dict=}")
        for key in (
            "FNumber",
            "FocalLength",
            "MakerNote",
            "SceneType",
            "SubjectArea",
            "Software",
            "HostComputer",
            "UserComment",
        ):
            if key in _dict:
                _dict.pop(key)
        keys = list(_dict.keys())
        for keyword in (
            "DateTime",
            "GPS",
            "OffsetTime",
            "SubSecTime",
            "Tile",
            "Pixel",
            "Lens",
            "Resolution",
            "Value",
        ):
            for key in keys:
                if key.startswith(keyword) or key.endswith(keyword):
                    _dict.pop(key)
        _res = {
            k: (v.decode() if isinstance(v, bytes) else v) for k, v in _dict.items()
        }
        logger.info(f"{_res=}")
        return _res

    @staticmethod
    def get_image_data(file: Path) -> tuple:
        """Get image file data

        Args:
            file: image file path

        Returns:
            tuple: data, info
        """
        size = getsize(file)
        m_ts = datetime.fromtimestamp(getmtime(file)).strftime(TS_FORMAT)
        with Image.open(file) as img:
            data = img.convert("RGB")
            d_info = {
                "file_size": Common.readable_file_size(size),
                "file_ts": m_ts,
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "info": img.info,
            }
            for key in ("icc_profile", "xmp"):
                if key in img.info:
                    img.info.pop(key)
            if "exif" in img.info:
                exif_data = img.info.pop("exif")
                d_info["exif"] = Common.decode_exif(exif_data)

        return data, d_info

    @staticmethod
    def jsn_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, IFDRational):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    @staticmethod
    def are_images_equal(path1: Path, path2: Path) -> bool:
        """Check if two image files are visually equal pixel-wise

        Args:
            path1: image1 file path
            path2: image2 file path

        Returns:
            bool: True - visually equal, False - not visually equal
        """
        data1, meta1 = Common.get_image_data(path1)
        data2, meta2 = Common.get_image_data(path2)

        logger.info(
            f"{path1}:\n{json.dumps(meta1, indent=2, default=Common.jsn_serial)}"
        )
        logger.info(
            f"{path2}:\n{json.dumps(meta2, indent=2, default=Common.jsn_serial)}"
        )
        return ImageChops.difference(data1, data2).getbbox() is None

    @staticmethod
    def get_crop_box(width, height, border_width) -> tuple[float, float, float, float]:
        """Get the crop box tuple

        Args:
            width: image width int
            height: image height int
            border_width: border width int

        Returns:
            tuple[float, float, float, float]
        """
        crop_left = border_width
        crop_top = border_width
        crop_right = width - border_width
        crop_bottom = height - border_width
        return crop_left, crop_top, crop_right, crop_bottom

    @staticmethod
    def prepare_all_files(in_path: Path, out_path: Path | str):
        """

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE

        Returns:
            iterable: files list generator
        """
        if out_path != REPLACE:
            out_path.mkdir(parents=True, exist_ok=True)
        _files = itertools.chain.from_iterable(in_path.glob(p) for p in PATTERNS)
        return _files

    @staticmethod
    def multiprocess_progress_bar(func, desc, tasks: list) -> int:
        """Run task in multiprocess with progress bar

        Args:
            func: function to be run in multiprocess
            desc: description str
            tasks: tasks list for multiprocess pool

        Returns:
            int: success_cnt
        """
        success_cnt = 0
        files_cnt = len(tasks)
        workers = max(cpu_count(), 4)

        with Pool(workers) as pool:
            with tqdm(total=files_cnt, desc=desc) as pbar:
                for ok, res in pool.starmap(func, tasks):
                    if ok:
                        success_cnt += 1
                    else:
                        tqdm.write(f"Error: {res}")
                    pbar.update()
        return success_cnt

    @staticmethod
    def set_out_file(in_path: Path, out_path: Path, extra: str) -> Path:
        """Set the output file path

        Args:
            in_path: input file path
            out_path: output dir path
            extra: extra str in output file name

        Returns:
            Path:
        """
        out_path.mkdir(parents=True, exist_ok=True)
        out_file = out_path
        if out_path.is_dir():
            filename = f"{in_path.stem}_{extra}{in_path.suffix}"
            out_file = Path(f"{out_path}/{filename}")
        return out_file
