from pathlib import Path
from platformdirs import user_cache_dir
import os
import urllib.request
import zipfile
import subprocess
import wget


def main():
    # Assume this script runs by the appropriate micromamba env.
    rom_path = Path(user_cache_dir("portal-env"))
    if not rom_path.exists():
        print(f"Downloading ROM to '{rom_path}'...")
        rom_path.mkdir(parents=True)
        cache_dir = rom_path
        zip_path = os.path.join(cache_dir, "sega-megadrive-genesis.zip")
        zip_url = "https://archive.org/download/No-Intro-Collection_2016-01-03/Sega-MegaDrive-Genesis.zip"

        # Download the zip file
        # print("Downloading ROMs...")
        wget.download(zip_url, zip_path)

        # Unzip it
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(cache_dir)

        # Run retro.import
        print("Importing ROMs to gym-retro...")
        subprocess.run(["python3", "-m", "retro.import", cache_dir], check=True)

        # Clean up
        print("Cleaning up...")
        os.remove(zip_path)


if __name__ == '__main__':
    main()
