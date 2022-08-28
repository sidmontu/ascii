#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont


def font2png(
    glyph_num: int,
    width: int,
    height: int,
    output_dir: str,
    path_to_font: str = "fonts/courier.ttf",
    background_color: str = "white",
    glyph_color: str = "black",
):
    """
    Convert an input font file into individual glyph png files.

    Args:

        glyph_num (int): ASCII code of glyph to generate

        width (int): Output png image width of each glyph.

        height (int): Output png image height of each glyph.

        output_dir (str): Output directory to write png files to.

        path_to_font (str): Path to font file (.ttf) to use. Default is set to
        the 'courier.tff' font provided in this project.

        background_color (str): Color of background, default = "white"

        glyph_color (str): Color of glyph, default = "black"

    Returns: None
    """

    # load font
    font = ImageFont.truetype(path_to_font, min(width, height), encoding="utf-8")

    # make image, use black color as default
    glyph = chr(glyph_num)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    offset_w, offset_h = font.getoffset(glyph)
    w, h = draw.textsize(glyph, font=font)
    pos = ((width - w - offset_w) / 2, (height - h - offset_h) / 2)

    # draw the image
    draw.text(pos, glyph, "black", font=font)

    # write to output
    img.save(f"{output_dir}/{glyph_num}.png")
