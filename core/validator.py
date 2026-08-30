"""
Quality Control (QC) Filter & Dataset Splitter for Đà Nẵng - Quảng Nam Tráp Dataset.
"""

import json
import os
import random
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class DatasetValidator:
    """Quality Control filter and train/val dataset splitter."""

    def __init__(self, train_ratio: float = 0.8):
        self.train_ratio = train_ratio

    def validate_sample(self, sample: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a single sample against strict domain rules.

        Returns (is_valid, reason).
        """
        if not isinstance(sample, dict) or "messages" not in sample:
            return False, "Missing 'messages' key"

        messages = sample["messages"]
        if not isinstance(messages, list) or len(messages) < 4:
            return False, "Dialogue too short (must be >= 4 messages)"

        roles = [m.get("role") for m in messages if isinstance(m, dict)]
        if "user" not in roles or "assistant" not in roles:
            return False, "Missing required roles (user/assistant)"

        full_text = " ".join([m.get("content", "") for m in messages]).lower()

        # Strict Rule 1: Heo Quay policy check
        # If heo quay is mentioned, assistant must clearly state shop DOES NOT supply roasted pig.
        if "heo quay" in full_text:
            assistant_texts = " ".join(
                [m.get("content", "").lower() for m in messages if m.get("role") == "assistant"]
            )
            has_disclaimer = any(
                phrase in assistant_texts
                for phrase in [
                    "không bán heo quay",
                    "không cung cấp heo quay",
                    "không có heo quay",
                    "tự đặt heo quay",
                    "tự mang heo quay",
                    "xếp mâm giúp",
                    "decor miễn phí",
                ]
            )
            if not has_disclaimer:
                return (
                    False,
                    "Violated Heo Quay policy (Assistant must clarify shop does NOT supply heo quay)",
                )

        # Strict Rule 2: Must mention domain locations or product standards
        required_keywords = [
            "tráp",
            "đà nẵng",
            "quảng nam",
            "5 tráp",
            "rồng phượng",
            "thường",
            "hoa tươi",
            "burgundy",
            "nem chả",
            "trầu cau",
            "miễn phí",
            "ship",
        ]
        keyword_hits = sum(1 for kw in required_keywords if kw in full_text)
        if keyword_hits < 3:
            return False, f"Insufficient local domain context (matched {keyword_hits} keywords)"

        return True, "Valid"

    def process_and_split(
        self, samples: List[Dict[str, Any]], output_dir: str
    ) -> Tuple[int, int, int]:
        """Validate all samples and split into dataset_train.jsonl (80%) and dataset_val.jsonl (20%).

        Returns (total_valid, train_count, val_count).
        """
        valid_samples = []
        rejected_count = 0

        for sample in samples:
            is_valid, reason = self.validate_sample(sample)
            if is_valid:
                valid_samples.append(sample)
            else:
                rejected_count += 1
                logger.debug(f"Sample rejected: {reason}")

        random.shuffle(valid_samples)
        total_valid = len(valid_samples)
        train_count = int(total_valid * self.train_ratio)
        train_data = valid_samples[:train_count]
        val_data = valid_samples[train_count:]

        os.makedirs(output_dir, exist_ok=True)
        train_path = os.path.join(output_dir, "dataset_train.jsonl")
        val_path = os.path.join(output_dir, "dataset_val.jsonl")

        with open(train_path, "w", encoding="utf-8") as f:
            for item in train_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        with open(val_path, "w", encoding="utf-8") as f:
            for item in val_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        logger.info(
            f"QC Finished: {total_valid} valid samples ({rejected_count} rejected). "
            f"Train: {len(train_data)}, Val: {len(val_data)}"
        )
        return total_valid, len(train_data), len(val_data)
