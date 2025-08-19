import tarfile
import zipfile
from pathlib import Path
import tempfile
import lzma
import shutil


ALL_ARCHIVE_EXTENSIONS = [
    ".tar.gz", ".tar.xz", ".tar.bz2", ".zip", ".tar"
]


def extract_archive(src_path: Path, dst_path: Path):
    """
    Extracts an archive (tar.gz, tar.xz, zip, etc.) to dst_path.
    If the archive contains a single root directory, its contents are flattened.
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path)
    dst_path.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. Extract archive into temporary location
        if src_path.suffix == ".zip":
            with zipfile.ZipFile(src_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
        elif src_path.suffixes[-2:] in [[".tar", ".gz"], [".tar", ".xz"], [".tar", ".bz2"]]:
            with tarfile.open(src_path, 'r:*') as tar_ref:
                tar_ref.extractall(tmpdir)
        elif src_path.suffix == ".tar":
            with tarfile.open(src_path, 'r') as tar_ref:
                tar_ref.extractall(tmpdir)
        else:
            raise ValueError(f"Unsupported archive format: {src_path.suffixes}")

        # 2. Flatten if single top-level directory
        children = list(tmpdir.iterdir())
        if len(children) == 1 and children[0].is_dir():
            inner = children[0]
            for item in inner.iterdir():
                shutil.move(str(item), dst_path / item.name)
        else:
            for item in tmpdir.iterdir():
                shutil.move(str(item), dst_path / item.name)

def decompress_lzma_file(input_path, output_path):
    with lzma.open(input_path, 'rb') as compressed_file:
        with open(output_path, 'wb') as decompressed_file:
            shutil.copyfileobj(compressed_file, decompressed_file)