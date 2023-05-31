#!/usr/bin/env python3
"""
CLI script to convert a font's glyphs into png images which will be used to
ascii-fy an image.
"""

import typer
from ascii.font2png import make_glyph
from pathlib import Path

app = typer.Typer()


@app.command()
def convert(
    ascii_from: int = 32,
    ascii_to: int = 126,
    glyph_width: int = 7,
    glyph_height: int = 9,
    output_dir: str = "./glyphs",
):
    """
    Convert font glyphs to png images.

    Args:

        ascii_from (int): Starting ASCII code. Default = 32.

        ascii_to (int): Ending ASCII code (inclusive). Default = 126

        glyph_width (int): Width of the png output (in px). Default = 12

        glyph_height (int): Height of the png output (in px). Default = 16

        output_dir (str): Path to directory to write output pngs to. Default is
        set to "./glyphs"

    Returns: None
    """
    # make sure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for glyph_num in range(ascii_from, ascii_to + 1):
        make_glyph(glyph_num, glyph_width, glyph_height, output_dir)


def _main():
    """
    Dummy function to run typer CLI script using `poetry run ...` commands.

    Args: None, Returns: None
    """
    app()
