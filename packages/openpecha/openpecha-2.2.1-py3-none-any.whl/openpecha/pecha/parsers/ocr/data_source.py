import gzip
import json
import os
from pathlib import Path
from zipfile import ZipFile

from bs4 import BeautifulSoup

from openpecha.buda.api import get_image_list as buda_get_image_list
from openpecha.buda.api import image_group_to_folder_name
from openpecha.config import get_logger
from openpecha.utils import read_json

# Initialize the logger
logger = get_logger(__name__)


class GoogleVisionSource:
    def __init__(
        self,
        bdrc_scan_id,
        buda_data,
        ocr_import_info,
        ocr_disk_path,
    ):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data

    def get_image_list(self, image_group_id):
        """Get the image list from either local JSON file or BUDA API.

        Args:
            image_group_id (str): Image group ID of the volume

        Returns:
            list: List of image filenames
        """
        # Try to get image list from local file first
        if self.ocr_disk_path and os.path.exists(
            self.ocr_disk_path / f"{image_group_id}.json"
        ):
            buda_il = read_json(self.ocr_disk_path / f"{image_group_id}.json")
            if isinstance(buda_il, list):
                return list(map(lambda ii: ii["filename"], buda_il))
            else:
                logger.error(f"Expected list from read_json, got {type(buda_il)}")
                return []

        # If local file doesn't exist or path not provided, use BUDA API
        try:
            buda_il = buda_get_image_list(self.bdrc_scan_id, image_group_id)
            if isinstance(buda_il, list):
                return list(map(lambda ii: ii["filename"], buda_il))
            else:
                logger.error(
                    f"Expected list from buda_get_image_list, got {type(buda_il)}"
                )
                return []
        except ImportError:
            logger.error("BUDA API module not available")
            return []
        except Exception as e:
            logger.error(f"Error getting image list from BUDA API: {e}")
            return []

    def get_source_info(self):
        return self.buda_data

    def get_image_data(self, image_group_id, image_id):
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        # Fix for 'dict' object has no attribute 'rfind'
        if isinstance(image_id, dict) and "filename" in image_id:
            image_filename = image_id["filename"]
        else:
            image_filename = image_id

        expected_ocr_filename = image_filename[: image_filename.rfind(".")] + ".json.gz"
        image_ocr_path = self.ocr_disk_path / vol_folder / expected_ocr_filename
        ocr_object = None
        try:
            ocr_object = json.load(gzip.open(str(image_ocr_path), "rb"))
        except Exception as e:
            logger.exception(f"could not read {image_ocr_path}: {e}")
        return ocr_object


