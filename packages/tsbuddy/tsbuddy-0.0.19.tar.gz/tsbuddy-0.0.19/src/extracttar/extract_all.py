import tarfile
import gzip
from pathlib import Path
import shutil
import re

def extract_tar_archive(tar_path, output_dir):
    """
    Extract tar archive to output_dir.
    If it's an HMON archive (matches known pattern), auto-rename top-level extracted folders/files if needed.
    """
    output_dir.mkdir(exist_ok=True)
    is_hmon = re.match(r"hmondata_chassis\d+(\.\d+)?\.tar\.gz$", tar_path.name)
    with tarfile.open(tar_path, 'r:*') as tar:
        members = tar.getmembers()
        if is_hmon:
            # Find top-level names
            top_level_members = {member.name.split('/')[0] for member in members}
            rename_map = {}
            for name in top_level_members:
                target_path = output_dir / name
                if target_path.exists():
                    # Auto-rename
                    counter = 1
                    while True:
                        new_name = f"{name}_{counter}"
                        new_path = output_dir / new_name
                        if not new_path.exists():
                            rename_map[name] = new_name
                            break
                        counter += 1
            # Adjust paths in tar members
            for member in members:
                parts = member.name.split('/')
                if parts[0] in rename_map:
                    parts[0] = rename_map[parts[0]]
                    member.name = '/'.join(parts)
        tar.extractall(path=output_dir, members=members)
    print(f"Extracted archive {tar_path} to {output_dir}")

def decompress_gz_file(gz_path, output_dir):
    """
    Decompress a single gzip-compressed file.
    """
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / gz_path.with_suffix('').name  # remove .gz extension
    if output_file.exists():
        print(f"Skipping existing: {output_file}")
        return
    with gzip.open(gz_path, 'rb') as f_in, open(output_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"Decompressed: {output_file}")

def extract_archives(base_path):
    """
    Recursively extract all .tar, .tar.gz, .tgz, and .gz files,
    including nested archives, while avoiding repeated extraction.
    """
    base_path = Path(base_path)
    processed = set()
    archives_found = True
    while archives_found:
        archives_found = False
        # --- HMON extraction order logic ---
        hmon_pattern = re.compile(r"hmondata_chassis\d+\.(\d+)\.tar\.gz$")
        hmon_archives = []
        other_archives = []
        for archive_path in base_path.rglob('*'):
            if archive_path in processed:
                continue
            m = hmon_pattern.match(archive_path.name)
            if m:
                hmon_archives.append((int(m.group(1)), archive_path))
            elif (archive_path.suffix == '.tar' or
                  archive_path.suffixes[-2:] == ['.tar', '.gz'] or
                  archive_path.suffix == '.tgz' or
                  archive_path.suffix == '.gz'):
                other_archives.append(archive_path)
        # Sort and extract HMON archives by number
        for _, archive_path in sorted(hmon_archives):
            extract_tar_archive(archive_path, archive_path.parent)
            processed.add(archive_path)
            archives_found = True
        # Extract other archives as before
        for archive_path in other_archives:
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

def main():
    extract_archives('.')

if __name__ == '__main__':
    main()
