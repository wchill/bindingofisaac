import argparse
import os
import sys
import subprocess
import shutil
import warnings
from pathlib import Path


def extract_nsp(path):
    nsp_name = Path(path).stem
    if not os.path.exists(nsp_name):
        process = subprocess.run(
            ["./hactool", "-t", "pfs0", path, "--outdir", nsp_name]
        )
        process.check_returncode()

    return nsp_name


def find_largest_nca(path):
    nca_size = 0
    nca_path = None
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            if not name.endswith(".nca"):
                continue
            path = os.path.join(root, name)
            size = os.path.getsize(path)
            if nca_size < size:
                nca_size = size
                nca_path = path

    return nca_path


def extract_romfs(base, update):
    base_nca_path = find_largest_nca(base)
    update_nca_path = find_largest_nca(update)
    updated_romfs_path = f"romfs_{Path(update_nca_path).stem}"

    if not os.path.exists(updated_romfs_path):
        process = subprocess.run(
            [
                "./hactool",
                "--basenca",
                base_nca_path,
                "--romfsdir",
                updated_romfs_path,
                update_nca_path,
            ]
        )
        process.check_returncode()

    return updated_romfs_path


def copy_files(update_romfs, dlc_romfs, dest, *files):
    os.makedirs(dest, exist_ok=True)
    for name in files:
        try:
            shutil.copyfile(
                f"{update_romfs}/rp_patch/resources/{name}", f"{dest}/{name}"
            )
        except Exception as e:
            shutil.copyfile(f"{dlc_romfs}/resources/{name}", f"{dest}/{name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--update", required=True)
    parser.add_argument("--dlc", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    base_nsp = args.base
    update_nsp = args.update
    dlc_nsp = args.dlc
    output_dir = args.output

    shutil.rmtree("update", ignore_errors=True)

    base_path = extract_nsp(base_nsp)
    update_path = extract_nsp(update_nsp)
    dlc_path = extract_nsp(dlc_nsp)

    updated_romfs_path = extract_romfs(base_path, update_path)

    dlc_nca_path = find_largest_nca(dlc_path)
    dlc_romfs_path = f"romfs_{Path(dlc_nca_path).stem}"
    if not os.path.exists(dlc_romfs_path):
        process = subprocess.run(
            ["./hactool", dlc_nca_path, "--romfsdir", dlc_romfs_path]
        )
        process.check_returncode()

    copy_files(
        updated_romfs_path,
        dlc_romfs_path,
        output_dir,
        "stringtable.sta",
        "items.xml",
        "itempools.xml",
        "recipes.xml",
        "items_metadata.xml",
    )
