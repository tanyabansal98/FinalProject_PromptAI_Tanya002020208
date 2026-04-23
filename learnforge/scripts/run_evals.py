#!/usr/bin/env python3
"""Run all evaluations."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluation")

for script in ["eval_rag.py", "eval_content.py", "eval_e2e.py"]:
    path = os.path.join(EVAL_DIR, script)
    if os.path.exists(path):
        print(f"\n{'='*40}\nRunning {script}\n{'='*40}")
        subprocess.run([sys.executable, path], cwd=PROJECT_ROOT)
    else:
        print(f"⚠️ {script} not found")
