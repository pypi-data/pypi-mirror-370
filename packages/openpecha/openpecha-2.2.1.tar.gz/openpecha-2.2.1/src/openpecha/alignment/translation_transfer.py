from pathlib import Path
from typing import Dict, List

from stam import AnnotationStore

from openpecha.config import get_logger
from openpecha.pecha import Pecha, get_anns, load_layer

logger = get_logger(__name__)


class TranslationAlignmentTransfer:
    @staticmethod
    def is_empty(text: str) -> bool:
        return not text.strip().replace("\n", "")

    def get_segmentation_ann_path(self, pecha: Pecha) -> Path:
        path = next(pecha.layer_path.rglob("segmentation-*.json"))
        return path

    def map_layer_to_layer(
        self, src_layer: AnnotationStore, tgt_layer: AnnotationStore
    ) -> Dict[int, List[int]]:
        logger.info(
            "Mapping annotations from source layer to target layer based on span overlaps..."
        )
        map: Dict[int, List[int]] = {}

        src_anns = get_anns(src_layer, include_span=True)
        tgt_anns = get_anns(tgt_layer, include_span=True)

        for src_ann in src_anns:
            src_start, src_end = src_ann["Span"]["start"], src_ann["Span"]["end"]
            src_idx = (
                src_ann["alignment_index"][0]
                if src_ann["segmentation_type"] == "alignment"
                else int(src_ann["index"])
            )
            map[src_idx] = []
            for tgt_ann in tgt_anns:
                tgt_start, tgt_end = tgt_ann["Span"]["start"], tgt_ann["Span"]["end"]
                tgt_idx = (
                    tgt_ann["alignment_index"][0]
                    if tgt_ann["segmentation_type"] == "alignment"
                    else int(tgt_ann["index"])
                )

                is_overlap = (
                    src_start <= tgt_start < src_end or src_start < tgt_end <= src_end
                )
                is_contained = tgt_start < src_start and tgt_end > src_end
                is_edge_overlap = tgt_start == src_end or tgt_end == src_start
                if (is_overlap or is_contained) and not is_edge_overlap:
                    map[src_idx].append(tgt_idx)

        logger.info("Mapping from layer to layer complete.")
        return dict(sorted(map.items()))

    def get_root_pechas_mapping(
        self, pecha: Pecha, alignment_id: str
    ) -> Dict[int, List[int]]:
        logger.info(
            f"Getting root mapping for pecha '{pecha.id}' using alignment layer '{alignment_id}'..."
        )
        segmentation_ann_path = self.get_segmentation_ann_path(pecha)
        segmentation_layer = load_layer(segmentation_ann_path)
        alignment_layer = load_layer(pecha.layer_path / alignment_id)
        mapping = self.map_layer_to_layer(alignment_layer, segmentation_layer)
        logger.info("Root pecha mapping created.")
        return mapping

    def get_translation_pechas_mapping(
        self,
        pecha: Pecha,
        alignment_id: str,
        segmentation_id: str,
    ) -> Dict[int, List[int]]:
        logger.info(f"Getting translation mapping for pecha '{pecha.id}'...")
        segmentation_ann_path = pecha.layer_path / segmentation_id
        segmentation_layer = load_layer(segmentation_ann_path)
        alignment_layer = load_layer(pecha.layer_path / alignment_id)
        mapping = self.map_layer_to_layer(segmentation_layer, alignment_layer)
        logger.info("Translation pecha mapping created.")
        return mapping

    def mapping_to_text_list(self, mapping: Dict[int, List[str]]) -> List[str]:
        logger.info("Flattening mapping to text list...")
        max_root_idx = max(mapping.keys(), default=0)
        res = []
        for i in range(1, max_root_idx + 1):
            texts = mapping.get(i, [])
            text = "\n".join(texts)
            if self.is_empty(text):
                logger.debug(f"Text at index {i} is empty. Appending empty string.")
                res.append("")
            else:
                logger.debug(f"Text at index {i} has content. Appending text.")
                res.append(text)
        logger.info(f"Flattened list created with {len(res)} segments.")
        return res

    def get_serialized_translation_alignment(
        self,
        root_pecha: Pecha,
        root_alignment_id: str,
        root_translation_pecha: Pecha,
        translation_alignment_id: str,
    ) -> List[str]:
        logger.info("Generating serialized translation alignment...")
        root_map = self.get_root_pechas_mapping(root_pecha, root_alignment_id)
        layer = load_layer(root_translation_pecha.layer_path / translation_alignment_id)
        anns = get_anns(layer, include_span=True)

        map: Dict[int, List[str]] = {}
        for ann in anns:
            aligned_idx = ann["alignment_index"][0]
            text = ann["text"]
            if not root_map.get(aligned_idx):
                logger.debug(
                    f"No root mapping found for aligned index {aligned_idx}. Skipping."
                )
                continue
            root_segmentation_idx = root_map[aligned_idx][0]
            map.setdefault(root_segmentation_idx, []).append(text)

        logger.info("Serialized translation alignment mapping created.")
        return self.mapping_to_text_list(map)

    def get_serialized_translation_segmentation(
        self,
        root_pecha: Pecha,
        root_alignment_id: str,
        translation_pecha: Pecha,
        translation_alignment_id: str,
        translation_segmentation_id: str,
    ) -> List[str]:
        logger.info("Generating serialized translation segmentation...")
        root_map = self.get_root_pechas_mapping(root_pecha, root_alignment_id)
        translation_map = self.get_translation_pechas_mapping(
            translation_pecha, translation_alignment_id, translation_segmentation_id
        )

        layer = load_layer(translation_pecha.layer_path / translation_segmentation_id)
        anns = get_anns(layer, include_span=True)
        logger.debug(f"Loaded {len(anns)} translation segmentation annotations.")

        map: Dict[int, List[str]] = {}
        for ann in anns:
            text = ann["text"]
            idx = int(ann["index"])

            aligned_idx = translation_map[idx][0]
            root_segmentation_idx = root_map[aligned_idx][0]
            map.setdefault(root_segmentation_idx, []).append(text)

        logger.info("Serialized translation segmentation mapping created.")
        return self.mapping_to_text_list(map)
