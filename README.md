# Xtreme Firmware Asset (Un)Packer

Xtreme Firmware for Flipper Zero comes with the option to install custom asset packs. This replaces the default flipper animations with whatever the user wants. Said asset packs are encoded frame-by-frame in the XBM format (blarg). These can be opened on Linux with some mild effort, but this script aims to convert and knit XBM frames into the more prevalent GIF format.

## Setup

You will only need the `Pillow` and `heatshrink2` libraries. Using a `venv` is recommended (in general). 


```bash
# Install and create a venv
pip3 install venv
python3 -m venv unpacker

# Clone repo and move files
gh repo clone mattryczek/xfw-unpacker

#  OR

git clone https://github.com/mattryczek/xfw-unpacker.git

cp xfw-unpacker/unpacker.py xfw-unpacker/requirements.txt unpacker/

# Activate venv and install dependencies
cd unpacker
source bin/activate
pip3 install -r requirements.txt
```

## Usage
The script will read through all the folders in its parent directory and attempt to rebuild any packed animations into GIFs. Reconstructed animations will be placed into the `Unpacked` folder mirroring the inital asset packs' structure. Individual frames will be exported as PNG files, and stored in the `Frames` directory. GIFs will end up in the `GIFs` folder. Folders with no XBM frame data or `manifest.txt` file will be ignored. 

```bash
# Assuming you followed the above setup instructions

cd unpacker
source bin/activate
python3 unpacker.py
```