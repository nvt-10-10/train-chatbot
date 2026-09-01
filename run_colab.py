#!/usr/bin/env python3
"""
Single command entry point for Google Colab fine-tuning Qwen2.5-14B-Instruct.
Run in Colab:
!python trap_danang_quangnam_hybrid/run_colab.py
"""
import os
import sys

# Change directory to root project if executed from subfolder
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from train_qwen14b import main

if __name__ == "__main__":
    main()
