#!/usr/bin/env python3
"""
CLI script to convert a font's glyphs into png images which will be used to
ascii-fy an image.
"""

from os import makedirs

import typer
from ascii.font2png import font2png
from pathlib import Path

app = typer.Typer()


@app.command()
def convert(glyph_num: int):
    """
    Convert font glyphs to png images.
    """
    # make sure output directory exists
    Path("./glyphs").mkdir(parents=True, exist_ok=True)

    font2png(glyph_num, 12, 24, "./glyphs")

def _main():
    """
    Dummy function to run typer CLI script using `poetry run ...` commands.

    Args: None, Returns: None
    """
    app()
