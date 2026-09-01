#!/usr/bin/env python3
"""
🚀 Single-file Python Script to Fine-tune Qwen2.5-14B-Instruct using Unsloth (QLoRA)
Compatible with: Kaggle, Google Colab, and Local GPU Server.
Dataset target: raw_samples.jsonl / dataset.jsonl
Export target: Ollama GGUF (q4_k_m) + Modelfile
"""

import os
import sys

# Disable WANDB to prevent circular import issues on Kaggle/Colab
os.environ["WANDB_DISABLED"] = "true"

def check_environment():
    """Kiểm tra sơ bộ môi trường huấn luyện."""
    try:
        import torch
        print(f"📌 PyTorch Version: {torch.__version__}")
        print(f"📌 CUDA Available: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ Chưa cài đặt PyTorch!")

def main():
    print("=" * 65)
    print("🚀 UNSLOTH QWEN2.5-14B-INSTRUCT FINE-TUNING PIPELINE (.PY VERSION)")
    print("=" * 65)

    check_environment()

    import torch
    from datasets import load_dataset
    from unsloth import FastLanguageModel, is_bfloat16_supported
    from unsloth.chat_templates import get_chat_template
    from trl import SFTTrainer
    from transformers import TrainingArguments

    # 1. Xác định Môi trường (Kaggle, Colab, hay Local)
    is_kaggle = os.path.exists("/kaggle/working")
    is_colab = "COLAB_GPU" in os.environ or os.path.exists("/content")

    if is_kaggle:
        output_base_dir = "/kaggle/working/qwen2.5_14b_output"
        print("💻 Phát hiện Môi trường: KAGGLE NOTEBOOK")
    elif is_colab:
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            output_base_dir = "/content/drive/MyDrive/Qwen2.5-14B-FineTuned"
            print("🔗 Phát hiện Môi trường: GOOGLE COLAB (Đã mount Drive)")
        except Exception:
            output_base_dir = "./qwen2.5_14b_output"
            print("💻 Phát hiện Môi trường: GOOGLE COLAB")
    else:
        output_base_dir = "./qwen2.5_14b_output"
        print("💻 Phát hiện Môi trường: LOCAL / GPU SERVER")

    os.makedirs(output_base_dir, exist_ok=True)

    # 2. Kiểm tra GPU
    if not torch.cuda.is_available():
        print("❌ CRITICAL: Cần có GPU CUDA để tiến hành Fine-tune mô hình 14B!")
        sys.exit(1)

    gpu_count = torch.cuda.device_count()
    gpu_stats = torch.cuda.get_device_properties(0)
    print(f"📌 GPU Device: {gpu_stats.name} (Số lượng GPU: {gpu_count})")
    print(f"📌 Total VRAM: {gpu_stats.total_memory / 1024**3:.2f} GB")

    # 3. Tìm file Dataset
    import glob
    possible_paths = [
        "/kaggle/input/**/raw_samples.jsonl",
        "/kaggle/input/**/dataset.jsonl",
        "/content/drive/MyDrive/raw_samples.jsonl",
        "/content/drive/MyDrive/data-train/raw_samples.jsonl",
        "/content/drive/MyDrive/train-chatbot/data/raw_samples.jsonl",
        "data/raw_samples.jsonl",
        "data-train/raw_samples.jsonl",
        "raw_samples.jsonl",
        "data-train/dataset.jsonl",
        "dataset.jsonl",
    ]
    
    dataset_path = None
    for p in possible_paths:
        matches = glob.glob(p, recursive=True)
        if matches:
            dataset_path = matches[0]
            break

    if not dataset_path:
        print("❌ Không tìm thấy file dataset (raw_samples.jsonl hoặc dataset.jsonl)!")
        print("👉 Vui lòng upload file dataset vào cùng thư mục với script này.")
        sys.exit(1)

    print(f"✅ Đã tìm thấy dataset: {dataset_path}")

    # 4. Cấu hình Model 14B QLoRA 4-bit
    max_seq_length = 2048
    model_name = "unsloth/Qwen2.5-14B-Instruct-bnb-4bit"

    print(f"\n📦 Loading Model & Tokenizer: {model_name}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    # 5. Thiết lập QLoRA Adapters
    print("⚙️ Setting up PEFT / QLoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    # 6. Format Chat Template Qwen2.5
    tokenizer = get_chat_template(
        tokenizer,
        chat_template="qwen-2.5",
    )

    def formatting_prompts_func(examples):
        convs = examples["messages"]
        texts = [
            tokenizer.apply_chat_template(
                convo, tokenize=False, add_generation_prompt=False
            )
            for convo in convs
        ]
        return {"text": texts}

    # 7. Load & Prepare Dataset
    print("🔄 Loading & Formatting Dataset...")
    full_dataset = load_dataset("json", data_files=dataset_path, split="train")
    split_dataset = full_dataset.train_test_split(test_size=0.1, seed=3407)
    train_dataset = split_dataset["train"].map(formatting_prompts_func, batched=True)
    eval_dataset = split_dataset["test"].map(formatting_prompts_func, batched=True)

    print(f"📊 Tổng mẫu: {len(full_dataset)} | Train: {len(train_dataset)} | Validation: {len(eval_dataset)}")

    # 8. Huấn luyện SFTTrainer
    checkpoints_dir = os.path.join(output_base_dir, "checkpoints")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            num_train_epochs=3,
            learning_rate=2e-4,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=5,
            eval_strategy="steps",
            eval_steps=20,
            save_strategy="steps",
            save_steps=20,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=checkpoints_dir,
            report_to="none",
        ),
    )

    print("\n🔥 STARTING FINE-TUNING QWEN2.5-14B-INSTRUCT...")
    trainer_stats = trainer.train()
    print(f"✅ Training completed in {trainer_stats.metrics['train_runtime']:.2f} seconds!")

    # 9. Test Inference Phản hồi
    print("\n🧪 TESTING INFERENCE AFTER FINE-TUNING...")
    FastLanguageModel.for_inference(model)

    test_messages = [
        {
            "role": "system",
            "content": "Bạn là Chuyên viên Tư vấn Tráp Cưới cao cấp của Tráp Lễ Cưới Hỏi Thiên Di (Đà Nẵng & Quảng Nam).",
        },
        {
            "role": "user",
            "content": "Chào shop, bên mình có giao 5 tráp Rồng Phượng về Điện Bàn không? Phí vận chuyển tính thế nào?",
        },
    ]

    inputs = tokenizer.apply_chat_template(
        test_messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    ).to("cuda")

    outputs = model.generate(input_ids=inputs, max_new_tokens=256, use_cache=True)
    decoded = tokenizer.batch_decode(outputs)[0]
    print("\n--- RESPONSE FROM TRAINED MODEL ---")
    if "<|im_start|>assistant" in decoded:
        print(decoded.split("<|im_start|>assistant\n")[1].replace("<|im_end|>", "").strip())
    else:
        print(decoded)

    # 10. Save GGUF & Modelfile cho Ollama
    gguf_dir = os.path.join(output_base_dir, "qwen2.5_14b_gguf")
    lora_dir = os.path.join(output_base_dir, "qwen2.5_14b_lora")

    print(f"\n💾 Saving LoRA weights to {lora_dir}...")
    model.save_pretrained(lora_dir)
    tokenizer.save_pretrained(lora_dir)

    print(f"\n📦 Exporting GGUF (Quantization Q4_K_M) cho Ollama sang {gguf_dir}...")
    try:
        model.save_pretrained_gguf(gguf_dir, tokenizer, quantization_method="q4_k_m")
        
        modelfile_path = os.path.join(gguf_dir, "Modelfile_qwen14b")
        modelfile_content = f"""FROM ./unsloth.Q4_K_M.gguf

TEMPLATE \"\"\"{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ .Response }}<|im_end|>\"\"\"

PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
"""
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)

        print(f"📄 Đã tạo Ollama Modelfile tại: {modelfile_path}")
        print("\n🎉 HOÀN TẤT! Đường dẫn file mô hình:")
        print(f"📍 {gguf_dir}")

    except Exception as e:
        print(f"⚠️ Lưu GGUF thất bại: {e}")

if __name__ == "__main__":
    main()