class BDRCGBSource:
    def __init__(
        self,
        bdrc_scan_id,
        buda_data,
        ocr_import_info,
        ocr_disk_path,
    ):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.image_info = {}
        self.cur_zip = None
        self.cur_image_group_id = None

    def _get_image_list(self, image_group_id):
        """Get the image list from either local JSON file or BUDA API.

        Args:
            image_group_id (str): Image group ID of the volume

        Returns:
            list: List of image filenames
        """
        # Try to get image list from local file first
        if self.ocr_disk_path and os.path.exists(
            self.ocr_disk_path / f"{image_group_id}.json"
        ):
            return read_json(self.ocr_disk_path / f"{image_group_id}.json")

        # If local file doesn't exist or path not provided, use BUDA API
        try:
            return buda_get_image_list(self.bdrc_scan_id, image_group_id)
        except ImportError:
            logger.error("BUDA API module not available")
            return []
        except Exception as e:
            logger.error(f"Error getting image list from BUDA API: {e}")
            return []

    def get_image_list(self, image_group_id):
        self.get_images_info(image_group_id)
        buda_il = self._get_image_list(image_group_id)
        # format should be a list of image_id (/ file names)
        if isinstance(buda_il, list):
            return list(map(lambda ii: ii["filename"], buda_il))
        else:
            logger.error(f"Expected list from _get_image_list, got {type(buda_il)}")
            return []

    def get_hocr_filename(self, image_id):
        if not self.images_info:
            logger.error(
                "images_info is None or empty. Did you forget to call get_images_info()?"
            )
            return None

        for filename, img_ref in self.images_info.items():
            if img_ref == image_id:
                return filename

        logger.warning(f"No matching filename found for image_id: {image_id}")
        return None

    def get_images_info(self, image_group_id):
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        image_info_path = (
            Path(f"{self.ocr_disk_path}") / "info" / vol_folder / "gb-bdrc-map.json"
        )
        self.images_info = read_json(image_info_path)

    def get_source_info(self):
        return self.buda_data

    def get_image_group_data(self, image_group_id):
        if image_group_id == self.cur_image_group_id and self.cur_zip is not None:
            return self.cur_zip
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        zip_path = Path(f"{self.ocr_disk_path}") / "output" / vol_folder / "html.zip"
        self.cur_zip = ZipFile(zip_path)
        return self.cur_zip

    def get_image_data(self, image_group_id, image_filename):
        hocr_filename = self.get_hocr_filename(image_filename) + ".html"
        zf = self.get_image_group_data(image_group_id)
        try:
            for filename in zf.filelist:
                if filename.filename.split("/")[-1] == hocr_filename:
                    with zf.open(filename.filename) as hocr_file:
                        return hocr_file.read()
        except KeyError:
            logger.error(f"Error: {image_filename} not found in image_info.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None


class HOCRIASource:
    def __init__(
        self,
        bdrc_scan_id,
        buda_data,
        ocr_import_info,
        ocr_disk_path,
    ):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.image_hocr = {}
        self.image_info = {}

    def get_image_list(self, image_group_id):
        """Get image list for the given image group ID.

        This method can handle both local JSON files and BUDA API calls.

        Args:
            image_group_id (str): Image group ID of the volume

        Returns:
            list: List of image filenames
        """
        self.get_images_info(image_group_id)
        buda_il = self._get_image_list(image_group_id)
        # format should be a list of image_id (/ file names)
        if isinstance(buda_il, list):
            return list(map(lambda ii: ii["filename"], buda_il))
        else:
            logger.error(f"Expected list from _get_image_list, got {type(buda_il)}")
            return []

    def _get_image_list(self, image_group_id):
        """Get the raw image list data from either local file or BUDA API.

        Args:
            image_group_id (str): Image group ID of the volume

        Returns:
            list: Raw image list data
        """
        # Try to get image list from local file first
        if self.ocr_disk_path and os.path.exists(
            self.ocr_disk_path / f"{image_group_id}.json"
        ):
            return read_json(self.ocr_disk_path / f"{image_group_id}.json")

        # If local file doesn't exist or path not provided, use BUDA API
        try:
            return buda_get_image_list(self.bdrc_scan_id, image_group_id)
        except ImportError:
            logger.error("BUDA API module not available")
            return []
        except Exception as e:
            logger.error(f"Error getting image list from BUDA API: {e}")
            return []

    def get_images_info(self, image_group_id):
        curr_image = {}
        image_list = self._get_image_list(image_group_id)
        image_group_hocr = self.get_image_group_hocr(image_group_id)
        if image_group_hocr:
            hocr_html = BeautifulSoup(image_group_hocr, "html.parser")
            pages_hocr = hocr_html.find_all("div", {"class": "ocr_page"})
            for image_number, image_filename in enumerate(image_list):
                filename = image_filename["filename"]
                for page_hocr in pages_hocr:
                    if int(page_hocr["id"][5:]) == image_number:
                        curr_image[filename] = {"page_info": page_hocr}
                        self.image_info.update(curr_image)
                        curr_image = {}

    def get_image_group_hocr(self, image_group_id):
        vol_num = self.buda_data["image_groups"][image_group_id]["volume_number"]
        image_group_hocr_path = (
            Path(f"{self.ocr_disk_path}")
            / f"bdrc-{self.bdrc_scan_id}-{vol_num}_hocr.html"
        )
        try:
            hocr_html = image_group_hocr_path.read_text(encoding="utf-8")
            return hocr_html
        except FileNotFoundError:
            logger.error(f"Error: {image_group_hocr_path} not found.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None

    def get_source_info(self):
        return self.buda_data

    def get_image_data(self, image_group_id, image_filename):
        try:
            page_hocr = self.image_info[image_filename]["page_info"]
            return page_hocr
        except KeyError:
            logger.error(f"Error: {image_filename} not found in image_info.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None
