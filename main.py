#!/usr/bin/env python3
"""
CLI Main Entrypoint for Đà Nẵng & Quảng Nam Wedding Tráp Synthetic Data Pipeline.
"""

import argparse
import asyncio
import os
import sys
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
    TimeElapsedColumn,
)
from rich.panel import Panel
from rich.table import Table

from core.generator import OllamaDataGenerator
from core.validator import DatasetValidator
from core.git_pusher import GitDatasetPusher

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Đà Nẵng & Quảng Nam Wedding Tráp Synthetic Data Generator & GitHub Auto-Pusher"
    )
    parser.add_argument(
        "--num-samples",
        "-n",
        type=int,
        default=50,
        help="Number of synthetic consultation samples to generate (default: 50)",
    )
    parser.add_argument(
        "--ollama-model",
        "-m",
        type=str,
        default="qwen2.5:14b-instruct",
        help="Local Ollama model name (default: qwen2.5:14b-instruct)",
    )
    parser.add_argument(
        "--ollama-host",
        type=str,
        default="http://localhost:11434",
        help="Ollama API Host URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=4,
        help="Number of concurrent async Ollama workers (default: 4)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="./data",
        help="Output directory for generated dataset (default: ./data)",
    )
    parser.add_argument(
        "--push-git",
        "-p",
        action="store_true",
        help="Auto commit and push generated dataset files to GitHub",
    )
    parser.add_argument(
        "--git-remote",
        type=str,
        default="origin",
        help="Git remote name (default: origin)",
    )
    parser.add_argument(
        "--git-branch",
        type=str,
        default="main",
        help="Git branch name (default: main)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset existing cached raw samples and start generation from scratch",
    )
    return parser.parse_args()


async def main_async():
    args = parse_args()

    console.print(
        Panel.fit(
            f"[bold magenta]Tráp Lễ Cưới Hỏi Thiên Di - Synthetic Data Generator (Đà Nẵng & Quảng Nam)[/bold magenta]\n"
            f"[cyan]Ollama Model:[/cyan] {args.ollama_model} | [cyan]Host:[/cyan] {args.ollama_host}\n"
            f"[cyan]Target Samples:[/cyan] {args.num_samples} | [cyan]Concurrency:[/cyan] {args.concurrency}\n"
            f"[cyan]Output Directory:[/cyan] {args.output_dir} | [cyan]Auto Git Push:[/cyan] {args.push_git}",
            title="[bold yellow]System Initialization[/bold yellow]",
        )
    )

    generator = OllamaDataGenerator(
        model_name=args.ollama_model, host=args.ollama_host, concurrency=args.concurrency
    )

    raw_save_path = os.path.join(args.output_dir, "raw_samples.jsonl")
    if args.reset and os.path.exists(raw_save_path):
        os.remove(raw_save_path)
        console.print("[yellow]⚠️ --reset flag passed. Removed existing raw_samples.jsonl checkpoint.[/yellow]")

    console.print("\n[bold green]🚀 Step 1: Generating Synthetic Consulting Dialogues via Ollama...[/bold green]\n")
    
    samples = []
    sample_counter = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[yellow]Generating dialogues...", total=args.num_samples)
        
        def update_progress(count: int, sample: Optional[Dict[str, Any]] = None, is_initial: bool = False):
            nonlocal sample_counter
            if is_initial:
                sample_counter += count
                progress.update(task, completed=count)
                if count > 0:
                    console.print(f"[bold cyan]🔄 Loaded {count} existing raw samples from checkpoint: {raw_save_path}[/bold cyan]")
                return

            progress.update(task, advance=count)
            if sample and isinstance(sample, dict) and "messages" in sample:
                messages = sample.get("messages", [])
                if isinstance(messages, list):
                    sample_counter += 1
                    
                    # Extract first User and Assistant content for preview
                    user_msg = next(
                        (
                            m.get("content")
                            for m in messages
                            if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
                        ),
                        "",
                    )
                    ast_msg = next(
                        (
                            m.get("content")
                            for m in messages
                            if isinstance(m, dict) and m.get("role") == "assistant" and isinstance(m.get("content"), str)
                        ),
                        "",
                    )
                    
                    # Print live preview panel in console and write to logger
                    logger.info(f"✨ [Mẫu #{sample_counter}/{args.num_samples}] hoàn thành | Khách: {user_msg[:60]}...")
                    console.print(
                        Panel(
                            f"[bold cyan]👤 Khách hàng:[/bold cyan] {user_msg[:180]}...\n\n"
                            f"[bold green]🤖 Shop tư vấn:[/bold green] {ast_msg[:250]}...",
                            title=f"[bold bright_yellow]✨ Live Preview [Mẫu #{sample_counter} Complete][/bold bright_yellow]",
                            border_style="cyan",
                        )
                    )

        samples = await generator.generate_dataset(
            num_samples=args.num_samples,
            progress_callback=update_progress,
            raw_save_path=raw_save_path,
        )

    console.print(f"\n[bold green]✅ Generated {len(samples)} raw dialogue samples.[/bold green]")

    console.print("\n[bold green]🔍 Step 2: Quality Control (QC) & Dataset Partitioning (80/20)...[/bold green]")
    validator = DatasetValidator(train_ratio=0.8)
    total_valid, train_count, val_count = validator.process_and_split(samples, args.output_dir)

    train_path = os.path.join(args.output_dir, "dataset_train.jsonl")
    val_path = os.path.join(args.output_dir, "dataset_val.jsonl")

    # Display Metrics Table
    table = Table(title="Dataset Partitioning & Quality Control Summary")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta")
    table.add_column("File Destination / Description", style="green")

    table.add_row("Total Generated", str(len(samples)), "Raw Ollama responses")
    table.add_row("Passed Quality Control", str(total_valid), "Domain rules & Heo Quay disclaimer checked")
    table.add_row("Training Split (80%)", str(train_count), train_path)
    table.add_row("Validation Split (20%)", str(val_count), val_path)

    console.print(table)

    if args.push_git:
        console.print("\n[bold green]📦 Step 3: Git Staging, Committing & Pushing to GitHub...[/bold green]")
        pusher = GitDatasetPusher(repo_path=".")
        success = pusher.commit_and_push(
            files_to_push=[train_path, val_path],
            remote_name=args.git_remote,
            branch_name=args.git_branch,
        )
        if success:
            console.print("[bold bright_green]🎉 Successfully committed and pushed dataset to GitHub![/bold bright_green]")
        else:
            console.print("[bold red]❌ Failed to push dataset to GitHub. Check your Git configuration.[/bold red]")

    console.print("\n[bold gold1]✨ Pipeline completed successfully![/bold gold1]")


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        console.print("\n[bold red]Execution interrupted by user.[/bold red]")
        sys.exit(1)
