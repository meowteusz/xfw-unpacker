# Xtreme Firmware Asset (Un)Packer

Xtreme Firmware for Flipper Zero comes with the option to install custom asset packs. This replaces the default flipper animations with whatever the user wants. Said asset packs are encoded frame-by-frame in the XBM format (blarg). These can be opened on Linux with some mild effort, but this script aims to convert and knit XBM frames into the more prevalent GIF format.

## Setup

You will only need the `Pillow` and `heatshrink2` libraries. Using a `venv` is highly recommended (in general). 


```bash
# Install and create a venv
pip3 install venv
python3 -m venv unpacker

# Clone repo and move files
gh repo clone mattryczek/xfw-unpacker

#  OR

git clone https://github.com/mattryczek/xfw-unpacker.git

cp xfw-unpacker/unpacker.py xfw-unpacker/requirements.txt unpacker/
cd unpacker
pip3 install -r requirements.txt
```

## Usage
The script will read through all the folders in its containing directory and attempt to rebuild any animations into GIFs. Folders with no XBM frame data will be ignored. Reconstructed GIFs will be placed into the `asset_raws` folder, mirroring their inital structure.

```bash
cd unpacker
python3 unpacker.py
```