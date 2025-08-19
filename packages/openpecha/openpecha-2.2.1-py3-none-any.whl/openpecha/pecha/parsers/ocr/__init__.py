import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict

from openpecha.config import get_logger
from openpecha.pecha import Pecha
from openpecha.pecha.parsers.ocr.data_source import (
    BDRCGBSource,
    GoogleVisionSource,
    HOCRIASource,
)
from openpecha.pecha.parsers.ocr.google_vision import GoogleVisionParser
from openpecha.pecha.parsers.ocr.hocr import HOCRParser

logger = get_logger(__name__)


class BdrcParser:
    IA = "IA"

    def parse(
        self,
        input: str | Path,
        metadata: Dict[str, Any],
        pecha_id: str | None = None,
    ) -> Pecha:  # Assuming "Pecha" is a class you have
        """
        Inputs:
            input: Zip file path
            metadata: metadata for the file
            output_path: Output path
            pecha_id: Optional Pecha ID

        Process:
            - Extract the zip file content
            - Determine the data provider based on the zip file structure
            - Parse the data using the appropriate data provider
            - Create OPF (replace with your actual OPF creation logic)

        Output:
            - Create OPF (replace with your actual OPF creation logic)
        """
        input_path = Path(input)
        # 1. Create a temporary directory for extraction
        extract_dir = Path(tempfile.mkdtemp())  # Creates a temp directory
        work_id = metadata["bdrc"]["ocr_import_info"]["bdrc_scan_id"]
        work_path = extract_dir / work_id

        try:
            # 2. Extract the zip file
            with zipfile.ZipFile(input_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

        except zipfile.BadZipFile:
            logger.error(f"Invalid zip file: {input_path}")
            raise  # Re-raise to signal the invalid input
        except Exception as e:
            logger.error(f"Error while parsing OCR: {e}")
            raise  # Re-raise to propagate the error

        # 3. Determine the data provider based on the extracted structure
        data_source = self.determine_data_source(work_path, metadata)

        # 4. Parse the data using the determined data provider
        if data_source is None:
            raise ValueError("No data provider found for the given zip file")

        elif isinstance(data_source, BDRCGBSource):
            pecha = HOCRParser().parse(data_source, pecha_id, {})

        elif isinstance(data_source, HOCRIASource):
            pecha = HOCRParser(mode=self.IA).parse(data_source, pecha_id, {})

        elif isinstance(data_source, GoogleVisionSource):
            pecha = GoogleVisionParser().parse(data_source, pecha_id, {})

        else:
            raise ValueError("Unsupported data provider")

        return pecha

    def determine_data_source(
        self, work_path: Path, metadata: Dict[str, Any]
    ) -> BDRCGBSource | HOCRIASource | GoogleVisionSource:
        """
        Determines the appropriate data source based on the extracted zip file structure.

        This method should be adapted to your specific zip file organization.
        The current logic is based on the presence/absence of certain directories.

        Args:
            work_path: Path to the directory where the zip file was extracted.
            metadata: The original metadata passed to the parser (may be needed for provider setup).

        Returns:
            An instance of the appropriate data provider class.

        Raises:
            ValueError: If no suitable data provider can be determined.
        """
        ocr_path = work_path
        ocr_import_info = metadata["bdrc"]["ocr_import_info"]
        buda_data = metadata["bdrc"]["buda_data"]
        bdrc_scan_id = ocr_import_info["bdrc_scan_id"]

        if not ocr_path.is_dir():
            raise ValueError(f"OCR directory not found: {ocr_path}")

        # Determine provider based on directory content (customize this logic)
        if any(ocr_path.rglob(pattern="*json.gz")):  # Look for Google Vision data
            return GoogleVisionSource(
                bdrc_scan_id=bdrc_scan_id,
                buda_data=buda_data,
                ocr_import_info=ocr_import_info,
                ocr_disk_path=ocr_path,
            )
        elif any(ocr_path.rglob(pattern="*html.zip")):  # Look for BDRC GB data
            return BDRCGBSource(
                bdrc_scan_id=bdrc_scan_id,
                buda_data=buda_data,
                ocr_import_info=ocr_import_info,
                ocr_disk_path=ocr_path,
            )
        else:  # Assume HOCR IA data
            return HOCRIASource(
                bdrc_scan_id=bdrc_scan_id,
                buda_data=buda_data,
                ocr_import_info=ocr_import_info,
                ocr_disk_path=ocr_path,
            )
