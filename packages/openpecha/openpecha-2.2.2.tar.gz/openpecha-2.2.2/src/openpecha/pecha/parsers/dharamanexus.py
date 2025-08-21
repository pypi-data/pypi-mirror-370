import json
import re
from pathlib import Path
from typing import Any, Dict, List

import pyewts

from openpecha.config import PECHAS_PATH
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import Pagination, SegmentationAnnotation, Span
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers import BaseParser

ewts = pyewts.pyewts()


class DharamanexusParser(BaseParser):
    def __init__(self, regex_pattern):
        self.regex_pattern = regex_pattern
        self.state = {}
        self.temp_state: Dict[str, Any] = {
            "base_text": "",
            "annotations": {"segments": {}, "pages": {}},
            "prev_info_dict": {},
        }

    def get_category_wise_files(self, files_json_path):
        with open(files_json_path) as f:
            files = json.load(f)
        category_file_paths: Dict = {}
        for file in files:
            category = file["category"]
            text_name = file["textname"]
            if category not in category_file_paths.keys():
                category_file_paths[category] = {text_name: [file["filename"]]}
            else:
                if text_name not in category_file_paths[category].keys():
                    category_file_paths[category][text_name] = [file["filename"]]
                else:
                    category_file_paths[category][text_name].append(file["filename"])
        return category_file_paths

    def read_json(self, file_path):
        with open(file_path) as f:
            return json.load(f)

    def sort_file_names(self, files):
        parts = re.findall(self.regex_pattern, files)
        key: List[int | float] = []
        for part in parts:
            if part.isdigit():
                key.append(int(part))
            elif re.match(r"\d+\.\d+", part):
                key.append(float(part))
            else:
                key.append(part.strip())
        return key

    def get_info_dict(self, segment_id, page_id, text):
        text_len = len(text)
        curr_dict: Dict[str, Any] = {"annotations": {"segments": {}, "pages": {}}}
        if self.temp_state["prev_info_dict"]:
            segment_start = (
                self.temp_state["prev_info_dict"]["segments"]["span"]["end"] + 1
            )
            segment_end = segment_start + text_len
            curr_dict["annotations"]["segments"][segment_id] = {
                "span": {"start": segment_start, "end": segment_end}
            }
            if page_id == self.temp_state["prev_info_dict"]["page_id"]:
                page_start = self.temp_state["prev_info_dict"]["pages"]["span"]["start"]
                curr_dict["annotations"]["pages"][page_id] = {
                    "span": {"start": page_start, "end": segment_end}
                }
            elif page_id != self.temp_state["prev_info_dict"]["page_id"]:
                page_start = (
                    self.temp_state["prev_info_dict"]["pages"]["span"]["end"] + 1
                )
                curr_dict["annotations"]["pages"][page_id] = {
                    "span": {"start": page_start, "end": page_start + text_len}
                }
        else:
            curr_dict["annotations"]["segments"][segment_id] = {
                "span": {"start": 0, "end": text_len}
            }
            curr_dict["annotations"]["pages"][page_id] = {
                "span": {"start": 0, "end": text_len}
            }
        return curr_dict

    def get_temp_state(self, json_file: List[Dict[str, Any]]) -> None:
        for info in json_file:
            text = ewts.toUnicode(info["original"])
            segment_id = info["segmentnr"]
            page_id = info["folio"]
            curr_dict = self.get_info_dict(segment_id, page_id, text)
            if self.temp_state["base_text"] == "":
                self.temp_state["base_text"] = text
            elif (
                self.temp_state["base_text"] != ""
                and self.temp_state["prev_info_dict"]["page_id"] == page_id
            ):
                self.temp_state["base_text"] += " " + text
            elif self.temp_state["prev_info_dict"]["page_id"] != page_id:
                self.temp_state["base_text"] += "\n" + text
            self.temp_state["annotations"]["segments"][segment_id] = curr_dict[
                "annotations"
            ]["segments"][segment_id]
            self.temp_state["annotations"]["pages"][page_id] = curr_dict["annotations"][
                "pages"
            ][page_id]
            self.temp_state["prev_info_dict"] = {
                "segment_id": segment_id,
                "page_id": page_id,
                "segments": curr_dict["annotations"]["segments"][segment_id],
                "pages": curr_dict["annotations"]["pages"][page_id],
            }

    def make_state(self, input):
        for vol, file_paths in input.items():
            for file_path in file_paths:
                json_file = self.read_json(file_path)
                self.get_temp_state(json_file)
            self.state[vol] = {
                "base_text": self.temp_state["base_text"],
                "annotations": self.temp_state["annotations"],
            }
            self.temp_state = {
                "base_text": "",
                "annotations": {"segments": {}, "pages": {}},
                "prev_info_dict": {},
            }

    def write_to_pecha(self, pecha, metadata):
        bases = {}
        order = 1
        for vol, data in self.state.items():
            base_name = pecha.set_base(content=data["base_text"])

            segment, _ = pecha.add_layer(base_name, AnnotationType.SEGMENTATION)
            index = 1
            for segment_id, segment_span in data["annotations"]["segments"].items():
                segment_ann = SegmentationAnnotation(
                    span=Span(
                        start=segment_span["span"]["start"],
                        end=segment_span["span"]["end"],
                    ),
                    index=index,
                    segment_id=segment_id,
                )
                pecha.add_annotation(segment, segment_ann, AnnotationType.SEGMENTATION)
                index += 1
            segment.save()

            pagination, _ = pecha.add_layer(base_name, AnnotationType.PAGINATION)
            for page_id, page_ann in data["annotations"]["pages"].items():
                page_ann = Pagination(
                    span=Span(
                        start=page_ann["span"]["start"], end=page_ann["span"]["end"]
                    ),
                    page_info=page_id,  # folio
                )
                pecha.add_annotation(pagination, page_ann, AnnotationType.PAGINATION)
            pagination.save()

            curr_base = {
                "source_metadata": {
                    "source_id": vol,
                    "total_segments": len(data["annotations"]["segments"]),
                    "total_pages": len(data["annotations"]["pages"]),
                },
                "base_file": base_name,
                "order": order,
            }

            bases[base_name] = curr_base
            order += 1

        pecha.set_metadata(
            {"id": pecha.id, "parser": self.name, "bases": bases, **metadata}
        )

    def parse(
        self,
        input: Any,
        metadata: Dict | Path,
        output_path: Path = PECHAS_PATH,
    ):
        self.make_state(input)

        pecha = Pecha.create(output_path)
        self.write_to_pecha(pecha, metadata)
        return pecha

    def get_sorted_file_paths(self, file_paths):
        for _, texts in file_paths.items():
            sorted_texts = sorted(texts.keys(), key=self.sort_file_names)
            for text_name in sorted_texts:
                files = texts[text_name]
                sorted_files = sorted(files, key=self.sort_file_names)
        return sorted_files
