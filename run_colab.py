#!/usr/bin/env python3
"""
Single command entry point for Google Colab fine-tuning Qwen2.5-14B-Instruct.
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from train_qwen14b import main
except ImportError:
    parent_dir = os.path.dirname(script_dir)
    sys.path.insert(0, parent_dir)
    from train_qwen14b import main

if __name__ == "__main__":
    main()
