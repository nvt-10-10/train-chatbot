# 🌺 Hybrid Fine-Tuning Pipeline: Đà Nẵng & Quảng Nam Wedding Tráp Advisor

Hệ thống Hybrid Fine-Tuning 2 Mô-đun hoàn chỉnh:
1. **Mô-đun Local (Ubuntu/Lenovo)**: Sinh tự động $N$ cuộc hội thoại tư vấn tráp cưới chuẩn ngữ cảnh địa phương (Đà Nẵng & Quảng Nam) bằng Ollama (`qwen2.5:14b-instruct`), chạy bộ lọc Quality Control (QC), tự động chia 80% train (`dataset_train.jsonl`) / 20% val (`dataset_val.jsonl`) và push trực tiếp lên GitHub.
2. **Mô-đun Google Colab (`train_colab.ipynb`)**: Fine-Tune mô hình `unsloth/Qwen2.5-7B-Instruct-bnb-4bit` bằng Unsloth (QLoRA), tự động export mô hình định dạng GGUF và push trực tiếp lên Hugging Face Hub.

---

## 🏛️ 1. Quy chuẩn Sản phẩm & Ràng buộc Địa phương

- **Phạm vi phục vụ**: Nhận và giao tráp tận nhà toàn bộ khu vực Đà Nẵng (Hải Châu, Thanh Khê, Sơn Trà, Ngũ Hành Sơn, Cẩm Lệ, Liên Chiểu, Hòa Vang) và Quảng Nam (Hội An, Điện Bàn, Đại Lộc, Duy Xuyên, Thăng Bình, Tam Kỳ...).
- **Chính sách ship**: Miễn phí/phí nhẹ nội thành Đà Nẵng. Quảng Nam tính phí ship theo km. Đảm bảo bọc màng co chống xốc cẩn thận.
- **Sản phẩm chính (Bộ 5 Tráp Quả - Đế mây, hoa tươi đỏ Burgundy)**:
  1. **BỘ 5 TRÁP RỒNG PHƯỢNG (CAO CẤP)**:
     - Tráp 1: Rồng kết nghệ thuật (Táo đỏ / Trái cây).
     - Tráp 2: Phượng kết nghệ thuật (Trầu cau tem cánh phụng).
     - Tráp 3: Trà Rượu decor cao cấp.
     - Tráp 4: Nem Chả (Đặc sản Đà Nẵng/Chợ Huyện).
     - Tráp 5: Bánh cưới / Bánh kem tháp hoa tươi.
  2. **BỘ 5 TRÁP BÌNH THƯỜNG (TRUYỀN THỐNG / HOA TƯƠI CƠ BẢN)**:
     - Tráp 1: Trái cây Táo đỏ viền hoa tươi Burgundy.
     - Tráp 2: Trầu cau cánh phụng viền hoa tươi.
     - Tráp 3: Trà Rượu decor hoa tươi.
     - Tráp 4: Nem Chả (Đặc sản Đà Nẵng/Chợ Huyện).
     - Tráp 5: Bánh cưới / Bánh kem / Bánh khối hoa tươi.
- **Quy định quan trọng**:
  - **KHÔNG bán Heo Quay**: Shop không cung cấp tráp heo quay. Nếu khách tự mang heo quay tới, shop xếp mâm & decor hoa tươi **miễn phí**.
  - **Lễ vật tự mang (bánh su xê, phu thê, bánh in...)**: Khách mang tới shop xếp mâm & decor hoa tươi **miễn phí 100%**.
- **Văn phong**: Xởi lởi, nhiệt tình, chuẩn giọng miền Trung (*mâm quả, dầm ngõ, nem chả, chốt giùm em, ship tận nơi...*).

---

## 🛠️ 2. Hướng dẫn Mô-đun Local (Sinh Data & Push GitHub)

### Bước 2.1: Cài đặt Môi trường Local
```bash
# Khởi động dịch vụ Ollama local và kéo model Qwen 2.5 14B
ollama pull qwen2.5:14b-instruct

# Di chuyển vào thư mục dự án
cd trap_danang_quangnam_hybrid

# Cài đặt các thư viện Python
pip install -r requirements.txt
```

### Bước 2.2: Chạy Lệnh CLI Sinh Data + QC + Auto Push GitHub
```bash
# Sinh 50 mẫu data, QC lọc sạch, tự động push lên GitHub
python main.py --num-samples 50 --ollama-model qwen2.5:14b-instruct --push-git --git-remote origin --git-branch main
```

**Các tham số tùy chọn CLI:**
- `--num-samples` / `-n`: Số lượng conversation cần sinh (Mặc định: 50).
- `--ollama-model` / `-m`: Model Ollama local (Mặc định: `qwen2.5:14b-instruct`).
- `--concurrency` / `-c`: Số luồng chạy song song async (Mặc định: 4).
- `--output-dir` / `-o`: Thư mục lưu dataset JSONL (Mặc định: `./data`).
- `--push-git` / `-p`: Tự động git commit và push dataset lên GitHub.

---

## 🚀 3. Hướng dẫn Mô-đun Google Colab (`train_colab.ipynb`)

1. Đẩy file `train_colab.ipynb` lên Google Drive hoặc mở trực tiếp trên [Google Colab](https://colab.research.google.com/).
2. Đổi môi trường Runtime sang **GPU (T4 hoặc A100)** (`Runtime` -> `Change runtime type` -> `T4 GPU`).
3. Mở notebook và chạy từng bước:
   - **Bước 1-2**: Cài đặt Unsloth và clone/pull dataset mới nhất từ GitHub Repo của bạn.
   - **Bước 3-4**: Load `unsloth/Qwen2.5-7B-Instruct-bnb-4bit` và định dạng dataset theo Qwen 2.5 Chat Template.
   - **Bước 5**: Chạy SFTTrainer fine-tune cực nhanh.
   - **Bước 6**: Inference thử nghiệm câu trả lời tư vấn tráp cưới.
   - **Bước 7-8**: Export GGUF (`q4_k_m`) và push thẳng lên **Hugging Face Hub**.

---

## 📁 4. Cấu trúc Mã nguồn Dự án

```text
trap_danang_quangnam_hybrid/
├── config/
│   ├── __init__.py
│   ├── personas.py          # Chân dung khách hàng ĐN - Quảng Nam & nhu cầu
│   └── scenarios.py         # Kịch bản tư vấn bộ 5 tráp, heo quay, bánh tự mang
├── core/
│   ├── __init__.py
│   ├── generator.py         # Engine sinh data Async với Ollama
│   ├── validator.py         # Bộ lọc QC & chia 80% train / 20% val
│   └── git_pusher.py        # Tự động git commit & push dataset lên GitHub
├── main.py                  # Lệnh CLI sinh data + auto push lên GitHub
├── train_colab.ipynb        # Jupyter Notebook Unsloth QLoRA trên Google Colab
├── requirements.txt         # Thư viện Python phục vụ local
└── README.md                # Hướng dẫn chi tiết A-Z
```
