import subprocess
import sys
import shutil
from pathlib import Path


def list_mp4(base: Path):
    return [f for f in base.iterdir() if f.is_file() and f.suffix.lower() == ".mp4"]


def is_handbrake_file(file: Path) -> bool:
    return file.stem.endswith("_handbrake")


def original_name_from_handbrake(hb: Path) -> str:
    # video_handbrake.mp4 -> video.mp4
    return hb.stem.removesuffix("_handbrake") + hb.suffix


def restore_metadata(base: Path):
    files = list_mp4(base)

    originals = [f for f in files if not is_handbrake_file(f)]

    for original in originals:
        expected_hb = base / f"{original.stem}_handbrake{original.suffix}"

        if not expected_hb.exists():
            print(f"⚠️  Missing handbrake output: {original.name}")
            continue

        cmd = [
            "exiftool",
            "-overwrite_original",
            "-P",
            "-TagsFromFile", str(original),
            "-All:All",

            # dates
            "-CreateDate<${CreateDate}",
            "-ModifyDate<${ModifyDate}",
            "-MediaCreateDate<${MediaCreateDate}",
            "-MediaModifyDate<${MediaModifyDate}",
            "-TrackCreateDate<${TrackCreateDate}",
            "-TrackModifyDate<${TrackModifyDate}",
            "-FileModifyDate<${FileModifyDate}",

            # GPS / location
            "-GPSLatitude<${GPSLatitude}",
            "-GPSLongitude<${GPSLongitude}",
            "-GPSAltitude<${GPSAltitude}",
            "-GPSCoordinates<${GPSCoordinates}",
            "-LocationInformation<${LocationInformation}",
            "-LocationISO6709<${LocationISO6709}",
            "-Keys:LocationInformation<${Keys:LocationInformation}",

            expected_hb.as_posix()
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            print(f"✅ Metadata restored: {expected_hb.name}")
        else:
            print(f"❌ Metadata restore failed: {expected_hb.name}")
            print(result.stderr.decode())


def isolate_missing(base: Path):
    target = base / "not-hanbraked"
    target.mkdir(exist_ok=True)

    files = list_mp4(base)
    originals = [f for f in files if not is_handbrake_file(f)]

    for original in originals:
        expected_hb = base / f"{original.stem}_handbrake{original.suffix}"
        if expected_hb.exists():
            continue

        print(f"📦 Moving (NO handbrake): {original.name}")
        shutil.move(original, target / original.name)


def isolate_present(base: Path):
    target = base / "handbraked"
    target.mkdir(exist_ok=True)

    files = list_mp4(base)
    originals = [f for f in files if not is_handbrake_file(f)]

    for original in originals:
        expected_hb = base / f"{original.stem}_handbrake{original.suffix}"
        if not expected_hb.exists():
            continue

        print(f"📦 Moving (HAS handbrake): {original.name}")
        shutil.move(original, target / original.name)


def show_menu():
    print("\nSelect an action:")
    print("1. Restore metadata to handbrake outputs")
    print("2. Isolate videos WITHOUT handbrake output")
    print("3. Isolate videos WITH handbrake output")
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
        elif choice == "0":
            print("Done.")
            break
        else:
            print("Invalid choice. Use numbers, not anger.")


if __name__ == "__main__":
    main()