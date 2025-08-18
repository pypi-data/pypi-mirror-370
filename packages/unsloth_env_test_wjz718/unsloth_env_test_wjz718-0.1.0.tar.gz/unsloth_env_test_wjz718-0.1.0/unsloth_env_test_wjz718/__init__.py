"""
unsloth_env_test_wjz718 - A minimal PyPI package example.

This package provides a single function `get_readme` that returns a simple tutorial.
"""
__version__ = "0.1.0"   # ← 必须要有

def get_readme() -> str:
    """
    Return a simple tutorial string.
    """
    return """
# 使用教程

1. 安装:
   ```bash
   pip install mypackage"""