#!/usr/bin/env python3

"""
Routines for ASCII-fying an input image.
"""

from os import listdir
from typing import Tuple
from PIL import Image
import numpy as np
import re
from os.path import join
from tqdm import tqdm

def _pad(img, pad_top, pad_right, pad_bottom, pad_left, pad_color):
    """
    """
    w, h = img.size
    w_ = w + pad_left + pad_right
    h_ = h + pad_top + pad_bottom
    img_ = Image.new(img.mode, (w_, h_), pad_color)
    img_.paste(img, (pad_left, pad_top))
    return img_

def _calc_pads(v, x):
    """
    """
    if (v % x):
        remainder = x - (v % x)
        a = remainder // 2
        b = a + (remainder % 2)
    else:
        a, b = 0, 0

    return a, b

def run(
    img_path: str,
    output_img_path: str,
    glyphs_dir: str,
    glyph_size: Tuple[int, int],
    num_iterations: int,
    beta: int = 2, # SED = 2, KLD = 1
    epsilon: int = 0
):
    """
    Top-level routine for running the ASCII-fication process.

    Args:

        beta (int): Set 2 for SED, 1 for KLD

    Returns:
    """
    # load the glyphs
    glyphs = []
    for glyph in listdir(glyphs_dir):
        if glyph.endswith(".png"):
            glyph_num = int(re.sub("\.png", "", glyph))
            glyphs.append((join(glyphs_dir, glyph), glyph_num, chr(glyph_num)))
    glyphs = sorted(glyphs, key = lambda x: x[1])

    num_glyphs = len(glyphs)
    print(f"> Found {num_glyphs} glyphs in directory {glyphs_dir}")

    # read in images & convert to grayscale
    img = Image.open(img_path).convert('L')
    print(f"> Converted {img_path} to grayscale.")

    # partition the input image
    # define P and Q, and the glyph dimensions
    Q, P = img.size
    g_col, g_row = glyph_size

    print(f"> Image size = {Q} x {P}, glyph size = {g_col} x {g_row} (= {g_col*g_row} px)")

    # pad the image to be a multiple of g_col/g_row
    pad_left, pad_right = _calc_pads(Q, g_col)
    pad_top, pad_bottom = _calc_pads(P, g_row)

    print(f"> Padding image by [top = {pad_top}], [bottom = {pad_bottom}], [left = {pad_left}], [right = {pad_right}]")
    img = _pad(img, pad_top, pad_right, pad_bottom, pad_left, 255)

    print(f"> Padded image to {img.size} (width % {g_col} = {img.size[0] % g_col}), (height % {g_row} = {img.size[1] % g_row})")

    # calculate number of blocks
    num_blocks_per_row = img.size[1] // g_row
    num_blocks_per_col = img.size[0] // g_col
    print(f"> Creating {num_blocks_per_col} x {num_blocks_per_row} blocks (= {num_blocks_per_col * num_blocks_per_row} blocks) of size {g_col} x {g_row}")

    # convert image into numpy array
    np_img = np.array(img).swapaxes(0, 1)

    # break matrix into glyph chunks
    V = np_img.reshape(np_img.shape[0] // g_col, g_col, np_img.shape[1] // g_row, g_row).swapaxes(1, 2).reshape(-1, g_col * g_row).swapaxes(0, 1)
    print(f"> Created matrix V of size {V.shape}, expected shape = ({g_row*g_col}, {num_blocks_per_row*num_blocks_per_col})")

    # load the glyphs as a matrix
    W = []
    glyph_px = []
    for glyph_file, glyph_num, glyph_char in glyphs:
        g_img = np.array(Image.open(glyph_file).convert('L'))
        glyph_px.append(g_img.swapaxes(0, 1))
        g_img = g_img.reshape(-1)
        l2norm = np.sqrt(np.sum(g_img))
        vector = g_img/l2norm
        W.append(vector)
    W = np.array(W).swapaxes(0, 1)
    print(f"> Created weights matrix from glyphs of shape = {W.shape}")

    # create random matrix
    H = np.random.rand(num_glyphs, num_blocks_per_row*num_blocks_per_col)
    print(f"> Created random matrix H of shape = {H.shape}")

    for _ in tqdm(range(num_iterations)):
        WH = np.matmul(W, H)
        WH_num = V / (WH ** (2 - beta))
        WH_den = WH ** (beta - 1)
        tW = np.transpose(W)
        H_next = np.multiply(H, np.nan_to_num(np.divide(np.matmul(tW, WH_num), np.matmul(tW, WH_den)), nan=0, posinf=0, neginf=0))
        H = H_next
    H_i = np.argmax(H, axis=0)

    # reconstruct image using ascii characters
    H_i = H_i.reshape(num_blocks_per_col, num_blocks_per_row)
    ascii_img = np.zeros((img.size[0], img.size[1]))
    for x in range(num_blocks_per_col):
        for y in range(num_blocks_per_row):
            ascii_img[(x*g_col):((x+1)*g_col), (y*g_row):((y+1)*g_row)] = glyph_px[H_i[x, y]]
    ascii_img = ascii_img.swapaxes(0, 1)
    print(f"> Converted to ASCII image of shape = {ascii_img.shape}")

    # save as png
    out_img = Image.fromarray(ascii_img)
    out_img = out_img.convert('RGB')
    out_img.save(output_img_path)
    print(f"> Written output ASCII image to {output_img_path} successfully.")
