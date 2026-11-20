import argparse
import shutil
from pathlib import Path
from collections import Counter

FILE_CATEGORIES = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"
    ],
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx",
        ".xls", ".xlsx", ".csv", ".odt", ".rtf"
    ],
    "Code": [
        ".py", ".js", ".html", ".css", ".java", ".cpp",
        ".c", ".h", ".php", ".json", ".ts", ".jsx"
    ],
    "Audio": [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"
    ],
    "Videos": [
        ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm"
    ],
    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"
    ],
    "Others": []
}


def get_category(file_path):
    extension = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"


def get_unique_path(destination):
    if not destination.exists():
        return destination

    counter = 1

    while True:
        new_name = f"{destination.stem}_{counter}{destination.suffix}"
        new_destination = destination.with_name(new_name)

        if not new_destination.exists():
            return new_destination

        counter += 1


def scan_files(source, recursive=False):
    category_folders = set(FILE_CATEGORIES.keys())

    if recursive:
        all_files = source.rglob("*")
    else:
        all_files = source.iterdir()

    for file_path in all_files:
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(source)

        if relative_path.parts[0] in category_folders:
            continue

        yield file_path


def organize_files(source, recursive=False, apply_changes=False):
    source = Path(source).expanduser().resolve()

    if not source.exists():
        print("Error: Directory does not exist.")
        return

    if not source.is_dir():
        print("Error: The specified path is not a directory.")
        return

    files = list(scan_files(source, recursive))

    if not files:
        print("No files found.")
        return

    statistics = Counter()
    moved_count = 0
    error_count = 0

    print("\n" + "=" * 50)
    print("             FILE ORGANIZER PRO")
    print("=" * 50)

    if apply_changes:
        print("MODE: ORGANIZATION")
    else:
        print("MODE: PREVIEW")

    print(f"Directory: {source}")
    print("-" * 50)

    for file_path in files:
        category = get_category(file_path)
        destination_folder = source / category
        destination = destination_folder / file_path.name

        statistics[category] += 1

        if not apply_changes:
            print(f"[PREVIEW] {file_path.name} -> {category}/")
            continue

        try:
            destination_folder.mkdir(parents=True, exist_ok=True)
            destination = get_unique_path(destination)

            shutil.move(str(file_path), str(destination))

            print(f"[MOVED] {file_path.name} -> {category}/{destination.name}")
            moved_count += 1

        except OSError as error:
            print(f"[ERROR] {file_path.name}: {error}")
            error_count += 1

    print("\n" + "=" * 50)
    print("             ORGANIZATION SUMMARY")
    print("=" * 50)

    for category, count in sorted(statistics.items()):
        print(f"{category:<15} : {count} file(s)")

    print("-" * 50)
    print(f"Total files scanned : {len(files)}")

    if apply_changes:
        print(f"Successfully moved  : {moved_count}")
        print(f"Errors              : {error_count}")
    else:
        print("No files were moved.")
        print("Use --apply to organize the files.")

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Automatically organize files by their extensions."
    )

    parser.add_argument(
        "directory",
        help="Path to the directory you want to organize."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move files instead of previewing."
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan files inside subdirectories."
    )

    args = parser.parse_args()

    organize_files(
        source=args.directory,
        recursive=args.recursive,
        apply_changes=args.apply
    )


if __name__ == "__main__":
    main()
