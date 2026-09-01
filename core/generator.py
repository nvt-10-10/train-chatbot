"""
Async Ollama Synthetic Data Generator for Đà Nẵng & Quảng Nam Wedding Tráp Dataset.
"""

import os
import asyncio
import json
import random
import logging
import hashlib
import re
from typing import List, Dict, Any, Optional
import ollama

from config.personas import CUSTOMER_PERSONAS
from config.scenarios import SYSTEM_PROMPT_TEMPLATE, GENERATION_SCENARIOS

logger = logging.getLogger(__name__)


def compute_sample_signature(sample: Dict[str, Any]) -> str:
    """Compute a signature hash based on normalized user content for deduplication."""
    if not isinstance(sample, dict) or "messages" not in sample:
        return ""
    messages = sample.get("messages", [])
    user_texts = []
    for m in messages:
        if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str):
            clean_text = re.sub(r"[^\w\s]", "", m.get("content", "").lower())
            clean_text = re.sub(r"\s+", " ", clean_text).strip()
            user_texts.append(clean_text)
    if not user_texts:
        return ""
    combined = " | ".join(user_texts)
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


class OllamaDataGenerator:
    """Async Data Generator using Ollama local model with deduplication."""

    def __init__(
        self,
        model_name: str = "qwen2.5:14b-instruct",
        host: str = "http://localhost:11434",
        concurrency: int = 4,
    ):
        self.model_name = model_name
        self.concurrency = concurrency
        self.client = ollama.AsyncClient(host=host)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def generate_single_dialogue(
        self, persona: Dict[str, Any], scenario: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a single unique conversation JSON based on persona and scenario."""
        async with self.semaphore:
            random_tones = [
                "Thân thiện, hân hoan chuẩn bị ngày cưới/đám hỏi",
                "Hơi băn khoăn về chi phí và chất lượng dịch vụ",
                "Lo lắng vấn đề vận chuyển đường dài và bảo quản hoa tươi",
                "Thẳng thắn, muốn chốt thông tin nhanh chóng và chi tiết",
                "Chú trọng tính thẩm mỹ, decor hoa tươi tone màu theo concept (Đỏ Burgundy, Hồng Pastel, Vàng Hoàng Gia, Trắng Tinh Khôi...)",
                "Quan tâm đến văn hóa tráp cưới truyền thống xứ Quảng",
            ]
            tone_variation = random.choice(random_tones)
            random_seed = random.randint(1000, 999999)

            prompt = f"""Hãy đóng vai tạo một cuộc hội thoại tư vấn thực tế KHÔNG TRÙNG LẶP giữa Khách hàng và Chuyên viên Tư vấn của Tráp Lễ Cưới Hỏi Thiên Di (Đà Nẵng & Quảng Nam).

[MÃ BIẾN THỂ ĐỘC BẢN #{random_seed}]
SẮC THÁI & HƯỚNG TƯ VẤN: {tone_variation}

THÔNG TIN KHÁCH HÀNG:
- Tên & Khu vực: {persona['name']} ({persona['location']})
- Nhu cầu/Đặc điểm: {persona['trait']}
- Ưa thích: {persona['preference']}
- Đồ lễ mang thêm (nếu có): {persona['custom_items']}
- Nhu cầu giao hàng: {persona['shipping_need']}

KỊCH BẢN TƯ VẤN CHÍNH:
- Chủ đề: {scenario['topic']}
- Hướng dẫn: {scenario['guidance']}

QUY CHUẨN THÔNG TIN BẮT BUỘC:
1. Tráp Lễ Cưới Hỏi Thiên Di tập trung BỘ 5 TRÁP QUẢ (Đế tráp linh hoạt tùy chọn mẫu, hoa tươi cao cấp với đa dạng Tone màu: Đỏ Burgundy mặc định, Hồng Pastel, Vàng Hoàng Gia, Trắng Tinh Khôi, Cam Đất... Hỗ trợ phối tone màu MIỄN PHÍ theo yêu cầu):
   - Loại 1: Bộ 5 Tráp Rồng Phượng (Tráp 1: Rồng Táo đỏ; Tráp 2: Phượng Trầu cau tem cánh phụng; Tráp 3: Trà Rượu cao cấp; Tráp 4: Nem Chả đặc sản; Tráp 5: Bánh cưới/Bánh kem tháp hoa tươi).
   - Loại 2: Bộ 5 Tráp Thường (Tráp 1: Trái cây Táo viền hoa; Tráp 2: Trầu cau cánh phụng viền hoa; Tráp 3: Trà Rượu decor hoa; Tráp 4: Nem Chả đặc sản; Tráp 5: Bánh cưới/Bánh khối/Bánh kem).
2. TỪ CHỐI HEO QUAY: Tráp Cưới Thiên Di KHÔNG bán và KHÔNG nhận làm/xếp mâm cho Heo quay dưới mọi hình thức, từ tốn từ chối và tập trung tư vấn Bộ 5 Tráp Quả cao cấp.
3. KHÁCH TỰ MANG BÁNH/LỄ VẬT (Bánh su xê, phu thê, bánh in...): Tráp Cưới Thiên Di hỗ trợ xếp mâm & decor hoa tươi chỉn chu.
4. SHIP HÀNG: Miễn phí ship 100% trong bán kính 10km; Khu vực xa hơn 10km hoặc các huyện/thành phố Quảng Nam (Hội An, Điện Bàn, Tam Kỳ, Duy Xuyên...) tính phí ship hợp lý theo khoảng cách km thực tế, cam kết ship tận nơi.
5. Giọng điệu tư vấn chuẩn thương hiệu Tráp Lễ Cưới Hỏi Thiên Di: xởi lởi, nhiệt tình đậm chất miền Trung, diễn đạt tự nhiên không lặp từ.
6. NHÂN VIÊN TƯ VẤN TỰ ĐỘNG & THÔNG BÁO CHỦ PAGE/SHOP: Khi chốt tone màu hoa, chốt mẫu tráp hoặc chốt đơn giá/hợp đồng -> Từ tốn mời khách chờ trong ít phút để hệ thống gửi thông báo trực tiếp đến Chủ Page / Chủ Shop liên hệ tư vấn 1-1 theo Zalo/Hotline 079 944 4167, FB: https://www.facebook.com/tuyen.di.744207, Email: thiendi26021212@gmail.com, Địa chỉ: 138 Phan Châu Trinh, P. An Mỹ, TP. Tam Kỳ, Quảng Nam (51100).
7. NGUYÊN TẮC BÁO GIÁ THAM KHẢO & BÀN GIAO CHỦ SHOP: AI KHÔNG báo giá cụ thể chốt cứng vì đơn giá thực tế biến động theo giá hoa tươi/trái cây thị trường từng thời điểm và chất lượng đồ lễ do khách yêu cầu. AI chỉ đưa mức giá THAM KHẢO KHỞI ĐIỂM (Bộ 5 Tráp Thường từ ~4.000.000 VNĐ; Bộ 5 Tráp Rồng Phượng từ ~5.500.000 VNĐ). Khi khách hỏi báo giá cụ thể -> Nhẹ nhàng mời khách chờ để Chủ Shop / Chủ Page liên hệ tư vấn và báo giá chính xác.

YÊU CẦU ĐẦU RA JSON CHUẨN:
Trả về duy nhất 1 JSON block hợp lệ có dạng:
{{
  "messages": [
    {{"role": "system", "content": "{SYSTEM_PROMPT_TEMPLATE.strip().replace(chr(10), ' ')}"}},
    {{"role": "user", "content": "..."}},
    {{"role": "assistant", "content": "..."}},
    {{"role": "user", "content": "..."}},
    {{"role": "assistant", "content": "..."}}
  ]
}}
Hội thoại phải có ít nhất 2 lượt trao đổi (user - assistant - user - assistant). Trả về JSON thuần túy, không kèm lời giải thích Markdown hay chú thích gì khác ngoài JSON.
"""

            try:
                temp = round(random.uniform(0.75, 0.95), 2)
                response = await self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    format="json",
                    options={"temperature": temp, "top_p": 0.9},
                )
                raw_text = response.get("response", "").strip()

                # Extract JSON from potential code fences
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()

                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError:
                    cleaned_text = raw_text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
                    data = json.loads(cleaned_text)

                if isinstance(data, dict) and "messages" in data:
                    messages = data.get("messages")
                    if isinstance(messages, list):
                        valid_messages = [
                            m for m in messages
                            if isinstance(m, dict)
                            and isinstance(m.get("role"), str)
                            and isinstance(m.get("content"), str)
                        ]
                        if len(valid_messages) >= 4:
                            data["messages"] = valid_messages
                            return data
                        else:
                            logger.warning(f"Sample rejected: only {len(valid_messages)} valid messages (min 4 required)")
                    else:
                        logger.warning("Sample rejected: 'messages' key is not a list")
                else:
                    logger.warning("Sample rejected: JSON root is not a dict with 'messages'")
            except Exception as e:
                logger.warning(f"Error parsing dialogue JSON: {e}")
                return None
            return None

    async def generate_dataset(
        self,
        num_samples: int,
        progress_callback=None,
        raw_save_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate a batch of unique dialogues asynchronously with continuous saving & resume support."""
        seen_signatures = set()
        existing_samples = []

        if raw_save_path and os.path.exists(raw_save_path):
            try:
                with open(raw_save_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                item = json.loads(line)
                                if (
                                    isinstance(item, dict)
                                    and "messages" in item
                                    and isinstance(item["messages"], list)
                                ):
                                    sig = compute_sample_signature(item)
                                    if sig and sig not in seen_signatures:
                                        seen_signatures.add(sig)
                                        existing_samples.append(item)
                            except json.JSONDecodeError:
                                continue
                logger.info(f"Loaded {len(existing_samples)} unique existing samples from {raw_save_path}")
            except Exception as e:
                logger.warning(f"Failed to read existing samples from {raw_save_path}: {e}")

        needed = num_samples - len(existing_samples)
        if needed <= 0:
            if progress_callback:
                progress_callback(len(existing_samples), None, is_initial=True)
            return existing_samples[:num_samples]

        if progress_callback and existing_samples:
            progress_callback(len(existing_samples), None, is_initial=True)

        results = list(existing_samples)
        raw_file = None
        if raw_save_path:
            os.makedirs(os.path.dirname(os.path.abspath(raw_save_path)), exist_ok=True)
            raw_file = open(raw_save_path, "a", encoding="utf-8")

        try:
            new_unique_count = 0
            while new_unique_count < needed:
                batch_size = min(self.concurrency * 2, needed - new_unique_count)
                tasks = []
                for _ in range(batch_size):
                    persona = random.choice(CUSTOMER_PERSONAS)
                    scenario = random.choice(GENERATION_SCENARIOS)
                    tasks.append(self.generate_single_dialogue(persona, scenario))

                for future in asyncio.as_completed(tasks):
                    res = await future
                    if res:
                        sig = compute_sample_signature(res)
                        if sig and sig not in seen_signatures:
                            seen_signatures.add(sig)
                            results.append(res)
                            new_unique_count += 1
                            if raw_file:
                                raw_file.write(json.dumps(res, ensure_ascii=False) + "\n")
                                raw_file.flush()
                                logger.info(f"💾 Saved sample #{len(results)} to {raw_save_path}")
                            if progress_callback:
                                progress_callback(1, res)
                            if new_unique_count >= needed:
                                break
                        else:
                            logger.warning("Skipped duplicate dialogue sample, retrying new sample...")
                    else:
                        logger.warning("Generation task returned None (parsing/validation failed), retrying...")
        finally:
            if raw_file:
                raw_file.close()

        return results
