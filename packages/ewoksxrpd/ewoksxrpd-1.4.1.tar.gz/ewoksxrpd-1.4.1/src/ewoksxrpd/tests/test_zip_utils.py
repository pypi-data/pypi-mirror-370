import os
import warnings
import zipfile
from pathlib import Path


from ..tasks.utils.zip_utils import open_in_zipfile


def test_extracted_file_contents(tmp_path: Path):
    archive_path = tmp_path / "archive.zip"
    extracted_path = tmp_path / "zip_content"
    file_inside_zip = "folder/nested.txt"
    file_contents = b"zip test!"

    with zipfile.ZipFile(archive_path, mode="w") as zipf:
        with open_in_zipfile(zipf, file_inside_zip, mode="w") as f:
            f.write(file_contents)

    _unzip(archive_path, extracted_path)

    extracted_file = extracted_path / file_inside_zip

    assert extracted_file.exists()
    assert extracted_file.read_bytes() == file_contents


def test_permissions_applied(tmp_path: Path):
    archive_path = tmp_path / "archive.zip"
    extracted_path = tmp_path / "unzipped"
    file_inside_zip = "data.txt"

    with zipfile.ZipFile(archive_path, mode="w") as zipf:
        with open_in_zipfile(zipf, file_inside_zip, mode="w") as f:
            f.write(b"abc")

    _unzip(archive_path, extracted_path)

    extracted_file = extracted_path / file_inside_zip
    assert extracted_file.exists()

    with zipfile.ZipFile(archive_path) as zipf:
        info = zipf.getinfo(file_inside_zip)
        perm_bits = (info.external_attr >> 16) & 0o777

    current_umask = os.umask(0)
    os.umask(current_umask)
    expected = 0o666 & ~current_umask

    assert perm_bits == expected


def test_pathlib_support(tmp_path: Path):
    archive_path = tmp_path / "archive.zip"
    extracted_path = tmp_path / "unzipped"
    internal_file = Path("subdir") / "file.txt"
    data = b"12345"

    with zipfile.ZipFile(archive_path, mode="w") as zipf:
        with open_in_zipfile(zipf, internal_file, mode="w") as f:
            f.write(data)

    _unzip(archive_path, extracted_path)

    extracted_file = extracted_path / internal_file
    assert extracted_file.exists()
    assert extracted_file.read_bytes() == data


def test_multiple_files_in_one_archive(tmp_path: Path):
    archive_path = tmp_path / "archive.zip"
    extracted_path = tmp_path / "unzipped"
    contents = (
        ("a.txt", b"AAA"),
        ("b/b.txt", b"BBB1"),
        ("b/b.txt", b"BBB2"),
        ("c/c/c.txt", b"CCC"),
    )
    final_content = {
        "a.txt": b"AAA",
        "b/b.txt": b"BBB2",
        "c/c/c.txt": b"CCC",
    }

    with zipfile.ZipFile(archive_path, mode="w") as zipf:
        for name, content in contents:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Duplicate name:.*")
                with open_in_zipfile(zipf, name, mode="w") as f:
                    f.write(content)

    _unzip(archive_path, extracted_path)

    for name, expected in final_content.items():
        extracted_file = extracted_path / name
        assert extracted_file.exists()
        assert extracted_file.read_bytes() == expected


def _unzip(archive_path: Path, extracted_path: Path) -> None:
    with zipfile.ZipFile(archive_path) as zipf:
        zipf.extractall(path=extracted_path)
