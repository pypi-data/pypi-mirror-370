from pathlib import Path
from typing import Any, Dict, List

from stam import AnnotationStore

from openpecha.config import get_logger
from openpecha.pecha import Pecha, get_anns, load_layer
from openpecha.utils import (
    adjust_segment_num_for_chapter,
    get_chapter_for_segment,
    parse_alignment_index,
)

logger = get_logger(__name__)


def is_empty(text: str) -> bool:
    """
    Return True if text is empty or contains only newlines.
    """
    return not text.strip().replace("\n", "")


class CommentaryAlignmentTransfer:
    @staticmethod
    def get_first_valid_root_idx(ann) -> int | None:
        indices = parse_alignment_index(ann["alignment_index"])
        return indices[0] if indices else None

    @staticmethod
    def is_valid_ann(anns: Dict[int, Dict[str, Any]], idx: int) -> bool:
        return idx in anns and not is_empty(anns[idx]["text"])

    def get_segmentation_ann_path(self, pecha: Pecha) -> Path:
        """
        Return the path to the first segmentation layer JSON file in the pecha.
        """
        return next(pecha.layer_path.rglob("segmentation-*.json"))

    def index_annotations_by_root(
        self, anns: List[Dict[str, Any]]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Return a dict mapping root_idx_mapping to the annotation dict.
        """
        return {int(ann["index"]): ann for ann in anns}

    def map_layer_to_layer(
        self, src_layer: AnnotationStore, tgt_layer: AnnotationStore
    ) -> Dict[int, List[int]]:
        """
        Map annotations from src_layer to tgt_layer based on span overlap or containment.
        Returns a mapping from source indices to lists of target indices.
        """

        def is_match(src_start, src_end, tgt_start, tgt_end):
            """Helper to check if spans overlap or are contained (not edge overlap)."""
            is_overlap = (
                src_start <= tgt_start < src_end or src_start < tgt_end <= src_end
            )
            is_contained = tgt_start < src_start and tgt_end > src_end
            is_edge_overlap = tgt_start == src_end or tgt_end == src_start
            return (is_overlap or is_contained) and not is_edge_overlap

        mapping: Dict[int, List[int]] = {}
        src_anns = get_anns(src_layer, include_span=True)
        tgt_anns = get_anns(tgt_layer, include_span=True)

        for src_ann in src_anns:
            src_start, src_end = src_ann["Span"]["start"], src_ann["Span"]["end"]
            try:
                src_idx = (
                    src_ann["alignment_index"][0]
                    if src_ann["segmentation_type"] == "alignment"
                    else int(src_ann["index"])
                )
            except ValueError:
                continue
            mapping[src_idx] = []
            for tgt_ann in tgt_anns:
                tgt_start, tgt_end = tgt_ann["Span"]["start"], tgt_ann["Span"]["end"]
                try:
                    tgt_idx = (
                        tgt_ann["alignment_index"][0]
                        if tgt_ann["segmentation_type"] == "alignment"
                        else int(tgt_ann["index"])
                    )
                except ValueError:
                    continue
                if is_match(src_start, src_end, tgt_start, tgt_end):
                    mapping[src_idx].append(tgt_idx)

        logger.info("Mapping from layer to layer complete.")
        return dict(sorted(mapping.items()))

    def get_root_pechas_mapping(
        self, pecha: Pecha, alignment_id: str
    ) -> Dict[int, List[int]]:
        """
        Get mapping from pecha's alignment layer to segmentation layer.
        """
        segmentation_ann_path = self.get_segmentation_ann_path(pecha)
        segmentation_layer = load_layer(segmentation_ann_path)
        alignment_layer = load_layer(pecha.layer_path / alignment_id)
        return self.map_layer_to_layer(alignment_layer, segmentation_layer)

    def get_commentary_pechas_mapping(
        self, pecha: Pecha, alignment_id: str, segmentation_id: str
    ) -> Dict[int, List[int]]:
        """
        Get mapping from pecha's segmentation layer to alignment layer.
        """
        segmentation_ann_path = pecha.layer_path / segmentation_id
        segmentation_layer = load_layer(segmentation_ann_path)
        alignment_layer = load_layer(pecha.layer_path / alignment_id)
        return self.map_layer_to_layer(segmentation_layer, alignment_layer)

    def get_serialized_commentary(
        self,
        root_pecha: Pecha,
        root_alignment_id: str,
        commentary_pecha: Pecha,
        commentary_alignment_id: str,
    ) -> List[str]:
        """
        Serialize commentary annotations with root/segmentation mapping and formatting.
        """
        root_map = self.get_root_pechas_mapping(root_pecha, root_alignment_id)
        root_segmentation_path = self.get_segmentation_ann_path(root_pecha)
        root_segmentation_anns = self.index_annotations_by_root(
            get_anns(load_layer(root_segmentation_path))
        )
        root_anns = self.index_annotations_by_root(
            get_anns(load_layer(root_pecha.layer_path / root_alignment_id))
        )
        commentary_anns = get_anns(
            load_layer(commentary_pecha.layer_path / commentary_alignment_id)
        )

        res: List[str] = []
        for ann in commentary_anns:
            result = self.process_commentary_ann(
                ann, root_anns, root_map, root_segmentation_anns
            )
            if result is not None:
                res.append(result)
        return res

    def get_serialized_commentary_segmentation(
        self,
        root_pecha: Pecha,
        root_alignment_id: str,
        commentary_pecha: Pecha,
        commentary_alignment_id: str,
        commentary_segmentation_id: str,
    ) -> List[str]:
        root_map = self.get_root_pechas_mapping(root_pecha, root_alignment_id)
        commentary_map = self.get_commentary_pechas_mapping(
            commentary_pecha, commentary_alignment_id, commentary_segmentation_id
        )

        root_segmentation_path = self.get_segmentation_ann_path(root_pecha)
        root_segmentation_anns = self.index_annotations_by_root(
            get_anns(load_layer(root_segmentation_path))
        )
        root_anns = self.index_annotations_by_root(
            get_anns(load_layer(root_pecha.layer_path / root_alignment_id))
        )
        commentary_segmentation_anns = get_anns(
            load_layer(commentary_pecha.layer_path / commentary_segmentation_id)
        )
        logger.info(
            "Root and Commentary Annotations retrieved for Commentary Transfer."
        )

        res: List[str] = []
        for ann in commentary_segmentation_anns:
            try:
                text = ann["text"]
                if is_empty(text):
                    continue

                if not commentary_map[int(ann["index"])]:
                    res.append(text)
                    continue

                aligned_idx = commentary_map[int(ann["index"])][0]
                if not self.is_valid_ann(root_anns, aligned_idx):
                    res.append(text)
                    continue

                if not root_map[aligned_idx]:
                    res.append(text)
                    continue

                root_display_idx = root_map[aligned_idx][0]
                if not self.is_valid_ann(root_segmentation_anns, root_display_idx):
                    res.append(text)
                    continue

                chapter_num = get_chapter_for_segment(root_display_idx)
                processed_root_display_idx = adjust_segment_num_for_chapter(
                    root_display_idx
                )
                res.append(
                    self.format_serialized_commentary(
                        chapter_num, processed_root_display_idx, text
                    )
                )
            except Exception as e:
                logger.error(
                    f"Error processing annotation: {ann}\nException: {e}", exc_info=True
                )
        return res

    @staticmethod
    def format_serialized_commentary(chapter_num: int, seg_idx: int, text: str) -> str:
        """Format the serialized commentary string."""
        return f"<{chapter_num}><{seg_idx}>{text}"

    def process_commentary_ann(
        self,
        ann: dict,
        root_anns: dict,
        root_map: dict,
        root_segmentation_anns: dict,
    ) -> str | None:
        """Process a single commentary annotation and return the serialized string, or None if not valid."""
        commentary_text = ann["text"]
        if is_empty(commentary_text):
            return None

        root_idx = ann["alignment_index"][0]
        if root_idx is None or not self.is_valid_ann(root_anns, root_idx):
            return commentary_text

        if not root_map[root_idx]:
            return commentary_text

        root_display_idx = root_map[root_idx][0]
        if not self.is_valid_ann(root_segmentation_anns, root_display_idx):
            return commentary_text

        chapter_num = get_chapter_for_segment(root_display_idx)
        processed_root_display_idx = adjust_segment_num_for_chapter(root_display_idx)
        return self.format_serialized_commentary(
            chapter_num, processed_root_display_idx, commentary_text
        )
