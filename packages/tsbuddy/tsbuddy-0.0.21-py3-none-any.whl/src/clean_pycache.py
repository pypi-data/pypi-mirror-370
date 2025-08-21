import os
import shutil

def clean_pycache_and_pyc(start_dir="."):
    pycache_dirs_deleted = 0
    pyc_files_deleted = 0
    for root, dirs, files in os.walk(start_dir):
        # Delete __pycache__ directories
        for dir_name in dirs:
            if dir_name == "__pycache__":
                full_path = os.path.join(root, dir_name)
                print(f"Deleting directory: {full_path}")
                shutil.rmtree(full_path)
                pycache_dirs_deleted += 1
        # Delete .pyc files
        for file_name in files:
            if file_name.endswith(".pyc"):
                pyc_file_path = os.path.join(root, file_name)
                print(f"Deleting file: {pyc_file_path}")
                os.remove(pyc_file_path)
                pyc_files_deleted += 1
    print(f"Deleted {pycache_dirs_deleted} __pycache__ directories and {pyc_files_deleted} .pyc files.")

# if __name__ == "__main__":
#     clean_pycache_and_pyc(start_dir=".")  # Change to "." if you want to clean the entire project

# for linux run: find . -type d -name "__pycache__" -exec rm -r {} +