#!/usr/bin/env python3
"""
CLI tool for ASCII-fyig an input image.
"""

import typer
from ascii.asciify import run
from pathlib import Path

app = typer.Typer()


@app.command()
def asciify(
    img_path: str,
    output_img_path: str, 
    glyphs_dir: str = "./glyphs",
    glyph_width: int = 7,
    glyph_height: int = 9,
    num_iterations: int = 1000,
):
    run(img_path, output_img_path, glyphs_dir, (glyph_width, glyph_height), num_iterations)


def _main():
    """
    Dummy function to run typer CLI script using `poetry run ...` commands.

    Args: None, Returns: None
    """
    app()
