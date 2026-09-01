#!/usr/bin/env python3
"""
🔍 Dataset Validator & Cleaner for Qwen / Unsloth JSONL Fine-Tuning
Dùng để kiểm tra và tự động sửa lỗi cú pháp, tin nhắn rác (...) trong file raw_samples.jsonl
"""

import json
import os
import sys

def check_and_clean_dataset(file_path="data/raw_samples.jsonl", auto_fix=False):
    if not os.path.exists(file_path):
        # Kiểm tra đường dẫn dự phòng
        if os.path.exists("raw_samples.jsonl"):
            file_path = "raw_samples.jsonl"
        elif os.path.exists("../data/raw_samples.jsonl"):
            file_path = "../data/raw_samples.jsonl"
        else:
            print(f"❌ Không tìm thấy file dataset tại: {file_path}")
            return

    print(f"🔍 Đang kiểm tra file: {file_path}\n" + "-"*50)
    
    bad_lines = []
    cleaned_lines = []
    removed_msg_count = 0
    total_lines = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line_str = line.strip()
            total_lines += 1
            if not line_str:
                bad_lines.append((idx, "Dòng trống"))
                continue
            
            try:
                data = json.loads(line_str)
                messages = data.get("messages", [])
                if not isinstance(messages, list) or len(messages) == 0:
                    bad_lines.append((idx, "Thiếu trường `messages` hoặc danh sách rỗng"))
                    continue
                
                valid_messages = []
                has_error = False
                
                for m_idx, m in enumerate(messages):
                    if not isinstance(m, dict) or "role" not in m or "content" not in m:
                        bad_lines.append((idx, f"Message thứ {m_idx} không đủ thông tin (`role`, `content`)"))
                        has_error = True
                        break
                    
                    role = m.get("role")
                    content = str(m.get("content", "")).strip()
                    
                    if role not in ["system", "user", "assistant"]:
                        bad_lines.append((idx, f"Role không hợp lệ: '{role}' ở message {m_idx}"))
                        has_error = True
                        break
                    
                    if not content or content in ["...", "…"]:
                        bad_lines.append((idx, f"Nội dung rỗng/chứa '...' ở message {m_idx} ({role})"))
                        removed_msg_count += 1
                        has_error = True
                        # Không thêm message bị lỗi này vào valid_messages
                    else:
                        valid_messages.append(m)
                
                if valid_messages:
                    data["messages"] = valid_messages
                    cleaned_lines.append(json.dumps(data, ensure_ascii=False))

            except json.JSONDecodeError as e:
                bad_lines.append((idx, f"Lỗi cú pháp JSON: {e}"))

    # Báo cáo kết quả
    print(f"📊 BÁO CÁO KIỂM TRA DATASET:")
    print(f" - Tổng số dòng kiểm tra: {total_lines}")
    print(f" - Số dòng HỢP LỆ: {len(cleaned_lines)}")
    print(f" - Số dòng CÓ LỖI: {len(bad_lines)}")
    print(f" - Số tin nhắn rác (...) phát hiện: {removed_msg_count}")
    
    if bad_lines:
        print("\n⚠️ CHI TIẾT LỖI TÌM THẤY:")
        for line_num, reason in bad_lines[:20]:
            print(f"   • Dòng {line_num}: {reason}")
        if len(bad_lines) > 20:
            print(f"   ... và {len(bad_lines) - 20} lỗi khác.")
    else:
        print("\n✅ DATASET HOÀN TOÀN SẠCH & KHÔNG CÓ LỖI!")

    # Tự động ghi lại file nếu bật auto_fix
    if auto_fix and bad_lines:
        print("\n🧹 Đang làm sạch và ghi lại file...")
        with open(file_path, "w", encoding="utf-8") as f:
            for l in cleaned_lines:
                f.write(l + "\n")
        print(f"✅ Đã lưu file đã làm sạch vào: {file_path}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/raw_samples.jsonl"
    fix = "--fix" in sys.argv
    check_and_clean_dataset(path, auto_fix=fix)
