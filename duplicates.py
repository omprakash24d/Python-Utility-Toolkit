import os
import sys
import hashlib
import time
import csv
import multiprocessing
import logging
import argparse

import tqdm

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

def hashfile(path, blocksize=65536, hash_algo='sha256'):
    """Generates the hash of a file in chunks."""
    try:
        hasher = hashlib.new(hash_algo)
        with open(path, "rb") as file:
            buf = file.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = file.read(blocksize)
        return hasher.hexdigest()
    except (FileNotFoundError, PermissionError, OSError) as e:
        log.warning(f"Skipping '{path}' due to an OS error: {e}")
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred while hashing '{path}': {e}")
        return None

def process_file_for_hashing(path, hash_algo):
    """Worker function for multiprocessing pool."""
    return path, hashfile(path, hash_algo=hash_algo)

def find_duplicates(parent_folder, hash_algo='sha256'):
    """
    Finds duplicate files using a two-pass approach.
    Returns a dictionary of duplicate groups, where keys are hashes.
    """
    size_map = {}
    found_duplicates = {}
    
    # Pass 1: Group files by size
    file_list = []
    try:
        for dirName, _, filenames in os.walk(parent_folder):
            for filename in filenames:
                file_path = os.path.join(dirName, filename)
                if os.path.islink(file_path):
                    continue
                file_list.append(file_path)
    except PermissionError as e:
        log.critical(f"Permission denied for '{parent_folder}'. Please run with administrator privileges. Exiting.")
        sys.exit(1)

    log.info("Pass 1: Grouping by file size...")
    with tqdm.tqdm(total=len(file_list), unit='files') as pbar:
        for path in file_list:
            try:
                file_size = os.path.getsize(path)
                size_map.setdefault(file_size, []).append(path)
            except Exception as e:
                log.warning(f"Skipping '{path}' due to an error: {e}")
            pbar.update(1)

    potential_duplicates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    total_to_hash = sum(len(paths) for paths in potential_duplicates.values())
    
    if total_to_hash == 0:
        return {}

    # Pass 2: Hash comparison for files with identical sizes using multiprocessing
    log.info("Pass 2: Hashing potential duplicates with multiprocessing...")
    
    tasks = []
    for paths in potential_duplicates.values():
        for path in paths:
            tasks.append((path, hash_algo))
    
    with multiprocessing.Pool(os.cpu_count()) as pool:
        results = list(tqdm.tqdm(pool.starmap(process_file_for_hashing, tasks), total=len(tasks), unit='files'))
    
    hashes = {}
    for path, file_hash in results:
        if file_hash:
            hashes.setdefault(file_hash, []).append(path)
    
    for file_hash, file_paths in hashes.items():
        if len(file_paths) > 1:
            found_duplicates[file_hash] = file_paths

    return found_duplicates

def save_to_csv(duplicate_groups, output_path):
    """Saves duplicate file pairs to a CSV file."""
    if not duplicate_groups:
        log.info("No duplicates to save.")
        return

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Original File', 'Duplicate File'])
            
            for file_paths in duplicate_groups.values():
                original = file_paths[0]
                for duplicate in file_paths[1:]:
                    writer.writerow([original, duplicate])
        log.info(f"\n✅ Duplicate file report saved to '{output_path}'.")
    except IOError as e:
        log.error(f"Failed to write to CSV file '{output_path}': {e}")

def delete_duplicates(duplicate_groups, dry_run):
    """Prompts for and handles deletion of duplicate files."""
    if not duplicate_groups:
        log.info("No duplicates to delete.")
        return

    log.info("\n--- Duplicate Deletion ---")
    log.info(f"Mode: {'Dry Run' if dry_run else 'Live'}")

    for file_paths in duplicate_groups.values():
        original = file_paths[0]
        duplicates_to_delete = file_paths[1:]
        
        log.info(f"\nOriginal: {original}")
        log.info("Duplicates:")
        for i, dup in enumerate(duplicates_to_delete):
            log.info(f"  [{i+1}] {dup}")

        if dry_run:
            log.info("  -> (Dry Run) These files would be deleted.")
            continue

        choice = input("Delete these duplicates? (y/n, or a to abort all): ").lower()
        if choice == 'y':
            for dup in duplicates_to_delete:
                try:
                    os.remove(dup)
                    log.info(f"  -> Deleted: {dup}")
                except Exception as e:
                    log.error(f"  -> Error deleting {dup}: {e}")
        elif choice == 'a':
            log.info("Deletion aborted by user.")
            break

def interactive_mode():
    """Runs the script in interactive mode, prompting the user for input."""
    log.info("Running in interactive mode.")
    log.info("Enter your options below, or press Ctrl+C to exit.")

    directory_path = input("Enter the full path of the directory to scan: ")
    while not os.path.isdir(directory_path):
        log.error("Invalid path. Please enter a valid directory.")
        directory_path = input("Enter the full path of the directory to scan: ")

    output_filename = input(f"Enter a filename for the CSV report (or press Enter for 'duplicate_files.csv'): ")
    if not output_filename:
        output_filename = 'duplicate_files.csv'
    
    delete_choice = input("Do you want to delete duplicates? (y/n): ").lower()
    delete = delete_choice == 'y'
    dry_run = False
    if delete:
        dry_run_choice = input("Run in dry-run mode to see what would be deleted? (y/n): ").lower()
        dry_run = dry_run_choice == 'y'

    hash_algo_choice = input("Choose a hashing algorithm (md5 or sha256): ").lower()
    hash_algo = 'md5' if hash_algo_choice == 'md5' else 'sha256'
    
    return directory_path, output_filename, delete, dry_run, hash_algo

def main():
    parser = argparse.ArgumentParser(
        description="Finds and manages duplicate files in a specified directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("path", nargs='?', help="The full path of the directory to scan.", type=str, default=None)
    parser.add_argument("-o", "--output", help="The name of the CSV output file.", default="duplicate_files.csv", type=str)
    parser.add_argument("-d", "--delete", action="store_true", help="Prompts to delete duplicate files after scan.")
    parser.add_argument("--dry-run", action="store_true", help="Shows what files would be deleted without removing them.")
    parser.add_argument("--hash-algo", choices=['md5', 'sha256'], default='sha256', help="Hashing algorithm to use for file comparison.")
    
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        parser.print_help()
        directory_path, output_filename, delete, dry_run, hash_algo = interactive_mode()
    else:
        args = parser.parse_args()
        directory_path = args.path
        output_filename = args.output
        delete = args.delete
        dry_run = args.dry_run
        hash_algo = args.hash_algo
        
    if dry_run:
        log.info("Running in Dry Run mode. No files will be deleted.")
    
    if not os.path.isdir(directory_path):
        log.critical(f"Error: Directory '{directory_path}' not found or is not a valid directory.")
        sys.exit(1)
        
    start_time = time.time()
    log.info(f"Starting scan of '{directory_path}'...")
    
    duplicate_groups = find_duplicates(directory_path, hash_algo=hash_algo)

    if not duplicate_groups:
        log.info("\n🎉 No duplicate files found.")
    else:
        num_duplicates = sum(len(v)-1 for v in duplicate_groups.values())
        log.info(f"\n🔍 Found {num_duplicates} duplicate files in {len(duplicate_groups)} groups.")
        save_to_csv(duplicate_groups, output_filename)

    end_time = time.time()
    elapsed_time = end_time - start_time
    log.info(f"Scan completed in {elapsed_time:.2f} seconds.")

    if delete:
        delete_duplicates(duplicate_groups, dry_run)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("\nScan interrupted by user. Exiting.")
        sys.exit(0)