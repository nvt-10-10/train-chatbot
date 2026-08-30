#!/usr/bin/env python3
"""
Test script to generate and preview 1 sample consultation dialogue.
"""

import asyncio
import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from config.personas import CUSTOMER_PERSONAS
from config.scenarios import GENERATION_SCENARIOS
from core.generator import OllamaDataGenerator
from core.validator import DatasetValidator

console = Console()


async def main():
    console.print("\n[bold yellow]🧪 ĐANG TEST GENERATE 1 MẪU HỘI THOẠI THỬ NGHIỆM...[/bold yellow]\n")

    generator = OllamaDataGenerator(
        model_name="qwen2.5:14b-instruct",
        host="http://localhost:11434",
        concurrency=1,
    )

    persona = CUSTOMER_PERSONAS[0]  # Khách Hải Châu, Đà Nẵng
    scenario = GENERATION_SCENARIOS[0]  # Tư vấn 5 tráp Rồng Phượng vs Thường

    console.print(f"[cyan]Khách hàng:[/cyan] {persona['name']} ({persona['location']})")
    console.print(f"[cyan]Chủ đề tư vấn:[/cyan] {scenario['topic']}\n")
    console.print("[dim]Đang kết nối Ollama qwen2.5:14b-instruct... Vui lòng chờ vài giây...[/dim]\n")

    sample = await generator.generate_single_dialogue(persona, scenario)

    if not sample:
        console.print("[bold red]❌ Lỗi: Không sinh được dữ liệu từ Ollama local.[/bold red]")
        return

    # Run Quality Control check
    validator = DatasetValidator()
    is_valid, reason = validator.validate_sample(sample)

    console.print(
        Panel.fit(
            f"[bold green]Trạng thái Quality Control (QC):[/bold green] {is_valid} ({reason})",
            title="[bold blue]QC Validation Check[/bold blue]",
        )
    )

    # Print formatted conversation turns
    console.print("\n[bold magenta]=== NỘI DUNG HỘI THOẠI ĐƯỢC SINH TỰ ĐỘNG ===[/bold magenta]\n")
    for msg in sample.get("messages", []):
        role = msg.get("role", "").upper()
        content = msg.get("content", "")

        if role == "SYSTEM":
            console.print(Panel(content[:300] + "...", title="[bold yellow]SYSTEM PROMPT[/bold yellow]", border_style="yellow"))
        elif role == "USER":
            console.print(Panel(content, title="[bold cyan]👤 KHÁCH HÀNG (USER)[/bold cyan]", border_style="cyan"))
        elif role == "ASSISTANT":
            console.print(Panel(content, title="[bold green]🤖 SHOP TƯ VẤN (ASSISTANT)[/bold green]", border_style="green"))

    # Print raw JSON format
    console.print("\n[bold yellow]=== ĐỊNH DẠNG DỮ LIỆU JSONL CHUẨN FINE-TUNE ===[/bold yellow]\n")
    json_str = json.dumps(sample, ensure_ascii=False, indent=2)
    console.print(Syntax(json_str, "json", theme="monokai", line_numbers=True))


if __name__ == "__main__":
    asyncio.run(main())
