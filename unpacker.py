#!/usr/bin/env python
from PIL import Image, ImageOps, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

import heatshrink2
import pathlib
import shutil
import typing
import time
import re
import io
import os


def wrap_xbm(data: str) -> bytes:
    return bytes(
        f"#define im_width 128\n#define im_height 64\nstatic unsigned char im_bits[] = {{{data}}};",
        "utf-8",
    )


def bm2xbm(img: pathlib.Path) -> bytes:
    with open(img, "rb") as frame:
        data = frame.read()
        frame.close()

    if data[:2] == b"\x01\x00":
        # Pop compression flag bits & length metadata
        data = data[4:]

        # Decompress data
        data = heatshrink2.decompress(data, window_sz2=8, lookahead_sz2=4)

        # Get bytes as a `str` list, one byte per index
        data = data.hex(",").split(",")

        # Prepend each byte with '0x'
        data = list(map(lambda x: "0x" + x, data))

        # Collect list into `str` and get rid of brackets, quotes
        data = str(data)[1:-1].replace("'", "")

    elif data[:1] == b"\x00":
        # Pop compression bit
        data = data[1:]

        # Get bytes as a `str` list, one byte per index
        data = data.hex(",").split(",")

        # Prepand each byte with '0x'
        data = list(map(lambda x: "0x" + x, data))

        # Collect list into `str` and get rid of brackets, quotes
        data = str(data)[1:-1].replace("'", "")
    else:
        print("Unrecognized compression flag!")
        data = b"\x00"

    return wrap_xbm(data)


def convert_bm(img: "Image.Image | pathlib.Path") -> bytes:
    if not isinstance(img, Image.Image):
        img = Image.open(img)

    with io.BytesIO() as output:
        img = img.convert("1")
        img = ImageOps.invert(img)
        img.save(output, format="XBM")
        # img.show()
        xbm = output.getvalue()

    f = io.StringIO(xbm.decode().strip())

    # Delete newlines, delete spaces. Split string into preamble (W + H) and bits assignment. Drop semicolon
    data = f.read().strip().replace("\n", "").replace(" ", "").split("=")[1][:-1]

    # Drop brackets (first and last char). Fix separator. Drop 0x prefix.
    data_str = data[1:-1].replace(",", " ").replace("0x", "")
    data_bin = bytearray.fromhex(data_str)

    data_encoded_str = heatshrink2.compress(data_bin, window_sz2=8, lookahead_sz2=4)
    data_enc = bytearray(data_encoded_str)
    data_enc = bytearray([len(data_enc) & 0xFF, len(data_enc) >> 8]) + data_enc

    if len(data_enc) + 2 < len(data_bin) + 1:
        return b"\x01\x00" + data_enc
    else:
        return b"\x00" + data_bin


def unpack_anim(src: pathlib.Path, dst: pathlib.Path, gif: pathlib.Path):
    if not (src / "meta.txt").is_file():
        return

    dst.mkdir(parents=True, exist_ok=True)
    gif.mkdir(parents=True, exist_ok=True)

    images = []

    # Big lambda ensures in-order traversal and thus in-order GIF file ^3^
    for frame in sorted(
        src.iterdir(),
        key=lambda x: (
            int(x.stem.split("_")[-1]) if x.stem.split("_")[-1].isdigit() else -1
        ),
    ):
        if not frame.is_file():
            continue
        if frame.name == "meta.txt":
            shutil.copyfile(src / "meta.txt", dst / "meta.txt")
            continue
        elif frame.name.startswith("frame_"):
            # (dst / frame.with_suffix(".xbm").name).write_bytes(bm2xbm(frame))

            img_bytes = io.BytesIO(bm2xbm(frame))
            img = Image.open(img_bytes, mode="r", formats=["XBM"])
            img = ImageOps.invert(img)
            img.save(dst / frame.with_suffix(".png").name, format="PNG")
            images.append(img)

    # Edit the duration on this line if GIFs are too fast or slow.
    images[0].save(
        gif / f"{src.stem}.gif",
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=167,
        disposal=2,
        loop=1,
        transparency=1,
        format="GIF",
    )


def unpack(
    input: "str | pathlib.Path", output: "str | pathlib.Path", logger: typing.Callable
):
    input = pathlib.Path(input)
    output = pathlib.Path(output)

    for source in input.iterdir():
        if source == output:
            continue
        if not source.is_dir():
            continue

        logger(f"Unpack: custom user pack '{source.name}'")
        unpacked = output / source.name
        if unpacked.exists():
            try:
                if unpacked.is_dir():
                    shutil.rmtree(unpacked, ignore_errors=True)
                else:
                    unpacked.unlink()
            except Exception:
                pass

        if (source / "Anims/manifest.txt").exists():
            (unpacked / "Anims").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(
                source / "Anims/manifest.txt", unpacked / "Anims/manifest.txt"
            )
            manifest = (source / "Anims/manifest.txt").read_bytes()

            for anim in re.finditer(rb"Name: (.*)", manifest):
                anim = (
                    anim.group(1)
                    .decode()
                    .replace("\\", "/")
                    .replace("/", os.sep)
                    .replace("\r", "\n")
                    .strip()
                )
                logger(f"Decompile: anim for pack '{source.name}': {anim}")
                unpack_anim(
                    source / "Anims" / anim,
                    unpacked / "Anims" / anim,
                    unpacked / "gifs",
                )


if __name__ == "__main__":
    print(
        "This will look through all the subfolders next to this file and try to unpack them\n"
        "The resulting asset packs will be saved to 'asset_raws' in this folder\n"
    )

    here = pathlib.Path(__file__).absolute().parent
    start = time.perf_counter()

    unpack(here, here / "asset_raws", logger=print)

    end = time.perf_counter()
    print(f"\nFinished in {round(end - start, 2)}s\n")
