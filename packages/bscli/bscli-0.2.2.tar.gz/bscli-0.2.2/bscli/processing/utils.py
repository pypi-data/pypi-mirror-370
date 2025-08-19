from pathlib import Path


def get_all_files(path: Path) -> list[Path]:
    result = []

    for dir_ in path.iterdir():
        if dir_.is_dir():
            result.extend(get_all_files(dir_))
        elif dir_.is_file():
            result.append(dir_)

    return result


def filter_files(files: list[Path], extensions: list[str]) -> list[Path]:
    return [
        file for file in files if file.suffix.lower().removeprefix(".") in extensions
    ]
