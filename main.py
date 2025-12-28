import subprocess
import sys
import shutil
from pathlib import Path


def list_mp4(base: Path):
    return [f for f in base.iterdir() if f.is_file() and f.suffix.lower() == ".mp4"]


def is_handbrake_file(file: Path) -> bool:
    return file.stem.endswith("_handbrake")


def restore_metadata(base: Path):
    files = list_mp4(base)
    originals = [f for f in files if not is_handbrake_file(f)]

    for original in originals:
        hb = base / f"{original.stem}_handbrake{original.suffix}"
        if not hb.exists():
            print(f"⚠️  No handbrake output: {original.name}")
            continue

        cmd = [
            "exiftool",
            "-overwrite_original",
            "-P",
            "-TagsFromFile", str(original),
            "-All:All",

            "-CreateDate<${CreateDate}",
            "-ModifyDate<${ModifyDate}",
            "-MediaCreateDate<${MediaCreateDate}",
            "-MediaModifyDate<${MediaModifyDate}",
            "-TrackCreateDate<${TrackCreateDate}",
            "-TrackModifyDate<${TrackModifyDate}",
            "-FileModifyDate<${FileModifyDate}",

            "-GPSLatitude<${GPSLatitude}",
            "-GPSLongitude<${GPSLongitude}",
            "-GPSAltitude<${GPSAltitude}",
            "-GPSCoordinates<${GPSCoordinates}",
            "-LocationInformation<${LocationInformation}",
            "-LocationISO6709<${LocationISO6709}",
            "-Keys:LocationInformation<${Keys:LocationInformation}",

            hb.as_posix()
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✅ Metadata restored: {hb.name}")


def isolate_missing(base: Path):
    target = base / "not-hanbraked"
    target.mkdir(exist_ok=True)

    for f in list_mp4(base):
        if is_handbrake_file(f):
            continue

        hb = base / f"{f.stem}_handbrake{f.suffix}"
        if hb.exists():
            continue

        print(f"📦 Moving (no handbrake): {f.name}")
        shutil.move(f, target / f.name)


def isolate_present(base: Path):
    target = base / "handbraked"
    target.mkdir(exist_ok=True)

    for f in list_mp4(base):
        if is_handbrake_file(f):
            continue

        hb = base / f"{f.stem}_handbrake{f.suffix}"
        if not hb.exists():
            continue

        print(f"📦 Moving (has handbrake): {f.name}")
        shutil.move(f, target / f.name)


def isolate_handbrake_files(base: Path):
    target = base / "handbraked-files"
    target.mkdir(exist_ok=True)

    for f in list_mp4(base):
        if not is_handbrake_file(f):
            continue

        print(f"📦 Moving handbrake file: {f.name}")
        shutil.move(f, target / f.name)


def show_menu():
    print("\nSelect action:")
    print("1. Restore metadata to handbrake outputs")
    print("2. Isolate originals WITHOUT handbrake output")
    print("3. Isolate originals WITH handbrake output")
    print("4. Isolate HANDRAKED video files (_handbrake.mp4)")
    print("0. Exit")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tool.py <folder_path>")
        sys.exit(1)

    base = Path(sys.argv[1])
    if not base.is_dir():
        raise ValueError(f"Invalid directory: {base}")

    while True:
        show_menu()
        choice = input("Enter number: ").strip()

        if choice == "1":
            restore_metadata(base)
        elif choice == "2":
            isolate_missing(base)
        elif choice == "3":
            isolate_present(base)
        elif choice == "4":
            isolate_handbrake_files(base)
        elif choice == "0":
            print("Done.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()