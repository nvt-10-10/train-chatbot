"""
Personas module defining customer profiles for Đà Nẵng & Quảng Nam wedding tráp consulting.
"""

from typing import List, Dict, Any

CUSTOMER_PERSONAS: List[Dict[str, Any]] = [
    {
        "id": "dn_dragon_phoenix_vip",
        "name": "Anh Hoàng (Hải Châu, Đà Nẵng)",
        "location": "Quận Hải Châu, Đà Nẵng",
        "budget_level": "Cao cấp",
        "preference": "Bộ 5 Tráp Rồng Phượng",
        "trait": "Thích sự hoành tráng, decor hoa tươi tone đỏ rượu Burgundy sang trọng, chú trọng hình thức tráp Rồng Phượng cao cấp cho lễ đám hỏi/đám cưới.",
        "custom_items": "Có ý định tự mang thêm bánh su xê / bánh phu thê hộp quà đẹp từ tiệm quen tới nhờ shop xếp mâm.",
        "shipping_need": "Giao nội thành Đà Nẵng (Hải Châu)."
    },
    {
        "id": "qn_hoian_traditional",
        "name": "Chị Mai (TP. Hội An, Quảng Nam)",
        "location": "TP. Hội An, Quảng Nam",
        "budget_level": "Vừa phải / Truyền thống",
        "preference": "Bộ 5 Tráp Thường (Hoa tươi cơ bản)",
        "trait": "Thích nét đẹp mộc mạc đan mây, viền hoa tươi Burgundy tinh tế, tiết kiệm ngân sách nhưng vẫn chỉn chu.",
        "custom_items": "Tự mang bánh in đặc sản Hội An và mứt hạt sen gia đình làm tới nhờ shop trang trí viền hoa tươi.",
        "shipping_need": "Giao tận nhà ở Hội An, quan tâm màng co bảo vệ chống xốc và phí ship."
    },
    {
        "id": "qn_dienban_heoquay_query",
        "name": "Chú Tuấn (TX. Điện Bàn, Quảng Nam)",
        "location": "Thi xã Điện Bàn, Quảng Nam",
        "budget_level": "Truyền thống",
        "preference": "Bộ 5 Tráp Rồng Phượng + Hỏi thêm Heo Quay",
        "trait": "Hỏi rõ shop có làm tráp Heo Quay không. Shop cần khéo léo giải thích KHÔNG bán heo quay nhưng sẵn sàng hỗ trợ xếp mâm nếu gia đình tự đặt heo quay mang tới.",
        "custom_items": "Muốn hỏi mang heo quay hoặc bánh su xê tới.",
        "shipping_need": "Giao về Điện Bàn (gần Nam Phước), cần đảm bảo hoa tươi không bị dập."
    },
    {
        "id": "dn_camle_standard_5trap",
        "name": "Chị Thanh (Quận Cẩm Lệ, Đà Nẵng)",
        "location": "Quận Cẩm Lệ, Đà Nẵng",
        "budget_level": "Tiêu chuẩn",
        "preference": "Bộ 5 Tráp Thường (Đế mây, hoa tươi Burgundy)",
        "trait": "Cần tư vấn chi tiết từng tráp gồm những gì (Trái cây, Trầu cau cánh phụng, Trà rượu, Nem chả, Bánh cưới).",
        "custom_items": "Tự mang bánh cưới/bánh kem tháp hoa tới shop xếp.",
        "shipping_need": "Giao Cẩm Lệ, Đà Nẵng."
    },
    {
        "id": "qn_tamky_distance_ship",
        "name": "Anh Đức (TP. Tam Kỳ, Quảng Nam)",
        "location": "TP. Tam Kỳ, Quảng Nam",
        "budget_level": "Cao cấp",
        "preference": "Bộ 5 Tráp Rồng Phượng",
        "trait": "Lo lắng giao hàng xa từ Đà Nẵng vào Tam Kỳ. Cần shop cam kết bọc màng co chống xốc kỹ càng và báo phí ship minh bạch.",
        "custom_items": "Không mang đồ riêng, dùng trọn gói của shop.",
        "shipping_need": "Giao xa Tam Kỳ, Quảng Nam."
    },
    {
        "id": "qn_dailoc_duyxuyen_custom",
        "name": "Cô Lan (Huyện Đại Lộc / Duy Xuyên, Quảng Nam)",
        "location": "Huyện Duy Xuyên, Quảng Nam",
        "budget_level": "Truyền thống",
        "preference": "Bộ 5 Tráp Thường",
        "trait": "Giọng đậm Quảng Nam (dầm ngõ, mâm quả, chốt giùm tui). Muốn tự chuẩn bị bánh su xê và chả bò quê mang đến shop decor.",
        "custom_items": "Tự đem bánh su xê và chả bò nhà làm tới shop decor hoa tươi.",
        "shipping_need": "Giao về Duy Xuyên."
    }
]
