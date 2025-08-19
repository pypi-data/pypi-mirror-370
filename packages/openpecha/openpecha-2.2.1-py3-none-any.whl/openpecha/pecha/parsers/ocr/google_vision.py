import statistics

from fontTools import unicodedata

from openpecha.config import get_logger
from openpecha.pecha.parsers.ocr.ocr import UNICODE_CHARCAT_FOR_WIDTH, BBox, OCRParser

# Initialize the logger
logger = get_logger(__name__)


class GoogleVisionParser(OCRParser):
    """
    OpenPecha Parser for Google OCR JSON output of scanned pecha.
    """

    def __init__(self, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
        self.check_postprocessing = False

    def has_space_attached(self, symbol):
        """Checks if symbol has space followed by it or not

        Args:
            symbol (dict): symbol info

        Returns:
            boolean: True if the symbol has space followed by it
        """
        if (
            "property" in symbol
            and "detectedBreak" in symbol["property"]
            and "type" in symbol["property"]["detectedBreak"]
            and symbol["property"]["detectedBreak"]["type"] == "SPACE"
        ):
            return True
        return False

    def get_language_code_from_gv_poly(self, gv_poly):
        lang = ""
        properties = gv_poly.get("property", {})
        if properties:
            languages = properties.get("detectedLanguages", [])
            if languages:
                lang = languages[0]["languageCode"]
        if lang == "" or lang == "und":
            # this is not always true but replacing it with None is worse
            # with our current data
            return self.default_language
        if lang in ["bo", "en", "zh"]:
            return lang
        if lang == "dz":
            return "bo"
        # English is a kind of default for our purpose
        return "en"

    def get_bboxinfo_from_vertices(self, vertices):
        """
        Vertices do not always have dots in the same order. The current hypothesis
        is that their order represents the rotation of characters detected by
        the OCR.

        This is not documented on

        https://cloud.google.com/vision/docs/reference/rest/v1/projects.locations.products.referenceImages#Vertex

        though, so use the angle value with caution.
        """
        if len(vertices) == 0:
            return None
        idx_smallest = -1
        smallest_x = -1
        smallest_y = -1
        largest_x = -1
        largest_y = -1
        for idx, v in enumerate(vertices):
            if "x" not in v or "y" not in v:
                continue
            smallest_x = v["x"] if smallest_x == -1 else min(v["x"], smallest_x)
            smallest_y = v["y"] if smallest_y == -1 else min(v["y"], smallest_y)
            largest_x = max(v["x"], largest_x)
            largest_y = max(v["y"], largest_y)
            # here we have to account for cases where the 4 dots don't form a rectangle
            # because coordinates are shifted by 1, see test_bbox_info for some example
            if abs(v["x"] - smallest_x) < 3 and abs(v["y"] - smallest_y) < 3:
                idx_smallest = idx
        if smallest_x == -1 or smallest_y == -1 or largest_y == -1 or largest_x == -1:
            return None
        angle = None
        if len(vertices) == 4 and idx_smallest != -1:
            angle = 0
            if idx_smallest == 1:
                angle = 270
            if idx_smallest == 2:
                angle = 180
            if idx_smallest == 3:
                angle = 90
        return [smallest_x, largest_x, smallest_y, largest_y, angle]

    def dict_to_bbox(self, word):
        """Convert bounding bbox to BBox object

        Args:
            word (dict): bounding gv_poly of a word infos

        Returns:
            obj: BBox object of bounding bbox
        """
        confidence = word.get("confidence")
        if "boundingBox" not in word or "vertices" not in word["boundingBox"]:
            return None
        vertices = word["boundingBox"]["vertices"]
        bboxinfo = self.get_bboxinfo_from_vertices(vertices)
        if bboxinfo is None:
            return None
        if self.remove_rotated_boxes and bboxinfo[4] > 0:
            return None
        return BBox(
            bboxinfo[0],
            bboxinfo[1],
            bboxinfo[2],
            bboxinfo[3],
            bboxinfo[4],
            confidence=confidence,
        )

    def get_width_of_vertices(self, vertices):
        if len(vertices) < 4:
            return None
        # oddly enough, sometimes Google returns a vertex with x=-1...
        smallest_x = None
        largest_x = -1
        for v in vertices:
            if "x" not in v or "y" not in v:
                continue
            smallest_x = v["x"] if smallest_x is None else min(v["x"], smallest_x)
            largest_x = max(v["x"], largest_x)
        if smallest_x is None:
            return None
        dif = largest_x - smallest_x
        return dif

    def get_char_base_bboxes_and_avg_width(self, response):
        """Return bounding bboxs in page response

        Args:
            response (dict): google ocr output of a page

        Returns:
            list: list of BBox object which saves required info of a bounding bbox
        """
        bboxes = []
        widths = []
        for page in response["fullTextAnnotation"]["pages"]:
            for block in page["blocks"]:
                cur_line_boxes = []
                for paragraph in block["paragraphs"]:
                    for word in paragraph["words"]:
                        bbox = self.dict_to_bbox(word)
                        if bbox is None:
                            # case where we ignore the bbox for some reason
                            # for instance rotated text
                            continue
                        cur_word = ""
                        for symbol in word["symbols"]:
                            symbolunicat = unicodedata.category(symbol["text"][0])
                            if symbolunicat in UNICODE_CHARCAT_FOR_WIDTH:
                                vertices = symbol["boundingBox"]["vertices"]
                                width = self.get_width_of_vertices(vertices)
                                if width is not None and width > 0:
                                    widths.append(width)
                            cur_word += symbol["text"]
                            if self.has_space_attached(symbol):
                                cur_word += " "
                        if cur_word:
                            bbox.text = cur_word
                            # the language returned by Google OCR is not particularly helpful
                            # language = self.get_language_code_from_gv_poly(word)
                            # instead we use our custom detection system
                            bbox.language = self.get_main_language_code(cur_word)
                            cur_line_boxes.append(bbox)
                bboxes.append(cur_line_boxes)
        avg_width = statistics.mean(widths) if widths else None
        logger.debug("average char width: %f", avg_width)
        return bboxes, avg_width

    def get_bboxes_for_page(self, image_group_id, image_filename):
        ocr_object = self.data_source.get_image_data(image_group_id, image_filename)
        try:
            page_content = ocr_object["textAnnotations"][0]["description"]
        except Exception as e:
            logger.error(
                f"OCR page is empty {page_content} (no textAnnotations[0]/description): {e}"
            )
            return None, 0
        return self.get_char_base_bboxes_and_avg_width(ocr_object)
