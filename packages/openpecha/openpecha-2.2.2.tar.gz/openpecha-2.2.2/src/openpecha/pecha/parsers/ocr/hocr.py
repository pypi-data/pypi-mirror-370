from bs4 import BeautifulSoup

from openpecha.config import get_logger
from openpecha.pecha.parsers.ocr.ocr import BBox, OCRParser

# Initialize the logger
logger = get_logger(__name__)


class HOCRParser(OCRParser):
    """
    OpenPecha Formatter for Google OCR HOCR output of scanned pecha.
    """

    def __init__(self, mode=None, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
        self.mode = mode
        self.word_span = 0

    def get_word_text_with_space(self, line_text, word_box):
        """check for space after word_text using line_text, add space to word_text if found"""
        text = word_box.text
        self.word_span += len(text)
        if len(line_text) == self.word_span:
            return text
        else:
            next_character = line_text[self.word_span]
            if next_character == " ":
                self.word_span += 1
                text = text + " "
        return text

    def parse_box(self, line_box, word_box):
        """parse the word_box to create bbox for the text in word_box.

        Args:
             line_text (_type_): line from the page html
             word_box (_type_): word from the above line

         Returns:
             box : bbox for text in word_box with vertices, confidence, language
        """
        line_text = line_box.text
        if not word_box.has_attr("title"):
            return None
        boxinfos = word_box["title"].split(";")
        coords = None
        angle = None
        confidence = None
        for boxinfo in boxinfos:
            boxinfo_parts = boxinfo.strip().split(" ")
            if boxinfo_parts[0] == "bbox":
                # in HOCR's, bbox order is x0, y0, x1, y1
                coords = [
                    int(boxinfo_parts[1]),
                    int(boxinfo_parts[2]),
                    int(boxinfo_parts[3]),
                    int(boxinfo_parts[4]),
                ]
            elif boxinfo_parts[0] == "textangle":
                # angle is indicated counter-clockwise in hocr so
                # we need to convert it to our internal value system:
                angle = int(boxinfo_parts[1])
                if angle != 0:
                    angle = 360 - angle
            elif boxinfo_parts[0] == "x_wconf":
                confidence = float(boxinfo_parts[1]) / 100.0
        if coords is None:
            return None
        if self.remove_rotated_boxes and angle is not None and angle > 0:
            return None
        language = self.get_main_language_code(word_box.text)
        text = self.get_word_text_with_space(line_text, word_box)
        # but we initialize as x1, x2, y1, y2
        box = BBox(
            coords[0],
            coords[2],
            coords[1],
            coords[3],
            angle=angle,
            text=text,
            confidence=confidence,
            language=language,
        )
        return box

    def get_boxes(self, hocr_page_html):
        """parse the hocr_page_html for one html file per page for bboxes of the page

        Args:
            hocr_page_html (html): html of the page

        Returns:
            boxes: list of bbox dict
        """
        bboxes = []
        hocr_html = BeautifulSoup(hocr_page_html, "html.parser")
        line_boxes = hocr_html.find_all("span", {"class": "ocr_line"})
        for line_box in line_boxes:
            cur_line_boxes = []
            self.word_span = 0
            word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
            for word_box in word_boxes:
                bbox = self.parse_box(line_box, word_box)
                if bbox is not None:
                    cur_line_boxes.append(bbox)
            bboxes.append(cur_line_boxes)
        return bboxes

    def get_boxes_for_IA(self, page_html):
        """parse the page_html for one html file per volume for bboxes of the page

        Args:
            hocr_page_html (html): html of the page

        Returns:
            boxes: list of bbox dict
        """
        bboxes = []
        paragraphs_html = page_html.find_all("p", {"class": "ocr_par"})
        for paragraph_html in paragraphs_html:
            line_boxes = paragraph_html.find_all("span", {"class": "ocr_line"})
            for line_box in line_boxes:
                cur_line_boxes = []
                self.word_span = 0
                word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
                for word_box in word_boxes:
                    bbox = self.parse_box(line_box, word_box)
                    if bbox is not None:
                        cur_line_boxes.append(bbox)
                bboxes.append(cur_line_boxes)
        return bboxes

    def get_bboxes_for_page(self, image_group_id, image_filename):
        bboxes = []
        hocr_page_html = self.data_source.get_image_data(image_group_id, image_filename)
        if hocr_page_html:
            if self.mode == "IA":
                bboxes = self.get_boxes_for_IA(hocr_page_html)
            else:
                bboxes = self.get_boxes(hocr_page_html)
        return bboxes, None
