"""
Async Ollama Synthetic Data Generator for Đà Nẵng & Quảng Nam Wedding Tráp Dataset.
"""

import asyncio
import json
import random
import logging
from typing import List, Dict, Any, Optional
import ollama

from config.personas import CUSTOMER_PERSONAS
from config.scenarios import SYSTEM_PROMPT_TEMPLATE, GENERATION_SCENARIOS

logger = logging.getLogger(__name__)


class OllamaDataGenerator:
    """Async Data Generator using Ollama local model."""

    def __init__(
        self,
        model_name: str = "qwen2.5:14b-instruct",
        host: str = "http://localhost:11434",
        concurrency: int = 4,
    ):
        self.model_name = model_name
        self.client = ollama.AsyncClient(host=host)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def generate_single_dialogue(
        self, persona: Dict[str, Any], scenario: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a single conversation JSON based on persona and scenario."""
        async with self.semaphore:
            prompt = f"""Hãy đóng vai tạo một cuộc hội thoại tư vấn thực tế giữa Khách hàng và Chuyên viên Tư vấn Tráp Cưới Đà Nẵng & Quảng Nam.

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
1. Shop tập trung BỘ 5 TRÁP QUẢ (Đế mây, hoa tươi đỏ Burgundy):
   - Loại 1: Bộ 5 Tráp Rồng Phượng (Tráp 1: Rồng Táo đỏ; Tráp 2: Phượng Trầu cau tem cánh phụng; Tráp 3: Trà Rượu cao cấp; Tráp 4: Nem Chả đặc sản; Tráp 5: Bánh cưới/Bánh kem tháp hoa tươi).
   - Loại 2: Bộ 5 Tráp Thường (Tráp 1: Trái cây Táo viền hoa; Tráp 2: Trầu cau cánh phụng viền hoa; Tráp 3: Trà Rượu decor hoa; Tráp 4: Nem Chả đặc sản; Tráp 5: Bánh cưới/Bánh khối/Bánh kem).
2. KHÔNG BÁN HEO QUAY: Khách hỏi heo quay thì báo shop không bán, nhưng nếu khách tự mang heo quay tới shop hỗ trợ mâm mây & decor hoa tươi MIỄN PHÍ.
3. KHÁCH TỰ MANG BÁNH/LỄ VẬT (Bánh su xê, phu thê, bánh in...): Shop hỗ trợ xếp mâm & decor hoa tươi MIỄN PHÍ 100%.
4. SHIP HÀNG: Miễn phí/phí nhẹ nội thành Đà Nẵng; Quảng Nam (Hội An, Điện Bàn, Tam Kỳ, Duy Xuyên...) tính phí ship hợp lý, bọc màng co chống xốc an toàn.
5. Giọng điệu tư vấn đậm chất miền Trung, xởi lởi, nhiệt tình.

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
                response = await self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    format="json",
                    options={"temperature": 0.7, "top_p": 0.9},
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
                    # Robust fallback: replace unescaped control characters
                    cleaned_text = raw_text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
                    data = json.loads(cleaned_text)

                if isinstance(data, dict) and "messages" in data:
                    return data
            except Exception as e:
                logger.warning(f"Error parsing dialogue JSON: {e}")
                return None
            return None

    async def generate_dataset(
        self, num_samples: int, progress_callback=None
    ) -> List[Dict[str, Any]]:
        """Generate a batch of dialogues asynchronously."""
        tasks = []
        for _ in range(num_samples):
            persona = random.choice(CUSTOMER_PERSONAS)
            scenario = random.choice(GENERATION_SCENARIOS)
            tasks.append(self.generate_single_dialogue(persona, scenario))

        results = []
        for future in asyncio.as_completed(tasks):
            res = await future
            if res:
                results.append(res)
            if progress_callback:
                progress_callback(1, res)
        return results
