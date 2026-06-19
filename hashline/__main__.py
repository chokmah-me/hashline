"""Allow running the package as a module.

Usage:
    python -m hashline read path/to/file.py
    python -m hashline compose --model gemini
    python -m hashline --help
"""

from .cli import main

if __name__ == "__main__":
    main()
