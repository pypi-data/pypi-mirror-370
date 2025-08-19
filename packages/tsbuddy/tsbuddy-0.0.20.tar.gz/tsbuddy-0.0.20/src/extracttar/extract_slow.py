
import tarfile
import gzip
from pathlib import Path
import shutil

def extract_tar_archive(tar_path, output_dir):
    """
    Extract a .tar, .tar.gz, or .tgz archive into its parent directory.
    """
    output_dir.mkdir(exist_ok=True)
    with tarfile.open(tar_path, 'r:*') as tar:
        tar.extractall(path=output_dir)
    print(f"[TAR] Extracted: {tar_path}")

def decompress_gz_file(gz_path, output_dir):
    """
    Decompress a single .gz file (not a tar archive).
    """
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / gz_path.with_suffix('').name  # strip .gz extension
    if output_file.exists():
        print(f"[GZ] Skipping existing: {output_file}")
        return
    with gzip.open(gz_path, 'rb') as f_in, open(output_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"[GZ] Decompressed: {gz_path}")

def extract_archives(base_path):
    """
    Recursively extracts all .tar, .tar.gz, .tgz, and .gz files (including nested),
    without reprocessing the same archive twice.
    """
    base_path = Path(base_path)
    processed = set()
    while True:
        archives_found = False
        # Scan fresh every time through the loop to find new nested files
        for archive_path in base_path.rglob('*'):
            archive_path = archive_path.resolve()
            if archive_path in processed or not archive_path.is_file():
                continue
            if archive_path.suffix == '.tar':
                extract_tar_archive(archive_path, archive_path.parent)
                processed.add(archive_path)
                archives_found = True
            elif archive_path.suffixes[-2:] == ['.tar', '.gz'] or archive_path.suffix == '.tgz':
                extract_tar_archive(archive_path, archive_path.parent)
                processed.add(archive_path)
                archives_found = True
            elif archive_path.suffix == '.gz':
                try:
                    with tarfile.open(archive_path, 'r:gz') as tar:
                        extract_tar_archive(archive_path, archive_path.parent)
                        processed.add(archive_path)
                        archives_found = True
                except tarfile.ReadError:
                    decompress_gz_file(archive_path, archive_path.parent)
                    processed.add(archive_path)
                    archives_found = True
        if not archives_found:
            break  # No new archives found → finished

def main():
    extract_archives('.')

if __name__ == '__main__':
    main()
