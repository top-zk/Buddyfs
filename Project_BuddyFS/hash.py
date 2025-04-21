import os
import hashlib
import argparse
from natsort import natsorted


def compute_file_hash(filepath, hash_algorithm='sha256'):
    hash_func = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def read_bin_files_and_compute_hashes(input_dir, hash_algorithm='sha256'):
    bin_files_hashes = {}
    bin_files = [file_name for file_name in os.listdir(input_dir) if file_name.endswith('.bin')]
    bin_files = natsorted(bin_files)

    for file_name in bin_files:
        file_path = os.path.join(input_dir, file_name)
        file_hash = compute_file_hash(file_path, hash_algorithm)
        bin_files_hashes[file_name] = file_hash
    return bin_files_hashes

def main():
    parser = argparse.ArgumentParser(description="Compute hash values of .bin files in a directory.")
    parser.add_argument("input_dir", type=str, help="Directory containing the .bin files.")
    parser.add_argument("--hash_algorithm", type=str, default="sha256", choices=hashlib.algorithms_available,
                        help="Hash algorithm to use (default: sha256).")
    parser.add_argument("--output_file", type=str, default="hashes.txt", help="Output file to save hash values.")
    args = parser.parse_args()

    input_dir = args.input_dir
    hash_algorithm = args.hash_algorithm
    output_file = args.output_file

    hashes = read_bin_files_and_compute_hashes(input_dir, hash_algorithm)

    if not hashes:
        print("No .bin files found in the specified directory.")
    else:
        print("Computed Hashes for .bin files:")
        with open(output_file, "w") as f:
            for file_name, file_hash in hashes.items():
                print(f"{file_name}: {file_hash}")
                f.write(f"{file_name}: {file_hash}\n")
        print(f"Hashes written to {output_file}")


if __name__ == "__main__":
    main()